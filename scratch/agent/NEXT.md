# NEXT work unit (after s717: TriGen enters L_1DB0 but never reaches L_1E80)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

Implement one regeneration-safe, phase-gated route trace from actual TriGen
continuation L_1DB0 through only its first reachable branch labels. Preserve
the s716 0x05 table/route control and give every candidate exit its own
phase-scoped budget; do not add markers to unrelated inline handlers.

## Competing hypotheses

- **H-trigen-dpc-loop:** live L_1DB0 repeats through its DPC scheduler path
  without reaching L_1E80; the TriGen command's next pointer is not
  finalized on that visit.
- **H-trigen-hidden-exit:** L_1DB0 reaches a non-L_1E80 child/return label
  that reloads or changes the command pointer; that label is the next place
  to measure r17.
- **H-trigen-probe-state-loss:** the active 0x05 probe is overwritten before
  the reload, so entry is real but the missing reload is an instrument defect.

## Discriminating measurement

In one phase-6 task, live 0x05→0x15AC→L_15AC→0x0C→L_1298→L_1DB0 plus a
first-hit row for each static successor/loop label selects DPC loop or the
concrete hidden exit. A phase-6 L_1DB0 entry followed by a reload with the
probe inactive selects state loss. Each possible result names the next exact
measurement; no null is a verdict without the route control.

## Commands

    rg -n -C 12 '^L_1DB0:|^L_1E48:|^L_1E5C:|^L_1E6C:|^L_1E70:|^L_1E80:' build/factor5_ucode/factor5_ucode_recompiled.c
    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_INLINE_ADVANCE=1 \
      PROBE_KEYS="3:start 7:start" PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=300 \
      zsh tools/probe.sh scratch/agent/s718_trigen_l1db0_exit 120 1
