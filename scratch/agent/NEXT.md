# NEXT work unit

HYPOTHESIS-ID: item-317-step3-fix-next-ranked-leads

## s496 fixed the #2-ranked lead (48 sites) -- do NOT re-audit from scratch

s494 built `scratch/agent/s494_item317_step3_tracer.py` (control-flow-aware taint tracer for the
`0x801163B0` reload idiom, item -317 step 3). s495 audited an 8-location sample of its 150 distinct
flagged dereference locations via a subagent read against the full existing-guard-shape catalog:
**8/8 confirmed TRUE_POSITIVE, 0 false positives** -- the tracer is trustworthy at scale. s495 fixed
the #1 lead (`NODE_LIST_HEAD_SIBLING_R4_GUARD`, 35 sites). s496 fixed the #2 lead
(`RENDER_LIT_MESH_R2_GUARD`, funcs_4.c 0x80014C6C, `renderLitMeshFaceGroup`, 48 sites -- the single
largest location in the whole population), 1st live-verify clean (0 fires, 0 regressions,
hangarbay-entry n=34, full duration, rc=0), 2nd confirm queued
(`scratch/agent/soak_queue/s496_render_lit_mesh_r2_confirm.sh`).

**IMPORTANT -- line numbers drift.** s496 found NEXT.md's recorded line number for the #1 remaining
lead (`funcs_4.c:18192`) had drifted 13 lines from a prior regen (each new guard shifts every
subsequent line). Do NOT trust any line number below verbatim -- before writing a fix, re-run:
```
python3 scratch/agent/s494_item317_step3_tracer.py --scan
```
then dedupe the fresh JSON report yourself (group `(file, hit.line, hit.kind, hit.off, hit.reg)` from
`scratch/agent/s494_item317_step3_report.json`, count sources per group, sort descending) to get the
CURRENT top-ranked locations, and cross-check the function name via `awk` backward-scan for the
nearest `RECOMP_FUNC` line above the flagged line. Only then read the exact surrounding source.

## Remaining audit-confirmed leads (s495's original 8-sample, 2 now fixed)

Ranked by shared reload-site count at the time of the s495 audit (re-derive current line numbers
before use, per above):
1. `funcs_3.c:6979` (write, `ctx->r2+0x4`) -- 40 sites. **Next up.**
2. `funcs_3.c:15977` (write, `ctx->r2+0x4`) -- 32 sites.
3. `funcs_4.c:3299` (write, `ctx->r2+0x4`) -- 26 sites.
4. `funcs_3.c:28922` (write, `ctx->r2+0x4`) -- 18 sites.
5. `funcs_3.c:83` (write, `ctx->r2+0x4`, function `heapFreeListInsert`) -- 1 site (singleton).
6. `funcs_3.c:858` (read, `ctx->r3+0x0`, function `countDisplayListChunks`) -- 1 site (singleton).

All share the same shape confirmed twice now (s495's audit, s496's direct fix): `ctx->r2` (or
`ctx->r3` for the read at 858) reloaded from the `0x801163B0` table with only a null check
(`==0`/`!=0`), no `0x80000000`-`0x80800000` range check, before the flagged dereference, and no
nearby existing guard covers it. Fix shape: fresh range-check-and-skip block per site (same as
`RENDER_LIT_MESH_R2_GUARD`/`NODE_LIST_HEAD_SIBLING_R4_GUARD`), not an extension of an existing guard.

## This session's work unit

**Fix `funcs_3.c:6979` (40 sites, next priority).** Steps (mirror s496's process exactly):
1. Re-run the tracer's `--scan`, dedupe fresh, confirm the current line number and function name for
   this lead before reading source (see line-drift warning above).
2. `Read`/`sed -n` the ~40-60 lines around the flagged write in
   `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_3.c` -- confirm register/
   offset, containing function (search backward for nearest `RECOMP_FUNC`), and check for a genuinely
   absent nearby guard (search +/-500 lines for `GUARD`).
3. Check downstream control flow: does anything after the flagged write still use the same register
   before it's reassigned? If not, skip-the-write-on-invalid is safe (the pattern used for both s495
   and s496's fixes). If yes, this may need a block-skip instead (the `ORIENTED_FACE_DERIVED_PTR_GUARD`
   shape) -- judge from the actual control flow, don't assume.
4. Write a new named guard (name it after the containing function/idiom) as a literal-string-anchor
   patch in `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`, confirm
   `text.count(old)==1` before writing.
5. Regen: delete only the affected `funcs_*.c` file (N64Recomp skips regen of files that already
   exist) -> `make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py` (check report for `... patched x1`
   on the new guard name, no errors, no SKIPPED beyond the known-permanent S392_H3A/S393_H3B
   remainder) -> `cd build` -> `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
   . -j8`.
6. Live-verify: copy `scratch/agent/soak_queue/s496_render_lit_mesh_r2_confirm.sh` as a template (it
   has the correct 3-level `../../..` path -- do NOT copy the older s495 template, which had the bug
   below), add the new guard's `ROGUESQ_LOG_<NAME>_GUARD=1` env var, run manually (foreground,
   `run_in_background: true` + `TaskOutput block=true` to wait) first. Expect: 0 fires on the new guard
   is fine (rare-path bug) as long as `hangarbay-entry` n~30+ confirms the positive control and no
   sibling guard regresses. Queue a 2nd confirm to `scratch/agent/soak_queue/` after a clean 1st
   live-verify.
7. Re-run `--scan` after the fix to see the flagged `NEEDS_GUARD` count actually drop (was 390 after
   s496's fix) -- a free (no game run) regression/progress signal. Expect a small drop (a handful, not
   40) -- only reload sites whose ALL downstream unsafe hits are at this one location will flip to
   SAFE, same as s496's 392->390 for a "48 sites" fix.

**After `funcs_3.c:6979` is fixed and confirmed**, work down the ranked list (15977, 3299, 28922, then
the two singletons) one location at a time, each with its own live-verify before moving to the next.
Do NOT batch multiple unverified fixes into one build/soak cycle.

## Wider unaudited population
~144 of the 150 distinct dedup'd locations remain formally unaudited (150 - 6 from s495's sample, 2 of
which are now fixed). Once the ranked-list fixes above are done, widen the audit sample (another 8-10
locations, weighted toward mid/low shared-count) rather than assuming the whole population is clean
from one 8-site sample.

## Soak queue status
- `scratch/agent/soak_queue/s496_render_lit_mesh_r2_confirm.sh` queued (2nd independent confirm of
  `RENDER_LIT_MESH_R2_GUARD`).
- `scratch/agent/soak_queue/s496_sibling_r4_confirm_retry.sh` queued (corrected retry of s495's 2nd
  confirm of `NODE_LIST_HEAD_SIBLING_R4_GUARD` -- the original `s495_sibling_r4_confirm.sh` had a
  path-depth bug (`../..` instead of `../../..`) that made it fail before the game ever launched,
  rc=1/0s, not a real test).
- **Check any other queued/done recipe for the same two-vs-three-level relative-path mistake before
  trusting its rc** -- this was a one-off copy error in s495's session, not a systemic pattern found
  elsewhere yet, but hasn't been swept for.

## M5 lead-check
Cleared s494 (no new lead). Due again once 3+ sessions have passed from s494, i.e. s498+. (Unaffected
by this session -- item -317 step 3 continuation is unrelated to M5.)
