# NEXT work unit

HYPOTHESIS-ID: item-317-step3-blanket-sweep

## Step 0 reminder for next iteration

`docs/CURRENT-TRUTH.md` is now 62938 bytes — **over the 60000 maintenance trigger**. The NEXT
iteration must be a MAINTENANCE iteration per `tools/agent/ITERATION.md` Step 0: compact toward the
~35 KB target (migrate durable material to `docs/PROJECT-OVERVIEW.md`, prune/merge superseded and
closed Next-steps items, renumber the backlog into one monotonic sequence, refresh the stale "as of
session N" headline). Do NOT run item -317 step 3 experiments in that iteration. A net shrink of
>=200 lines counts as ADVANCED.

## s524 recap -- read this first

s524 did two things:

1. **Folded in item -317 step 3's queued 2nd confirm for `BEGIN_FRAME_DL_CHUNK_R3_GUARD`**
   (`s523_begin_frame_dl_chunk_r3_confirm`, rc=3, 181s per the flat log): the detailed `run.log`
   showed 0 `begin-frame-dl-chunk-r3-guard` fires, 1 benign already-catalogued `hangarmenu-a0-guard`
   co-fire, `hangarbay-entry n=33` positive control. **`BEGIN_FRAME_DL_CHUNK_R3_GUARD` is now FULLY
   CLOSED 2/2.** The crash itself was NEW and notable: a Bus error directly inside `do_rom_read`
   (`osPiStartDma_recomp` -> `do_dma` -> `do_rom_read`, `si_addr=0x380000003`) -- the exact call-stack
   shape of the historically-major `do_rom_read`/`piDmaWorker` DMA-corruption family believed fixed
   since s147/148 (~375 sessions ago). Filed as **item -326**, single occurrence, not chased -- but
   flagged for extra attention if it recurs (see `docs/CURRENT-TRUTH.md` item -326 for the full
   writeup and the reasoning for why one occurrence isn't enough to conclude anything).
2. **Picked up item -317 step 3's blanket sweep again** and fixed its 23rd site (4th guard in
   `beginFrameDLChunk`): `BEGIN_FRAME_DL_CHUNK_R4_GUARD` (`funcs_3.c:14306`/`0x8000AEB4`, 36 shared
   reload sites at scan time). 1st live-verify was the cleanest of the whole campaign: 0 own-guard
   fires, 1 benign co-fire, `hangarbay-entry n=35`, and the process ran the **full scheduled 300s**
   with **zero crashes of any kind**. 2nd confirm queued:
   `scratch/agent/soak_queue/s524_begin_frame_dl_chunk_r4_confirm.sh` -- fold its result in next
   session (after the maintenance pass).

Both written up: `docs/CURRENT-TRUTH.md` item -317 and new item -326, `PORTING-STATE.md` Session 524.

## The work unit AFTER maintenance: resume item -317 step 3's blanket sweep

Per the user directive's priority order, M3's top-ranked work unit is still item -317 step 3: the
~150-location blanket sweep of the s494 tracer's derived-pointer reload idiom across
`funcs_3.c`/`funcs_4.c`. **~121 locations remain unaudited** (23 of ~150 fixed so far, 22 fully
closed 2/2, the 23rd's 2nd confirm queued).

1. **Re-run the tracer fresh** before picking a site -- line numbers drift with every insertion, and
   per the s521 gotcha, do NOT pass a custom `--out`:
   ```
   cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
   python3 scratch/agent/s494_item317_step3_tracer.py --scan
   python3 scratch/agent/s506_dedupe.py
   ```
2. Pick the next-highest-count tier from the fresh output. As of the s524 scan (STALE, taken before
   R4's own confirm regen -- re-run first): `funcs_3.c:13886`/`14802`/`15209`/`15693`/`16159` (36
   sites each, `beginFrameDLChunk` -- the remaining members of the tied-top tier R1/R2/R3/R4 came
   from), `funcs_3.c:11625` (30 sites, `emitColorFillRect`), `funcs_4.c:4457`
   (`submitSceneNodeRender`, 30 sites).
3. Follow the exact established fix pattern (see any of the 23 guards in `docs/CURRENT-TRUTH.md` item
   -317, or `BEGIN_FRAME_DL_CHUNK_R4_GUARD`/`fixup_game_funcs.py` for the freshest example): null
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
   also reload from DIFFERENT global table slots (R1/R3/R4 all load `0x801163B0`/`0x8000B560`-ish
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
6. **Watch for item -326 recurring** (`do_rom_read+608`/`last-guest-pc=0x800025ac`, Bus error,
   `si_addr=0x380000003`). If any live-verify or confirm this campaign hits it a 2nd time, STOP the
   sweep and escalate it -- do not just re-file it as background noise. See `docs/CURRENT-TRUTH.md`
   item -326 for why this one specific signature needs different handling than the routine
   filed-not-chased single-occurrence breadcrumbs.

**Caveat from item -319's own resolution (s520)**: `beginFrameDLChunk` has at least TWO structurally
distinct vulnerable-reload idioms -- the s494 tracer's own `+0x63B0` self-referential shape (this
sweep's tiers, now including R1/R2/R3/R4), and the `-0x23A8` sibling-global shape covered by
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

Live-verify: copy `scratch/agent/soak_queue/s524_begin_frame_dl_chunk_r4_confirm.sh` (or any recent
`done/` script) as a template -- add `ROGUESQ_LOG_<NEW_GUARD_NAME>=1` to the env block (keep every
existing `ROGUESQ_LOG_*` armed for regression checking), run it manually/foreground first (1st
live-verify -- launch as a backgrounded Bash call and poll with a Monitor watching
`pgrep -x RogueSquadron64Recomp`, per the s523 tooling gotcha), then copy the same env block into a
fresh `soak_queue/<name>_confirm.sh` for the loop to run as the 2nd independent confirm. Read the
actual `run.log` inside the output directory, not just the thin flat summary line in
`SOAK-RESULTS.md` -- the flat line's `rc=3` can mean "crashed on an unrelated already-catalogued
background-noise family after a fully clean, positively-controlled run," which counts as CLOSED, not
as a guard failure (established s518/s522/s523/s524 precedent).

## Budget note

This is iteration N on `item-317-step3-blanket-sweep` (systematic sweep, one guard per iteration,
same slug for the whole campaign per the exit contract's guidance for long systematic sweeps --
each iteration DOES produce a discriminating result: a new guard fixed and verified, or a confirm
folded in, so this does not trip the "3 consecutive non-ADVANCED iterations" rule). The very next
iteration is a MAINTENANCE iteration (see Step 0 reminder above) -- that does not break the slug or
the budget counter, it's an interleaved housekeeping pass. Continue picking off tiers top-down once
maintenance is done, until the tracer reports zero remaining `NEEDS_GUARD` sites, then step back and
re-run the tracer with a broader idiom pattern if this one is exhausted.
