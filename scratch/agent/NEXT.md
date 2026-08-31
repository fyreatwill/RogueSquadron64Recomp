# NEXT work unit — capture callback registration and voice-child reachability

HYPOTHESIS-ID: m5-callback-reachability-after-static-audit

Session 3332 proved that `0x80019B74` walks the SI callback table at
`0x8011A8A4`, and that `initMusyXVoiceTable` registers `0x8009B5A8` while
`0x8009BD7C` is a child routine with no registration callsite. Perform one
ground-truth-first reachability capture; do not change behavior or add a
mitigation.

## Competing hypotheses

- `H-PortInitAndChildReached`: port reaches `initMusyXVoiceTable`, dispatches
  `0x8009B5A8`, and reaches the indirect `0x8009BD7C` child in hangar.
- `H-PortInitReachedChildMissing`: port registers/dispatches `0x8009B5A8`,
  but the child edge remains absent while retail reaches it.
- `H-PortInitializerMissing`: positive callback controls fire, but the port
  never reaches `initMusyXVoiceTable` or registers `0x8009B5A8`.

## Discriminator

Ask the independent retail oracle first for the same target-phase controls,
then build one port instrument containing all arms and controls. Retain the
whole-RDRAM positive control, callback-registration source `0x80007910`, VI
dispatcher `0x80019B74`, `initMusyXVoiceTable` entry `0x8009BBA0`,
`serviceVoicePoolFrame` entry `0x8009B5A8`, and `accumulateVoiceSampleOffset`
entry `0x8009BD7C`, plus the existing slot/status rows. Phase-gate at VI-512.

A port row for initializer + dispatcher target + child, with retail rows for
the same PCs, selects the first hypothesis. Initializer/registration and
dispatcher rows without the child select the second. Missing initializer or
registration rows with positive callback controls select the third. Any
missing positive control makes the capture unevaluable and requires a fixed
rerun in the same iteration.

The Sessions 3330–3332 qualification/audit authorize no Step 3 contract
change.
