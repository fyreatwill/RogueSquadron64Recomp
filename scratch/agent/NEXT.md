# NEXT work unit (after s721: boot mirrors the host FF0 stage)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

Build both arms of a narrow FF0-stage A/B: default behavior and a new
`ROGUESQ_SKIP_HOST_FF0_STAGE=1` arm that suppresses only the redundant host
`poke_be32(0xFF0, dl_ptr)` after boot. s721 established that boot already
leaves this exact value; this unit tests whether the host rewrite nevertheless
has a hidden ordering role. Retain the pre/post row and TriGen route/source
row as same-run positive controls. This is source ownership, not a mitigation.

## Competing hypotheses

- **H-ff0-stage-redundant:** without the host rewrite, boot's exact value
  reaches L_1DB0 and the default and suppressed arms have the same source rows.
- **H-ff0-stage-orders-state:** despite equal values at the immediate probe,
  suppressing the rewrite changes a later source row or task outcome.
- **H-ff0-stage-couples-another-writer:** suppression exposes a later DMEM
  rewrite, visible as a source-row value that differs from both boot and task data.

## Discriminating measurement

Run both arms concurrently using the same phase gate. In each arm, the
pre/post row must show boot/task/post values and the existing complete 0x05
route plus `staged_dram==refill_dram` source row must fire. Equal source rows
and task outcomes support H-ff0-stage-redundant; any arm-only divergence
supports H-ff0-stage-orders-state or H-ff0-stage-couples-another-writer.

## Commands

    # Add the env-gated FF0-store arm; build once, then run both arms together.
    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \\
      ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_INLINE_ADVANCE=1 \\
      PROBE_KEYS="3:start 7:start" PROBE_PHASE_WIDTH=1024 \\
      PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \\
      zsh tools/probe.sh scratch/agent/s722_ff0_default 60 1 &
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \\
      ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_INLINE_ADVANCE=1 \\
      ROGUESQ_SKIP_HOST_FF0_STAGE=1 PROBE_KEYS="3:start 7:start" \\
      PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \\
      zsh tools/probe.sh scratch/agent/s722_ff0_skip 60 1 &
    wait
