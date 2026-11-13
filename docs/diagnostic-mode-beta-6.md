# Diagnostic mode — beta 6 local test package

Includes root universal app 1.7.1-beta-6/code 144, signed with the existing
zahahah owner certificate, and module v6.7.1-beta-6/code 211.

**Enable diagnostic mode** is under Settings > Miscellaneous and defaults off.
Its description is: Generates logs to help troubleshoot problems.

- Off: detailed app/relay/hook logs and module shell traces are suppressed.
  Essential warnings, errors, control protocols and safety status remain.
- On: extra local diagnostic messages help investigate playback and setup.
  The app verifies the root-owned property and private marker before saving.
- No PCM/audio recording and no automatic report upload are added.
- Raw native pointers and full root commands are no longer logged.
- Existing logs are not automatically shared. They can contain app/device
  details; review them before manually sending a report.
- App logging changes at runtime; module shell traces follow the choice on
  their next invocation. This switch does not reboot or restart audio.

The root readiness probe remains a functional receipt even when diagnostics are
off. Recovery observations and all one-shot mount/HAL guards are retained.
Global/Session/Fusion audio processing is unchanged. This build is for local
user testing, not a newly published stable GitHub release.

Validation before packaging: root unit tests and release assembly, rootless and
plugin compilation, native sanitizer suites, module host regressions (54 retired
path skips), exact owner signer/package/version and ELF/payload verification.
The new toggle still needs user validation on the physical device. Existing app
lint debt is not represented as fixed by this build.
