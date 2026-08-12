# NEXT work unit (after s716: TriGen reaches resident relay and L_1DB0)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

Implement one regeneration-safe, phase-gated `r17` step trace only inside
actual TriGen continuation `L_1DB0`. Preserve the s716 `0x05` table/route
control and its dedicated phase-scoped budget; do not add markers to unrelated
inline handlers.

## Competing hypotheses

- **H-trigen-advance-conformant:** `L_1DB0`'s measured handler-local advances
  total the reference's extra 32 bytes after the universal dispatcher `+8`.
- **H-trigen-advance-mismatch:** one measured `L_1DB0` increment differs from
  the reference and accounts for the 40-byte command total mismatch.
- **H-trigen-continuation-opaque:** `L_1DB0` delegates before a measurable
  `r17` advance; its next concrete target must be traced instead.

## Discriminating measurement

In one phase-6 task, live `0x05→0x15AC→L_15AC→0x0C→L_1298→L_1DB0` plus
per-site `r17` rows selects a conformant or mismatched increment. The complete
route control with no `L_1DB0` step selects delegation/opaque, not a zero.

## Commands

    rg -n -C 12 '^L_1DB0:|r17 = RSP_ADD32' build/factor5_ucode/factor5_ucode_recompiled.c
    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_INLINE_ADVANCE=1 \
      PROBE_KEYS="3:start 7:start" PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=300 \
      zsh tools/probe.sh scratch/agent/s717_trigen_l1db0 120 1
