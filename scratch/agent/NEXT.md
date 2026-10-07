# Next work unit: M5 Step 4c qualified 94648 store witness run

HYPOTHESIS-ID: m5-audio-step4c-94648-port-store

Session 4076 repaired the regeneration-safe `s2609` witness. The guest
`0x80094648` store exists in generated source, but s4075 could not observe it
because the witness insertion was skipped by an already-present s2586 marker.

Competing hypotheses:

- H94648-port-store-live: the port executes the indexed store with a valid
  destination/value relation after the fix; the new witness will report rows
  in the title/hangar phase buckets.
- H94648-port-branch: the fixed witness remains silent in the target phase,
  while the complete `startSongSequence` branch trace shows a predicate or
  loop-state divergence before `0x80094648`.
- H94648-port-value: the store executes, but its requested byte or effective
  destination differs from retail; paired rows will show the mismatch.
- Hcoverage: any required retail whole-RDRAM/title/hangar or isolated-port
  phase control is missing, making the null unevaluable.

Discriminating measurement: rebuild after the fixup through the normal
regeneration order, then run one same-build retail-gated isolated image
capture with `PROBE_PHASE_WIDTH=1024` and `PROBE_KEYS_FROM_PHASE=1`. Require
the retail positive controls, the port title/hangar gates, the new
`m5-94648-control`, and phase-keyed `m5-94648` rows. Live selects rows with a
retail-shaped destination/value relation; branch selects valid controls plus
entry/branch rows and zero store rows; value selects store rows with a
destination/value mismatch; coverage selects any missing control.

Exact commands: run the repository's normal regeneration/fixup pipeline from
the companion N64Recomp tree, build the Debug target, then adapt
`scratch/agent/run_s4075_m5_step4_94648.sh` only to assert the new
`m5-94648-control`/row markers. Run from `build/`, capture logs under
`scratch/agent/s4077_m5_step4c_94648`, and SIGKILL both processes. Do not alter
the guest store or any gate.
