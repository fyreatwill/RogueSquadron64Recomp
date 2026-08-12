# NEXT work unit (after s725: FF0 mirror default-off)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

Perform one static, regeneration-safe audit of the live `L_1DB0` TriGen
continuation: enumerate its command-source inputs and every branch before the
`L_1E48→L_1E5C→L_11B0` loop. Do not add another unconstrained reroll.

## Competing hypotheses

- **H-l1db0-valid-chunk-loop:** the `r1+0x30` source is a documented chunk
  stream and repeated cap returns are an expected long-running route.
- **H-l1db0-stale-source:** the continuation repeatedly reloads an old chunk
  base, so only three natural FULL_SYNC boundaries reach RT64 post-sec2.
- **H-l1db0-branch-loss:** a generated/fixup branch bypasses the natural
  root/EndDL route after the first chunk.

## Discriminating measurement

Before a build, record a complete static table for `L_1DB0` through its
indirect exit: each RSP-DMEM read/write, condition, target, and producer of
the `r1+0x30` source, cross-checked against `docs/F5-UCODE-REFERENCE.md`.
Then add one phase-scoped trace (in `tools/fixup_factor5_ucode.py`, not the
generated C) that logs the source, selected branch, and next target for the
first 16 qualified phase-3 `0x05→L_15AC→L_1298→L_1DB0` routes. The existing
route marker must fire in the same run. A stable documented chunk transition
supports H-l1db0-valid-chunk-loop; a repeated stale source or an unexpected
branch identifies the appropriate alternative.

Ground-truth boundary: the retail oracle cannot inspect RSP DMEM or branch
state. Use the Factor 5 reference for command semantics and label any runtime
result single-source until an independent game-visible consequence is joined.

## Commands

    rg -n -C 8 'L_1DB0:|0X30, r1|L_1E48|L_1E5C|L_11B0' build/factor5_ucode/factor5_ucode_recompiled.c
    rg -n -C 8 'L_1DB0|TriGen|chunk' docs/F5-UCODE-REFERENCE.md tools/fixup_factor5_ucode.py
    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_INLINE_ADVANCE=1 \
      PROBE_KEYS="3:start 7:start" PROBE_PHASE_WIDTH=1024 \
      PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
      zsh tools/probe.sh scratch/agent/s726_l1db0_branch 45 1
