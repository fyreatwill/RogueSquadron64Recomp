# NEXT work unit — join candidate pointer stores to consumer loads

HYPOTHESIS-ID: m5-state-pointer-writer

Session 3474's qualified store census found title-scoped pointer-valued stores
at `0x800027C4`, `0x800027D0`, `0x800027DC`, and repeated `0x80003C28`, but
did not capture loads or a shared producer/consumer ordinal. Do not repeat the
span census unchanged.

Competing hypotheses and discriminating outcomes:

- `H-InterveningPointerWriter`: a candidate store value becomes the consumer's
  `s1`; a same-ordinal store-to-load match selects this.
- `H-AlternateDispatch`: the consumer `s1` is supplied without a matching
  candidate store; live target rows plus no match select this.
- `H-ObservationInvalid`: controls or target rows fail; no conclusion is
  allowed until the same run's positive controls fire.

Discriminating measurement: one regeneration-safe, title-gated table that
records candidate pointer stores, loads of the actual consumer state source,
the producer input, and all four output/state PCs with a shared in-run ordinal.
The candidate store PCs are `0x800027C4`, `0x800027D0`, `0x800027DC`, and
`0x80003C28`; include the actual `s1` source/load sites discovered from the
generated `rs_free` path. Build all hooks together, retain the four-PC and
pointer-checkpoint positive controls, and use one image-arm run only.

Before building, inspect generated code around `rs_free` and the candidate
sites to identify exact load addresses. Then use the validated route:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

`mkdir -p scratch/agent/s3475_m5_pointer_join && cd build && env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUTOPILOT='3:start,7:start,11:start,15:a,30:start,45:start,60:a' PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_M5_TABLE_SELECTION=1 ROGUESQ_LOG_M5_STATE_POINTER=1 ROGUESQ_LOG_M5_OUTPUT_STATE_FIELDS=1 ROGUESQ_AUDIO_UCODE=1 ./RogueSquadron64Recomp > ../scratch/agent/s3475_m5_pointer_join/run.log 2>&1 & pid=$!; sleep 80; kill -KILL "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true`

Expected outcomes: matching store/load/consumer ordinals select
`H-InterveningPointerWriter`; live controls and consumers without a match
select `H-AlternateDispatch`; absent controls or target rows are
`H-ObservationInvalid` and require redesign, not a null conclusion.
