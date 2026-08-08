# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s526 recap -- read this first

s526 was a normal work-unit iteration (no pending confirm to fold in; s525's maintenance pass left the
sweep at a clean 25/25, all fully closed 2/2).

1. **Re-ran the tracer fresh** (`s494_item317_step3_tracer.py --scan` then `s506_dedupe.py`, no custom
   `--out`, per the s521 gotcha): 448 raw reload sites (318 `NEEDS_GUARD`), top tier still the 5 tied
   remaining `beginFrameDLChunk` members at 36 sites each (R1-R4 had dropped out once fixed).
2. **Source-traced and FIXED `BEGIN_FRAME_DL_CHUNK_R5_GUARD`** (`funcs_3.c:13886`, guest address
   `0x8000AD84`, load pair `0x8000AD74`/`0x8000AD78` -- distinct from R1-R4's own pairs). Exact same
   shape as every prior guard in this lineage: null-check gates one arm safely, non-null fallthrough
   dereferences the reload unconditionally with no range check, downstream reload at `0x8000ADA0` feeds
   the pre-existing `GENERIC_CACHE_GUARD` deref at `0x8000ADA4` (s434) confirming skip-on-invalid is
   safe. Added to `tools/fixup_game_funcs.py` (N64Recomp repo) matching the R1-R4 pattern exactly.
3. **1st live-verify clean, the cleanest class again**: 0 `begin-frame-dl-chunk-r5-guard` fires, 0
   regressions on ~60 other armed guard families (1 benign pre-existing `hangarmenu-a0-guard` hit, item
   -265, unrelated), `hangarbay-entry n=35` positive control, **full 300s scheduled duration completed
   with rc=0 and zero crashes of any kind** (118 frames captured). 2nd independent confirm queued:
   `scratch/agent/soak_queue/s526_begin_frame_dl_chunk_r5_confirm.sh`.
4. Tally: item -317 step 3 now 26/~150 fixed, 25 fully closed 2/2, R5 pending its 2nd confirm. ~120
   sites remain after R5 drops out of the tier. No new breadcrumb crash surfaced this session.

Full detail: `docs/CURRENT-TRUTH.md` item -317, `PORTING-STATE.md` Session 526.

## The work unit for the NEXT iteration

**If `scratch/agent/SOAK-RESULTS.md` has a new line for `s526_begin_frame_dl_chunk_r5_confirm`**: read
its `run.log` (not just the flat summary line -- an `rc=3` can mean "crashed on an unrelated
already-catalogued background-noise family after a fully clean, positively-controlled run", which still
counts as CLOSED). If 0 `begin-frame-dl-chunk-r5-guard` fires and a strong `hangarbay-entry` positive
control, mark `BEGIN_FRAME_DL_CHUNK_R5_GUARD` FULLY CLOSED 2/2 in `docs/CURRENT-TRUTH.md` item -317 (26
fixed, 26 fully closed) and fold the result into `PORTING-STATE.md`. Then continue to the next site
below in the SAME iteration (this is a fold-in-then-pick iteration, matching the s521-s525 pattern).

**If no confirm result is queued yet**, this is a normal pick-the-next-site iteration:

1. **Re-run the tracer fresh** before picking a site -- line numbers drift with every insertion:
   ```
   cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
   python3 scratch/agent/s494_item317_step3_tracer.py --scan
   python3 scratch/agent/s506_dedupe.py
   ```
2. Pick the next-highest-count tier from the fresh output. As of the s526 scan (STALE once R5's own
   regen lands -- re-run first): `funcs_3.c:14802`/`15209`/`15693`/`16159` (36 sites each, the
   remaining `beginFrameDLChunk` members of the tied-top tier), `funcs_3.c:11625` (30 sites,
   `emitColorFillRect`), `funcs_4.c:4457` (`submitSceneNodeRender`, 30 sites).
3. Follow the exact established fix pattern (see any of the 26 guards in `docs/CURRENT-TRUTH.md` item
   -317, or `docs/PROJECT-OVERVIEW.md` §22-§24 for the full guard-by-guard table): null check gates one
   arm, non-null fallthrough has no `0x80000000`-`0x80800000` range check before a write-through deref,
   downstream control flow reloads the register from the same table again -- skip-on-invalid is safe.
   Confirm this shape holds at the specific site before writing the fix, AND confirm the picked line
   isn't already guarded by reading the actual generated source AND grepping `fixup_game_funcs.py` for
   the guest address (the tracer's own dedupe ranking can lag a stale canonical report file, see the
   s521 gotcha below).
4. **If the site is in `beginFrameDLChunk`**: that function carries `g_rs64_last_guest_pc` breadcrumb
   writes between every disassembly comment and its corresponding C statement (unlike e.g.
   `renderLitMeshFaceGroup`, which doesn't) -- the fixup patch's old/new match strings MUST include
   that breadcrumb line or the string replace silently no-ops (`text.count(old) == 0`, caught by
   checking the count before trusting the patch applied). Multiple sites in this function also reload
   from DIFFERENT global table slots -- confirm each new site's own load-pair address before assuming
   it's a duplicate of a prior guard.
5. Regen/build/live-verify/queue-2nd-confirm sequence (see Regen reminder below). **If the 1st
   live-verify attempt crashes early (<~60s) on the async Metal.framework/system-thread cluster
   (`pc-symbol` containing `isPlatformOrVariantPlatformVersionAtLeast.cold` with an absurd offset, OR
   `pc=0x800ab0e0`/similar addresses, already-catalogued items -10/-9/-303/-315/-508) with a weak
   `hangarbay-entry` count (<~10), discard it per Iron Rule 1 and retry once** -- this cluster can
   manifest as EITHER SIGSEGV or SIGABRT, so check the `pc-symbol` pattern, not just the signal number.
6. **Watch for a 2nd/3rd occurrence of the new items from this campaign**: item -326
   (`do_rom_read+608`/`last-guest-pc=0x800025ac`, matches the historically-major `do_rom_read`/
   `piDmaWorker` family believed fixed since s147/148 -- if it recurs, STOP the sweep and escalate,
   this is not routine background noise) and item -327 (`submitSceneNodeRender+67668`/
   `last-guest-pc=0x80010e6c`, already 2 occurrences 21 sessions apart -- a 3rd would justify a
   source-trace).

**Important**: after launching a foreground live-verify run in the background, use TaskOutput with
`block=true` to actually wait for it to finish IN THIS TURN before ending the turn -- do NOT end the
turn on "waiting for the background run" and expect a later turn to pick it up. The Stop hook checks
`scratch/agent/STATUS` every turn and will block/fail the iteration if it's still `WORKING` when the
turn ends. (s526 gotcha: ending a turn mid-wait cost one extra turn recovering from the Stop hook
block -- block on TaskOutput instead of narrating a promise to check back later.)

## Regen reminder (every fix)

```
cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py
# delete stale RecompiledFuncs/funcs_*.c first (item -20 standing rule) -- N64Recomp skips
# regenerating files that already exist, which risks a stale patch surviving a fixup re-run
python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"
cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml
python3 fixup_game_funcs.py   # audit the report for the expected xN counts, no anomalies
cd ~/Documents/Tools/RogueSquadron64Recomp/build && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8
```

Live-verify: copy any recent `soak_queue/done/*.sh` script as a template -- add
`ROGUESQ_LOG_<NEW_GUARD_NAME>=1` to the env block (keep every existing `ROGUESQ_LOG_*` armed for
regression checking), run it manually/foreground first (1st live-verify -- launch as a backgrounded
Bash call and use TaskOutput with `block=true` to wait for it to finish in the same turn), then copy the
same env block into a fresh `soak_queue/<name>_confirm.sh` for the loop to run as the 2nd independent
confirm. Read the actual `run.log` inside the output directory, not just the thin flat summary line in
`SOAK-RESULTS.md` -- the flat line's `rc=3` can mean "crashed on an unrelated already-catalogued
background-noise family after a fully clean, positively-controlled run," which counts as CLOSED, not as
a guard failure.

## Budget note

This is iteration N on `item-317-step3-blanket-sweep` (systematic sweep, one guard per iteration, same
slug for the whole campaign per the exit contract's guidance for long systematic sweeps). s525's
maintenance interlude does not break the slug or the budget counter -- it's interleaved housekeeping,
not a stalled iteration on the hypothesis. s526 was ADVANCED (a real fix landed), so the stall counter
is at 0. Continue picking off tiers top-down until the tracer reports zero remaining `NEEDS_GUARD`
sites, then step back and re-run the tracer with a broader idiom pattern if this one is exhausted.
