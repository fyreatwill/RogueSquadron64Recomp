# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## s523 recap -- read this first

s523 did two things:

1. **Folded in item -317 step 3's queued 2nd confirm for `BEGIN_FRAME_DL_CHUNK_R2_GUARD`**
   (`s522_begin_frame_dl_chunk_r2_confirm`, rc=3, 157s per the flat log): the detailed `run.log`
   showed 0 `begin-frame-dl-chunk-r2-guard` fires, 6 benign zero-value init-time co-fires (no
   regression), `hangarbay-entry n=32` strong positive control. The crash itself
   (`pc-symbol=emitAllocatedDLCommand+4680`/`last-guest-pc=0x80008764`, signal 10 Bus error) is
   byte-range-consistent with the already-catalogued `emitAllocatedDLCommand`/`beginFrameDLChunk`
   SIGBUS background-noise family (documented s354-366). **`BEGIN_FRAME_DL_CHUNK_R2_GUARD` is now
   FULLY CLOSED 2/2.**
2. **Picked up item -317 step 3's blanket sweep again** and fixed its 22nd site (3rd guard in
   `beginFrameDLChunk`): `BEGIN_FRAME_DL_CHUNK_R3_GUARD` (`funcs_3.c:13381`/`0x8000AC0C`, 36 shared
   reload sites at scan time, reloads the SAME underlying global as R1 -- `0x801163B0` -- from its
   own distinct load-instruction pair). 1st live-verify CLEAN (0 own-guard fires, 0 fires on every
   other armed guard family, `hangarbay-entry n=2700+` -- one of the strongest positive controls of
   the whole campaign). Crashed at ~124s on signal 6 (Abort trap),
   `pc-symbol=__isPlatformOrVariantPlatformVersionAtLeast.cold.4` (absurd multi-billion-byte offset)
   -- the established symbolizer tell for the already-catalogued async Metal.framework/system-thread
   crash cluster (items -10/-9/-303/-315/-508), this time surfacing as a SIGABRT instance instead of
   the cluster's more common SIGSEGV. Checked and ruled out the alternative explanation (the unrelated
   guest-triggered `BREADCRUMB9`/s343 `do_break()` abort family, which shares the same fixed
   `si_addr=0x18c6a85e8` siginfo address) by reading the actual source at the crash's
   `last-guest-pc=0x80015228`: it's a floating-point multiply inside `processSceneNode`, not a
   `divu`/`break` trap idiom. 2nd confirm queued: `scratch/agent/soak_queue/s523_begin_frame_dl_chunk_r3_confirm.sh`
   -- fold its result in next session.

Both written up: `docs/CURRENT-TRUTH.md` item -317, `docs/PROJECT-OVERVIEW.md` §23 guard table
(rows 22-24), `PORTING-STATE.md` Session 523.

**Tooling gotcha learned this session**: a `Monitor`/`pgrep` watch on the game process must match how
it actually appears in `ps aux` -- it runs as `./RogueSquadron64Recomp` (no `build/` prefix) since
`probe.sh` execs it after `cd`-ing into `build/`. A path-qualified pgrep pattern
(`build/RogueSquadron64Recomp`) silently never matches and fires an instant false "process exited"
notification. Use `pgrep -x RogueSquadron64Recomp` and, if in doubt, verify with a direct
`ps aux | grep` before trusting a monitor result.

## The work unit: resume item -317 step 3's blanket sweep

Per the user directive's priority order, M3's top-ranked work unit is still item -317 step 3: the
~150-location blanket sweep of the s494 tracer's derived-pointer reload idiom across
`funcs_3.c`/`funcs_4.c`. **~124 locations remain unaudited** (22 of ~150 fixed so far, 21 fully
closed 2/2, the 22nd's 2nd confirm queued).

1. **Re-run the tracer fresh** before picking a site -- line numbers drift with every insertion, and
   per the s521 gotcha, do NOT pass a custom `--out`:
   ```
   cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
   python3 scratch/agent/s494_item317_step3_tracer.py --scan
   python3 scratch/agent/s506_dedupe.py
   ```
2. Pick the next-highest-count tier from the fresh output. As of the s523 scan (STALE, taken before
   R3's own regen, re-run first): `funcs_3.c:13873`/`14293`/`14776`/`15183`/`15667`/`16133` (36 sites
   each, `beginFrameDLChunk` -- the remaining members of the tied-top tier R1/R2/R3 came from),
   `funcs_3.c:16120` (34 sites, `beginFrameDLChunk`), `funcs_3.c:11625` (30 sites, `emitColorFillRect`),
   `funcs_4.c:4457` (`submitSceneNodeRender`, 30 sites).
3. Follow the exact established fix pattern (see any of the 22 guards in `docs/PROJECT-OVERVIEW.md`
   §22-§23, or `BEGIN_FRAME_DL_CHUNK_R3_GUARD`/`fixup_game_funcs.py` for the freshest example): null
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
   also reload from DIFFERENT global table slots (R1/R3 both load `0x801163B0`/`0x8000B560`-ish
   addresses -- confirmed same underlying global, different load-instruction pairs; R2 loaded a
   different `0x63B0`-offset slot entirely at `0x8000AA8C`-`0x8000AA90`) -- confirm each new site's
   own load-pair address before assuming it's a duplicate of a prior guard (it can share the
   underlying global with an earlier guard and still be a distinct, unguarded write site).
5. Regen/build/live-verify/queue-2nd-confirm sequence (see Regen reminder below). **If the 1st
   live-verify attempt crashes early (<~60s) on the async Metal.framework/system-thread cluster
   (`pc-symbol` containing `isPlatformOrVariantPlatformVersionAtLeast.cold` with an absurd offset,
   OR `pc=0x800ab0e0`/similar addresses, already-catalogued items -10/-9/-303/-315/-508) with a weak
   `hangarbay-entry` count (<~10), discard it per Iron Rule 1 and retry once** -- this cluster can
   manifest as EITHER SIGSEGV or SIGABRT (confirmed s523), so check the `pc-symbol` pattern, not just
   the signal number, when deciding whether a crash is this already-catalogued noise.

**Caveat from item -319's own resolution (s520)**: `beginFrameDLChunk` has at least TWO structurally
distinct vulnerable-reload idioms -- the s494 tracer's own `+0x63B0` self-referential shape (this
sweep's tiers, now including R1/R2/R3), and the `-0x23A8` sibling-global shape covered by
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

Live-verify: copy `scratch/agent/soak_queue/s523_begin_frame_dl_chunk_r3_confirm.sh` (or any recent
`done/` script) as a template -- add `ROGUESQ_LOG_<NEW_GUARD_NAME>=1` to the env block (keep every
existing `ROGUESQ_LOG_*` armed for regression checking), run it manually/foreground first (1st
live-verify -- launch as a backgrounded Bash call and poll with a Monitor watching
`pgrep -x RogueSquadron64Recomp`, per this session's tooling gotcha above), then copy the same env
block into a fresh `soak_queue/<name>_confirm.sh` for the loop to run as the 2nd independent confirm.
Read the actual `run.log` inside the output directory, not just the thin flat summary line in
`SOAK-RESULTS.md` -- the flat line's `rc=3` can mean "crashed on an unrelated already-catalogued
background-noise family after a fully clean, positively-controlled run," which counts as CLOSED, not
as a guard failure (established s518/s522/s523 precedent).

## Budget note

This is iteration N on `item-317-step3-blanket-sweep` (systematic sweep, one guard per iteration,
same slug for the whole campaign per the exit contract's guidance for long systematic sweeps --
each iteration DOES produce a discriminating result: a new guard fixed and verified, or a confirm
folded in, so this does not trip the "3 consecutive non-ADVANCED iterations" rule). Continue picking
off tiers top-down until the tracer reports zero remaining `NEEDS_GUARD` sites, then step back and
re-run the tracer with a broader idiom pattern if this one is exhausted.
