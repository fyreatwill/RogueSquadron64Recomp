# Next work unit: qualify the M5 source-construction caller boundary

HYPOTHESIS-ID: m5-source-construction-caller-boundary

Run one rebuilt, phase-gated paired capture of the qualified retail oracle and
canonical real-audio/LLE/ungated/solo/spin-yield port to replace the invalid
generated `ra=0` caller field at the `0x800078EC` source-construction boundary.
Do not change guest behavior, audio waits, caps, predicates, slot state, or
writeback.

Competing hypotheses and discriminator:

- H-retail-port-caller-split: retail and port execute different source
  construction callers. Discriminator: phase-keyed oracle previous-PC/call
  tuples differ from a valid port call-site attribution while both controls
  reach title 1024 and hangar 512.
- H-shared-caller-different-state: both routes use the same caller but enter
  with different arguments or state. Discriminator: joined caller PCs match,
  while source/destination/length or phase-keyed state differs.
- H-route-invalid: either arm lacks the whole-RDRAM positive control or a
  target phase, so the comparison is unevaluable. Discriminator: missing
  control, title, or hangar gate in the captured logs.

Exact commands:

1. Read `docs/M5-AUDIO-PLAN.md`, the existing source-context recipe, and
   `tools/oracle/README.md`; arm the oracle whole-RDRAM and phase controls first.
2. Build one Debug `RogueSquadron64Recomp` binary carrying every caller-PC
   discriminator and positive-control counter.
3. Run the retail oracle and port capture concurrently with phase gates; kill
   both with SIGKILL and inspect bounded log excerpts, never a stopwatch.

Expected outcomes: matching valid caller tuples select H-shared-caller-
different-state; differing valid tuples select H-retail-port-caller-split;
missing controls or target phases select H-route-invalid and preserve the
previous qualified split without a causal claim.
