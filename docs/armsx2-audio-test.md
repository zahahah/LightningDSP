# ARMSX2 AAudio Compatibility Test 32

This Actions-only prototype embeds the signed root universal app `1.7.1-armsx2-audio-test-30` (version code 119). ARMSX2's Android source configures Oboe for output with `PerformanceMode::LowLatency` by default. Its Oboe loader resolves AAudio functions through `dlsym`, and Oboe is linked into the page-size-specific `libemucore_4k.so` or `libemucore_16k.so`. The compatibility hook now recognizes those two app-local core libraries and applies its existing AAudio request rewrite there.

## Test setup

Install the app APK and module ZIP from the same Actions artifact. In Vector/LSPosed, enable LightningDSP for ARMSX2, then enable **Improve app compatibility** in LightningDSP and fully close/reopen ARMSX2. Keep ARMSX2's optional **OpenSL ES audio** setting off to test its default Oboe/AAudio path.

The change only rewrites the recognized AAudio low-latency builder request in these two known ARMSX2 libraries. It does not modify audio samples, callbacks, or the emulator source. Expect some extra output latency. Session Mode still depends on the session exposed by the running stream; this compatibility rewrite alone does not promise a per-session effect.

The host hook/GOT tests, app root unit tests, and release build passed. No ARMSX2 device runtime test has validated interception, route selection, latency, or audible DSP. The reported user's exact app version and runtime backend are not available; source behavior can vary by build.
