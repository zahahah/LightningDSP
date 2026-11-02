# Apply effects to all mixers: experimental test build

This is an Actions test artifact, not a new stable or prerelease publication.
The existing native driver and ldspctl are unchanged. The app keeps the normal
Global attachment and can add per-session effects for compatible normal playback
on other mixers. It does not force apps onto a shared output.

Test 2 corrects parsing of supported AudioFlinger track rows with spatial-status
columns following latency and adds bounded inspection retries with privacy-safe
diagnostics. A previous dump from the same firmware yields an eligible normal
track after the fix. The later report's raw dumps were not supplied here, so
this does not by itself confirm the cause or the fix on that device.

Test 3 retains an already-owned supplemental effect while its paused playback
session, client identity and uncovered output remain verified. It does not create
new effects for inactive sessions, and rejects invalid or uncertain topology.
The settings label is now **Cover additional sessions**, shown only in Global
Mode. Playback after returning from another app requires device validation.

The root Audio processing setting **Cover additional sessions** defaults to
on and only runs in Global mode. Disable it to remove supplemental instances
and keep the ordinary Global attachment. Unknown or inconsistent diagnostics
must not be treated as successful coverage. Special/actual FAST, direct, MMAP,
offload and unsupported playback paths are not promised coverage.

The current native helper cannot select among multiple contexts. Before adding
supplemental effects, the app blocks unscoped native writes, drains its worker
and reapplies the global's complete current state through AudioEffect. While
extras exist, each engine uses its own AudioEffect parameter path. Native
control can resume only after extras are closed and the current global state is
fenced. No first-context selection or blind native broadcast is introduced.

## Device validation still required

The Android framework normally suspends the global effect when a session effect
is enabled on the same output. The controller must remove its own fallback
when the output becomes covered by Global and never force the global unsuspended.
However, an ACTIVE orphan/global STOPPING transition has a source-level window
for transient overlapping processing. This build does not claim that window is
fixed or that all firmware transitions are free of duplicate processing.

Host tests and compilation are not audio validation. The DuckStation/reference
and simultaneous cases, output migrations/reopen, cleanup and suspension,
profiles/presets, Bluetooth/USB, latency and callback deadlines must be tested
separately on an authorized device. Use a comfortable volume and a modest cut,
not a positive gain boost. No installer, restart or audio-service operation has
been executed on a device by the build process.

The APK alone requires the matching LightningDSP driver already installed.
The module ZIP includes the same signed APK as the standalone artifact. Existing
signature-mismatch and migration confirmation rules remain unchanged.
