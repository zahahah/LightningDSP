# Stable KernelSU update feed

`module.prop` points KernelSU's `updateJson` check at the stable `master/update.json` endpoint. This direct update feed is separate from KernelSU's module-catalog submission and does not publish or install a module by itself.

## Publishing sequence

1. Merge the intended stable module source, `module.prop`, and `changelog.md` into `master`.
2. Build and upload the matching `LightningDSP-<tag>.zip` release asset from that stable source. Publish the GitHub release only after the tag and asset are ready; do not mark beta/experimental builds as stable.
3. The serialized `update-stable-feed.yml` release workflow checks out full master history and runs `tools/update_stable_feed.py`. It verifies the release is published and non-prerelease, its tag commit is an ancestor of master, the tagged `module.prop` has the expected module ID/version/versionCode, and the actual uploaded ZIP contains exactly matching module metadata. It also bounds the ZIP and its parsed metadata, and checks that the tag's raw `changelog.md` is readable.
4. Only then does the workflow update and commit `update.json` on `master`. It changes no other files and uses a non-force push; if master advances concurrently, the push fails closed and the feed remains unchanged.

The generator rejects beta-like tags, drafts, prereleases, untrusted or duplicate ZIP assets, duplicate/malformed `module.prop` keys, metadata disagreement, and versionCode downgrades. Experimental releases therefore cannot replace the stable feed. Existing v6.7 HTML changelog URLs are accepted only as the legacy canonical URL and are migrated to the raw Markdown URL.

The app independently requires the published stable feed, GitHub's latest stable release, the tagged `module.prop`, and the canonical uploaded release ZIP to agree. It compares only the installed module's `versionCode`; unknown metadata and network failures produce no prompt.
