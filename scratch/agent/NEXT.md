# Next work unit: qualify source-construction predecessor/state setup

HYPOTHESIS-ID: m5-source-construction-predecessor-state

Run one rebuilt, phase-gated paired retail-oracle/port capture that follows
the selected caller split into the argument-setup boundary immediately before
port `rs_memset` callsites `0x8008F2CC` (title) and `0x800AB694` (hangar).
Keep the whole-RDRAM positive control and both target VI phase gates. Do not
change guest behavior, audio waits, caps, predicates, slot state, or
writeback.

Competing hypotheses and discriminator:

- H-shared-source-state: retail and port reach equivalent source-construction
  state despite different caller paths. Discriminator: phase-keyed source,
  destination, length, and immediately preceding setup writes match after
  normalizing the caller identity.
- H-port-predecessor-state-split: the caller split brings different setup
  state into the port memset. Discriminator: the port callsite rows join to
  setup arguments or object pointers absent from the retail phase-keyed
  predecessor/context rows.
- H-route-invalid: either arm lacks the whole-RDRAM control or title/hangar
  gate. Discriminator: any required control or phase bucket is missing; keep
  the s4148 caller split as the last qualified result.

Exact commands:

1. Read the existing `s4148` evidence and `tools/oracle/README.md`; arm the
   oracle control and phase gates before interpreting any setup null.
2. Use the existing regeneration-safe `s2240` callsite annotations and add
   one batched phase-scoped setup/entry probe for both port callsites.
3. Build once with `cmake --build build --config Debug --target
   RogueSquadron64Recomp`.
4. Run `zsh scratch/agent/run_s4148_m5_source_callsite.sh` after updating its
   probe env/output tag for the setup join; SIGKILL both processes and inspect
   bounded summaries only.

Expected outcomes: matching normalized setup tuples select
H-shared-source-state; a valid joined setup difference selects
H-port-predecessor-state-split; missing controls or target phases select
H-route-invalid without a causal claim.
