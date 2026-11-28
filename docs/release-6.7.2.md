# LightningDSP 6.7.2-beta.2

This pre-release brings the work-profile and SystemUI volume-panel updates, additional late-load recovery for a verified Samsung Exynos effects factory, and the app's optional libxposed API 102 test build. The ARM64 audio driver and `ldspctl` helper are unchanged from 6.7.1.

### Changes

#### Module and app package
- Include app **1.7.2/code 152**, package `com.lightning.dsp`, signed with the existing owner certificate. The module ZIP carries the legacy-hook root universal APK; the separate API 102 candidate is available from the app Actions artifact for targeted testing.
- Set module version **6.7.2-beta.2/code 214**. The stable KernelSU update feed remains on **6.7.1/code 212**; this pre-release does not move the stable feed.
- Keep the driver and `ldspctl` helper unchanged. Both require Android 16/API 36 or newer; Android 15/API 35 and older cannot resolve a Binder NDK symbol they import. This beta does not fix that native compatibility limitation.

#### Work profiles and per-app controls
- Enable work-profile DSP by default only when Android exposes an eligible profile. Existing saved choices remain unchanged, and the setting is available in **Volume Manager → Settings → App controls**.
- Carry the app's separate work-profile rows and per-app volume/DSP controls into the packaged release. Preserve full Android UIDs and personal/work separation in Session and Fusion.
- Keep Fusion available when Android restricts work-profile package inventory; effect routing still depends on what Android exposes through the supported root path.

#### Fusion exclusions
- On 64-bit ARM64 Android 17/API 37, use a guarded direct AudioPolicyService AIDL update for large Fusion exclusion lists while keeping the relay and its owned remote-submix route.
- The current transport guard allows up to 8,192 UID entries. This is not literally unlimited, and the direct path is not enabled on other Android versions; those continue using the legacy AudioPolicy rule path.
- This path has been exercised on the project's Pixel 10 Pro XL. That does not establish compatibility with every Android 17 OEM build.

#### SystemUI volume panel
- Include the app's optional SystemUI replacement improvements: safer initialization, stock-panel fallback until the LightningDSP surface is ready, content-sized expansion, lock-screen and wake/unlock handling, and touch pass-through outside the visible panel.
- SystemUI replacement still requires its hook enabled in a compatible Vector/LSPosed setup. It is opt-in; normal stock volume behavior remains the fallback.

#### Late-load recovery and diagnostics
- Add a narrowly scoped KernelSU late-load path for the verified Samsung Exynos AIDL effects factory, whose library lookup may use the audio APEX. It checks the live factory, namespace and config, and still requires a verified firmware reload handler before any reload request.
- Preserve the regular boot path and the existing recovery guards. The change does not restart `audioserver` directly, relax SELinux, or prove that an effect registered or processed audio.
- Document the Android 16 minimum for the current native binaries in the README and clarify that a compatible native rebuild is planned, not included.

### Requirements and limitations

This is a root-only module with an ARM64 driver; APK support for multiple ABIs does not make the driver universal. On KernelSU, a mounting metamodule such as Magic Mount or NoMount is required. Global Mode still cannot remove one app from a shared output mix.

The Exynos late-load path has passed host fixtures and packaging checks, but it has not been verified on a Galaxy A57 or other live Exynos firmware. Mounting the driver does not prove effect discovery, attachment or audible processing. Work-profile and SystemUI behavior also need broader device testing.

The app pre-release offers two root universal APKs with the same package, version and owner signature: the legacy Xposed build is the default/module-embedded choice; the libxposed API 102 variant is a separate test candidate for a compatible modern hook framework. They are alternative builds, not two apps. Keep the legacy build if the modern framework does not load the module hooks.

### Corrections in progress before stable

- We are investigating intermittent Fusion distortion reported with SBC Bluetooth audio. LDAC has been stable in the reports so far; the cause is not confirmed and no fix is claimed in this beta.
- We are continuing work on the hooked SystemUI volume panel for Samsung One UI, where it can remain unreliable. It has been stable in testing on the project's Pixel 10 Pro XL, but that does not establish Samsung or device-wide compatibility.
- We are investigating late-mounted audio APEX availability in temp-root environments. The guarded Exynos late-load path in this beta does not yet establish that this separate timing case is fixed.

Host tests and shell checks passed for the module changes; the release package and checksums must also pass validation before publication. None of these checks replaces live device validation. This Actions artifact does not update the stable KernelSU feed or publish a GitHub release.
