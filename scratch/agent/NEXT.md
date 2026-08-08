# NEXT work unit

HYPOTHESIS-ID: item-317-step3-fix-next-ranked-leads

## s504 recap — read this first

s504 was a triggered MAINTENANCE iteration (Step 0 of ITERATION.md: `docs/CURRENT-TRUTH.md` had grown to
65,633 bytes, over the 60,000-byte threshold). Compacted it to 47,371 bytes (204 net lines removed,
ADVANCED per the maintenance rule) by migrating the s493-503 item -317 step-3 fix-campaign play-by-play
into a new `docs/PROJECT-OVERVIEW.md` §22 and leaving only current-status text in CURRENT-TRUTH. No
experiment was run this session, per the maintenance-iteration rule.

While reading for accuracy, folded in the two soaks that had been sitting unread in
`scratch/agent/SOAK-RESULTS.md` since s502/s503:
- `s502_emit_frame_rdp_init_dl_r2e_confirm`: CLEAN — R2E guard now FULLY CLOSED 2/2.
- `s503_emit_frame_rdp_init_dl_r2f_confirm`: CLEAN — R2F guard now FULLY CLOSED 2/2. Its crash
  (`submitSceneNodeRender+67668`/`last-guest-pc=0x80010e6c`) is the SAME function as item -318 but a
  DIFFERENT guest PC than item -318's `0x800109b8` — a 4th data point for that thread, not a 4th
  confirmed occurrence of the specific 3x-recurring signature.

**All 8 step-3 leads fixed so far are now FULLY CLOSED 2/2.**

**Important correction to item -318**: its "new correlation" reading (the `x0`/`x9`=`0x0000000300000000`
value linking it to the `initVec4TripletFromArgs+68` family) is very likely a FALSE LEAD. CURRENT-TRUTH's
own overturned-conclusions section (s216-218→s219) already established that this constant in `x0`/`x8` is
the process's RDRAM host base pointer, present by construction in every `MEM_W`-macro fault — not written
corruption. This session's R2E/R2F confirms add two more sightings in two MORE different registers (`x8`,
`x11`), a fourth and fifth register pairing across the accumulated data, which further supports "common
incidental constant" over "one bug's corrupted value." **If picking up item -318, skip the
cross-family-register angle** — trace `appendRdpStateDl+144`'s actual dereference at guest offset `+144`
instead; that half of the item (the exact-signature 3x recurrence) is unaffected and still real.

## Decision point for this session: two legitimate options, pick one

### Option A: pivot to item -318's investigation (the appendRdpStateDl+144 recurrence, not the register angle)

Three independent occurrences (s498, s501, s503) of `pc-symbol=appendRdpStateDl+144`,
`last-guest-pc=0x800109b8` meets item -318's own pre-set "3rd occurrence" threshold. If you pick this,
change `HYPOTHESIS-ID` to `item-318-appendrdpstatedl-3rd-occurrence` and read `docs/CURRENT-TRUTH.md` item
-318's full body for the concrete next step: source-trace what `appendRdpStateDl` dereferences at guest
offset `+144` (fresh guest-address lookup in `funcs_3.c`, cross-referenced against
`submitSceneNodeRender`'s call-argument setup immediately before `0x800109b8` in `funcs_4.c`). **Do not**
spend time on the `0x0000000300000000` cross-family correlation — see the correction above.

**Discriminating outcome**: if the trace finds a genuine unguarded/unvalidated dereference at
`appendRdpStateDl+144` that plausibly explains a wild pointer, write a guard, live-verify, queue a confirm
— same recipe as every other item in this file. If it finds nothing conclusive, document the negative
result and consider item -318 CLOSED-INCONCLUSIVE rather than leaving it open indefinitely.

### Option B: continue the tied-40 tier (fallback, same proven recipe, 8/8 clean so far)

```
python3 scratch/agent/s494_item317_step3_tracer.py --scan
```

then dedupe (group `(file, hit.line, hit.kind, hit.off, hit.reg)` from
`scratch/agent/s494_item317_step3_report.json`, count sources, sort descending). **Current tied-at-40
tier (from s503's post-fix dedup, re-verify before touching source — line numbers WILL have drifted if
Option A touched `funcs_3.c`)**:

```
funcs_3.c:7384   (write, ctx->r2+0x4)
funcs_3.c:8344   (write, ctx->r2+0x4)
funcs_3.c:7700   (write, ctx->r2+0x4)
funcs_3.c:8688   (write, ctx->r2+0x4)
funcs_4.c:17346  (write, ctx->r2+0x4, renderLitMeshFaceGroup -- flagged since s497, unfixed 8 sessions)
```

Recommend `funcs_3.c:7384` if you stay on this path.

## The M5 audio-lead cadence is a SEPARATE, independent check (not tied to rule 8)

Last checked s502 (zero new leads). Due again once 3+ sessions have passed — s506+. Not due this session.

## Reference: the fix recipe (repeated 8x now, copy exactly, for Option B)

1. Delete `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_3.c` (only the file
   you're touching).
2. `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py`
3. `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml`
4. Add the new guard block to `~/Documents/Tools/N64Recomp/fixup_game_funcs.py` (copy the most recent
   `EMIT_FRAME_RDP_INIT_DL_R2*_GUARD` block verbatim, rename `r2f`->`r2g` etc., update the guest address,
   update the session/item comment).
5. `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` — redirect the FULL report to an in-repo
   scratch file (not `/tmp`) and grep it for the new guard's `patched x1` line; confirm no NEW
   anchor-count mismatches beyond the known-permanent S392_H3A/S393_H3B remainder.
6. `cd ~/Documents/Tools/RogueSquadron64Recomp/build && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8`
7. Copy the most recent `sNNN_..._manual.sh` to a new `sNNN_..._manual.sh`, add the new guard's env var,
   run it, grep its `run.log` (not the top-level summary) for the new guard's tag and for all other
   `-guard` tags to check for regressions.
8. Copy the manual script to a `_confirm.sh` variant in `scratch/agent/soak_queue/` for the loop to run.
9. Re-run the tracer `--scan`, dedupe, update this file's tied-40 tier and recommendation.
10. Update `PORTING-STATE.md` (new session entry), `docs/CURRENT-TRUTH.md` (item -317 body + count),
    commit, `scratch/agent/STATUS`=DONE, `scratch/agent/OUTCOME`=ADVANCED.
