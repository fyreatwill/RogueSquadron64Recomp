# Session 3333 — M5 callback registration and voice-child reachability

## Ground truth

The retail Rice oracle ran for 75 seconds with the whole-RDRAM positive
control, callback-table watch, and the validated Start schedule. Controls
passed: 38,859 whole-RDRAM writes, 19 writes in `0x8011A8A4:0x8011A8B4`, and
the route reached title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`.
Retail execution counts were: `0x80019B74` = 6,572,
`initMusyXVoiceTable 0x8009BBA0` = 2, `serviceVoicePoolFrame 0x8009B5A8` =
2,169, and `accumulateVoiceSampleOffset 0x8009BD7C` = 1,163. The child was
reached from `0x80097E48` and `0x80097EBC`.

## Port capture

One 150-second port run reached title at 13.3 seconds and hangar at 25.1
seconds. Positive controls fired in the target phases: VI callback loop and
slot controls, audio task ABI/DMA, guest receive, PCM source and consumer,
filter audit, route state, and key-on instrumentation. The port callback table
poll reported `0x80003250` plus `0x8009123C` in its nonzero slots throughout
the target phases; it never reported `0x8009B5A8`. The dispatcher trace likewise
reported the synth target `0x8009123C`, not `0x8009B5A8`.

No port rows fired for `serviceVoicePoolFrame`, `initMusyXVoiceTable`, or
`accumulateVoiceSampleOffset`; the only `init-voice-sample` rows were the two
host-positive controls. The voice-slot poll did fire in hangar and observed
`max=1`, `active=0`, then `active=1`, so the null is not explained by failure
to reach the phase or by a silent diagnostic.

## Result

This selects `H-PortInitializerMissing` for the qualified port route: retail
reaches the initializer, registers/dispatches `0x8009B5A8`, and reaches the
child, while the port reaches the same phase but installs/dispatches
`0x8009123C` instead. This is two-line evidence from the callback-table state
poll and the dispatcher-target trace, with independent retail PC counts.
It identifies the missing registration/initializer path but does not name the
writer that installs the synth target. No behavior change or mitigation was
made.
