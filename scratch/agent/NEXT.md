# NEXT work unit

HYPOTHESIS-ID: item-317-step3-fix-next-ranked-leads

## Continuing this slug (s502 would be iteration 3 of the streak started at s500 after s499's
## mandatory M5 pivot — per iron rule 8, 3 consecutive iterations forces a pivot PREAMBLE, not a
## hard block yet; a 4th would block. Read this whole file before picking, including the item -318
## alternative below, and make an explicit choice rather than defaulting.)

s501 fixed `EMIT_FRAME_RDP_INIT_DL_R2D_GUARD` (`funcs_3.c:6014`, `emitFrameRdpInitDl`, 40 shared
reload sites), 1st live-verify clean, 2nd confirm queued
(`scratch/agent/soak_queue/s501_emit_frame_rdp_init_dl_r2d_confirm.sh`). **Six step-3 leads fixed so
far, four FULLY CLOSED 2/2**: `NODE_LIST_HEAD_SIBLING_R4_GUARD` (s495, 35 sites),
`RENDER_LIT_MESH_R2_GUARD` (s496, 48 sites), `EMIT_FRAME_RDP_INIT_DL_R2_GUARD` (s497, `funcs_3.c`,
40 sites), `EMIT_FRAME_RDP_INIT_DL_R2B_GUARD` (s498, same function, 40 sites) — plus
`EMIT_FRAME_RDP_INIT_DL_R2C_GUARD` (s500, 1/2, confirm still not folded in as of s501 — check
SOAK-RESULTS.md first thing) and `EMIT_FRAME_RDP_INIT_DL_R2D_GUARD` (s501, 1/2, pending its queued
2nd confirm) at 1/2 each.

**When you pick this back up: first check whether the loop already ran s500's AND s501's queued 2nd
confirms.** Read `scratch/agent/SOAK-RESULTS.md` tail for lines mentioning
`s500_emit_frame_rdp_init_dl_r2c_confirm` and `s501_emit_frame_rdp_init_dl_r2d_confirm`; if present,
read each one's `run.log` in `scratch/agent/soak_results/<name>/run.log` for guard-fire detail (the
top-level `.log` is only a 12-line summary), fold the results into the ledger (mark R2C and/or R2D
fully CLOSED if clean, 2/2), THEN start the next work. If they haven't run yet, either fold them in
when they appear, or proceed to the next fix and let the loop pick up the queued confirms in the
background — don't block a whole iteration waiting on them.

## NEW this session — item -318, a live corroborating lead on the `appendRdpStateDl+144` crash

s501's 1st live-verify crashed on the SAME `pc-symbol=appendRdpStateDl+144`,
`last-guest-pc=0x800109b8` signature s498 filed as "plausibly item -306, not chased" — but this time
with real corroboration: four sibling guards (`freelist-next-guard`, `generic-cache-guard`,
`dl-list-append-rwrite-guard`, `dl-list-reset-rnode-guard`) fired with an IDENTICAL corrupted value
(`0xB0BB7280`) in the 4 lines immediately before the crash, and the crash's own mcontext dump
carries that same value +8 (`x10=0x30bb7288`). Source-level trace placed all four guard sites AND
`last-guest-pc=0x800109b8` inside **`submitSceneNodeRender`** (`funcs_4.c`, starts line 6), not
`appendRdpStateDl` — `0x800109B8` is `submitSceneNodeRender`'s own call site
(`appendRdpStateDl(rdram, ctx);`, `funcs_4.c` ~line 2995), and `g_rs64_last_guest_pc` isn't updated
again once control leaves the caller, so it names the call site, not necessarily the fault site,
when the callee crashes before its own first logged instruction. Full writeup: `docs/CURRENT-TRUTH.md`
item -318, `PORTING-STATE.md` Session 501.

**If you pivot to this instead of another tied-40 lead:** this is still item -317's idiom-class
lineage (same corrupted-pointer-into-free-list-guard-chain shape as the original session-490
discovery), so it counts as continuing the systematic audit, not a reactive single-crash chase.
Two independent occurrences (s498 all-zero, s501 non-trivial `0xB0BB7280`) is not yet a third
confirm, so treat any conclusion here as still provisional. Concrete next steps:
1. Read `funcs_3.c` `appendRdpStateDl` (starts line 26458) and find what it actually dereferences at
   host offset `+144` — this needs a FRESH disassembly-offset-to-guest-address mapping (144 bytes of
   compiled ARM64 code from function entry is NOT proportional to guest-MIPS bytes; use `nm`/`atos`
   or a debug build symbol table, or count `RECOMP_FUNC` bodies' emitted C statements from the top
   and correlate via a small instrumented rebuild if `atos` isn't precise enough).
2. Cross-check whether `appendRdpStateDl` also reloads from the `0x801163B0` global (the item -317
   family's root cause) — if so, this may just be a 7th "step 3" sibling lead in a function the
   tracer's current scan scope doesn't cover yet (`s494_item317_step3_tracer.py --scan` only covers
   `funcs_3.c`/`funcs_4.c`; `appendRdpStateDl` IS in `funcs_3.c`, so re-check the tracer's per-func
   report for it directly rather than assuming it's out of scope — a first check this session found
   NO tracer hits for `appendRdpStateDl`, meaning either it doesn't reload `0x801163B0` directly, or
   the corruption arrives via `ctx` state left over from the caller rather than a fresh reload; don't
   assume, re-verify).
3. If (2) is negative, trace what `submitSceneNodeRender` passes into the call at `0x800109B8`
   (likely `ctx->r4`/`ctx->r5` argument registers per the MIPS calling convention — read the ~20
   lines before the call site, `funcs_4.c` ~2975-2995) and whether that argument is derived from the
   same corrupted state the four guards just flagged.
4. Only reaches ADVANCED/fix-worthy once you have a concrete guarded write to add, verified the same
   way as every other item -317 fix (build, live-verify, 0 fires + 0 regressions or a NEW confirmed
   fire, queue 2nd confirm).

## Recommended default: continue the tied-40 tier (lower effort, proven recipe) unless item -318's
## trace above turns up something concrete quickly

**Before writing a fix, re-run:**
```
python3 scratch/agent/s494_item317_step3_tracer.py --scan
```
then dedupe the fresh JSON report yourself (group `(file, hit.line, hit.kind, hit.off, hit.reg)` from
`scratch/agent/s494_item317_step3_report.json`, count sources per group, sort descending) to get the
CURRENT top-ranked locations, and cross-check the function name via `awk` backward-scan for the
nearest `RECOMP_FUNC` line above the flagged line. Line-drift precedent: s496 caught +13, s498
caught +13, s500/s501 caught NONE — always confirm rather than assume either way.

## Current tied-at-40 tier (from s501's post-fix dedup — re-verify line numbers fresh per the drift
warning above before touching source; DO NOT trust these verbatim)

```
funcs_3.c:6347   (write, ctx->r2+0x4)
funcs_3.c:6657   (write, ctx->r2+0x4)
funcs_3.c:7358   (write, ctx->r2+0x4)
funcs_3.c:8318   (write, ctx->r2+0x4)
funcs_3.c:7674   (write, ctx->r2+0x4)
funcs_3.c:8662   (write, ctx->r2+0x4)
funcs_4.c:17346  (write, ctx->r2+0x4, renderLitMeshFaceGroup -- flagged since s497, still unfixed)
```
All the `funcs_3.c` entries are very likely still inside `emitFrameRdpInitDl` (same function fixed
6x already this lineage) -- confirm each via the awk backward-scan, don't assume, but expect it.
**Recommend `funcs_3.c:6347`** (or whichever is confirmed lowest-line/first-encountered in that
function after a fresh `--scan`) as the next pick if you stay on the tied-40 tier. This function has
now had SIX guards added; if two or three more tied-40 sites all resolve to the same idiom, it may be
worth pausing to ask whether a single blanket per-call-site range-check helper (rather than N
individual named guards) would be lower-maintenance for the remaining `emitFrameRdpInitDl` sites --
not required, just a standing option if the copy-paste starts to feel unwieldy (now at 6 near-
identical named guards in one function).

## Remaining leads from s495's original 8-sample not yet in the tied-40 tier
1. `funcs_4.c:3299`-ish (write, `ctx->r2+0x4`) -- 26 sites at last audit, re-derive current line.
2. `funcs_3.c:28922`-ish (write, `ctx->r2+0x4`) -- 18 sites at last audit, re-derive current line.
3. `funcs_3.c:83`-ish (write, `ctx->r2+0x4`, function `heapFreeListInsert`) -- 1 site (singleton).
4. `funcs_3.c:858`-ish (read, `ctx->r3+0x0`, function `countDisplayListChunks`) -- 1 site (singleton).

## Reference: the fix recipe (repeated 6x now, copy exactly)

1. Delete `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_3.c` (only the file
   you're touching, not all `funcs_*.c` -- proven sufficient in this lineage for 6 sessions running).
2. `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py`
3. `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml`
4. Add the new guard block to `~/Documents/Tools/N64Recomp/fixup_game_funcs.py` (copy the most recent
   `EMIT_FRAME_RDP_INIT_DL_R2*_GUARD` block verbatim, rename `r2d`->`r2e` etc., update the guest
   address, update the session/item comment).
5. `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` -- audit the report for the new guard's
   `patched x1` line and confirm no NEW anchor-count mismatches beyond the known-permanent
   S392_H3A/S393_H3B SKIPPED remainder.
6. `cd ~/Documents/Tools/RogueSquadron64Recomp/build && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8`
7. Copy `scratch/agent/manual_runs/s501_emit_frame_rdp_init_dl_r2d_manual.sh` to a new
   `sNNN_..._manual.sh`, add the new guard's env var, run it (foreground or background+block, it
   takes ~120-300s), then grep its `run.log` (NOT the top-level summary) for the new guard's tag and
   for all other `-guard` tags to check for regressions.
8. Copy the manual script to a `_confirm.sh` variant in `scratch/agent/soak_queue/` for the loop to
   run as the 2nd independent confirm.
9. Re-run the tracer `--scan`, dedupe, update this file's tied-40 tier and recommendation.
10. Update `PORTING-STATE.md` (new session entry), `docs/CURRENT-TRUTH.md` (item -317 body + count),
    commit, `scratch/agent/STATUS`=DONE, `scratch/agent/OUTCOME`=ADVANCED.
