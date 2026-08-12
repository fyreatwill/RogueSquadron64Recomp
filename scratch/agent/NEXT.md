# NEXT work unit (after s715: Tri conforms; TriGen live continuation is opaque)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

Implement one regeneration-safe, phase-gated route trace for live opcode
`0x05` for backlog item 1. Preserve the table control, but give `0x05` its own
phase-scoped budget so other inline opcodes cannot consume it. Log the
DMA-provided table word, its `do_indirect_jump` target, and the first selected
overlay continuation; then instrument only the actual continuation's `r17`
steps. The static `L_15AC` marker was 0 despite 9--15 live TriGen samples per
phase-6 task, so it is not a valid continuation proxy.

## Competing hypotheses

- **H-trigen-resident-relay:** the live `0x05` table target reaches resident
  `L_15AC`; the prior zero marker was only a shared log-budget failure.
- **H-trigen-direct-overlay:** the live table target bypasses `L_15AC` and
  enters a DMA-populated continuation through `do_indirect_jump`.
- **H-trigen-advance-mismatch:** after locating that continuation, one of its
  internal `r17` advances differs from the reference's 32-byte extra advance.

## Discriminating measurement

The same phase must print a live `0x05` table word and its subsequent indirect
target. A live `L_15AC` row selects H-trigen-resident-relay; a distinct target
selects H-trigen-direct-overlay. Only a located continuation plus an observed
wrong individual increment can select H-trigen-advance-mismatch.

## Commands

    rg -n -C 8 'TriGen|Tri\b|inline data' docs/F5-UCODE-REFERENCE.md
    rg -n -C 8 'do_indirect_jump|^L_15AC:|^L_1268:|jump_target = r2' \
      build/factor5_ucode/factor5_ucode_recompiled.c
    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_INLINE_ADVANCE=1 \
      PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=300 \
      zsh tools/probe.sh scratch/agent/s716_trigen_route 30 1

Append the route and verdict to `docs/F5-UCODE-REFERENCE.md`. If the target is
located and an internal advance is wrong, correct the regeneration-safe fixup
and rerun the same phase-gated control in that iteration.
