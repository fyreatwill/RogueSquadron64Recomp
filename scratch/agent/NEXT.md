# NEXT work unit (s1147)

HYPOTHESIS-ID: m3-generated-boundary-anomaly

Trace the existing VI-640 state path and its transition trigger before
repeating the corrected NPC boundary test. Do not add a runtime guard.

Competing hypotheses and discriminator before the work unit:

- H1/producer reached: the VI-640 transition producer continues to run but
  never selects or commits the 1024 descriptor; its phase-scoped marker will
  continue after the last width-640 record.
- H2/producer not reached: execution remains active in slot/host/audio work,
  but no VI-640 transition-producer call occurs after the last phase record.
- H3/boundary relevance: the corrected boundary reaches the target phase;
  this requires both a positive task-control E9 row and a VI-1024 marker.

Discriminating measurement: one phase-scoped marker at the existing VI-640
transition producer, collected in the same run as the existing slot-dispatch,
host/audio, E9, and VI-width controls. Producer activity after the last
width-640 record selects H1; a positive control showing the process remains
active with no producer marker selects H2; VI-1024 plus task-control E9 selects
H3. A null producer result is invalid unless the positive activity controls
also fire.

```sh
rg -n 'update_screen|osViSetMode|setViMode|VI_.*1024|\[phase\]' src lib RecompiledFuncs tools | head -120
rg -n 'ROGUESQ_LOG_VI|ROGUESQ_PROBE_PHASE|slot-dispatch|e9-prov|e9-unified' src lib tools docs/debug-trace-env-vars.md | head -160
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_LOG_SLOT_DISPATCH=1 ROGUESQ_LOG_E9_PROVENANCE=1 ROGUESQ_LOG_E9_DISPATCH=1 ROGUESQ_LOG_VI_ARGS=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 190:start 220:start 250:start 300:a' zsh tools/probe.sh scratch/agent/next_s1147 300 0.5
```

Expected outcomes:

- PRODUCER ACTIVE/H1: producer marker continues after the last width-640
  record without VI-1024; identify the selector/commit condition next.
- PRODUCER ABSENT/H2: host/audio/slot positive controls continue but the
  producer marker stops; isolate the state-path caller before another boundary
  test.
- TARGET REACHED/H3: VI-1024 and a positive task-control E9 row both appear;
  then run the corrected-boundary crash comparison.
