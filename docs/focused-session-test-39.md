# Focused session test 39

This experimental module embeds the signed root universal LightningDSP app `1.7.1-focused-session-test-37` (version code 126) and uses module version `v6.7.1-focused-session-test-39` (version code 206).

The app changes are intended to prepare Session Mode effects earlier when a player announces an audio-effect session, keep opted-in AAudio session reuse available for `POWER_SAVING` and `NONE` performance modes without changing the requested mode, and retain foreground ownership correctly when activities overlap during transitions.

The AAudio compatibility path only runs in apps selected in Vector/LSPosed with the compatibility option enabled. This build does not change the native DSP driver or `ldsp.control`.

Validation: 554 root release unit tests passed with no failures or skips; AAudio construction and GOT host tests passed with sanitizers; signed root universal APK package, version, authorized certificate, alignment, and four ABIs were verified. Audible startup timing and continuity have not been validated on-device.
