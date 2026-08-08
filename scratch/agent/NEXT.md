# NEXT work unit

HYPOTHESIS-ID: item-317-step3-fix-next-ranked-leads

## Fresh start on this slug (s499 pivoted away for one session; this is iteration 1 of a new streak)

s499 folded in `EMIT_FRAME_RDP_INIT_DL_R2B_GUARD`'s 2nd confirm (clean, 2/2) and ran the overdue M5
lead-check (no new lead) per the loop's mandatory-pivot rule, after s496/s497/s498 ran three
straight iterations on this same slug. **All four leads fixed so far in item -317 step 3 are now
FULLY CLOSED, 2/2 confirms each**: `NODE_LIST_HEAD_SIBLING_R4_GUARD` (s495, 35 sites),
`RENDER_LIT_MESH_R2_GUARD` (s496, 48 sites), `EMIT_FRAME_RDP_INIT_DL_R2_GUARD` (s497,
`funcs_3.c:6979`, 40 sites), `EMIT_FRAME_RDP_INIT_DL_R2B_GUARD` (s498/s499, `funcs_3.c:7963`, 40
sites, same function as s497's fix). No open confirms remain in this lineage as of s499.

**IMPORTANT — line numbers drift, every session, predictably.** Before writing a fix, re-run:
```
python3 scratch/agent/s494_item317_step3_tracer.py --scan
```
then dedupe the fresh JSON report yourself (group `(file, hit.line, hit.kind, hit.off, hit.reg)` from
`scratch/agent/s494_item317_step3_report.json`, count sources per group, sort descending) to get the
CURRENT top-ranked locations, and cross-check the function name via `awk` backward-scan for the
nearest `RECOMP_FUNC` line above the flagged line. This check has caught real drift in 2 of the last
4 sessions that ran it (s496: +13 lines, s498: another +13 lines, same function both times, because
each guard block added to `emitFrameRdpInitDl` shifts every later line in that same file) — treat it
as load-bearing, not a formality.

**Note on the log location for any live-verify you run:** the loop's own `SOAK-RESULTS.md` line and
its `scratch/agent/soak_results/<name>_<timestamp>.log` file are ONLY a 12-line `probe.sh` summary
(pid, phase-reach time, key-press log, crash line) — they do NOT contain guard-fire detail. The full
game stdout with every `ROGUESQ_LOG_*` line is inside the capture directory itself:
`scratch/agent/soak_results/<name>/run.log`. Always read that file (grep, don't cat raw — it runs
tens of thousands of lines) when verifying fires/regressions from a queued confirm, not just the
top-level summary log.

## Current tied-at-40 tier (from s498's dedup — re-verify line numbers fresh per the drift warning
above before touching source; DO NOT trust these verbatim)

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
function fixed 4x already this lineage) -- confirm each via the awk backward-scan, don't assume, but
expect it. **Recommend `funcs_3.c:5695`** (or whichever is confirmed lowest-line/first-encountered
in that function after a fresh `--scan`) as the next pick.

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
6. Live-verify: copy `scratch/agent/soak_queue/done/s498_emit_frame_rdp_init_dl_r2b_confirm_*.sh` as
   a template (correct 3-level `../../..` path), add the new guard's
   `ROGUESQ_LOG_<NAME>_GUARD=1` env var, run manually (foreground; use Bash run_in_background + wait
   rather than ending the turn early -- the Stop hook will reject STATUS=WORKING). Expect: 0 fires on
   the new guard is fine (rare-path bug) as long as `hangarbay-entry` n~30+ confirms the positive
   control and no sibling guard regresses. Queue a 2nd confirm to `scratch/agent/soak_queue/` after a
   clean 1st live-verify.
7. Re-run `--scan` after the fix -- check via the per-hit-line query (see PORTING-STATE.md Session
   497/498 for the exact python snippet) that the fixed line no longer appears as an unsafe hit
   anywhere, even if the aggregate `NEEDS_GUARD` count doesn't move.

**After this fix is confirmed**, continue down the combined list (tied-40 tier + s495's original
ranked list) one location at a time, each with its own live-verify before moving to the next. Do NOT
batch multiple unverified fixes into one build/soak cycle.

**Mandatory-pivot reminder:** if this becomes the 3rd consecutive iteration on this same slug with no
new lead closed, the loop will force a pivot preamble on the iteration after. Either land a fix each
iteration, or explicitly design/run the single highest-information discriminating probe instead of
repeating the same manual fix-one-lead motion a 4th time.

## Wider unaudited population
~139 of the 150 distinct dedup'd locations remain formally unaudited. Once the ranked-list fixes
above are done, widen the audit sample (another 8-10 locations, weighted toward mid/low shared-count)
rather than assuming the whole population is clean from one 8-site sample.

## Old crash filed s498, not yet recurred -- do not chase on a single occurrence
s498's live-verify crashed at 123.8s on `pc-symbol=appendRdpStateDl+144`, `last-guest-pc=0x800109b8`
-- plausible (not confirmed) link to item -306's old flagged-not-chased cross-function-call
reload-propagation gap into `appendRdpStateDl`. Has NOT recurred as of s499 (s499's own confirm of
the same guard crashed on a different, already-catalogued signature instead). If this exact
`appendRdpStateDl+144` signature recurs 2+ times total, the highest-value next move is reading
`appendRdpStateDl`'s body directly against item -306's flagged call sites -- not another idiom-class
scan.

## Soak queue status
Empty -- no queued recipes as of s499 (the only outstanding one, `EMIT_FRAME_RDP_INIT_DL_R2B_GUARD`'s
2nd confirm, was folded in this session).

## M5 lead-check
Cleared s499 (no new lead -- grepped sessions 495-498, only hit was a stale citation of an
already-closed thread). Due again once 3+ sessions have passed from s499, i.e. s502+.
