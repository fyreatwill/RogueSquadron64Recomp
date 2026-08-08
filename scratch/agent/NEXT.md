# NEXT work unit

HYPOTHESIS-ID: item-317-step3-fix-next-ranked-leads

## s498 fixed the #4 fix in this lineage (40 sites) -- do NOT re-audit from scratch

s494 built `scratch/agent/s494_item317_step3_tracer.py` (control-flow-aware taint tracer for the
`0x801163B0` reload idiom, item -317 step 3). s495 audited an 8-location sample of its 150 distinct
flagged dereference locations: **8/8 confirmed TRUE_POSITIVE, 0 false positives** -- the tracer is
trustworthy at scale. Four leads fixed so far, in order: `NODE_LIST_HEAD_SIBLING_R4_GUARD` (s495, 35
sites), `RENDER_LIT_MESH_R2_GUARD` (s496, 48 sites), `EMIT_FRAME_RDP_INIT_DL_R2_GUARD` (s497,
`funcs_3.c:6979`, 40 sites), `EMIT_FRAME_RDP_INIT_DL_R2B_GUARD` (s498, `funcs_3.c:7963`, 40 sites,
same function as s497's fix). **First THREE are now FULLY CLOSED, 2/2 confirms clean each.**
`EMIT_FRAME_RDP_INIT_DL_R2B_GUARD`'s 1st live-verify was clean (0 fires, 0 regressions,
`hangarbay-entry` n=32); 2nd confirm queued
(`scratch/agent/soak_queue/s498_emit_frame_rdp_init_dl_r2b_confirm.sh`).

**IMPORTANT -- line numbers drift, every session, predictably.** Before writing a fix, re-run:
```
python3 scratch/agent/s494_item317_step3_tracer.py --scan
```
then dedupe the fresh JSON report yourself (group `(file, hit.line, hit.kind, hit.off, hit.reg)` from
`scratch/agent/s494_item317_step3_report.json`, count sources per group, sort descending) to get the
CURRENT top-ranked locations, and cross-check the function name via `awk` backward-scan for the
nearest `RECOMP_FUNC` line above the flagged line. Only then read the exact surrounding source. s496
caught a 13-line drift, s498 caught another 13-line drift (same function, same magnitude -- every fix
inside `emitFrameRdpInitDl` shifts every later line in that file by however many lines the guard
block adds). This check has now caught real drift 2 of 4 sessions it ran -- treat it as load-bearing,
not a formality.

**Progress-signal caveat:** the aggregate `NEEDS_GUARD` count (390) has not moved across the last
THREE fixes even though all three ARE correctly recognized (a per-hit query confirms the fixed lines
no longer appear as unsafe hits anywhere -- verified again this session for s498's fix). This is
because most reload-site records have MULTIPLE unsafe hits across near-duplicate sibling locations in
the same function, and don't flip to SAFE until ALL of them are fixed. Don't treat a flat 390 as "the
fix didn't work" -- verify via the per-hit query (see PORTING-STATE.md Session 497 or 498 for the
exact python snippet), not via the aggregate count alone.

## Current tied-at-40 tier (fresh dedup, s498) -- fold into the ranked list

```
funcs_3.c:5695   (write, ctx->r2+0x4)
funcs_3.c:6001   (write, ctx->r2+0x4)
funcs_3.c:6321   (write, ctx->r2+0x4)
funcs_3.c:6631   (write, ctx->r2+0x4)
funcs_3.c:7332   (write, ctx->r2+0x4)
funcs_3.c:8292   (write, ctx->r2+0x4)
funcs_3.c:7648   (write, ctx->r2+0x4)
funcs_3.c:8636   (write, ctx->r2+0x4)
funcs_4.c:17346  (write, ctx->r2+0x4, renderLitMeshFaceGroup -- flagged since s497, still unfixed)
```
Most or all of the `funcs_3.c` entries are very likely still inside `emitFrameRdpInitDl` (same
function fixed twice already) -- confirm each via the awk backward-scan, don't assume, but expect it.
**Recommend `funcs_3.c:5695`** (or whichever is confirmed lowest-line/first-encountered in that
function) as the next pick -- same fix shape has now been applied 3x in this exact function, should be
fast.

## Remaining leads from s495's original 8-sample not yet in the tied-40 tier
1. `funcs_4.c:3299`-ish (write, `ctx->r2+0x4`) -- 26 sites at last audit, re-derive current line.
2. `funcs_3.c:28922`-ish (write, `ctx->r2+0x4`) -- 18 sites at last audit, re-derive current line.
3. `funcs_3.c:83`-ish (write, `ctx->r2+0x4`, function `heapFreeListInsert`) -- 1 site (singleton).
4. `funcs_3.c:858`-ish (read, `ctx->r3+0x0`, function `countDisplayListChunks`) -- 1 site (singleton).

## This session's work unit

**Fix the next-ranked lead (recommend the lowest-line `funcs_3.c` entry in the tied-40 tier above).**
Steps (mirror s497/s498's process exactly):
1. Re-run the tracer's `--scan`, dedupe fresh, confirm the current line number and function name for
   this lead before reading source (see line-drift warning above).
2. `Read`/`sed -n` the ~40-60 lines around the flagged write in
   `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_3.c` (or `funcs_4.c`) --
   confirm register/offset, containing function (search backward for nearest `RECOMP_FUNC`), and
   check whether the null-check arm gates the specific dereference or not (both shapes have occurred
   in this lineage). Judge from the actual control flow.
3. Check downstream control flow: does anything after the flagged write still use the same register
   before it's reassigned? If not, skip-the-write-on-invalid is safe (used for all fixes in this
   lineage so far). If yes, this may need a block-skip instead (the `ORIENTED_FACE_DERIVED_PTR_GUARD`
   shape) -- judge from the actual control flow, don't assume.
4. Write a new named guard (name it after the containing function/idiom, append a letter suffix if
   it's another sibling in an already-named function) as a literal-string-anchor patch in
   `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`, confirm `text.count(old)==1`
   before writing. Mirror the exact block shape of `EMIT_FRAME_RDP_INIT_DL_R2B_GUARD`.
5. Regen: delete only the affected `funcs_*.c` file (N64Recomp skips regen of files that already
   exist) -> `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py` ->
   `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml` ->
   `python3 fixup_game_funcs.py` (check report for `... patched x1` on the new guard name, no errors,
   no SKIPPED beyond the known-permanent S392_H3A/S393_H3B remainder) -> `cd
   ~/Documents/Tools/RogueSquadron64Recomp/build` ->
   `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8`.
6. Live-verify: copy `scratch/agent/soak_queue/s498_emit_frame_rdp_init_dl_r2b_confirm.sh` as a
   template (correct 3-level `../../..` path), add the new guard's `ROGUESQ_LOG_<NAME>_GUARD=1` env
   var, run manually (foreground; use Bash run_in_background + TaskOutput block=true to wait rather
   than ending the turn early -- the Stop hook will reject STATUS=WORKING). Expect: 0 fires on the new
   guard is fine (rare-path bug) as long as `hangarbay-entry` n~30+ confirms the positive control and
   no sibling guard regresses. Queue a 2nd confirm to `scratch/agent/soak_queue/` after a clean 1st
   live-verify.
7. Re-run `--scan` after the fix -- check via the per-hit-line query (see PORTING-STATE.md Session 497
   or 498 for the exact python snippet) that the fixed line no longer appears as an unsafe hit
   anywhere, even if the aggregate `NEEDS_GUARD` count doesn't move.

**After this fix is confirmed**, continue down the combined list (tied-40 tier + s495's original
ranked list) one location at a time, each with its own live-verify before moving to the next. Do NOT
batch multiple unverified fixes into one build/soak cycle.

## Wider unaudited population
~139 of the 150 distinct dedup'd locations remain formally unaudited. Once the ranked-list fixes
above are done, widen the audit sample (another 8-10 locations, weighted toward mid/low shared-count)
rather than assuming the whole population is clean from one 8-site sample.

## New crash filed this session -- plausible link to an OLD open question, worth a look before dismissing
s498's live-verify crashed at 123.8s on `pc-symbol=appendRdpStateDl+144`, `last-guest-pc=0x800109b8`
-- not an exact prior match, but item -306 (PROJECT-OVERVIEW §18) already flagged 10 sites where a
DIFFERENT table's raw reload survives a function-call boundary into `appendRdpStateDl` (among other
callees) unverified. If this crash signature recurs 2+ times, the highest-value next move is NOT
another idiom-class scan -- it's reading `appendRdpStateDl`'s body directly against item -306's
flagged call sites to check whether this is that exact gap. Filed per the strategic-priority rule
against reactive single-crash chases; do not chase on a single occurrence.

## Soak queue status
- `scratch/agent/soak_queue/s498_emit_frame_rdp_init_dl_r2b_confirm.sh` queued (2nd independent
  confirm of `EMIT_FRAME_RDP_INIT_DL_R2B_GUARD`).

## M5 lead-check
Cleared s494 (no new lead). Due again once 3+ sessions have passed from s494, i.e. s498+ -- due THIS
session's successor if the item -317 sibling-fix pass runs long, or explicitly next session.
