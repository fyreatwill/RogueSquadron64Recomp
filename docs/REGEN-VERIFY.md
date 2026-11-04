# Regen verification

How to check that a regenerated RecompiledFuncs tree builds the same code as the live tree. Added s6864.

    tools/regen_front.sh <new dir>              # make_elf -> N64Recomp into a scratch dir, real sizes from tools/func_sizes.txt
    tools/regen_replay.sh <copy of pristine>    # fixer and every step after it; never point it at a patched tree
    tools/regen_verify.sh <that dir> <out dir>  # compile both trees, compare per function

The source diff alone is not enough: the s6863 residual counted lines per file, so it could not see a line that moved.
`tools/regen_obj_compare.py` hashes each function's machine code plus the external symbols it calls. It ignores debug
info, static data layout, adrp pages and outliner numbering. Branch offsets to same-file functions are not masked, so a
function can still report as different after its neighbours moved; disassemble it with branch targets masked before
calling it a real difference. Control: one changed constant in funcs_1.c reports exactly `_pollDmaSlotStep`, 1 of 2783.

## s6864 baseline: 2708 functions same, 75 differ, 0 missing on either side

| Count | Class | Why it is safe on the default path |
|---|---|---|
| 14 | No source change | 0 instructions differ with branch targets masked: layout only |
| 1 | `intersectSegmentWithObjectSphere` | No source change; stack layout differs from the inlined s5904 tally, counters only |
| 13 | funcs_16 helpers (rs5904_tally, rs6657-rs6685) | Run only under ROGUESQ_OBJECTIVE_RESPONSE=1 / the hit census |
| 29 | Diagnostic lines only | Gated on g_rs64_store_diag or a ROGUESQ_LOG_* env |
| 18 | Read by hand, listed below | See below |

The 18, by what differs:
- Order of env-gated hooks only: `audioCueDispatcherNpcHandler` (s5798_init, LOG_HUDBIT), `musyxSynthFrame` (s4784_ev,
  LOG_S4784), `updateDestructionDebrisNpc`, `dealDamagetoDatItem`, `npcWingmanUpdate` (rs66xx, OBJECTIVE_RESPONSE).
- `partitionFramebufferMemory`: rs64_g1d_heapcap runs before the ROGUESQ_LOG_G1D_TASK print instead of after it.
- `stopVoiceSlotSynced`, `serviceVoicePoolFrame`, `initMusyXVoiceTable`: the store is unchanged; the store-diag post
  note lands before it instead of after. Only wrong when ROGUESQ_STORE_DIAG is on, and only for those four 0X4620 sites.
- `transformWorldPosToGridSpace`, `unpackGridVertexBytes`, `buildVisibleTerrainGridAroundCamera`, `transformObjectColliderCenter`:
  bound is RS64_RAM_TOP in regen, literal 0x80800000 in live, in opt-in logging and OBJECTIVE_RESPONSE code. Regen is the better one.
- `beginFrameDLChunk`, `tickTextureMaterialExpiry`, `binPolygonIntoTerrainGrid`, `scanConvertTriangleToSpanTable`,
  `streamTerrainGridCellsByDistance`: live-only diagnostics, listed next.

## s6865: same 2708 / 75 after removing s4563

The dead s4563 check left the replay list and the live tree. Replay from pristine, then compare: 2708 same, 75 differ, and the 75 are
the same names as the s6864 baseline. Live funcs_24.c before vs after: `_musyxSynthFrame` differs (the removed block, 184 -> 131
instructions) and three neighbours report as different with 0 instructions differing once branch targets are masked.

Two replays from the same pristine copy gave 0 differing lines, so the chain is deterministic on one host.

The pristine tree is whatever N64Recomp last wrote to a scratch dir, and those dirs get cleaned. s6865 rebuilt one from /tmp/s6864/ctl
(minus its control line; 0 lines against scratch_s5547_regen). If neither exists, run the front chain again.

## s6869: same 2708 / 75 after cutting decoded tails

`tools/regen_replay.sh` now runs `fixup_cut_decoded_tails.py` (docs/DECODED-TAIL-CENSUS.md). Replay from pristine, then compare:
2708 same, 75 differ, 0 missing, name set equal to scratch/s6864/cmp2.json. Both trees cut the same 18 functions.

## s6870: 2688 same, 78 differ, 17 only in live, with real function sizes

`tools/regen_front.sh` passes `tools/func_sizes.txt` to N64Recomp. Compare against the live tree: 2688 same, 78 differ, 17
only in live, 0 only in regen. `regen_front.sh <dir> none` still gives the old input: 0 differing lines against
scratch_s5547_regen. Full replay of both front ends, source diff: only the 17 functions, the dead labels and the tail comments.

- The 17 are the dropped `data_gap_` functions, listed in docs/DECODED-TAIL-CENSUS.md. The live tree still has them.
- 75 of the 78 are the s6864 names. New: `handleCraftSelectInput` (-14 adrp, -14 add), `data_gap_800E9B10` (opcodes equal),
  `rs64_bwatch` (+1 adrp, +1 add, -1 mov). All three sit in funcs_49.c and none has a source change. Compared by opcode counts,
  not instruction by instruction: clang sets up addresses differently once the file is smaller.
- `regen_obj_compare.py` matches objects by file name, so a file present on one side only is skipped silently. funcs_50.c
  is such a file here; it holds no functions.

Runtime, regen binary, one run per level, dd1 4:3 only: see the census doc.

## s6881: s6879 and s6880 survive a replay from pristine, after one order fix

First replay stopped in the fixer. s6879 was called twice: from the inline fixer block and from RS64_REPLAY. The inline call ran before
any s6144 text exists on pristine, because `apply_s6144_fpx` anchors on a line that a later step adds and skips silently when it is absent.
`apply_s6879_fpdepth` asserts on its anchors, so the fixer died. The live tree never showed this: there the script sees its own marker and returns.
Fix: the inline call is gone; RS64_REPLAY runs it right after s6144. Assert kept.

Rule for new apply scripts: add them to RS64_REPLAY only, in order. An inline fixer call runs before the replayed steps. An asserting script
stops the fixer there, and a tolerant one does nothing on pristine and reports nothing.

Result: 2684 same, 82 differ, 17 only in live, 1 only in regen, equal to s6871. Against s6870's name set the new diffs are exactly the 4 functions s6871 sized
(`rspbootTextPreamble`, `data_gap_800AF6A8`, `data_gap_800CC3D4`, `data_gap_80024A0C`), and only-in-regen is `static_5_800CC4E4`. No H-drift.
Control: `grep -h s6879`, `s6880` and `s6049` over funcs_9.c hash equal in live and regen (4, 18, 9 lines) and are absent from pristine;
`_rs64_s6880_wide` and `_rs64_s6879_fpk` are undefined symbols in both funcs_9 objects. No regen binary was linked or run this session.

## What a regen loses

Opt-in or count-only code that exists only in live: the s6500-s6526 funcs_9 chain plus s6518/s6519 (`ROGUESQ_FORFACE_LOG`,
closed thread), s6522 `ROGUESQ_CLAMPP`, s6314 `ROGUESQ_EDGE_FADE_TEST2`, s6201 alloc log, s5906 fine-test tally calls,
s6095 `rs64_s6093_cnt(3)` (no script exists for it; a counter). None run by default.

## Boot check, s6864

Regen binary (regen objects, every other object from live) vs live, lvl1 forced route, one run each, sequential: mission at
85 s / 84 s, 130 s hold verified, 0 stalls, 0 crash lines, 5927 / 5917 distinct framebuffer hashes. dd1 at 4:3 only.
