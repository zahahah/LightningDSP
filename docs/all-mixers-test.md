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
