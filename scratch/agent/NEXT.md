# Next work unit: retry source-construction producer/context join

HYPOTHESIS-ID: m5-source-producer-context-join

Use the s4150-qualified shared setup tuples to follow the phase-gated
`0x800078EC` source stores into their immediate caller/return context in one
route-stable paired retail-oracle/port capture. Keep the whole-RDRAM positive
control and title `0x00790400/1024` plus hangar `0x006AB400/512` gates. Do not
change guest behavior, audio waits, caps, predicates, slot state, or writeback;
do not use generated `ra=0` as caller evidence.

Competing hypotheses and the discriminator:

- H-producer-context-shared: the matched setup state feeds equivalent source
  construction. Discriminator: phase-keyed producer caller/return context and
  source-store arguments match between retail and port while the port value
  remains zero.
- H-producer-context-split: the divergence occurs between matched setup and
  the source store. Discriminator: retail and port phase-keyed producer rows
  have different predecessor, object, source, or selector context.
- H-route-invalid: either arm lacks the positive control or a target phase.
  Discriminator: any required control or phase bucket is missing; retain the
  s4150 shared-setup result without a causal producer conclusion.

Exact work:

1. Read `docs/M5-S4150-SOURCE-SETUP-SHARED.md` and the oracle README.
2. Reuse the regeneration-safe source-context and writer probes; batch the
   complete producer caller/context table in one build and one capture.
3. Build with `cmake --build build --config Debug --target
   RogueSquadron64Recomp`.
4. Run the paired oracle/port script for at least 75 seconds with SIGKILL
   cleanup, then inspect bounded summaries only.

Expected outcomes: matching producer context selects H-producer-context-shared;
an independently phase-keyed context difference selects
H-producer-context-split; missing controls or target phases selects
H-route-invalid.
