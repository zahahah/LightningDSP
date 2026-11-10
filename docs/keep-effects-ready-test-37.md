# Keep Effects Ready Test 37

This Actions-only test adds **Keep effects ready** below **Media session scanning** in Session Mode. It is off by default. When enabled, LightningDSP can retain effects for already-known audio sessions belonging to the app currently in the foreground or an app with active media controls. It is not restricted to AAudio streams or apps selected in Vector/LSPosed. The existing per-app DSP switch still applies, and Global Mode is unchanged.

The option uses root to grant Usage Access when needed so LightningDSP can identify the foreground app. Media-control apps are discovered from active media sessions when the notification-listener service is available. It does not invent session IDs or create audio sessions; it retains only sessions that the audio system has already exposed. Battery use may increase while the option is enabled.

Please test Session Mode with an ordinary media app and with an app that creates short/repeated sounds. Check app focus changes, pausing/resuming playback, switching apps, and disabling the option. Report whether effects remain available and whether inactive apps disappear from Audio processing active. This is an experimental build; focus/media discovery, cleanup timing, battery impact, and audible continuity have not yet been validated on-device.

The module embeds signed root universal app 1.7.1-focused-session-test-35/code 124. The native driver and helper are unchanged.
