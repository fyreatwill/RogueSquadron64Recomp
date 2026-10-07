# Next work unit: join producer caller state fields

HYPOTHESIS-ID: m5-producer-caller-state-join

Use the s4151-qualified context split to compare the caller state around the
retail `rs_memset` entry (`0x800078E0`) and the port's regeneration-safe
`0x800078EC` rows. Keep the whole-RDRAM positive control and title
`0x00790400/1024` plus hangar `0x006AB400/512` gates. Do not change guest
behavior, audio waits, caps, predicates, slot state, or writeback. Do not use
generated port `ra=0` as caller evidence.

Competing hypotheses and the discriminator:

- H-caller-state-shared: retail and port reach the same producer object/state
  through different observable callsite paths. Discriminator: phase-keyed
  `s0`, `s1`, object fields, source/destination, and length match after the
  known callsite differences.
- H-caller-state-split: the callsite difference carries a different producer
  state or object. Discriminator: at least one phase-keyed caller field or
  object/length tuple differs independently of the already observed callsite.
- H-route-invalid: a control or target phase is absent in either arm.
  Discriminator: missing whole-RDRAM control or any required title/hangar
  bucket invalidates the comparison.

Exact work:

1. Add one retail-oracle arm to the existing source-context recipe with
   `--pc-field-dump 0x800078E0` and phase-gated execution logging for
   `0x00790400:1024` and `0x006AB400:512`; retain the source-span watch and
   whole-RDRAM control.
2. Reuse the existing port source-context hook and run both arms from
   `build/` in one paired capture with SIGKILL cleanup.
3. Build once with `cmake --build build --config Debug --target
   RogueSquadron64Recomp`, then run the new paired script for at least 75
   seconds and inspect only bounded summaries.

Expected outcomes: matching caller fields selects H-caller-state-shared;
an independently phase-keyed field/object difference selects
H-caller-state-split; missing controls or phases selects H-route-invalid.
