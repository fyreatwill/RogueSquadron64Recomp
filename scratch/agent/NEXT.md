# NEXT work unit — repair the image-arm output/state witness control

HYPOTHESIS-ID: m5-output-state-contract-boundary

The new four-PC port schema is present and the silent arm is controlled, but
the image arm emitted zero new rows while older hooks proved its title path
live. Repair this control-path defect, then rerun both arms in one batch. The
oracle baseline is `scratch/agent/s3450_oracle_fixed.log`.

Competing hypotheses and discriminating outcomes:

- `H-ImageHookLive`: image positive control and all four new target buckets fire;
  run the planned phase/ordinal join.
- `H-ImageHookAbsent`: the new hook remains absent while older title hooks fire;
  the gate/control wiring is still wrong and no parity conclusion is allowed.
- `H-FieldDivergence`: both arms are controlled and the first mapped field
  differs; that field selects the missing contract edge.
- `H-JoinMismatch`: both arms are controlled but phase/ordinal cannot join;
  redesign only the join key.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env zsh scratch/agent/run_s3449_m5_state_tuple_context.sh

Keep waits, slots, dispatch, clear behavior, and PCM writeback unchanged. Use
SIGKILL teardown and capture under the existing non-dot output path.
