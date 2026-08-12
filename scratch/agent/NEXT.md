# NEXT work unit (after s719: TriGen refill source is entry−0x210, not +40)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

Trace the semantic writer of the live `r1+0x30` field that L_1DB0 copies into
DMEM[0x130] and L_11B0 uses as its refill DRAM address. First exhaustively
classify the generated stores and the `r1` ownership statically, then add one
regeneration-safe, phase-gated writer-to-consumer correlation row retaining
the existing 0x05 route control. This is source ownership, not a mitigation.

## Competing hypotheses

- **H-trigen-source-contract:** `r1+0x30` deliberately selects a separate
  continuation stream, so the stable −0x210 delta is legitimate scheduler
  behaviour rather than the reference TriGen inline advance.
- **H-trigen-source-writer-wrong:** the live writer computes/selects a stale or
  wrong source; its intended value is the entry command's post-inline physical
  address, making the −0x210 delta a concrete generated-stream defect.
- **H-trigen-source-alias:** DMEM[0x15C] is not owned by the active buffer at
  L_1DB0, so the s719 source pairing is an alias and must be replaced before a
  semantic conclusion.

## Discriminating measurement

One qualified 512-wide row must join the writer PC/value of `r1+0x30`, the
consumer value at L_1DB0, and the preceding L_11B0 saved base. A matching
writer→consumer value plus a separate-stream contract supports
H-trigen-source-contract; a matching but post-inline-wrong writer supports
H-trigen-source-writer-wrong; no ownership-preserving join supports
H-trigen-source-alias and invalidates s719's pairing rather than interpreting
its delta. The existing complete 0x05 route is the positive control.

## Commands

    rg -n -C 10 'RSP_MEM_W_STORE\\(0X30, r1|RSP_MEM_W_LOAD\\(0X30, r1|r1 =|L_1298:|L_1DB0:|L_11B0:' build/factor5_ucode/factor5_ucode_recompiled.c
    rg -n -C 8 'L_1298|0x30\\(\\$1\\)|0X30, r1' tools/fixup_factor5_ucode.py build/factor5_ucode
    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8
    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \\
      ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_INLINE_ADVANCE=1 \\
      PROBE_KEYS="3:start 7:start" PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=300 \\
      zsh tools/probe.sh scratch/agent/s720_trigen_source_writer 120 1
