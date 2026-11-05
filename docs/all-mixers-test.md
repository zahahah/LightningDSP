# Cover additional sessions: experimental test build

This is an Actions test artifact, not a new stable or prerelease publication.
The existing native driver and ldspctl are unchanged. The app keeps the normal
Global attachment and can add per-session effects for compatible normal playback
on other mixers. It does not force apps onto a shared output.

Test 2 corrects parsing of supported AudioFlinger track rows with spatial-status
columns following latency and adds bounded inspection retries with privacy-safe
diagnostics. A previous dump from the same firmware yields an eligible normal
track after the fix. The later report's raw dumps were not supplied here, so
this does not by itself confirm the cause or the fix on that device.

Test 6 fixes detection of the observed profile by reading the `0x800` flag
from the AudioAttributes field, not the separate stream-flags field.

Test 7 also enables the same conservative session coverage while Global Mode
is off. It does not create a synthetic session-zero/global effect: existing
session effects are respected, and database reservations prevent broadcasts or
the optional scanner from attaching a duplicate effect to an already-covered
session. The setting is visible in both root processing modes. Detection uses
one fresh topology read after the native worker barrier; attachment is still
validated before enable and verified afterward. The additional path and onset
latency have not yet been validated on a device.

Test 5 additionally admits the observed mono music profile used by the tested
WhatsApp voice message (PCM mono, music stream, `UNKNOWN` usage, exact client flag).
Other unknown flag combinations and communication usages remain excluded.

Test 4 also recognizes a paused transitional track state and retains only
attachments confirmed in both changing topology samples; no new attachment is
created from an unstable inspection. Device verification remains necessary.

Test 3 retains an already-owned supplemental effect while its paused playback
session, client identity and uncovered output remain verified. It does not create
new effects for inactive sessions, and rejects invalid or uncertain topology.
The setting is **Cover additional sessions**, shown in both root processing
modes. Playback after returning from another app requires device validation.

The root Audio processing setting **Cover additional sessions** defaults to
on. In Global Mode it supplements uncovered mixers; in Session Mode it covers
supported sessions not already handled by LightningDSP. Disable it to remove
supplemental instances and keep the selected mode's ordinary behavior. Unknown
or inconsistent diagnostics must not be treated as successful coverage. Special/actual FAST, direct, MMAP,
offload and unsupported playback paths are not promised coverage.

The current native helper cannot select among multiple contexts. Before adding
supplemental effects, the app blocks unscoped native writes and drains its
worker. When a session-zero endpoint exists it reapplies that endpoint's
complete current state through AudioEffect; in Session Mode with no such
endpoint, the barrier confirms earlier unscoped writes have drained and no
synthetic global effect is created. While extras exist, each engine uses its
own AudioEffect parameter path. Native control can resume only after extras
are closed and any live session-zero state is fenced. No first-context
selection or blind native broadcast is introduced.

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

## Test 8: AAudio compatibility experiment

In Audio processing, Improve app compatibility is off by default. Select only
incompatible user apps in Vector or LSPosed, enable this option, then restart
the selected app yourself. Its AAudio LOW_LATENCY requests are changed to NONE
when the native hook and root-controlled setting are both active. This can
increase latency and is not limited to streams proven uncovered at creation.
It remains requested for selected apps while the toggle is on, including when
the DSP power is off; turn the option off to stop changing new AAudio streams.
If normal open fails cleanly, the original request is retried. Other processes
and audio backends such as OpenSL ES and Java AudioTrack are not covered.

Hook readiness, Vector/LSPosed compatibility, the target process property
read, actual track mode, global/session ownership, duplicate effects and audible
DSP have not been validated on a device for this build. Hook log readiness
alone does not prove that audio is processed. The scan option is requested by
default in Session Mode, but requires DUMP access and retains broadcast fallback
when that access is unavailable.


## Test 9: safer AAudio experiment

Test 8 was associated with a black screen in NetherSX2 even after the option
was disabled; removing the app from the Vector scope and reopening it restored
operation. This test avoids inline patches of system AAudio functions and does
not load the native compatibility library when the option is disabled before
the target process starts. The cause of the black screen is not yet proven.

When enabled, the experimental ARM64 path changes imports only in eligible app
libraries with the complete supported layout. Some apps and audio backends will
not qualify; opening the app again is necessary after changing the setting or
Vector/LSPosed scope. If problems persist, disable the option, remove the app
from the framework scope and restart it. This has not yet been validated on
the target device.


## Test 14: root universal Volume Manager update

This module artifact embeds the signed Root universal APK built from
LightningDSP-App commit `dd6c1195893b98d3eda17aff3eb5f47544a8c0f6`. It includes
the Volume Manager media play/pause control, three-minute retention only after
a pause initiated by its own button, and theme-aware media controls and per-app
DSP power controls. Session Mode can show DSP power controls on demand or always;
Global Mode displays the setting as unavailable. The floating panel keeps its
center position and adds side clearance when controls need more width. Enabling
media controls explicitly grants only LightningDSP notification-listener access
through root, and refuses to enable the setting if that grant cannot be verified.
No Rootless APK is included. The module driver and helper remain ARM64-only.

The module's dual-entry ARM64 driver and `ldspctl` are unchanged. The app APK is
about 37 MB; the smaller size shown by Actions is the compressed artifact
download size, not the installed APK size. This remains an Actions test artifact,
not a stable or prerelease publication.

The Session Mode DSP power setting has a separate **Always show app DSP power
buttons** option; otherwise controls appear after tapping the LightningDSP card
icon. Its Global Mode setting remains visible but unavailable. The per-app DSP
power control is circular and theme-aware. Media play/pause controls adapt to the
app and floating-panel theme.

The three-minute media-retention timer now starts immediately when the user
presses Pause in the floating player control. It is anchored to that button
press, so the row remains visible while the asynchronous media-session state
catches up. A failed pause command rolls back the retention; natural or
app-originated pauses do not start it. The DSP card power control is centered
directly under its LightningDSP icon when expanded in the floating panel.

## Test 15: experimental OpenSL ES compatibility

Root universal app source commit: `3e9fb7c9416ccd71dec68d4b6598aac8711cc911` (built locally).

The existing opt-in **Improve app compatibility** also attempts to request
`SL_ANDROID_PERFORMANCE_NONE` for eligible mono/stereo PCM OpenSL ES buffer-queue
players in selected user-app processes. Vector or LSPosed scope and a restart of
the selected app are still required. Latency may increase. The native DSP driver
and ldspctl are unchanged.

This is a limited experiment: an app may override the requested mode, use an
unsupported audio backend or ELF layout, resolve imports dynamically, or run
its audio in a process where the hook is not loaded. Failure falls back to the
original path where possible. No claim is made that Eden or Bannerlator is fixed;
confirm track type, effect attachment and audible results on the target device.

## Mixers test 16: DirectAudio child launch experiment

The opt-in Xposed compatibility mode now adapts the documented DirectAudio
performance environment for selected apps when they launch a subprocess, while
leaving microphone-enabled or unknown capture configurations unchanged. Existing
AAudio and OpenSL compatibility paths are retained. Changes apply to new child
processes; restart the affected app after changing the setting. A child can change
its audio configuration later, and compatibility or audibility is not guaranteed.

Reduced-buffer normal tracks can be covered by session effects; actual FAST
tracks are still excluded. This experiment may increase latency and requires
validation on the affected device. The DirectAudio environment contract was
reviewed against [upstream DirectAudio](https://github.com/The412Banner/directaudio/blob/8cc1227bf1b929521e6b2df2509d8b309c4c4f25/directaudio.c).
