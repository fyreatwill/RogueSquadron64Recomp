# NEXT work unit

HYPOTHESIS-ID: item-317-step3-fix-next-ranked-leads

## Iron rule 8 was fixed mid-lineage — read this before assuming a pivot is due

`tools/agent/loop.sh` / `stop_gate.sh` / `ITERATION.md` now implement an outcome-blind-corrected
rule 8: **a gate-validated ADVANCED iteration resets the consecutive-iteration counter**, so a long
systematic sweep (this exact item -317 step-3 campaign) can hold ONE HYPOTHESIS-ID for many sessions
without tripping a forced pivot, as long as each iteration actually lands a real fix. Only consecutive
NON-ADVANCED iterations count toward the 3-strike/4-strike thresholds now. (s502 found this fix
already sitting uncommitted in the working tree — not made by that session — with no prior
PORTING-STATE entry; s502 committed it alongside its own work. If you're reading this and
`scratch/agent/PIVOT.md` exists, that's the CURRENT signal a pivot is mandatory — trust that file, not
a stale iteration count from an old NEXT.md.) Since s500, s501, and s502 were all gate-validated
ADVANCED, the counter is effectively back at 0 going into s503 — **do not treat s503 as needing a
pivot preamble on iteration-count grounds alone.** Keep this HYPOTHESIS-ID slug for as long as the
tied-40 tier keeps yielding real fixes; only change it on an actual pivot or close.

The M5 audio-lead cadence is a SEPARATE, independent check (not tied to rule 8): last checked s502
(zero new leads found), due again once 3+ sessions have passed (s506+).

## Check queued 2nd confirms first

Read `scratch/agent/SOAK-RESULTS.md` tail for lines mentioning:
- `s500_emit_frame_rdp_init_dl_r2c_confirm`
- `s501_emit_frame_rdp_init_dl_r2d_confirm`
- `s502_emit_frame_rdp_init_dl_r2e_confirm`

If present, read each one's `run.log` in `scratch/agent/soak_results/<name>/run.log` for guard-fire
detail (the top-level `.log` is only a 12-line summary), fold the results into the ledger (mark
R2C/R2D/R2E fully CLOSED 2/2 if clean), THEN start the next work. If any haven't run yet, either fold
them in when they appear or proceed to the next fix and let the loop pick up the queued confirms in
the background -- don't block a whole iteration waiting on them.

**Seven step-3 leads fixed so far, four FULLY CLOSED 2/2**: `NODE_LIST_HEAD_SIBLING_R4_GUARD` (s495,
35 sites), `RENDER_LIT_MESH_R2_GUARD` (s496, 48 sites), `EMIT_FRAME_RDP_INIT_DL_R2_GUARD` (s497,
`funcs_3.c`, 40 sites), `EMIT_FRAME_RDP_INIT_DL_R2B_GUARD` (s498, same function, 40 sites) — plus
`EMIT_FRAME_RDP_INIT_DL_R2C_GUARD` (s500, 1/2), `EMIT_FRAME_RDP_INIT_DL_R2D_GUARD` (s501, 1/2), and
`EMIT_FRAME_RDP_INIT_DL_R2E_GUARD` (s502, 1/2 — the cleanest live-verify in the lineage: 0 fires, 0
regressions, NO crash of any kind for the full 250s scheduled duration) each at 1/2, pending their
queued 2nd confirms.

## Item -318 status: unchanged, still 2 data points, not yet a 3rd confirm

The `appendRdpStateDl+144` / `submitSceneNodeRender`-call-site crash (item -318) has NOT recurred
since s501 — s502's live-verify hit no crash at all, so it neither confirmed nor refuted anything about
item -318. Still 2 independent occurrences (s498 all-zero, s501 non-trivial `0xB0BB7280`). Treat any
conclusion here as still provisional; do not chase reactively. If it recurs a 3rd time on a future
live-verify, that upgrades it to a real pattern worth a dedicated investigation session — see
`docs/CURRENT-TRUTH.md` item -318 for the concrete next steps already written (source-level offset
mapping into `appendRdpStateDl+144`, cross-check against the tracer's per-func report).

## Recommended default: continue the tied-40 tier (7th session running the identical proven recipe)

**Before writing a fix, re-run:**
```
python3 scratch/agent/s494_item317_step3_tracer.py --scan
```
then dedupe the fresh JSON report yourself (group `(file, hit.line, hit.kind, hit.off, hit.reg)` from
`scratch/agent/s494_item317_step3_report.json`, count sources per group, sort descending) to get the
CURRENT top-ranked locations, and cross-check the function name via `awk` backward-scan for the
nearest `RECOMP_FUNC` line above the flagged line. Line-drift precedent: s496 caught +13, s498 caught
+13, s500/s501 caught NONE, s502 caught +13 again — always confirm rather than assume either way.

## Current tied-at-40 tier (from s502's post-fix dedup — re-verify line numbers fresh per the drift
warning above before touching source; DO NOT trust these verbatim)

```
funcs_3.c:6670   (write, ctx->r2+0x4)
funcs_3.c:7371   (write, ctx->r2+0x4)
funcs_3.c:8331   (write, ctx->r2+0x4)
funcs_3.c:7687   (write, ctx->r2+0x4)
funcs_3.c:8675   (write, ctx->r2+0x4)
funcs_4.c:17346  (write, ctx->r2+0x4, renderLitMeshFaceGroup -- flagged since s497, still unfixed)
```
All the `funcs_3.c` entries are very likely still inside `emitFrameRdpInitDl` (same function fixed
7x already this lineage) -- confirm each via the awk backward-scan, don't assume, but expect it.
**Recommend `funcs_3.c:6670`** (or whichever is confirmed lowest-line/first-encountered in that
function after a fresh `--scan`) as the next pick if you stay on the tied-40 tier. This function has
now had SEVEN guards added; if two or three more tied-40 sites all resolve to the same idiom, it may
be worth pausing to ask whether a single blanket per-call-site range-check helper (rather than N
individual named guards) would be lower-maintenance for the remaining `emitFrameRdpInitDl` sites --
not required, just a standing option if the copy-paste starts to feel unwieldy (now at 7 near-
identical named guards in one function). Also worth a look: `funcs_4.c:17346`
(`renderLitMeshFaceGroup`) has been flagged and skipped over since s497 in favor of same-function
`emitFrameRdpInitDl` siblings every session — if the tied-40 tier in `emitFrameRdpInitDl` runs dry
soon, this is the next distinct function to audit.

## Remaining leads from s495's original 8-sample not yet in the tied-40 tier
1. `funcs_4.c:3299`-ish (write, `ctx->r2+0x4`) -- 26 sites at last audit, re-derive current line.
2. `funcs_3.c:28922`-ish (write, `ctx->r2+0x4`) -- 18 sites at last audit, re-derive current line.
3. `funcs_3.c:83`-ish (write, `ctx->r2+0x4`, function `heapFreeListInsert`) -- 1 site (singleton).
4. `funcs_3.c:858`-ish (read, `ctx->r3+0x0`, function `countDisplayListChunks`) -- 1 site (singleton).

## Reference: the fix recipe (repeated 7x now, copy exactly)

1. Delete `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_3.c` (only the file
   you're touching, not all `funcs_*.c` -- proven sufficient in this lineage for 7 sessions running).
2. `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py`
3. `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml`
4. Add the new guard block to `~/Documents/Tools/N64Recomp/fixup_game_funcs.py` (copy the most recent
   `EMIT_FRAME_RDP_INIT_DL_R2*_GUARD` block verbatim, rename `r2e`->`r2f` etc., update the guest
   address, update the session/item comment).
5. `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` -- audit the report for the new guard's
   `patched x1` line and confirm no NEW anchor-count mismatches beyond the known-permanent
   S392_H3A/S393_H3B SKIPPED remainder.
6. `cd ~/Documents/Tools/RogueSquadron64Recomp/build && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8`
7. Copy `scratch/agent/manual_runs/s502_emit_frame_rdp_init_dl_r2e_manual.sh` to a new
   `sNNN_..._manual.sh`, add the new guard's env var, run it (foreground or background+block, it
   takes ~120-300s), then grep its `run.log` (NOT the top-level summary) for the new guard's tag and
   for all other `-guard` tags to check for regressions.
8. Copy the manual script to a `_confirm.sh` variant in `scratch/agent/soak_queue/` for the loop to
   run as the 2nd independent confirm.
9. Re-run the tracer `--scan`, dedupe, update this file's tied-40 tier and recommendation.
10. Update `PORTING-STATE.md` (new session entry), `docs/CURRENT-TRUTH.md` (item -317 body + count),
    commit, `scratch/agent/STATUS`=DONE, `scratch/agent/OUTCOME`=ADVANCED.
