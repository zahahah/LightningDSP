# Samsung Volume Panel Workaround Test 31

This prototype embeds the signed universal root app `1.7.1-samsung-volume-test-29` (version code 118). It adds a narrowly scoped SystemUI hook for Samsung One UI's `VolumeDialogControl.onVolumeChangedW` path. While the root Volume Manager and its overlay permission are active, the hook removes only `FLAG_SHOW_UI`; a short-lived root-owned lease automatically expires if the volume bridge stops. The existing root `IVolumeController` path continues to open the LightningDSP panel.

## Test setup

Install the app APK and module ZIP from the same Actions artifact. In Vector/LSPosed, enable LightningDSP for **System Framework** and **System UI** (`com.android.systemui`), then restart SystemUI or reboot so the new scope and hook load. Enable the Volume Manager and press volume up/down in an ordinary app.

Expected result: LightningDSP's volume overlay appears without the Samsung volume panel. Volume still changes normally. Turning off the Volume Manager or its overlay permission restores the native panel. Safe-volume and other warning callbacks are not intentionally modified.

The automated tests verify the lease lifetime and source-level hook contract. No Samsung device runtime test has been performed for this prototype. If the hook cannot resolve the firmware's `VolumeDialogControl` class/method, it logs a fail-open diagnostic and preserves Samsung's normal panel.
