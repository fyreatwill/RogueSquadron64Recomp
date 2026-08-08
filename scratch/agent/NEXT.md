# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s522 recap -- read this first

s522 did two things:

1. **Folded in item -317 step 3's queued 2nd confirm for `BEGIN_FRAME_DL_CHUNK_R1_GUARD`**
   (`s521_begin_frame_dl_chunk_r1_confirm`, rc=3, 175s per the flat log): the detailed `run.log`
   showed 0 `begin-frame-dl-chunk-r1-guard` fires, one benign already-catalogued `hangarmenu-a0-guard`
   co-fire (item -265), `hangarbay-entry n=2700` strong positive control. The crash itself
   (`pc-symbol=coalesceFreeHeapBlocks+4424`/`last-guest-pc=0x8000247c`) is byte-identical to the
   already-catalogued background-noise heap-walker family (documented s354-366) -- same "clean pass
   despite unrelated background-noise crash" precedent as item -322's own closure.
   **`BEGIN_FRAME_DL_CHUNK_R1_GUARD` is now FULLY CLOSED 2/2.**
2. **Picked up item -317 step 3's blanket sweep again** and fixed its 21st site (2nd guard in
   `beginFrameDLChunk`): `BEGIN_FRAME_DL_CHUNK_R2_GUARD` (`funcs_3.c:12895`/`0x8000AA9C`, 36 shared
   reload sites at scan time, reloads a DIFFERENT `0x63B0`-offset table slot than R1). 1st live-verify
   CLEAN on the 2nd attempt (0 own-guard fires, 0 fires on every other armed guard family,
   `hangarbay-entry n=31` positive control) -- the 1st attempt was discarded per Iron Rule 1 (crashed
   at 20.3s on the already-catalogued Metal.framework async shader-compiler SIGSEGV cluster with only
   `hangarbay-entry n~5`, too weak a positive control). 2nd confirm queued:
   `scratch/agent/soak_queue/s522_begin_frame_dl_chunk_r2_confirm.sh` -- fold its result in next
   session.
3. **Surfaced a new single-occurrence crash**: the 2nd-attempt live-verify crashed at 129.4s on
   `pc-symbol=findLookupEntryByKey+2212 (local-symtab)`, `last-guest-pc=0x800ad0dc` -- genuinely new,
   filed as item -325, not chased (no 2nd occurrence yet).

Both written up: `docs/CURRENT-TRUTH.md` items -317/-325, `PORTING-STATE.md` Session 522.

## The work unit: resume item -317 step 3's blanket sweep

Per the user directive's priority order, M3's top-ranked work unit is still item -317 step 3: the
~150-location blanket sweep of the s494 tracer's derived-pointer reload idiom across
`funcs_3.c`/`funcs_4.c`. **~125 locations remain unaudited** (21 of ~150 fixed so far, 20 fully
closed 2/2, the 21st's 2nd confirm queued).

1. **Re-run the tracer fresh** before picking a site -- line numbers drift with every insertion, and
   per the s521 gotcha, do NOT pass a custom `--out`:
   ```
   cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
   python3 scratch/agent/s494_item317_step3_tracer.py --scan
   python3 scratch/agent/s506_dedupe.py
   ```
2. Pick the next-highest-count tier from the fresh output. As of the s522 scan (STALE, re-run
   first): `funcs_3.c:13368`/`13860`/`14280`/`14763`/`15170`/`15654` (36 sites each, `beginFrameDLChunk`
   -- the remaining members of the tied-top tier R1/R2 came from), `funcs_3.c:16120` (34 sites,
   `beginFrameDLChunk`), `funcs_3.c:11625` (30 sites, `emitColorFillRect`), `funcs_4.c:4457`
   (`submitSceneNodeRender`, 30 sites).
3. Follow the exact established fix pattern (see any of the 21 guards in `docs/PROJECT-OVERVIEW.md`
   §22-§23, or `BEGIN_FRAME_DL_CHUNK_R2_GUARD`/`fixup_game_funcs.py` for the freshest example): null
   check gates one arm, non-null fallthrough has no `0x80000000`-`0x80800000` range check before a
   write-through deref, downstream control flow reloads the register from the same table again --
   skip-on-invalid is safe. Confirm this shape holds at the specific site before writing the fix,
   AND confirm the picked line isn't already guarded by reading the actual generated source AND
   grepping `fixup_game_funcs.py` for the guest address (the tracer's own dedupe ranking can lag a
   stale canonical report file, see the s521 gotcha below).
4. **If the site is in `beginFrameDLChunk`**: that function carries `g_rs64_last_guest_pc`
   breadcrumb writes between every disassembly comment and its corresponding C statement (unlike
   e.g. `renderLitMeshFaceGroup`, which doesn't) -- the fixup patch's old/new match strings MUST
   include that breadcrumb line or the string replace silently no-ops (`text.count(old) == 0`,
   caught by checking the count before trusting the patch applied). Multiple sites in this function
   also reload from DIFFERENT global table slots (R1 was `0x801163B0`/`0x8000B560`-`0x8000B564`; R2
   was a different `0x63B0`-offset slot at `0x8000AA8C`-`0x8000AA90`) -- confirm each new site's own
   load-pair address before assuming it's a duplicate of a prior guard.
5. Regen/build/live-verify/queue-2nd-confirm sequence (see Regen reminder below). **If the 1st
   live-verify attempt crashes early (<~60s) on the Metal.framework async shader-compiler cluster
   (`pc=0x800ab0e0` or similar, already-catalogued items -10/-9/-303/-315/-508) with a weak
   `hangarbay-entry` count (<~10), discard it per Iron Rule 1 and retry once** -- this has now
   happened twice (s508, s522) and is a known flaky/unrelated async crash, not a signal about the
   guard.

**Caveat from item -319's own resolution (s520)**: `beginFrameDLChunk` has at least TWO structurally
distinct vulnerable-reload idioms -- the s494 tracer's own `+0x63B0` self-referential shape (this
sweep's tiers, now including R1 and R2), and the `-0x23A8` sibling-global shape covered by
`SIBLING_PTR_WRITE_GUARD`'s existing 121-site table. Do not assume every reload in this function is
covered by one guard family.

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

Live-verify: copy `scratch/agent/soak_queue/done/s522_begin_frame_dl_chunk_r2_confirm.sh` (or any
recent done/ script) as a template -- add `ROGUESQ_LOG_<NEW_GUARD_NAME>=1` to the env block (keep
every existing `ROGUESQ_LOG_*` armed for regression checking), run it manually/foreground first
(1st live-verify), then copy the same env block into a fresh `soak_queue/<name>_confirm.sh` for the
loop to run as the 2nd independent confirm. Read the actual `run.log` inside the output directory,
not just the thin flat summary line in `SOAK-RESULTS.md` -- the flat line's `rc=3` can mean "crashed
on an unrelated already-catalogued background-noise family after a fully clean, positively-controlled
run," which counts as CLOSED, not as a guard failure (established s518/s522 precedent).

## Budget note

This is iteration N on `item-317-step3-blanket-sweep` (systematic sweep, one guard per iteration,
same slug for the whole campaign per the exit contract's guidance for long systematic sweeps --
each iteration DOES produce a discriminating result: a new guard fixed and verified, or a confirm
folded in, so this does not trip the "3 consecutive non-ADVANCED iterations" rule). Continue picking
off tiers top-down until the tracer reports zero remaining `NEEDS_GUARD` sites, then step back and
re-run the tracer with a broader idiom pattern if this one is exhausted.
