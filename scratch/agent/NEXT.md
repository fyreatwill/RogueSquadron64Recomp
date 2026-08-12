# NEXT work unit (after s727: section-2 continuation is normal but task-skewed)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

Sample one paired `L_1DB0` branch/return per section-2 target task, preserving
the existing 16-task cap. This is one bounded instrumentation change and one
phase-gated run, not an unconstrained reroll.

## Competing hypotheses

- **H-l1db0-valid-chunk-loop:** section-2 TriGen routes advance through
  legitimate chunk sources and return `L_11B0→0x1088→L_1090`.
- **H-l1db0-stale-source:** post-sec2 cap traffic repeats one source/r17
  pair through the otherwise normal return path.
- **H-l1db0-branch-loss:** section 2 selects an unexpected DPC branch or an
  indirect target other than the normal DMA-helper continuation.

## Discriminating measurement

The s727 latch and route rows are mandatory positive controls. Add per-task
state to `Rs64E9Provenance`: the first eligible branch records one global
sample index and marks that task; its paired return reuses that index. Later
routes in the same task must not consume the cap. Sixteen distinct target task
ids with source/r17 and `target=0x1088` samples establish whether sources
progress (H-valid) or repeat as one stale pair (H-stale); any branch or target
outside the normal values supports H-branch. The retail oracle cannot inspect
RSP-local DMEM, so mark a qualified runtime result single-source until joined
to a game-visible consequence.

## Commands

    rg -n -C 5 'trigen_branch|trigen_return|g_e9prov.target|Rs64E9Provenance' src/rsp/dpc_bridge.cpp
    python3 tools/fixup_factor5_ucode.py build/factor5_ucode/factor5_ucode_recompiled.c
    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_INLINE_ADVANCE=1 \
      ROGUESQ_LOG_E9_PROVENANCE=1 PROBE_KEYS="3:start 7:start" \
      PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
      zsh tools/probe.sh scratch/agent/s727_l1db0_sec2 600 1
