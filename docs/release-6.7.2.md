# LightningDSP 6.7.2

This update brings the latest app fixes for work-profile DSP and the SystemUI volume panel. The ARM64 audio driver and `ldspctl` helper are unchanged from 6.7.1.

### Changes

- Include app **1.7.2/code 146**, signed with the existing LightningDSP owner certificate.
- Enable work-profile DSP by default when Android exposes a work profile. Existing saved choices are preserved, and the control is in **Volume Manager → Settings → App controls**.
- Improve work-profile app routing and per-app controls in Session and Fusion.
- Improve the optional SystemUI volume-panel replacement: expansion, lock-screen presentation, touch pass-through and transitions across wake/unlock.

### Requirements and limitations

The module is root-only and its audio driver is ARM64. Work-profile routing depends on Android exposing the profile and a complete package inventory to the authorized root path. The SystemUI replacement requires the LightningDSP SystemUI hook enabled in Vector/LSPosed; stock volume controls remain the fallback if the hook or app surface is unavailable.

Host unit tests and app build checks passed. This does not replace testing on more devices and firmware versions.
