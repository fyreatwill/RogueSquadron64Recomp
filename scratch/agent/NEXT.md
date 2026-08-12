# NEXT work unit (after s718: TriGen flushes DPC and refills a new DMEM buffer)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

Implement one regeneration-safe, phase-gated physical-source correlation for
the live `0x05→L_1DB0→L_11B0` path. Record the DRAM base that supplied the
active entry buffer and the `L_11B0` refill source, retaining the existing
0x05 route control. Do not compare raw DMEM offsets to the reference PC.

## Competing hypotheses

- **H-trigen-chunked-conformant:** the refill DRAM source is the entry command
  source plus 40 bytes, so the reference's command + inline-data advance is
  correct despite the DMEM buffer restart.
- **H-trigen-wrong-advance:** the refill source has a stable non-40-byte delta
  from the entry source, identifying a concrete generated-stream mapping bug.
- **H-trigen-source-opaque:** the available state fields do not identify both
  sources; first derive their ownership statically before interpreting a row.

## Discriminating measurement

In one qualified 512-wide task, route control plus a source row containing
`entry_dram`, `entry_offset`, and `refill_dram` measures the actual physical
delta. `refill_dram == entry_dram + entry_offset + 40` supports chunked
conformance; any other stable delta supports a mapping defect; absent source
ownership is an instrument-design failure, not a null result.

## Commands

    rg -n -C 12 'L_1DB0:|L_11B0:|RSP_MEM_W_LOAD\(0X30, r1\)|RSP_MEM_W_STORE\(0X30, r18\)|RSP_MEM_W_STORE\(0X5C, r18\)' build/factor5_ucode/factor5_ucode_recompiled.c
    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_INLINE_ADVANCE=1 \
      PROBE_KEYS="3:start 7:start" PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=300 \
      zsh tools/probe.sh scratch/agent/s719_trigen_phys_advance 120 1
