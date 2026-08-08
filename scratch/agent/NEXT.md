# NEXT work unit

HYPOTHESIS-ID: item-317-step3-fix-funcs4-18192

## s495 closed the tool-trust question and fixed its top lead -- do NOT re-audit from scratch

s494 built `scratch/agent/s494_item317_step3_tracer.py` (control-flow-aware taint tracer for the
`0x801163B0` reload idiom, item -317 step 3). s495 audited an 8-location sample of its 150 distinct
flagged dereference locations (top-shared, mid-range, and singleton buckets) via a subagent read
against the full existing-guard-shape catalog: **8/8 confirmed TRUE_POSITIVE, 0 false positives.**
That resolves the "is the tool trustworthy at scale" question this NEXT.md previously blocked on. The
6 audit-confirmed-but-still-unfixed locations from that sample, ranked by shared reload-site count:

1. `funcs_4.c:18192` (write, `ctx->r2+0x4`) -- **48 sites, the single largest location in the whole
   150-location population.** Function containing the dereference: `renderLitMeshFaceGroup` region
   (per the tracer's `func` field on one of its taint sources; re-derive the containing function name
   with `awk` before writing the fix, same as s495 did for the 5030 site).
2. `funcs_3.c:6979` (write, `ctx->r2+0x4`) -- 40 sites.
3. `funcs_3.c:15977` (write, `ctx->r2+0x4`) -- 32 sites.
4. `funcs_4.c:3299` (write, `ctx->r2+0x4`) -- 26 sites.
5. `funcs_3.c:28922` (write, `ctx->r2+0x4`) -- 18 sites.
6. `funcs_3.c:83` (write, `ctx->r2+0x4`, function `heapFreeListInsert`) -- 1 site (singleton).
7. `funcs_3.c:858` (read, `ctx->r3+0x0`, function `countDisplayListChunks`) -- 1 site (singleton).

Per the subagent's audit notes (see `PORTING-STATE.md` Session 495 for full text), all 6 of these
share the SAME code shape: `ctx->r2` (or `ctx->r3` for the read at 858) reloaded from the
`0x801163B0` table with only a null check (`==0`/`!=0`), no `0x80000000`-`0x80800000` range check,
before the flagged dereference. This is a DIFFERENT shape from the `funcs_4.c:5030` fix s495 shipped
(which was a sibling-register gap next to an existing `NODE_LIST_HEAD_GUARD`) -- these 6 have NO
nearby guard at all, so the fix is a fresh range-check-and-skip block at each site, not an extension
of an existing one.

## This session's work unit

**Fix `funcs_4.c:18192` (48 sites, top priority).** Steps:
1. `sed -n '18160,18195p' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_4.c`
   (or `Read` the same range) to see the exact current source around the flagged write -- confirm the
   register and offset, find the containing function name (search backward for the nearest
   `RECOMP_FUNC` line), and check there is genuinely no guard already covering it (the s495 audit did
   this at a distance via a general-purpose read; re-confirm directly before writing the fix, since the
   tool's job was auditing candidates, not guaranteeing zero drift between report and current source).
2. Write a new named guard (e.g. `RENDER_LIT_MESH_R2_GUARD` or similar -- name it after the containing
   function/idiom, following the `ORIENTED_FACE_DERIVED_PTR_GUARD`/`NODE_LIST_HEAD_SIBLING_R4_GUARD`
   naming precedent) as a literal-string-anchor patch in
   `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`, confirm `text.count(old)==1`
   before writing (uniqueness check), skip-the-write-on-invalid shape (same as
   `NODE_LIST_HEAD_WRITE_GUARD`/`NODE_LIST_HEAD_SIBLING_R4_GUARD`) unless the surrounding control flow
   makes a block-skip-to-label more natural (check whether other unsafe derefs share the same taint
   source further downstream before choosing skip-vs-block-skip, same judgment call s492 made for
   `ORIENTED_FACE_DERIVED_PTR_GUARD`).
3. Regen: remove `RecompiledFuncs/funcs_*.c` -> `make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py`
   (check report for `... patched x1` on the new guard name, no errors, no SKIPPED lines beyond the
   known-permanent S392_H3A/S393_H3B remainder) -> `cd
   /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build` -> `DEVELOPER_DIR=/Applications/
   Xcode.app/Contents/Developer cmake --build . -j8`.
4. Live-verify: copy `scratch/agent/soak_queue/s495_sibling_r4_confirm.sh` as a template, add the new
   guard's `ROGUESQ_LOG_<NAME>_GUARD=1` env var to the full sibling-guard set, run manually (foreground)
   first. Expect: 0 fires on the new guard is fine (rare-path bug, same as s495's clean pass) as long as
   `hangarbay-entry` n~31 confirms the positive control and no sibling guard regresses. Queue a 2nd
   confirm to `scratch/agent/soak_queue/` after a clean 1st live-verify.
5. Re-run `--scan` on the tracer (`python3 scratch/agent/s494_item317_step3_tracer.py --scan`) after the
   fix to see the flagged 393-raw-site count actually drop -- that's a free (no game run) regression/
   progress signal.

**After 18192 is fixed and confirmed**, work down the ranked list above (6979, 15977, 3299, 28922, then
the two singletons) in the same session or the next, one location at a time, each with its own
live-verify before moving to the next. Do NOT batch multiple unverified fixes into one build/soak
cycle -- iron rule "capture once, analyze many" is about instrumentation, not about skipping live-verify
between independent code changes.

**If `funcs_4.c:18192`'s context doesn't match the audit's summary** (drifted between report and
source, or the containing function isn't what's expected): stop, re-read the surrounding 40-60 lines
directly, and treat this as its own discriminating check before writing a fix -- don't guess.

## Wider unaudited population
144 of the 150 distinct dedup'd locations from the s494 tracer (150 total - 6 audited-this-session)
remain formally unaudited. The 0/8 false-positive rate from this session's sample is encouraging but is
one sample; once the ranked-list fixes above are done, the next useful move is widening the audit
sample (another 8-10 locations, weighted toward mid/low shared-count since the top-shared ones are now
covered) rather than assuming the whole population is clean from one 8-site sample.

## M5 lead-check
Cleared s494 (no new lead). Due again once 3+ sessions have passed from s494, i.e. s498+. (Unaffected
by this session -- item -317 step 3 continuation is unrelated to M5.)

## Soak queue status
`s495_sibling_r4_confirm.sh` queued (2nd independent confirm of `NODE_LIST_HEAD_SIBLING_R4_GUARD`).
