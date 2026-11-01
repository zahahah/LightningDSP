# Single-output experiment: backend boundary

Status: investigation, not an implemented feature. No routing payload is shipped.

## Evidence received on 2026-11-01

A supplied device report describes two simultaneous PCM MEDIA tracks on separate
MIXER outputs routed to the same speaker. DuckStation used RAW/FAST output flags
but was not observed as a fast track; Spotify used DEEP_BUFFER. Only the latter
output hosted the LightningDSP session-0 chain during simultaneous playback.
The report also describes migration of the same effect between outputs.

These are findings reported by the device investigator, not independently
reproduced here. The stable app/module versions in that report do not invalidate
the routing finding. Their exact output handles must not become configuration.

## Why recreation is not the backend

The app creates an AudioEffect for session 0 without an explicit output handle.
Recreating it delegates output selection to Android again; it neither merges two
simultaneously active mixers nor binds all their tracks to the chosen mixer.
Releasing a working effect before successful replacement also risks losing the
existing endpoint. The experimental automatic recreation path must stay removed.
Keep the beta-3 profile/preset protections and native readiness invalidation.

## AOSP extension examined

The [AudioPolicyService loader][service] tries
`libaudiopolicymanagercustom.so` using a library name, not a guaranteed vendor
path. Failure to load leaves the internal default factories selected. Successful
loading with missing factory symbols is fatal. Returning null from a selected
custom factory does **not** retry the default factory. Thus neither a missing
symbol nor a null-return compatibility guard is a safe runtime rollback.

The [manager header][header] exposes the virtual `getOutputForAttr` entry point,
but `getOutputForDevices` is private/non-virtual, while `selectOutput` and
`selectOutputForMusicEffects` are also non-virtual. Defining same-named methods
in a subclass does not intercept those base calls. A public-entry wrapper that
changes performance flags alone does not guarantee mixer concentration or effect
placement.

These are platform C++ APIs with [internal build dependencies][build], not a
stable NDK plugin ABI. For example, [Android 16's header][android16] and the main
header differ in the `setDeviceConnectionState` signature. ELF class, Android
SDK version, exported symbols and build IDs alone do not prove object/vtable
compatibility. These source observations do not establish the precise loader
or ABI compiled into the reported firmware.

## Conditions before a runnable experiment

- Establish matching platform source/headers and a buildable backend. Do not
  infer C++ layouts from a build ID or add guessed offsets/transactions.
- Restrict resolved-device output candidates for compatible PCM MEDIA/GAME,
  and keep session-0 effect placement consistent with the selected mixer.
- Preserve physical device selection and all functional requirements; leave
  calls, direct/offload, MMAP, bit-perfect, haptic and spatializer paths alone
  unless separately supported. RAW MIXER is not automatically MMAP or DIRECT.
- Prove original-policy delegation and rollback, route changes, concurrency,
  and existing-track behavior without restarting audioserver or weakening
  SELinux. Do not introduce a custom manager on an unverified framework ABI.
- Add the requested default-on preference only with an effective, verified
  capability gate. Saved preference is not evidence of applied routing.
- Keep ldsp.control unchanged. Verify DSP state convergence, latency,
  underruns and actual effect coverage separately on an authorized device.

No toggle, APK or ZIP should be distributed as a single-output implementation
until these conditions are met. The current packaging branch also contains
unfinished beta-4 metadata; it is not a distributable candidate.

## Alternative evaluated: privileged RENDER-only dynamic policy

A Java `AudioPolicy` with a RENDER-only `AudioMix` is a distinct candidate that
does not require a custom native manager or audio capture/replay. In the AOSP
manager examined, registration associates the mix with the first already-open,
nonduplicated output supporting its named physical device. Matching clients can
then receive that stored output before ordinary output selection. This could
concentrate the two reported normal PCM streams; it does not prove effect
placement or select an arbitrary mixer by handle.

It is not safe to translate this directly into a default-on generic rule:

- [Mixing rules][rules] can match usage, UID/user ID and session, but cannot
  exclude output flags, channel masks or rates. Native [mix matching][mixes]
  can match exact-format direct PCM as well as mixed PCM. A compatible session
  allowlist cannot exclude a later incompatible track reusing a session.
- Special requests can open a direct output and change the shared mix's stored
  output. Registration can invalidate a product strategy's tracks.
- A RENDER mix names a physical device; asynchronous route callbacks are not an
  atomic guarantee that a speaker policy stops before headphone/USB/BT routing.

A short-lived, session-restricted device experiment could test registration,
selected mixer/effect placement and unregister/Binder-death cleanup separately.
It would require explicit authorization to change routing and a separate scope:
success would not resolve the flag-exclusion or device-pinning limitations above
and would not unlock the requested default-on generic feature. Do not write a
throwaway routing helper as though it were the missing production backend. Do
not enable Volume Manager to own a policy; DSP routing needs its own lifetime.

The official [build table][builds] consulted on 2026-11-01 maps Android 17 r1 to
a different build than the supplied report. This does not prove matching source
is unavailable, but no exact source/ABI match has been established here. Do not
substitute the public tag as proof of binary compatibility.

[service]: https://android.googlesource.com/platform/frameworks/av/+/refs/heads/main/services/audiopolicy/service/AudioPolicyService.cpp
[header]: https://android.googlesource.com/platform/frameworks/av/+/refs/heads/main/services/audiopolicy/managerdefault/AudioPolicyManager.h
[build]: https://android.googlesource.com/platform/frameworks/av/+/refs/heads/main/services/audiopolicy/managerdefault/Android.bp
[android16]: https://android.googlesource.com/platform/frameworks/av/+/android-16.0.0_r1/services/audiopolicy/managerdefault/AudioPolicyManager.h
[rules]: https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/media/java/android/media/audiopolicy/AudioMixingRule.java
[mixes]: https://android.googlesource.com/platform/frameworks/av/+/refs/heads/main/services/audiopolicy/common/managerdefinitions/src/AudioPolicyMix.cpp
[builds]: https://source.android.com/docs/setup/reference/build-numbers
