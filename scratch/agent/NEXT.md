# NEXT work unit

HYPOTHESIS-ID: item-317-step3-fix-next-ranked-leads

## s497 fixed the #1-ranked remaining lead (40 sites) -- do NOT re-audit from scratch

s494 built `scratch/agent/s494_item317_step3_tracer.py` (control-flow-aware taint tracer for the
`0x801163B0` reload idiom, item -317 step 3). s495 audited an 8-location sample of its 150 distinct
flagged dereference locations: **8/8 confirmed TRUE_POSITIVE, 0 false positives** -- the tracer is
trustworthy at scale. s495 fixed the #1 lead (`NODE_LIST_HEAD_SIBLING_R4_GUARD`, 35 sites), s496 the
#2 (`RENDER_LIT_MESH_R2_GUARD`, 48 sites) -- **both now FULLY CLOSED, 2/2 confirms clean** (s497 folded
in both queued 2nd confirms: 0 fires on either guard, 0 regressions, hangarbay-entry n=31/35 positive
controls; `RENDER_LIT_MESH_R2`'s confirm crashed but on the pre-existing catalogued
`tickWrappingTimerAccumulatorList` div-by-zero trap, unrelated). s497 fixed the #3 lead
(`EMIT_FRAME_RDP_INIT_DL_R2_GUARD`, `funcs_3.c:6979`, `emitFrameRdpInitDl`, 40 sites), 1st live-verify
clean (0 fires, 0 regressions, hangarbay-entry n=32, full sibling-guard set), 2nd confirm queued
(`scratch/agent/soak_queue/s497_emit_frame_rdp_init_dl_r2_confirm.sh`).

**IMPORTANT -- line numbers drift.** Before writing a fix, re-run:
```
python3 scratch/agent/s494_item317_step3_tracer.py --scan
```
then dedupe the fresh JSON report yourself (group `(file, hit.line, hit.kind, hit.off, hit.reg)` from
`scratch/agent/s494_item317_step3_report.json`, count sources per group, sort descending) to get the
CURRENT top-ranked locations, and cross-check the function name via `awk` backward-scan for the
nearest `RECOMP_FUNC` line above the flagged line. Only then read the exact surrounding source. s496
caught a 13-line drift this way; s497 checked and found none -- the check itself is the rule, run it
every session regardless of outcome.

**Progress-signal caveat:** the aggregate `NEEDS_GUARD` count (390) has not moved across the last two
fixes even though both fixes ARE correctly recognized (a per-hit query confirms the fixed lines no
longer appear as unsafe hits anywhere). This is because most reload-site records have MULTIPLE unsafe
hits across near-duplicate sibling locations in the same function, and don't flip to SAFE until ALL of
them are fixed. Don't treat a flat 390 as "the fix didn't work" -- verify via the per-hit query shown
in PORTING-STATE.md Session 497, not via the aggregate count alone.

## New same-function sibling leads surfaced by s497's fresh dedup (fold into the ranked list)

Both functions already touched by this lineage have MORE unguarded sibling write sites at the same
shared-count tier as the ones already fixed -- same root idiom, same fix shape, high confidence:
1. `funcs_3.c:7950` (write, `ctx->r2+0x4`, `emitFrameRdpInitDl`) -- 40 sites.
2. `funcs_3.c:7319` (write, `ctx->r2+0x4`, `emitFrameRdpInitDl`) -- 40 sites.
3. `funcs_3.c:8266` (write, `ctx->r2+0x4`, `emitFrameRdpInitDl`) -- 40 sites.
4. `funcs_4.c:17346` (write, `ctx->r2+0x4`, `renderLitMeshFaceGroup`) -- 40 sites.
5. `funcs_4.c:17759` (write, `ctx->r2+0x4`, `renderLitMeshFaceGroup`) -- 36 sites.

## Remaining audit-confirmed leads from s495's original 8-sample (3 now fixed)

Ranked by shared reload-site count at the time of the s495 audit (re-derive current line numbers
before use, per above):
1. `funcs_3.c:15977` (write, `ctx->r2+0x4`) -- 32 sites. **Next up if not doing a same-function sibling.**
2. `funcs_4.c:3299` (write, `ctx->r2+0x4`) -- 26 sites.
3. `funcs_3.c:28922` (write, `ctx->r2+0x4`) -- 18 sites.
4. `funcs_3.c:83` (write, `ctx->r2+0x4`, function `heapFreeListInsert`) -- 1 site (singleton).
5. `funcs_3.c:858` (read, `ctx->r3+0x0`, function `countDisplayListChunks`) -- 1 site (singleton).

All share the same shape confirmed repeatedly now: `ctx->r2` (or `ctx->r3` for the read at 858)
reloaded from the `0x801163B0` table with only a null check, no `0x80000000`-`0x80800000` range check,
before the flagged dereference, and no nearby existing guard covers it. Fix shape: fresh
range-check-and-skip block per site, not an extension of an existing guard. **Judgment call this
session:** pick EITHER the highest-shared-count same-function sibling (list above, likely faster since
the function/shape is already understood) OR the next item in the original ranked list -- either is
defensible; don't spend a whole iteration deciding, just pick one and move.

## This session's work unit

**Fix the next-ranked lead (recommend `funcs_3.c:7950`, 40 sites, same function as s497's fix).**
Steps (mirror s497's process exactly):
1. Re-run the tracer's `--scan`, dedupe fresh, confirm the current line number and function name for
   this lead before reading source (see line-drift warning above -- it held this session, may not next).
2. `Read`/`sed -n` the ~40-60 lines around the flagged write in
   `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_3.c` (or `funcs_4.c`) --
   confirm register/offset, containing function (search backward for nearest `RECOMP_FUNC`), and
   check whether the null-check arm gates the specific dereference or not (both shapes have occurred
   in this lineage -- `RENDER_LIT_MESH_R2` neither arm gated it, `EMIT_FRAME_RDP_INIT_DL_R2` the null
   arm did gate it but non-null fallthrough didn't range-check). Judge from the actual control flow.
3. Check downstream control flow: does anything after the flagged write still use the same register
   before it's reassigned? If not, skip-the-write-on-invalid is safe (used for all fixes in this
   lineage so far). If yes, this may need a block-skip instead (the `ORIENTED_FACE_DERIVED_PTR_GUARD`
   shape) -- judge from the actual control flow, don't assume.
4. Write a new named guard (name it after the containing function/idiom) as a literal-string-anchor
   patch in `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`, confirm
   `text.count(old)==1` before writing. Mirror the exact block shape of
   `EMIT_FRAME_RDP_INIT_DL_R2_GUARD`/`RENDER_LIT_MESH_R2_GUARD` in that file.
5. Regen: delete only the affected `funcs_*.c` file (N64Recomp skips regen of files that already
   exist) -> `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py` ->
   `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml` ->
   `python3 fixup_game_funcs.py` (check report for `... patched x1` on the new guard name, no errors,
   no SKIPPED beyond the known-permanent S392_H3A/S393_H3B remainder) -> `cd
   ~/Documents/Tools/RogueSquadron64Recomp/build` ->
   `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8`.
6. Live-verify: copy `scratch/agent/soak_queue/s497_emit_frame_rdp_init_dl_r2_confirm.sh` as a
   template (correct 3-level `../../..` path), add the new guard's `ROGUESQ_LOG_<NAME>_GUARD=1` env
   var, run manually (foreground, `run_in_background: true` + `TaskOutput block=true` to wait) first.
   Expect: 0 fires on the new guard is fine (rare-path bug) as long as `hangarbay-entry` n~30+
   confirms the positive control and no sibling guard regresses. Queue a 2nd confirm to
   `scratch/agent/soak_queue/` after a clean 1st live-verify.
7. Re-run `--scan` after the fix -- check via the per-hit-line query (see PORTING-STATE.md Session 497
   for the exact python snippet) that the fixed line no longer appears as an unsafe hit anywhere, even
   if the aggregate `NEEDS_GUARD` count doesn't move (expected, per the progress-signal caveat above).

**After this fix is confirmed**, continue down the combined list (same-function siblings + s495's
original ranked list) one location at a time, each with its own live-verify before moving to the next.
Do NOT batch multiple unverified fixes into one build/soak cycle.

## Wider unaudited population
~143 of the 150 distinct dedup'd locations remain formally unaudited (150 - 6 from s495's sample - 3
site-tier duplicates just discovered, roughly). Once the ranked-list fixes above are done, widen the
audit sample (another 8-10 locations, weighted toward mid/low shared-count) rather than assuming the
whole population is clean from one 8-site sample.

## New unrelated crash filed this session (not chased)
s497's 1st live-verify crashed at 131.3s on `pc-symbol=coalesceFreeHeapBlocks+4424`,
`last-guest-pc=0x8000247c` -- a heap free-list-walk routine in `funcs_0.c`, NOT part of the
`0x801163B0` reload idiom this arc targets, and not previously catalogued anywhere in CURRENT-TRUTH or
PROJECT-OVERVIEW. Filed per the strategic-priority rule against reactive single-crash chases. If it
recurs 2+ times independently, it becomes a systematic-idiom-class-audit candidate (heap free-list
walk corruption) -- worth a grep check in future sessions' crash triage.

## Soak queue status
- `scratch/agent/soak_queue/s497_emit_frame_rdp_init_dl_r2_confirm.sh` queued (2nd independent confirm
  of `EMIT_FRAME_RDP_INIT_DL_R2_GUARD`).

## M5 lead-check
Cleared s494 (no new lead). Due again once 3+ sessions have passed from s494, i.e. s498+.
