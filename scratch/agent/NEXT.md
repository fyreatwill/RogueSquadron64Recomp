# NEXT work unit (after s724: host 0x130 mirror default-off)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

Make the host `DMEM[0xFF0]` mirror default-off and retain a diagnostic
`ROGUESQ_STAGE_HOST_FF0=1` restore arm. Keep 0x130 default-off. Validate both
arms in one build with the existing boot and direct L_11B0 source controls.

## Competing hypotheses

- **H-ff0-default-off-safe:** boot already mirrors `OSTask.data_ptr` into FF0,
  so removing the duplicate host write preserves the route and chunk source.
- **H-ff0-hidden-early-consumer:** a path reads FF0 after boot but before the
  usual generated bootstrap; only default-off loses boot/route control.
- **H-ff0-host-ordering:** the host write affects another phase-local state;
  the restore arm diverges despite matching source rows.

## Discriminating measurement

Run default-off and `ROGUESQ_STAGE_HOST_FF0=1` restore arms concurrently. In
each arm, require visibly distinct `host_stage=skipped/written` boot controls,
the complete `0x05→L_15AC→L_1298→L_1DB0` route, and direct
`L_11B0 chunk130==staged_dram==refill_dram`; compare phase-gated VI progress
and crash markers. Matching controls and progress support H-ff0-default-off-safe;
a missing boot/route/source or a phase divergence only in default-off supports
the corresponding alternative.

Ground-truth boundary: `tools/oracle/README.md` was checked before the prior
staging probes. Its retail watches observe RDRAM CPU accesses only, so it
cannot inspect this RSP-DMEM-local FF0 slot.

## Commands

    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_INLINE_ADVANCE=1 \
      PROBE_KEYS="3:start 7:start" PROBE_PHASE_WIDTH=1024 \
      PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
      zsh tools/probe.sh scratch/agent/s725_ff0_default_off 60 1

    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_INLINE_ADVANCE=1 \
      ROGUESQ_STAGE_HOST_FF0=1 PROBE_KEYS="3:start 7:start" \
      PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
      zsh tools/probe.sh scratch/agent/s725_ff0_restore 60 1
