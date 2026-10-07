# Next work unit: join producer entry/body object state

HYPOTHESIS-ID: m5-producer-object-body-join

Use the s4152-qualified phase-specific caller-state split to determine
whether retail's `rs_memset` entry state persists into the `0x800078EC` body
and whether the port's zero-fill context diverges before the store.

Competing hypotheses and the discriminator:

- H-entry-body-shared: retail entry and body preserve the same producer
  object/state. Discriminator: phase-keyed `s0`, `s1`, and pointed-field rows
  match between `0x800078E0` and `0x800078EC`; the port setup/store tuple is
  consistent with that object.
- H-entry-body-split: retail changes producer object/state between entry and
  body, or the port's setup object is not the retail body object.
  Discriminator: an independently phase-keyed `s0`, `s1`, or pointed-field
  difference appears, with the positive controls still valid.
- H-route-invalid: a control or target phase is absent in either arm.
  Discriminator: missing whole-RDRAM control or title/hangar bucket invalidates
  the comparison.

Exact work:

1. Build once with `cmake --build build --config Debug --target
   RogueSquadron64Recomp` after adding only a retail-oracle
   `--pc-field-dump 0x800078EC` arm to the existing s4152 recipe; retain
   `--pc-field-dump 0x800078E0`, source-span watch, whole-RDRAM control, and
   both phase gates.
2. Run the retail oracle and port concurrently for at least 75 seconds from
   `build/`, with SIGKILL cleanup. If the known startup race recurs, use the
   existing two-second launch stagger as the fixed route; do not alter guest,
   audio, wait, cap, predicate, slot, or writeback behavior.
3. Inspect bounded summaries only. Do not use generated port `ra=0` as caller
   evidence.

Expected outcomes: matching entry/body fields selects H-entry-body-shared;
an independently phase-keyed field/object difference selects
H-entry-body-split; missing controls or phases selects H-route-invalid.
