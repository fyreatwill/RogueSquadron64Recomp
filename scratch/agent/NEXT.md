# NEXT work unit

HYPOTHESIS-ID: item-317-step3-fix-next-ranked-leads

## s503 recap — read this first

s503 folded in the queued R2C and R2D 2nd confirms (both CLEAN, both now FULLY CLOSED 2/2), then
fixed the next tied-40-tier lead, `EMIT_FRAME_RDP_INIT_DL_R2F_GUARD` (`funcs_3.c:6670`,
`emitFrameRdpInitDl`, 40 shared sites). Its 1st live-verify was clean on the new guard (0 fires, 0
regressions) but **crashed on `appendRdpStateDl+144`/`last-guest-pc=0x800109b8` — item -318's
signature, now a 3RD independent occurrence (s498, s501, s503)** — AND this occurrence's mcontext
carried `x0`/`x9`=`0x0000000300000000`, the signature previously seen only on the separate
`initVec4TripletFromArgs+68` family (items -302/-306). Full writeup: `docs/CURRENT-TRUTH.md` item
-318 (updated this session) and `PORTING-STATE.md` Session 503.

## Decision point for this session: two legitimate options, pick one

### Option A (recommended): pivot to item -318's investigation

Item -318's own text pre-authorized this: "a 3rd occurrence upgrades this to a real pattern worth a
dedicated investigation session." That threshold is now met. This is NOT a reactive single-crash
chase (the thing the strategic-priority directive forbids) — it is exactly the "wait-for-recurrence
breadcrumb becomes active once it recurs enough" case the directive's own passive-breadcrumb policy
anticipates. If you pick this, change `HYPOTHESIS-ID` to something like
`item-318-appendrdpstatedl-3rd-occurrence` and read `docs/CURRENT-TRUTH.md` item -318's full body for
the two concrete discriminating steps already written there:
1. Source-trace what `appendRdpStateDl` dereferences at guest offset `+144` — fresh guest-address
   lookup in `funcs_3.c` (grep for `appendRdpStateDl`'s `RECOMP_FUNC` line, then find the instruction
   at byte offset +144 from its start, i.e. +36 MIPS instructions in), cross-referenced against
   `submitSceneNodeRender`'s call-argument setup immediately before `0x800109b8` in `funcs_4.c`.
2. Check whether the `0x0000000300000000` value in `x0`/`x9` can be traced to the SAME upstream
   source as the `initVec4TripletFromArgs+68` family's occurrences — grep both crash sites'
   preceding ~50 `run.log` lines (archived logs: `scratch/agent/soak_results/s503_emit_frame_rdp_init_dl_r2f_manual/run.log`
   for this occurrence; `s489_dl_alloc_propagation_manual/run.log` or similar for an
   `initVec4TripletFromArgs+68` instance) for a shared reload address or guard tag. If found, this
   resolves whether items -318 and -302/-306 are one bug or two — a big scope reduction either way.

**Discriminating outcome**: if step 1 finds a genuine unguarded/unvalidated dereference at
`appendRdpStateDl+144` that plausibly explains an `0x0000000300000000`-shaped wild pointer, that's a
real, fixable root cause — write a guard, live-verify, queue a confirm, same recipe as every other
item in this file. If step 1 finds nothing conclusive (e.g. the dereference target is bounds-checked
already, or the crash address doesn't map cleanly to a single guest instruction), step 2's
cross-family correlation check becomes the fallback discriminator; if that also comes up empty,
document both negative results and file item -318 as CLOSED-INCONCLUSIVE rather than leaving it open
indefinitely.

### Option B: continue the tied-40 tier (fallback, same proven recipe)

If you judge item -318 needs more setup than one iteration allows, the tied-40 tier is still a safe,
proven, ADVANCED-guaranteeing default — 8 sessions running the identical recipe with 0 failed
live-verifies on any fix itself. Re-run the tracer fresh (line numbers WILL have drifted if you
picked Option A and touched `emitFrameRdpInitDl` again, but should NOT have drifted if you go
straight to Option B without any other funcs_3.c edit):

```
python3 scratch/agent/s494_item317_step3_tracer.py --scan
```

then dedupe (group `(file, hit.line, hit.kind, hit.off, hit.reg)` from
`scratch/agent/s494_item317_step3_report.json`, count sources, sort descending). **Current
tied-at-40 tier (from s503's post-fix dedup, re-verify before touching source)**:

```
funcs_3.c:7384   (write, ctx->r2+0x4)
funcs_3.c:8344   (write, ctx->r2+0x4)
funcs_3.c:7700   (write, ctx->r2+0x4)
funcs_3.c:8688   (write, ctx->r2+0x4)
funcs_4.c:17346  (write, ctx->r2+0x4, renderLitMeshFaceGroup -- flagged since s497, still unfixed)
```

Recommend `funcs_3.c:7384` if you stay on this path. `funcs_4.c:17346`
(`renderLitMeshFaceGroup`) has been flagged and skipped 7 sessions running — worth picking up if
`emitFrameRdpInitDl`'s tier runs dry.

## Check queued 2nd confirms first, regardless of which option you pick

Read `scratch/agent/SOAK-RESULTS.md` tail for:
- `s502_emit_frame_rdp_init_dl_r2e_confirm` (queued since s502, may have run by now)
- `s503_emit_frame_rdp_init_dl_r2f_confirm` (queued this session)

If present, read each one's `run.log` in `scratch/agent/soak_results/<name>/run.log` (NOT the
top-level 12-line summary) for guard-fire detail, fold results into the ledger (mark CLOSED 2/2 if
clean), THEN start the next work. Don't block a whole iteration waiting on them if they haven't run
yet.

**Eight step-3 leads fixed total, six FULLY CLOSED 2/2**: `NODE_LIST_HEAD_SIBLING_R4_GUARD` (s495),
`RENDER_LIT_MESH_R2_GUARD` (s496), `EMIT_FRAME_RDP_INIT_DL_R2_GUARD` (s497), `...R2B_GUARD` (s498),
`...R2C_GUARD` (s500, 2/2 confirmed s503), `...R2D_GUARD` (s501, 2/2 confirmed s503) — plus
`...R2E_GUARD` (s502, 1/2) and `...R2F_GUARD` (s503, 1/2) each pending their 2nd confirm.

## The M5 audio-lead cadence is a SEPARATE, independent check (not tied to rule 8)

Last checked s502 (zero new leads found), due again once 3+ sessions have passed (s506+). Not due
this session (s503 is only 1 session past s502).

## Reference: the fix recipe (repeated 8x now, copy exactly, for Option B)

1. Delete `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_3.c` (only the file
   you're touching, not all `funcs_*.c` -- proven sufficient in this lineage for 8 sessions running).
2. `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py`
3. `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml`
4. Add the new guard block to `~/Documents/Tools/N64Recomp/fixup_game_funcs.py` (copy the most recent
   `EMIT_FRAME_RDP_INIT_DL_R2*_GUARD` block verbatim, rename `r2f`->`r2g` etc., update the guest
   address, update the session/item comment).
5. `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` -- redirect the FULL report to an
   in-repo scratch file (NOT `/tmp`, which is sandbox-blocked this session) and grep it for the new
   guard's `patched x1` line; confirm no NEW anchor-count mismatches beyond the known-permanent
   S392_H3A/S393_H3B remainder. If a piped/truncated grep shows nothing, verify directly by grepping
   the generated `funcs_3.c` for the new guard's enabled-flag variable name before assuming failure.
6. `cd ~/Documents/Tools/RogueSquadron64Recomp/build && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8`
7. Copy `scratch/agent/manual_runs/s503_emit_frame_rdp_init_dl_r2f_manual.sh` to a new
   `sNNN_..._manual.sh`, add the new guard's env var, run it (foreground or background+block, it
   takes ~120-300s), then grep its `run.log` (NOT the top-level summary) for the new guard's tag and
   for all other `-guard` tags to check for regressions.
8. Copy the manual script to a `_confirm.sh` variant in `scratch/agent/soak_queue/` for the loop to
   run as the 2nd independent confirm.
9. Re-run the tracer `--scan`, dedupe, update this file's tied-40 tier and recommendation.
10. Update `PORTING-STATE.md` (new session entry), `docs/CURRENT-TRUTH.md` (item -317 body + count),
    commit, `scratch/agent/STATUS`=DONE, `scratch/agent/OUTCOME`=ADVANCED.
