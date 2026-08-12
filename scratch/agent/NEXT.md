# NEXT work unit (after s726: early TriGen continuation is normal)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

Phase-latch the complete `L_1DB0` branch/return trace to section 2. This is
one bounded instrumentation change and one phase-gated run, not an
unconstrained reroll.

## Competing hypotheses

- **H-l1db0-valid-chunk-loop:** section-2 TriGen routes advance through
  legitimate chunk sources and return `L_11B0→0x1088→L_1090`.
- **H-l1db0-stale-source:** post-sec2 cap traffic repeats one source/r17
  pair through the otherwise normal return path.
- **H-l1db0-branch-loss:** section 2 selects an unexpected DPC branch or an
  indirect target other than the normal DMA-helper continuation.

## Discriminating measurement

Replace the fixed `phase==3` condition in the s726 branch/return probe with
the existing `g_e9prov.target` section-2 latch, retaining the first 16-row
budget. The existing section-2 latch banner and at least one
`0x05→L_15AC→L_1298→L_1DB0` route are mandatory positive controls. Monotonic
source/r17 progression plus `target=0x1088` supports H-valid; a repeated
source/r17 identifies H-stale; any other branch/target identifies H-branch.
The retail oracle cannot inspect RSP-local DMEM, so mark a qualified runtime
result single-source until joined to a game-visible consequence.

## Commands

    rg -n -C 5 'trigen_branch|trigen_return|g_e9prov.target' src/rsp/dpc_bridge.cpp tools/fixup_factor5_ucode.py
    python3 tools/fixup_factor5_ucode.py build/factor5_ucode/factor5_ucode_recompiled.c
    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_INLINE_ADVANCE=1 \
      ROGUESQ_LOG_E9_PROVENANCE=1 PROBE_KEYS="3:start 7:start" \
      PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
      zsh tools/probe.sh scratch/agent/s727_l1db0_sec2 600 1
