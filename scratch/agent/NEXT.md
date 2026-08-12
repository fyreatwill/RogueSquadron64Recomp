# NEXT work unit (after s722: FF0 host stage closed)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

Audit the independent host `DMEM[0x130]` chunk-source mirror with one
phase-scoped, same-run boot/pre/post/source probe. Do not change the FF0
default: s722 closed that duplicate write as an observed source of the wrong
TriGen continuation.

## Competing hypotheses

- **H-130-boot-mirror:** boot already establishes `DMEM[0x130]` to the task
  root, so the host mirror is redundant just like FF0.
- **H-130-host-required:** boot leaves 0x130 stale or absent and the host
  mirror is the necessary chunk-source seed.
- **H-130-later-writer:** boot and host agree initially, but a later writer
  changes the chunk source before L_11B0 consumes it.

## Discriminating measurement

Add boot/pre/post 0x130 values to the existing phase-scoped TriGen row and
record the L_11B0 consumer source in the same run. A three-way boot/task/post
equality plus matching consumer supports H-130-boot-mirror; boot mismatch
with post/task equality supports H-130-host-required; a consumer mismatch
after equality supports H-130-later-writer. The existing complete 0x05 route
and `staged_dram==refill_dram` row are mandatory positive controls.

## Commands

    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_INLINE_ADVANCE=1 \
      PROBE_KEYS="3:start 7:start" PROBE_PHASE_WIDTH=1024 \
      PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
      zsh tools/probe.sh scratch/agent/s723_130_source 60 1
