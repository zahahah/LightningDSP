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

## Mixers test 17: Oboe lookup and route-notification experiments

This build includes an experimental extension of **Improve app compatibility**
for AAudio functions resolved dynamically by an eligible app-local `liboboe.so`.
The JL Mod report identified Oboe 1.7.0 requesting low-latency playback and an
actual FAST track without LightningDSP coverage. The new adapter requests the
existing compatible playback path; it does not apply DSP directly to FAST tracks.
It remains opt-in, requires selecting the app in Vector/LSPosed, and requires
fully restarting the app. Compatibility, latency and audible results on JL Mod
remain unverified on a device. Existing AAudio, OpenSL ES and DirectAudio paths
are retained.

The app also includes a route-notification correction intended to prevent
unchanged output routes from triggering profile reconciliation and rebuilding
effect cards when physical volume changes. Effect headers also stop replaying
their highlight animation on every view bind, while real changes still animate.
The reported blinking can occur with
the Volume Manager enabled or disabled. This is a code-level diagnosis and fix,
not confirmation of the reported behavior on the user's device. Test physical
volume changes on the main page with both manager states, as well as real route
changes and device-profile selection.

App code 105 and module code 184 exceed the withdrawn beta-4 codes so existing
prototype and beta installations can update. The native driver and helper are
unchanged. Host tests and compilation are not audio validation.

## Mixers test 18: Volume Manager lifecycle experiment

This prototype aims to preserve the Volume Manager panel/controller after long
suspensions and recover unexpected loss of its helper using bounded backoff and
verified cleanup. This is a code-level hypothesis and correction, not an observed
runtime cause or confirmation that the reported device behavior is fixed.

The Oboe/JL Mod compatibility and physical-volume effect-header corrections from
test 17 are retained and are also not yet validated on the target device. Host
tests and compilation are not audio or lifecycle validation. Test long suspension,
foreground/background transitions, real volume controls, and ordinary global and
session playback coverage. No native DSP driver or ldspctl change is included.

App code 106 and module code 185 allow an update from test 17 and the withdrawn
beta 4 without lowering installed version codes.

## Mixers test 19: JL Mod soundfont compatibility and mode controls

This artifact embeds the signed root universal APK built from LightningDSP-App
commit `5a690216d85310b219c63f6e71e679f97a74d5eb`. Audio processing now presents
Global Mode and Session Mode as mutually exclusive choices. The opt-in app
compatibility hook also checks JL Mod's app-local TinySoundFont and Sonivox
backend libraries (`libmmapi_tsf.so` and `libmmapi_eas.so`) for Oboe's dynamic
AAudio lookup, in addition to `liboboe.so`. This targets the reported custom
SoundFont path without patching system AAudio or changing the DSP driver.

The affected app must be selected in Vector/LSPosed and **Improve app
compatibility** must be enabled. Restart the app after changing either setting.
This may increase latency. The user's JL Mod soundbank playback has not yet
been validated with this build; host tests and compilation do not prove device
compatibility or audibility. App code 107 and module code 186 are incremented
for upgrade testing. This is an Actions artifact, not a prerelease.

## Mixers test 20: JL Mod partial ELF page compatibility

Embeds LightningDSP-App `1.7.1-mixers-test-19` (code 108), source commit
`93f776d912cbe6814d6f197a92a0aaf1c6c5acd7`. The compatibility hook now allows
an import slot within a load segment's final partial 4 KiB page when no other
load segment shares that page. Exact ELF read bounds, non-executable mappings,
RELRO restoration and third-party hook checks remain enforced. The examined
JL Mod ELF still fails conservatively on 16 KiB pages because that page overlaps
another segment. Device playback and audible DSP remain unverified. Module code
187 allows updates from test 19. This is an Actions artifact, not a prerelease.

## Mixers test 21: remove confirmed inactive session effects

Embeds LightningDSP-App `1.7.1-mixers-test-20` (code 109), source commit
`c54a2bd904bd7df6dfba305a85dfeaa5afe133e0`. In Session Mode, an effect
attachment is now closed after two identity-consistent inactive AudioPolicy
observations and the existing grace interval. Confirmed inactive sessions are
not reattached until a fresh active observation appears. Unknown or incomplete
activity remains conservative. Host tests and build passed; on-device stale
session cleanup and resume behavior still need validation. Module code 188
allows updates from test 20. This is an Actions artifact, not a prerelease.


## Mixers test 23: preserve DSP through brief session gaps

Embeds LightningDSP-App `1.7.1-mixers-test-22` (code 111), source commit
`baaa40fa6e41703e958305fc2382eb278a42cff4`. Session Mode now keeps a per-session effect and its root service
alive for 10 seconds after a close broadcast, and cancels that pending cleanup if
the session reopens. Session-zero close remains immediate. Enhanced session
coverage also keeps short inactive sessions through a 10-second grace while
retaining identity confirmation and eventual cleanup. This is intended to avoid
reinitialization gaps between brief JL Mod soundbank effects; on-device audio
validation is still required. Module code 190 allows updates from test 21. This is
an Actions artifact, not a prerelease.

## Mixers test 24: prepare scoped AAudio sessions before playback

Embeds signed root universal LightningDSP-App `1.7.1-mixers-test-23` (code 112),
source `a85805279c05c5c11ade3117e17ffd3aded62885`. JL Mod logs showed a new session starting
about 922 ms before its DSP was enabled. This prototype requests preparation
while a compatible AAudio stream is opened, rather than relying only on scans
after playback has started. Only observed NONE session requests are temporarily
allocated; observed positive IDs and original builder settings are preserved.

The existing coverage controller independently validates Binder caller UID,
session, normal PCM layout, global-output exclusion and effect ownership. IPC
is only a hint and cannot request arbitrary parameters or privileged commands.
Deadlines are carried across IPC and rechecked before creation/activation.
Never-started preparations are cleaned up. Missing service/provider, unsupported
layout or timeout releases playback; preparation is not universally guaranteed.
Stream opening may be delayed by up to 2.2 seconds, so test responsiveness as
well as short sound effects. Fully restart the scoped emulator after updating.
The existing opt-in compatibility setting and Vector/LSPosed app scope are
required, along with enabled additional-session coverage.

Root tests, native ASan/UBSan tests and release assembly passed. Actual provider
access, first-frame coverage and audible JL Mod behavior require device testing.
Driver/helper and ldsp.control are unchanged. Module code 191 allows updates
from test 23. Actions artifact only, not a prerelease.

## Mixers test 25: accept shared fast rows and expose preparation failure phase

Embeds signed root universal LightningDSP-App `1.7.1-mixers-test-24` (code 113),
source `5068320994a7c2b2e654061ca054e4818006f222`. The AudioFlinger parser now
accepts unrelated `F<n> S` track rows while retaining their non-normal status;
these rows are not DSP targets. A regression test covers inactive shared rows,
normal PCM candidate discovery, and exclusion of active fast/shared-only tracks.

AAudio preparation errors now report a bounded phase, underlying exception class,
and fixed category, without logging exception text, paths, or caller inventories.
The latest user output confirms that `CompatibilityPreparationProvider` and
`com.lightning.dsp.compatibility` are registered. The only provider lookup error
shown is for Huawei's unrelated `com.huawei.appmarket.commondata` authority.
That rules out a missing LightningDSP manifest registration, but does not reveal
why the JL Mod provider call failed. This artifact adds diagnostics; it does not
claim to resolve JL Mod soundbank instability. Capture the new
`LightningDSP_AAudio` preparation line after fully restarting JL Mod.

Root tests and release assembly passed; runtime provider access and consistent
audible processing still require device validation. Driver/helper and
`ldsp.control` are unchanged. Module code 192 allows updates from test 24.
Actions artifact only, not a prerelease.


## Mixers test 26: make the preparation endpoint discoverable

Live Pixel testing with module test 25 showed repeated `provider_unresolved`
errors in JL Mod's audio process. Normal PCM playback and enabled session effects
were observed, but effects were created only after each new stream opened.
That delay is particularly problematic for short sounds. These observations do
not independently establish the cause of the reported distortion.

On Android 11+, the module's existing APK installation now requests Package
Manager's `--force-queryable` override for **LightningDSP only**. This targets
provider discovery from scoped apps without modifying those apps, granting them
package-inventory permissions, or bypassing provider caller/session validation.
The compatibility option remains opt-in and Vector/LSPosed app scope is still
required. Android 10 and older retain the previous install command. If a firmware
rejects the option, installation reports failure and preserves the existing app;
it does not uninstall or silently retry with weakened behavior.

This is the official AOSP install-session override, not the manifest
`forceQueryable` attribute, which is restricted for non-system apps:
https://android.googlesource.com/platform/frameworks/base/+/android11-release/services/core/java/com/android/server/pm/PackageManagerShellCommand.java

Flash the module through the normal installer to apply the install-session
metadata, then fully close and reopen the scoped emulator. Merely extracting the
unchanged APK or restarting the app does not apply this fix. No reinstall or
visibility modification is performed repeatedly by the boot service.

This artifact deliberately reuses the same signed root universal app
`1.7.1-mixers-test-24` (code 113), source
`5068320994a7c2b2e654061ca054e4818006f222`. Native driver/helper and
`ldsp.control` are unchanged. Module code 193 permits upgrades from test 25.
Provider resolution, pre-start preparation success, responsiveness and audible
JL Mod results still require testing after this change. It is not a confirmed
universal fix for distortion. Actions artifact only, not a prerelease.


## Mixers test 27: distinguish playing apps from retained session engines

Embeds signed root universal app `1.7.1-mixers-test-25` (code 114), source
`f1254990f2234d155f992ba145f38c393c7a028a`. Session Mode observes playback
activity even when optional Media session scanning is off; discovery remains
optional. Explicitly inactive sessions are bypassed immediately and are not
reported as Active. Ownership retained for short-gap reuse is not playback.
Ordinary-mode bypassed engines can resume on fresh active evidence without
requiring another OPEN broadcast. Enhanced discovery keeps bounded idle cleanup.

AudioService collection now distinguishes started players from paused, stopped,
released and idle players. Same-session concurrent players remain active when
any player is started. Unknown/failed observations are not advertised as Active,
and do not turn known-idle engines back on. Only a validated complete empty
player section counts as successful silence; malformed and unsupported output
remains unavailable. A fresh matching active observation restores processing.

Global-to-Session transitions explicitly remove session zero. Global baseline
behavior, the scoped compatibility pre-start path, UID/session safeguards and
Volume Manager's explicit-pause media retention are otherwise unchanged.
The test 26 provider-discovery installation correction is preserved.

519 root unit tests passed without failures or skips; rootless/plugin release
Kotlin compilation passed. Runtime pause/resume, background playback, muted but
active tracks and vendor layouts still require device validation. No native DSP
algorithm, driver/helper or ldsp.control changes. Module code 194 allows upgrades
from test 26. Actions artifact only, not a prerelease.

Lint was executed: 680 Error, 67 Fatal and 262 Warning findings. Lint is not
clean; a complete pre-existing-baseline comparison has not been established.

## Mixers test 28: opt-in AAudio session reuse for short sounds

Embeds the signed root universal app `1.7.1-mixers-test-26` (code 115), source
`58ed9f200596d3f712d2eb3dd713fcaeb8d7399b`. The new **Reuse AAudio session**
option is separate from and off by default. It is available only with
**Improve app compatibility** enabled and only affects apps selected in
Vector/LSPosed that load the LightningDSP hook. Fully close and reopen those
apps after changing either setting.

When enabled, the hook records the first successful allocated AAudio session
ID in that app process and reuses it for later builders that explicitly
requested no session. This is intended to let short sound effects share an
already-prepared effect session rather than causing repeated session setup.
An app-provided session ID is never replaced. If opening with the reused ID
fails, the hook clears it and makes one retry with the app's original request.
The existing compatibility option still changes eligible LOW_LATENCY requests
to NONE; session reuse does not itself guarantee that an app's output is
processed or that its audio policy accepts cross-stream session reuse.

Session IDs and effect attachment behavior vary by Android implementation.
This option can affect latency or application audio behavior and has not yet
been validated on-device with JL Mod or other short-sound workloads. Disable it
if streams fail or audio quality/regressions occur. Root tests, native AAudio
hook host tests and universal release compilation passed; runtime audio and
latency remain unverified. Driver, helper and `ldsp.control` are unchanged.
This is an Actions test artifact, not a prerelease.
