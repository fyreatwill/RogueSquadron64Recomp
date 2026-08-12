# NEXT work unit (after s723: host 0x130 mirror closed)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

Make the host `DMEM[0x130]` mirror default-off and retain a diagnostic
`ROGUESQ_STAGE_HOST_130=1` restore arm. Validate both arms in one build with
the direct `L_11B0` source probe. Do not change the FF0 default: s722 closed
that duplicate write as an observed source of the wrong TriGen continuation.

## Competing hypotheses

- **H-130-default-off-safe:** `L_1DB0` always seeds 0x130 from FF0 before
  `L_11B0`, so removing the duplicate host write preserves the route.
- **H-130-hidden-early-consumer:** an unqualified early path consumes 0x130
  before L_1DB0; the new default-off arm loses its source/VI control.
- **H-130-host-ordering:** the host write affects another phase-local state;
  the restore arm diverges despite identical direct source rows.

## Discriminating measurement

Run default-off and `ROGUESQ_STAGE_HOST_130=1` restore arms concurrently. In
each arm, require the complete `0x05→L_15AC→L_1298→L_1DB0` route plus direct
`L_11B0 chunk130==staged_dram==refill_dram` as positive controls; compare
phase-gated VI progress and crash markers. Matching controls and VI progress
support H-130-default-off-safe; a missing route/source or a phase divergence
in only default-off supports the corresponding alternative.

Ground-truth boundary: `tools/oracle/README.md` was checked before this
instrument. Its retail watches observe RDRAM CPU accesses only; its dummy-video
configuration cannot inspect this RSP DMEM-local 0x130 slot, so it cannot
provide an independent witness for this measurement.

## Commands

    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_INLINE_ADVANCE=1 \
      PROBE_KEYS="3:start 7:start" PROBE_PHASE_WIDTH=1024 \
      PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
      zsh tools/probe.sh scratch/agent/s724_130_default_off 60 1

    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_INLINE_ADVANCE=1 \
      ROGUESQ_STAGE_HOST_130=1 PROBE_KEYS="3:start 7:start" \
      PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
      zsh tools/probe.sh scratch/agent/s724_130_restore 60 1
