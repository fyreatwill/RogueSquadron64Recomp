# NEXT work unit (s2459) — test whether the generated alternate is equivalent

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Work unit

Run one ground-truth retail/port provenance capture centered on generated
`0x8008F2CC`, comparing its phase/task arguments and destination against the
retail callsite and the existing Factor 5 image identity. Observation only:
do not remap output, alter task data, change gates, or add guards.

## Competing hypotheses and discriminator

- H-AlternateEquivalent: port `0x8008F2CC` has the retail-equivalent arguments
  and joins the image/task identity as the missing second-range consumer.
- H-AlternateBootstrapOnly: it runs in the port, but only clears/bootstrap
  initializes `0x801797B0` and does not consume the image's second range.
- H-AlternateAbsent: the observed port row is not the same reachable path as
  retail's callsite, or is absent under a phase-matched capture.

The discriminator is one same-run tuple table of retail and port callsite PC,
predecessor/arguments, destination/length, VI phase/origin, and image ordinal/
row. Retail whole-RDRAM, exact-range, hangar-phase, and target-PC controls must
fire; the port image arm and its resolver positive control must fire. Matching
retail-equivalent tuples select H-AlternateEquivalent; only bootstrap tuples
with no image join select H-AlternateBootstrapOnly; no phase-matched callsite
is a non-result unless all controls pass.

## Exact commands

1. Inspect `tools/oracle/README.md` and run the retail oracle with
   `--watch-write 0x0:0x800000`, exact ranges `0x167650:0x167C50` and
   `0x1798B0:0x179A48`, `--watch-pc 0x8002BEEC,0x800078EC,0x8008F2CC`,
   `--pc-phase-log-width 0x006AB400:512`, and the verified Start schedule.
2. Inspect existing `m5-static-rsmemset-call` and image-stage joins.
3. Batch any callsite argument fields into the existing regeneration-safe
   probe, build once, and run the image arm with the qualified route,
   `ROGUESQ_AUDIO_UCODE=1`, phase-gated capture, and passive breadcrumbs.
4. Require every control before selecting a hypothesis; record missing
   controls as a non-result.
