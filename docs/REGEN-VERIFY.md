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

## s7421: class CD, drift since s6881 triaged (H-mirrored)

Fresh replay of the s7420 pristine front (`/tmp/s7420/front` -> `tools/regen_replay.sh` -> `tools/regen_verify.sh`) reproduces
s7420 exactly: 2664 same / 114 differ / 18 live-only / 3 regen-only (`scratch/s7421/regen_compare.json`). New classifier
`tools/s7421_regen_drift.py <live> <regen> <compare.json> --baseline scratch/s6871/v/compare.json --control` splits both trees
per function (comments dropped, statements normalised) and classifies every differing / one-sided function: CODEGEN (text equal;
the cause is the file context it names), ENVDIAG / REORDER-DIAG (only diagnostic or opt-in statements differ: no guest write, no
control flow on a non-diag condition), GUEST (N64Recomp sizing: data_gap_/static_/rspboot), LOST (live-only non-diag statement),
REORDER (same statements, non-diag order change). Reviewed env-gated LOST/REORDER rows live in `tools/s7421_regen_accept.tsv`.
Control (`--control`): a planted `ctx->r2 ^= ...` in a copy of an equal function -> LOST, a planted getenv/fprintf line -> ENVDIAG.

Against s6871's name set: 47 new differing, 15 no longer differing (the s6657-s6685 objective chain plus
`buildVisibleTerrainGridAroundCamera`, `intersectSegmentWithObjectSphere`, `unpackGridVertexBytes` now replay), 1 new live-only
(`s6593_hudptr_note`), 2 new regen-only (`s6992_note`, `s6992b_note`). New rows: 45 funcs_13 CODEGEN + 2 static notes, all caused
by `rs64_s5798_st` (the g_rs64_store_diag handler: watch branches in a different order, inlined into every RS64_S5798_ST caller,
which also changes which static notes get inlined); `rs64_s5798_st` itself REORDER-DIAG; 2 funcs_32 ENVDIAG
(`buildMenuImageTileWipeMesh`, `updatePilotSlotLogoModels`: 6 stale live `rs64_tctr` ROGUESQ_TICK_TRACE hooks; the current
g3_float_quanta_audit selection no longer picks them and the idempotent fixup never removes old hooks). **0 LOST, 0 OPEN.**
Baseline residue (also in the accept file): s6499/s6512-s6519 funcs_9 chain, s6314/s6328 EDGE_FADE block order, s5854 census vs
HUDBIT log order, HUDBIT blocks order in datItemSetObjectiveBooleanCount.

Second line (PATCH-tag census, live vs regen, funcs_50 excluded): live-only tags exactly s5904 + s6496-s6526 (the documented
opt-in list); tag-count deltas s2190/s6336/s7318/s7320 sit only in the 11 data_gap functions func_sizes.txt sizes as data; s6826
is the 6 stale tctr hooks; regen had MORE tags for s5787/s5790/s5791/s5809 (objective HUDBIT logs applied twice) and s5856/s6497.
Cause of the double apply: those four scripts are called inline in the fixer and again from RS64_REPLAY, and their idempotence
check looked for the tag only in a window of 40 + len(block) after the anchor, so any other block inserted at the same anchor hid
it. Fixed (whole-body check); `tools/s7421_idem_test.py` re-applies each after a 3.6 KB interposed block: fixed 0 added, HEAD copies
3/2/1/2 added (control). 13 more apply/fixup scripts use a windowed check (class CE).
After the fix, second fresh replay: 2671 same / 107 differ / 18 live-only / 3 regen-only (`scratch/s7421/regen_compare_after.json`);
s5787 3/3, s5790 2/2, s5791 1/1, s5809 2/2 tags live/regen; s7421_regen_drift --control rc 0, H-mirrored.

## s7422: class CE, windowed idempotence (H-once)
13 apply/fixup scripts tested "already applied?" in a fixed window. 8 run twice per regen (inline in fixup_game_funcs_vendored.py
and again in RS64_REPLAY): s5811/s5812/s5813/s5829/s5887/s5893/s5953/s5960. `tools/s7422_idem_class_test.py` applies each to the
pristine file, puts a 450 KB foreign block in front of each of its own tagged lines, applies again: fixed copies add 0; the
d1c50d659 copies add 1/1/3/-/1/1/3/1 (control; s5829 adds 0 because its anchor includes the next comment line, which its own insert
breaks). All 8 now check the whole function body. Fresh replay `/tmp/s7422/R` is byte-identical to `/tmp/s7421/R2` (diff -rq 0),
so no double happened in the real chain; the fix only removes the risk. Called once: s5693, s5697, s6303, s6311, fixup_preempt_point.
Regen>live tags: s5856 (live labels the same rs5907/rs5856_sinobj declaration line "s5904"), s6497 (live funcs_9 lost the s6497
bounds read and the s6789 `rs64_g3e_trace(8, ...)` line before `// 0x800429C0`; regen has both; diag-only) -> class CF.

## s7559: the s7558 drift (2607 / 141 / 18) is layout only

Trees: scratch/s7558/{replay,verify}. `tools/s7421_regen_drift.py ../N64Recomp/RecompiledFuncs scratch/s7558/replay
scratch/s7558/verify/compare.json --baseline scratch/s7421/regen_compare.json --control` exits 0, VERDICT H-mirrored.
Against the s7421 name set: 35 new differing functions, all **SLOTPERM** (new class), and 1 new CODEGEN (`s6992d_note`, static-note
inlining caused by `rs64_s5798_st`, as in s7421). 0 open LOST/REORDER; the 2 LOST and 2 REORDER rows are the accepted s7421 residue.

SLOTPERM: the only difference is the slot index argument of `RS64_S7487_LWX(pc, idx, ...)` (s7487 lwl/lwr watch). Both trees wrap
the same 410 sites at the same pcs (0 one-sided pcs). 178 keep their index, 215 shift by +16 and 16 by -216: the 16 funcs_3 sites at
0x8000D598-0x8000D640 got slots 394-409 in live (a later apply pass; `apply_s7487_lwlwatch.py` continues the index for sites a
later step adds) and 178-193 in replay (file order). The host stores the pc beside the slot on first sample
(`src/main/upstream_compat.cpp` s_s7487_site) and reports by pc, so the order changes no report and no behaviour; the macro does
nothing unless ROGUESQ_S7487 turns `g_rs64_s7487_on` on.

Second line, PATCH-tag census per tag (funcs_50 excluded): live-only tags are exactly s5904 + s6496-s6526 (the opt-in list above),
regen-only none. Count deltas equal the s7421 census except that s5787/s5790/s5791/s5809 now match (the s7421 idempotence fix).

Controls (`--control`, all in one run): planted `ctx->r2 ^=` -> LOST, planted getenv/fprintf -> ENVDIAG, one s7487 slot renumbered
-> SLOTPERM, one wrap's pc changed -> ENVDIAG (not SLOTPERM). Outputs: scratch/s7559/drift2.{out,json}.

## s7719: fresh replay 2620 / 141 / 18, H-mirrored both directions; the drift check is now a live sweep gate

Front: `tools/regen_front.sh scratch/s7719/pristine` is byte-identical to scratch/s7558/pristine (`diff -rq` empty), so every
change since s7558 is in the fixup chain. Replay (`tools/regen_replay.sh`, 3.5 min, one CPU) completes the tree; its trailing
s7363 host-array gate then failed on 19 unreviewed rows of host code added since (s7702_fbread, s7644_rspdma, rs64_standins,
s7576-trunc), all hand-read BOUNDED in s7719. regen_verify (now `RV_JOBS`, default 2, was a hard-coded 6): 2620 same, 141 differ,
18 live-only, 4 regen-only, funcs_50.c live-only (s7558: 2607 / 141 / 18).
- `s7421_regen_drift.py ... --baseline scratch/s7558/verify/compare.json --control`: rc 0, VERDICT H-mirrored, **new vs baseline {}**,
  control PASS. `s7423_live_stale.py --control` (regen-only statements, every function): VERDICT H-diag, control PASS.
- New `s7423_live_stale.py --reverse` (live-only statements in EVERY function, not only object-differing ones): 29 rows, all read by
  hand into tools/s7719_live_only_accept.tsv: setRngSeed dead tail after `return` (0x80003474-7C, regen cuts it by real size), 16
  data_gap functions (s6870), funcs_50.c (prelude only, 0 RECOMP_FUNC), the funcs_9 s6496-s6526 census chain, 5 ORDER rows already
  reviewed (s6864, s7421). Control: known s6499 live-only loop listed, planted store -> BEHAVIOUR, planted print -> DIAG.
- `tools/s7719_regen_gate.py` does front + `RS64_REPLAY_TREE_ONLY=1` replay in a temp dir + both directions with controls
  (2.6 min, one CPU), and is in the gate sweep. Wiring controls on a live copy: a planted live-only store -> reverse RED; one fixup
  line deleted from live -> forward RED.

## s7735: the replay also reproduces every compiled env reading

`tools/s7719_regen_gate.py` runs `tools/s7734_compiled_reader_census.py --tree <replay>` on its fresh replay: 0 unreviewed HIDDEN/NOREF
(378 distinct readings vs 379 live; the live-only one is the s6522 ROGUESQ_CLAMPP probe in funcs_9). Planted control: the replay's
funcs_23 B40 line put back to its pre-s7734 form reads HIDDEN (rc 1). The census `--tree DIR` flag works on any RecompiledFuncs tree.
