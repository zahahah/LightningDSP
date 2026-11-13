# Focused session test 40

This experimental module embeds the signed root universal LightningDSP app `1.7.1-focused-session-test-46` (version code 135) and uses module version `v6.7.1-focused-session-test-40` (version code 207).

Since test 39, the app adds the experimental App Mixer mode and its per-app inclusion control, bounded helper ownership monitoring, and earlier preparation of announced Session Mode effects. In Volume Manager, **Hide system apps** now filters only the full manager page; the floating panel keeps showing system apps. Per-app DSP power changes no longer produce a debug toast; effect attachment failures remain available in logs.

The app's universal root APK is signed with the authorized owner certificate and built from committed app source `510198bdb6f01e6942b877a0ff48643a4142fd04`. The module driver and `ldspctl` remain unchanged from test 39. App root unit tests, app release compilation, and universal APK assembly passed. The APK signature/package/version/four-ABI payload were verified. Device UI behavior and App Mixer audio routing remain experimental and require user testing; no runtime success is claimed.
