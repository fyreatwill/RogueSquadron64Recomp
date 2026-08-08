# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s525 recap -- read this first

s525 was a **MAINTENANCE iteration** (Step 0 triggered: `docs/CURRENT-TRUTH.md` was 62,938 bytes,
over the 60,000-byte cap). Two things happened:

1. **Folded in item -317 step 3's queued 2nd confirm for `BEGIN_FRAME_DL_CHUNK_R4_GUARD`**
   (`s524_begin_frame_dl_chunk_r4_confirm`, rc=3, 163s per the flat log): the detailed `run.log`
   showed 0 `begin-frame-dl-chunk-r4-guard` fires, 0 fires on any other of the ~59 armed guard
   families, `hangarbay-entry n=2600` strong positive control. **`BEGIN_FRAME_DL_CHUNK_R4_GUARD` is now
   FULLY CLOSED 2/2** -- item -317 step 3's tally is 25/25 guards fixed so far, ALL confirmed clean on
   both independent verifies. The crash on that confirm run (`submitSceneNodeRender+67668`/
   `last-guest-pc=0x80010e6c`, Bus error) turned out to be a byte-identical repeat of an unlabeled s503
   data point -- filed as new item **-327**, a genuine 2-occurrence signature 21 sessions apart (weaker
   than item -319's 3-in-8-sessions pattern that justified a source-trace; watch for a 3rd before
   escalating).
2. **Compacted `docs/CURRENT-TRUTH.md`** from 62,938 to 43,987 bytes (net -201 lines, git-diff
   verified): migrated items -319/-321/-322/-323/-324/-325/-326/-327's full mechanism writeups into a
   new `docs/PROJECT-OVERVIEW.md` §24, updated §23's guard table (rows 24-25 now show both
   `BEGIN_FRAME_DL_CHUNK_R3_GUARD` and `_R4_GUARD` CLOSED 2/2), replaced CURRENT-TRUTH's verbose
   per-item Next-steps entries with short pointer summaries, and refreshed the stale USER DIRECTIVE
   header counts. No information was lost -- everything trimmed already existed in PROJECT-OVERVIEW or
   was migrated there this session; git history preserves the rest.

Both written up: `docs/CURRENT-TRUTH.md` items -317/-320..-327, `docs/PROJECT-OVERVIEW.md` §23-§24,
`PORTING-STATE.md` Session 525.

## The work unit for the NEXT iteration: resume item -317 step 3's blanket sweep

Per the user directive's priority order, M3's top-ranked work unit is still item -317 step 3: the
~150-location blanket sweep of the s494 tracer's derived-pointer reload idiom across
`funcs_3.c`/`funcs_4.c`. **~121 locations remain unaudited** (25 of ~150 fixed so far, ALL 25 fully
closed 2/2 -- there is no pending confirm to fold in this time, so this iteration is a normal
work-unit iteration, not a fold-in-then-pick iteration).

1. **Re-run the tracer fresh** before picking a site -- line numbers drift with every insertion, and
   per the s521 gotcha, do NOT pass a custom `--out`:
   ```
   cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
   python3 scratch/agent/s494_item317_step3_tracer.py --scan
   python3 scratch/agent/s506_dedupe.py
   ```
2. Pick the next-highest-count tier from the fresh output. As of the s524 scan (STALE, taken before
   R4's own confirm regen -- re-run first): `funcs_3.c:13886`/`14802`/`15209`/`15693`/`16159` (36
   sites each, the remaining `beginFrameDLChunk` members of the tied-top tier that R1-R4 came from),
   `funcs_3.c:11625` (30 sites, `emitColorFillRect`), `funcs_4.c:4457` (`submitSceneNodeRender`, 30
   sites).
3. Follow the exact established fix pattern (see any of the 25 guards in `docs/CURRENT-TRUTH.md` item
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
Bash call and poll with a Monitor watching `pgrep -x RogueSquadron64Recomp`, per the s523 tooling
gotcha), then copy the same env block into a fresh `soak_queue/<name>_confirm.sh` for the loop to run
as the 2nd independent confirm. Read the actual `run.log` inside the output directory, not just the
thin flat summary line in `SOAK-RESULTS.md` -- the flat line's `rc=3` can mean "crashed on an
unrelated already-catalogued background-noise family after a fully clean, positively-controlled run,"
which counts as CLOSED, not as a guard failure.

## Budget note

This is iteration N on `item-317-step3-blanket-sweep` (systematic sweep, one guard per iteration, same
slug for the whole campaign per the exit contract's guidance for long systematic sweeps). s525's
maintenance interlude does not break the slug or the budget counter -- it's interleaved housekeeping,
not a stalled iteration on the hypothesis. Continue picking off tiers top-down until the tracer reports
zero remaining `NEEDS_GUARD` sites, then step back and re-run the tracer with a broader idiom pattern
if this one is exhausted.
