# LightningDSP 6.7.2

This update brings the latest app fixes for work-profile DSP and the SystemUI volume panel. The ARM64 audio driver and `ldspctl` helper are unchanged from 6.7.1.

### Changes

- Include app **1.7.2/code 146**, signed with the existing LightningDSP owner certificate.
- Enable work-profile DSP by default when Android exposes a work profile. Existing saved choices are preserved, and the control is in **Volume Manager → Settings → App controls**.
- Improve work-profile app routing and per-app controls in Session and Fusion.
- Improve the optional SystemUI volume-panel replacement: expansion, lock-screen presentation, touch pass-through and transitions across wake/unlock.
- **Actions test build:** try loading the driver from the Samsung Exynos audio APEX during KernelSU late-load. This runs only when the matching AIDL effects factory and a supported firmware reload handler can be verified. It leaves normal boot unchanged and does not restart audioserver directly.

### Requirements and limitations

The module is root-only and its audio driver is ARM64. Work-profile routing depends on Android exposing the profile and a complete package inventory to the authorized root path. The SystemUI replacement requires the LightningDSP SystemUI hook enabled in Vector/LSPosed; stock volume controls remain the fallback if the hook or app surface is unavailable.

Host unit tests and app build checks passed. This does not replace testing on more devices and firmware versions.

The Exynos path has not been verified on the Galaxy A57. A loaded driver does not guarantee effects on every output. When testing the Actions build, check that LightningDSP opens without a module error and that toggling a clear effect changes Spotify playback in Global Mode.
