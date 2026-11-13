# Fusion Mode integration — module v6.7.1-beta-5

This module integrates the main-branch root universal app 1.7.1-beta-5/code 143.
It is signed with the existing authorized zahahah owner certificate. Same-key
updates retain app data; never uninstall or clear data to resolve a mismatch.

## Changes since beta 4

- Fusion Mode captures eligible audio into a virtual route and processes one
  local DSP relay, with per-app exclusions controlled by Volume Manager DSP
  power buttons. It does not require Vector/LSPosed for ordinary Fusion use.
- Bound nonblocking capture/playback queues, fixed DSP quanta, safe configuration
  and shutdown ordering, and low-latency recovery floors reduce the problems
  observed during the prototype. No pitch or playback-speed compensation.
- Preserve independent Global and Session modes, scoped emulator compatibility,
  AAudio session reuse and authenticated session ownership/focus retention.
- Improve Samsung volume-panel interoperability and remote-volume recovery;
  keep non-Samsung paths and per-app ignore-volume-button behavior intact.
- Show per-app DSP buttons only when their master option is enabled. Offer
  on-demand and always-visible modes; explain unavailability in Global Mode.
- Group Audio Processing settings and add a direct toolbar shortcut with the
  supplied theme-tinted vector icon, also used in Settings.
- New root installations default to Fusion, Volume Manager, per-app DSP controls
  and supported media play/pause controls; existing saved choices survive.
  Notification access uses the existing root-assisted, app-scoped grant.
- Standardize persistent notification titles to Audio Processing; a running
  Fusion relay reports Fusion mode relay working. Keep errors and idle states.
- Keep stable-module update checks, per-version Skip, the update-check setting,
  and KernelSU's stable update feed. This beta does not change the stable feed
  or publish a new stable/prerelease GitHub release automatically.

## Validation and limits

Host regressions, root app tests, signed universal assembly and module payload
checks are required before distribution. Existing app lint debt remains.
The user reported successful Fusion playback on the tested Pixel; device/audio
behavior is not proven for all apps, effects, routes, firmware or soundbanks.
Fusion has capture/playback latency; no zero-latency guarantee is made.

The universal APK has four app ABIs. The matched module HAL driver remains
ARM64-only; driver and ldspctl hashes are unchanged. No recovery/mount/SELinux
safety guards were relaxed. KernelSU environments require a mounting metamodule
such as Magic Mount or NoMount. Other root managers use their supported mount
mechanism. This package does not install itself or reboot a device.
