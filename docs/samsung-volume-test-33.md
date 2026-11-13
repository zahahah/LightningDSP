# Samsung Volume Panel Test 33

This experimental module includes the root universal app with the One UI volume controller class correction contributed in PR #1. Enable LightningDSP for System UI in LSPosed/Vector as required, and restart System UI only as directed by the framework. Test volume buttons normally and with Ignore volume buttons enabled for an app. Test switching quickly between apps. Foreground detection is periodic, so transitions are not yet guaranteed. If the volume panel is unavailable, disable the LightningDSP Volume Manager. Test also on non-Samsung devices. Driver and helper are unchanged.

## App source attribution

The APK was built from `11bb18274a4e22388e693833d51836f2152529f5`. The current app branch commit is `fa4b353642bda9226fb3dc2ebd851739a6018fc3`, amended only to correct the co-author email. Both have the same source tree `a43ad2d8bfcb136c30f896b9b4fe438600e2b679`. The APK was not rebuilt.
