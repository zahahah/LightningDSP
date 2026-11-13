#!/usr/bin/env python3
"""Generate KernelSU update metadata only from a verified stable release archive."""
import io
import json
from pathlib import Path
import re
import stat
import subprocess
import tempfile
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from zipfile import BadZipFile, ZipFile

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "zahahah/LightningDSP"
API_URL = f"https://api.github.com/repos/{REPOSITORY}/releases/latest"
MODULE_ID = "ainur_lightningdsp"
STABLE_VERSION = re.compile(r"v\d+\.\d+(?:\.\d+)?")
MAX_API_BYTES = 2 * 1024 * 1024
MAX_MODULE_PROP_BYTES = 64 * 1024
MAX_ZIP_BYTES = 256 * 1024 * 1024
MAX_ZIP_ENTRIES = 10_000
MAX_UNCOMPRESSED_ZIP_BYTES = 1024 * 1024 * 1024


def properties(text):
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key in result:
            raise ValueError(f"duplicate module property: {key}")
        result[key] = value
    return result


def module_identity(module_prop, tag):
    if len(module_prop.encode("utf-8")) > MAX_MODULE_PROP_BYTES:
        raise ValueError("module.prop exceeds the size limit")
    props = properties(module_prop)
    if props.get("id") != MODULE_ID:
        raise ValueError("module.prop has the wrong module id")
    if props.get("version") != tag:
        raise ValueError("module.prop version does not match the stable release tag")
    code = props.get("versionCode", "")
    if not code.isdigit() or int(code) <= 0:
        raise ValueError("module.prop versionCode is missing or invalid")
    return props["id"], props["version"], int(code)


def validate_current_feed(feed):
    version = feed.get("version")
    code = feed.get("versionCode")
    if not isinstance(version, str) or not STABLE_VERSION.fullmatch(version):
        raise ValueError("existing stable feed has an invalid version")
    if type(code) is not int or code <= 0:
        raise ValueError("existing stable feed has an invalid versionCode")
    expected_zip = f"https://github.com/{REPOSITORY}/releases/download/{version}/LightningDSP-{version}.zip"
    expected_changelogs = {
        f"https://github.com/{REPOSITORY}/releases/tag/{version}",
        f"https://raw.githubusercontent.com/{REPOSITORY}/{version}/changelog.md",
    }
    if feed.get("zipUrl") != expected_zip or feed.get("changelog") not in expected_changelogs:
        raise ValueError("existing stable feed URLs are not trusted release URLs")
    return version, code


def release_tag(release):
    if release.get("draft") is not False or release.get("prerelease") is not False:
        raise ValueError("release is a draft or prerelease")
    if type(release.get("id")) is not int or release["id"] <= 0:
        raise ValueError("release does not have a valid GitHub release id")
    tag = release.get("tag_name")
    if not isinstance(tag, str) or not STABLE_VERSION.fullmatch(tag):
        raise ValueError("release tag is not a stable LightningDSP version")
    return tag


def verify_tag_is_on_master(tag, repo_root=ROOT):
    """Reject stable-looking tags whose commit was never merged into master."""
    if not STABLE_VERSION.fullmatch(tag):
        raise ValueError("release tag is not a stable LightningDSP version")
    remote_master = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", "refs/remotes/origin/master"],
        cwd=repo_root, check=False,
    )
    master_ref = "refs/remotes/origin/master" if remote_master.returncode == 0 else "refs/heads/master"
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", f"{tag}^{{commit}}", master_ref],
        cwd=repo_root, capture_output=True, check=False,
    )
    if result.returncode != 0:
        raise ValueError("release tag commit is not an ancestor of master")


def release_asset_url(release):
    tag = release_tag(release)
    asset_name = f"LightningDSP-{tag}.zip"
    asset_url = f"https://github.com/{REPOSITORY}/releases/download/{tag}/{asset_name}"
    assets = release.get("assets")
    if not isinstance(assets, list):
        raise ValueError("release assets are missing")
    archives = [asset for asset in assets if isinstance(asset, dict) and
                isinstance(asset.get("name"), str) and
                re.fullmatch(r"LightningDSP-.*\.zip", asset["name"], re.I)]
    matching = [asset for asset in archives if asset.get("name") == asset_name]
    if len(archives) != 1:
        raise ValueError("release must contain exactly one LightningDSP ZIP asset")
    if (len(matching) != 1 or matching[0].get("state") != "uploaded" or
            matching[0].get("browser_download_url") != asset_url):
        raise ValueError("stable release does not contain the expected uploaded HTTPS module ZIP")
    return asset_url


def module_prop_from_zip(archive_data):
    if len(archive_data) > MAX_ZIP_BYTES:
        raise ValueError("release ZIP exceeds the download size limit")
    try:
        with ZipFile(io.BytesIO(archive_data)) as archive:
            entries = archive.infolist()
            if len(entries) > MAX_ZIP_ENTRIES:
                raise ValueError("release ZIP contains too many entries")
            if sum(entry.file_size for entry in entries) > MAX_UNCOMPRESSED_ZIP_BYTES:
                raise ValueError("release ZIP exceeds the expanded size limit")
            module_props = [entry for entry in entries if entry.filename.lower() == "module.prop"]
            if len(module_props) != 1 or module_props[0].filename != "module.prop":
                raise ValueError("release ZIP must contain exactly one root module.prop")
            info = module_props[0]
            file_type = stat.S_IFMT(info.external_attr >> 16)
            if file_type not in (0, stat.S_IFREG):
                raise ValueError("release ZIP module.prop must be a regular file")
            if info.file_size > MAX_MODULE_PROP_BYTES:
                raise ValueError("release ZIP module.prop exceeds the size limit")
            data = archive.read(info)
            if len(data) > MAX_MODULE_PROP_BYTES:
                raise ValueError("release ZIP module.prop exceeds the size limit")
            return data.decode("utf-8")
    except (BadZipFile, RuntimeError, OSError) as error:
        raise ValueError("release asset is not a valid readable ZIP archive") from error


def stable_feed(release, tagged_module_prop, archive_data, current_feed):
    """Validate stable tag metadata and the actual released ZIP before generating feed JSON."""
    current_version, current_code = validate_current_feed(current_feed)
    tag = release_tag(release)
    zip_url = release_asset_url(release)
    tagged_identity = module_identity(tagged_module_prop, tag)
    archived_identity = module_identity(module_prop_from_zip(archive_data), tag)
    if archived_identity != tagged_identity:
        raise ValueError("release ZIP module identity/version differs from its immutable tag source")
    version_code = tagged_identity[2]

    if version_code < current_code:
        raise ValueError("refusing to downgrade the stable update feed")
    candidate = {
        "version": tag,
        "versionCode": version_code,
        "zipUrl": zip_url,
        "changelog": f"https://raw.githubusercontent.com/{REPOSITORY}/{tag}/changelog.md",
    }
    if version_code == current_code and candidate != current_feed:
        legacy_changelog = f"https://github.com/{REPOSITORY}/releases/tag/{tag}"
        if not (tag == current_version and current_feed.get("changelog") == legacy_changelog and
                {**current_feed, "changelog": candidate["changelog"]} == candidate):
            raise ValueError("refusing to replace the stable feed with a different release at the same versionCode")
    if version_code == current_code and tag != current_version:
        raise ValueError("stable release versionCode must increase monotonically")
    return candidate


def fetch_bytes(url, limit):
    request = Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "LightningDSP-stable-feed",
    })
    with urlopen(request, timeout=30) as response:
        final_url = urlsplit(response.geturl())
        if response.geturl() != url and not (
                urlsplit(url).hostname == "github.com" and final_url.scheme == "https" and
                final_url.username is None and final_url.password is None and
                final_url.hostname in {"release-assets.githubusercontent.com", "objects.githubusercontent.com"}):
            raise ValueError("GitHub release resource redirected unexpectedly")
        content_length = response.headers.get("Content-Length")
        if content_length and content_length.isdigit() and int(content_length) > limit:
            raise ValueError("GitHub release resource exceeds the size limit")
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError("GitHub release resource exceeds the size limit")
    return data


def fetch_latest_release():
    return json.loads(fetch_bytes(API_URL, MAX_API_BYTES).decode("utf-8"))


def fetch_tagged_module_prop(tag):
    return fetch_bytes(f"https://raw.githubusercontent.com/{REPOSITORY}/{tag}/module.prop",
                       MAX_MODULE_PROP_BYTES).decode("utf-8")


def verify_changelog(url):
    if not url.startswith(f"https://raw.githubusercontent.com/{REPOSITORY}/") or not url.endswith("/changelog.md"):
        raise ValueError("generated changelog URL is not a trusted raw Markdown URL")
    if not fetch_bytes(url, MAX_API_BYTES):
        raise ValueError("stable release changelog is empty")


def write_feed(feed, path=ROOT / "update.json"):
    """Atomically replace update.json only after all validation has passed."""
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                     prefix=path.name + ".", delete=False) as temporary:
        temp_path = Path(temporary.name)
        json.dump(feed, temporary, indent=2)
        temporary.write("\n")
    try:
        temp_path.replace(path)
    finally:
        temp_path.unlink(missing_ok=True)


def main():
    try:
        current = json.loads((ROOT / "update.json").read_text(encoding="utf-8"))
        release = fetch_latest_release()
        tag = release_tag(release)
        verify_tag_is_on_master(tag)
        tagged_module_prop = fetch_tagged_module_prop(tag)
        archive = fetch_bytes(release_asset_url(release), MAX_ZIP_BYTES)
        candidate = stable_feed(release, tagged_module_prop, archive, current)
        verify_changelog(candidate["changelog"])
        write_feed(candidate)
    except (OSError, URLError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit(f"Stable update feed unchanged: {error}") from error
    print(f"Updated stable module feed to {candidate['version']} ({candidate['versionCode']})")


if __name__ == "__main__":
    main()
