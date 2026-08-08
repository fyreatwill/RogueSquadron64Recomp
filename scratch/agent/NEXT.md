# NEXT work unit

HYPOTHESIS-ID: item-317-step3-fix-next-ranked-leads

## Continuing this slug (s500 is iteration 1 of a new streak after s499's mandatory M5 pivot)

s500 fixed `EMIT_FRAME_RDP_INIT_DL_R2C_GUARD` (`funcs_3.c:5695`, `emitFrameRdpInitDl`, 40 shared
reload sites), 1st live-verify clean, 2nd confirm queued
(`scratch/agent/soak_queue/s500_emit_frame_rdp_init_dl_r2c_confirm.sh`). **Five step-3 leads fixed so
far, four FULLY CLOSED 2/2**: `NODE_LIST_HEAD_SIBLING_R4_GUARD` (s495, 35 sites),
`RENDER_LIT_MESH_R2_GUARD` (s496, 48 sites), `EMIT_FRAME_RDP_INIT_DL_R2_GUARD` (s497, `funcs_3.c`,
40 sites), `EMIT_FRAME_RDP_INIT_DL_R2B_GUARD` (s498, same function, 40 sites) — plus
`EMIT_FRAME_RDP_INIT_DL_R2C_GUARD` (s500, same function, 40 sites) at 1/2, pending its queued 2nd
confirm.

**When you pick this back up: first check whether the loop already ran s500's queued 2nd confirm.**
Read `scratch/agent/SOAK-RESULTS.md` tail for a line mentioning
`s500_emit_frame_rdp_init_dl_r2c_confirm`; if present, read its `run.log` in
`scratch/agent/soak_results/s500_emit_frame_rdp_init_dl_r2c_confirm/run.log` for guard-fire detail
(the top-level `.log` is only a 12-line summary), fold the result into the ledger (mark R2C fully
CLOSED if clean, 2/2), THEN start the next fix. If it hasn't run yet, either fold it in when it
appears, or proceed to the next fix and let the loop pick up the queued confirm in the background —
don't block a whole iteration waiting on it.

**IMPORTANT — line numbers drift, every session, predictably (though s500 saw ZERO drift for once).**
Before writing a fix, re-run:
```
python3 scratch/agent/s494_item317_step3_tracer.py --scan
```
then dedupe the fresh JSON report yourself (group `(file, hit.line, hit.kind, hit.off, hit.reg)` from
`scratch/agent/s494_item317_step3_report.json`, count sources per group, sort descending) to get the
CURRENT top-ranked locations, and cross-check the function name via `awk` backward-scan for the
nearest `RECOMP_FUNC` line above the flagged line. This check has caught real drift in 2 of the last
5 sessions that ran it (s496: +13 lines, s498: another +13 lines, s500: none — always confirm rather
than assume either way) — treat it as load-bearing, not a formality. Also: when reading source with
`sed`, verify the line count with `sed ... | nl -ba -vSTARTLINE` or a follow-up `grep -n` — a
manually-counted `sed` window is easy to misalign by one line if there's a blank line at the top of
the range (caught this exact slip in s500 before any edit was made).

**Note on the log location for any live-verify you run:** the loop's own `SOAK-RESULTS.md` line and
its `scratch/agent/soak_results/<name>_<timestamp>.log` file are ONLY a 12-line `probe.sh` summary
(pid, phase-reach time, key-press log, crash line) — they do NOT contain guard-fire detail. The full
game stdout with every `ROGUESQ_LOG_*` line is inside the capture directory itself:
`scratch/agent/soak_results/<name>/run.log`. Always read that file (grep, don't cat raw — it runs
tens of thousands of lines) when verifying fires/regressions from a queued confirm, not just the
top-level summary log.

## Current tied-at-40 tier (from s500's post-fix dedup — re-verify line numbers fresh per the drift
warning above before touching source; DO NOT trust these verbatim)

```
funcs_3.c:6014   (write, ctx->r2+0x4)
funcs_3.c:6334   (write, ctx->r2+0x4)
funcs_3.c:6644   (write, ctx->r2+0x4)
funcs_3.c:7345   (write, ctx->r2+0x4)
funcs_3.c:8305   (write, ctx->r2+0x4)
funcs_3.c:7661   (write, ctx->r2+0x4)
funcs_3.c:8649   (write, ctx->r2+0x4)
funcs_4.c:17346  (write, ctx->r2+0x4, renderLitMeshFaceGroup -- flagged since s497, still unfixed)
```
All the `funcs_3.c` entries are very likely still inside `emitFrameRdpInitDl` (same function fixed
5x already this lineage) -- confirm each via the awk backward-scan, don't assume, but expect it.
**Recommend `funcs_3.c:6014`** (or whichever is confirmed lowest-line/first-encountered in that
function after a fresh `--scan`) as the next pick. Consider: this function has now had FIVE guards
added; if two or three more tied-40 sites all resolve to the same idiom, it may be worth pausing to
ask whether a single blanket per-call-site range-check helper (rather than N individual named guards)
would be lower-maintenance for the remaining `emitFrameRdpInitDl` sites — not required, just a
standing option if the copy-paste starts to feel unwieldy.

## Remaining leads from s495's original 8-sample not yet in the tied-40 tier
1. `funcs_4.c:3299`-ish (write, `ctx->r2+0x4`) -- 26 sites at last audit, re-derive current line.
2. `funcs_3.c:28922`-ish (write, `ctx->r2+0x4`) -- 18 sites at last audit, re-derive current line.
3. `funcs_3.c:83`-ish (write, `ctx->r2+0x4`, function `heapFreeListInsert`) -- 1 site (singleton).
4. `funcs_3.c:858`-ish (read, `ctx->r3+0x0`, function `countDisplayListChunks`) -- 1 site (singleton).

## This session's work unit

**Fix the next-ranked lead (recommend the lowest-line `funcs_3.c` entry in the tied-40 tier above).**
Steps (mirror s497/s498/s500's process exactly):
1. Re-run the tracer's `--scan`, dedupe fresh, confirm the current line number and function name for
   this lead before reading source (see line-drift warning above).
2. `Read`/`sed -n` (with an `nl -ba -vSTARTLINE` or `grep -n` cross-check, per the process note above)
   the ~40-60 lines around the flagged write in
   `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_3.c` (or `funcs_4.c`) --
   confirm register/offset, containing function (search backward for nearest `RECOMP_FUNC`), and
   check whether the null-check arm gates the specific dereference or not (both shapes have occurred
   in this lineage). Judge from the actual control flow.
3. Check downstream control flow: does anything after the flagged write still use the same register
   before it's reassigned? If not, skip-the-write-on-invalid is safe (used for all fixes in this
   lineage so far). If yes, this may need a block-skip instead (the `ORIENTED_FACE_DERIVED_PTR_GUARD`
   shape) -- judge from the actual control flow, don't assume.
4. Write a new named guard (name it after the containing function/idiom, append a letter suffix if
   it's another sibling in an already-named function -- next in the `emitFrameRdpInitDl` sequence
   would be `EMIT_FRAME_RDP_INIT_DL_R2D_GUARD`) as a literal-string-anchor patch in
   `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`, confirm `text.count(old)==1`
   before writing. Mirror the exact block shape of `EMIT_FRAME_RDP_INIT_DL_R2C_GUARD`.
5. Regen: delete only the affected `funcs_*.c` file (N64Recomp skips regen of files that already
   exist) -> `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py` ->
   `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml` ->
   `python3 fixup_game_funcs.py` (check report for `... patched x1` on the new guard name, no errors,
   no SKIPPED beyond the known-permanent S392_H3A/S393_H3B remainder) -> `cd
   ~/Documents/Tools/RogueSquadron64Recomp/build` ->
   `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8`.
6. Live-verify: copy `scratch/agent/manual_runs/s500_emit_frame_rdp_init_dl_r2c_manual.sh` as a
   template (correct 3-level `../../..` path), add the new guard's `ROGUESQ_LOG_<NAME>_GUARD=1` env
   var, run in the background via Bash `run_in_background: true`, then BLOCK on it finishing with a
   foreground `while kill -0 <pid>; do sleep 5; done` (or a `Monitor` until-loop) in the SAME
   iteration -- do NOT end your turn while STATUS=WORKING waiting on a background probe; the Stop hook
   will reject it. Expect: 0 fires on the new guard is fine (rare-path bug) as long as
   `hangarbay-entry` n~30+ confirms the positive control and no sibling guard regresses. Queue a 2nd
   confirm to `scratch/agent/soak_queue/` after a clean 1st live-verify.
7. Re-run `--scan` after the fix -- check via the per-hit-line query (see PORTING-STATE.md Session
   500 for the exact python snippet) that the fixed line no longer appears as an unsafe hit anywhere,
   even if the aggregate `NEEDS_GUARD` count doesn't move.

**After this fix is confirmed**, continue down the combined list (tied-40 tier + s495's original
ranked list) one location at a time, each with its own live-verify before moving to the next. Do NOT
batch multiple unverified fixes into one build/soak cycle.

**Mandatory-pivot reminder:** this is iteration 1 of a fresh streak on this slug (s499's M5 pivot
reset the count). If this becomes the 3rd consecutive iteration on this same slug with no new lead
closed, the loop will force a pivot preamble on the iteration after. Either land a fix each
iteration, or explicitly design/run the single highest-information discriminating probe instead of
repeating the same manual fix-one-lead motion a 4th time.

## Wider unaudited population
~138 of the 150 distinct dedup'd locations remain formally unaudited. Once the ranked-list fixes
above are done, widen the audit sample (another 8-10 locations, weighted toward mid/low shared-count)
rather than assuming the whole population is clean from one 8-site sample.

## Old crash filed s498, not yet recurred -- do not chase on a single occurrence
s498's live-verify crashed at 123.8s on `pc-symbol=appendRdpStateDl+144`, `last-guest-pc=0x800109b8`
-- plausible (not confirmed) link to item -306's old flagged-not-chased cross-function-call
reload-propagation gap into `appendRdpStateDl`. Has NOT recurred as of s500 (both s499's and s500's
own confirms crashed on other, already-catalogued signatures instead). If this exact
`appendRdpStateDl+144` signature recurs 2+ times total, the highest-value next move is reading
`appendRdpStateDl`'s body directly against item -306's flagged call sites -- not another idiom-class
scan.

## Recurring already-catalogued crash family, worth noting (not yet worth chasing)
`initVec4TripletFromArgs+68` with `x0`/`x9`=`0x0000000300000000` has now recurred at s463, s468,
s489, and s500 -- same host symbol and corruption signature each time, but DIFFERENT guest PCs
(`0x800ab068` at s489, `0x80065e94` at s500), so it is not a single fixed call site. Per the s216-219
overturned-conclusion note this is an RDRAM-base-decompose artifact, not yet root-caused. Four
occurrences across unrelated guard-verify runs suggests it's a generic, fairly common failure mode
in whatever's calling `initVec4TripletFromArgs` (likely something in the animation/transform
pipeline) rather than tied to any guard in this lineage -- a candidate for a future idiom-class audit
if it becomes the highest-value target, but not urgent (it's not blocking this lineage's progress).

## Soak queue status
One outstanding recipe as of s500: `scratch/agent/soak_queue/s500_emit_frame_rdp_init_dl_r2c_confirm.sh`
(2nd confirm of this session's new guard).

## M5 lead-check
Cleared s499 (no new lead). Due again once 3+ sessions have passed from s499, i.e. s502+.
