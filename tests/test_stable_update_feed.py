import json
from io import BytesIO
from pathlib import Path
import subprocess
import tempfile
import unittest
import warnings
from unittest.mock import patch
from zipfile import ZipFile

import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import update_stable_feed as feed


CURRENT = {
    "version": "v6.7",
    "versionCode": 159,
    "zipUrl": "https://github.com/zahahah/LightningDSP/releases/download/v6.7/LightningDSP-v6.7.zip",
    "changelog": "https://github.com/zahahah/LightningDSP/releases/tag/v6.7",
}


def release(tag="v6.8", draft=False, prerelease=False, code=160, asset_url=None):
    name = f"LightningDSP-{tag}.zip"
    return ({
        "id": 12345,
        "draft": draft,
        "prerelease": prerelease,
        "tag_name": tag,
        "assets": [{
            "name": name,
            "state": "uploaded",
            "browser_download_url": asset_url or
                f"https://github.com/zahahah/LightningDSP/releases/download/{tag}/{name}",
        }],
    }, f"id=ainur_lightningdsp\nversion={tag}\nversionCode={code}\n")


def module_zip(module_prop, duplicate=False):
    buffer = BytesIO()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with ZipFile(buffer, "w") as archive:
            archive.writestr("module.prop", module_prop)
            if duplicate:
                archive.writestr("module.prop", module_prop)
    return buffer.getvalue()


def archive_with_entries(entries):
    buffer = BytesIO()
    with ZipFile(buffer, "w") as archive:
        for name, value in entries:
            archive.writestr(name, value)
    return buffer.getvalue()


class StableUpdateFeedTests(unittest.TestCase):
    def test_generates_kernel_su_feed_for_matching_stable_release(self):
        release_data, props = release()
        self.assertEqual(feed.stable_feed(release_data, props, module_zip(props), CURRENT), {
            "version": "v6.8",
            "versionCode": 160,
            "zipUrl": "https://github.com/zahahah/LightningDSP/releases/download/v6.8/LightningDSP-v6.8.zip",
            "changelog": "https://raw.githubusercontent.com/zahahah/LightningDSP/v6.8/changelog.md",
        })

    def test_rejects_drafts_prereleases_and_beta_tags(self):
        for kwargs in ({"draft": True}, {"prerelease": True}, {"tag": "v6.8-beta-1"}):
            with self.subTest(kwargs=kwargs):
                release_data, props = release(**kwargs)
                with self.assertRaises(ValueError):
                    feed.stable_feed(release_data, props, module_zip(props), CURRENT)

    def test_rejects_mismatched_or_invalid_module_metadata(self):
        release_data, props = release()
        for bad_props in (
            props.replace("ainur_lightningdsp", "other"),
            props.replace("version=v6.8", "version=v6.9"),
            props.replace("versionCode=160", "versionCode=0"),
            props + "versionCode=161\n",
        ):
            with self.subTest(props=bad_props), self.assertRaises(ValueError):
                feed.stable_feed(release_data, bad_props, module_zip(props), CURRENT)

    def test_rejects_untrusted_or_missing_module_assets(self):
        release_data, props = release(asset_url="http://evil.invalid/module.zip")
        with self.assertRaisesRegex(ValueError, "expected uploaded HTTPS module ZIP"):
            feed.stable_feed(release_data, props, module_zip(props), CURRENT)
        release_data, props = release()
        release_data["assets"] = []
        with self.assertRaises(ValueError):
            feed.stable_feed(release_data, props, module_zip(props), CURRENT)

    def test_never_downgrades_or_changes_release_at_same_code(self):
        release_data, props = release(code=158)
        with self.assertRaisesRegex(ValueError, "downgrade"):
            feed.stable_feed(release_data, props, module_zip(props), CURRENT)
        release_data, props = release(tag="v6.7.1", code=159)
        with self.assertRaisesRegex(ValueError, "same versionCode"):
            feed.stable_feed(release_data, props, module_zip(props), CURRENT)

    def test_migrates_only_canonical_legacy_v67_changelog_url(self):
        release_data, props = release(tag="v6.7", code=159)
        migrated = feed.stable_feed(release_data, props, module_zip(props), CURRENT)
        self.assertEqual(migrated["versionCode"], 159)
        self.assertEqual(migrated["changelog"],
                         "https://raw.githubusercontent.com/zahahah/LightningDSP/v6.7/changelog.md")

    def test_changelog_is_verified_as_nonempty_trusted_raw_markdown(self):
        with patch.object(feed, "fetch_bytes", return_value=b"# v6.8 release notes") as fetch:
            feed.verify_changelog("https://raw.githubusercontent.com/zahahah/LightningDSP/v6.8/changelog.md")
            fetch.assert_called_once()
        with patch.object(feed, "fetch_bytes", return_value=b""):
            with self.assertRaisesRegex(ValueError, "changelog is empty"):
                feed.verify_changelog("https://raw.githubusercontent.com/zahahah/LightningDSP/v6.8/changelog.md")
        with self.assertRaisesRegex(ValueError, "not a trusted raw Markdown URL"):
            feed.verify_changelog("https://github.com/zahahah/LightningDSP/releases/tag/v6.8")

    def test_beta_module_checkout_cannot_replace_stable_feed(self):
        release_data, _ = release(tag="v6.8", code=208)
        experimental_props = "id=ainur_lightningdsp\nversion=v6.7.1-focused-session-test-41\nversionCode=208\n"
        with self.assertRaisesRegex(ValueError, "does not match"):
            feed.stable_feed(release_data, experimental_props, module_zip(experimental_props), CURRENT)

    def test_validates_metadata_inside_actual_release_zip(self):
        release_data, tagged_props = release()
        for archive_props in (
            tagged_props.replace("ainur_lightningdsp", "other"),
            tagged_props.replace("versionCode=160", "versionCode=161"),
            tagged_props + "versionCode=162\n",
        ):
            with self.subTest(archive_props=archive_props), self.assertRaises(ValueError):
                feed.stable_feed(release_data, tagged_props, module_zip(archive_props), CURRENT)
        with self.assertRaisesRegex(ValueError, "exactly one root module.prop"):
            feed.stable_feed(release_data, tagged_props, module_zip(tagged_props, duplicate=True), CURRENT)
        with self.assertRaisesRegex(ValueError, "not a valid readable ZIP"):
            feed.stable_feed(release_data, tagged_props, b"not a zip", CURRENT)
        with self.assertRaisesRegex(ValueError, "module.prop exceeds"):
            feed.stable_feed(release_data, tagged_props, module_zip("x" * (feed.MAX_MODULE_PROP_BYTES + 1)), CURRENT)

    def test_release_zip_limits_are_enforced_before_metadata_read(self):
        release_data, props = release()
        zip_data = module_zip(props)
        with patch.object(feed, "MAX_ZIP_BYTES", len(zip_data) - 1), \
                self.assertRaisesRegex(ValueError, "download size limit"):
            feed.stable_feed(release_data, props, zip_data, CURRENT)
        multi_entry = archive_with_entries([("module.prop", props), ("extra", "x")])
        with patch.object(feed, "MAX_ZIP_ENTRIES", 1), \
                self.assertRaisesRegex(ValueError, "too many entries"):
            feed.stable_feed(release_data, props, multi_entry, CURRENT)
        with patch.object(feed, "MAX_UNCOMPRESSED_ZIP_BYTES", 1), \
                self.assertRaisesRegex(ValueError, "expanded size limit"):
            feed.stable_feed(release_data, props, zip_data, CURRENT)

    def test_published_feed_metadata_is_stable_and_uses_raw_changelog(self):
        current = json.loads((ROOT / "update.json").read_text())
        self.assertEqual(current["version"], "v6.7")
        self.assertEqual(current["versionCode"], 159)
        self.assertEqual(current["changelog"],
                         "https://raw.githubusercontent.com/zahahah/LightningDSP/v6.7/changelog.md")

    def test_stable_feed_is_written_atomically_only_after_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "update.json"
            path.write_text(json.dumps(CURRENT))
            release_data, props = release()
            feed.write_feed(feed.stable_feed(release_data, props, module_zip(props), CURRENT), path)
            self.assertEqual(json.loads(path.read_text())["versionCode"], 160)
            self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_release_workflow_serializes_stable_only_feed_updates(self):
        workflow = (ROOT / ".github/workflows/update-stable-feed.yml").read_text()
        self.assertIn("types: [published]", workflow)
        self.assertIn("fetch-depth: 0", workflow)
        self.assertIn("github.event.release.prerelease == false", workflow)
        self.assertIn("group: lightningdsp-stable-module-feed", workflow)
        self.assertIn("python3 tools/update_stable_feed.py", workflow)
        self.assertIn("git merge-base --is-ancestor origin/master HEAD", workflow)
        self.assertIn("git push origin HEAD:master", workflow)

    def test_release_tag_must_be_an_ancestor_of_master(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            def git(*args):
                subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)

            git("init", "-b", "master")
            git("config", "user.name", "Test")
            git("config", "user.email", "test@example.invalid")
            (repo / "tracked.txt").write_text("master base")
            git("add", "tracked.txt")
            git("commit", "-m", "base")
            git("tag", "v6.8")
            feed.verify_tag_is_on_master("v6.8", repo)

            git("checkout", "--orphan", "experiment")
            (repo / "experiment.txt").write_text("branch-only release")
            git("add", "experiment.txt")
            git("commit", "-m", "experimental")
            git("tag", "v6.9")
            git("checkout", "master")
            with self.assertRaisesRegex(ValueError, "not an ancestor of master"):
                feed.verify_tag_is_on_master("v6.9", repo)


if __name__ == "__main__":
    unittest.main()
