# NEXT work unit

## s347 drained rate_3/4 and found the discriminating result: 3/4 crashes, 3 DIFFERENT symbols

Landed data on the m5step5v3 template (n=4): `rate_1` CRASH `allocOrEvictMaterialNode+944`, `rate_2`
CLEAN, `rate_3` CRASH `processSceneNode+1424`, `rate_4` CRASH `trackResourceListWithMappingTables+1192`.
Zero repeats of any single symbol; zero hits on family #3 (`waitForAnyAudioSlot`) or family #4
(post-cutscene stall) specifically, despite a 75% overall crash rate in the 4-run sample. This refutes
"de-stubbing produced one new concentrated family #5" (`allocOrEvictMaterialNode` didn't recur) and
supports "de-stubbing quieted #3/#4 specifically but the background crash rate in this window is still
high, just diffused across other (mostly already-catalogued or singleton) sites." Full writeup:
`docs/CURRENT-TRUTH.md` item -203, `PORTING-STATE` Session 347.

## The work unit: drain m5step5v3_rate_5..8, extend the sample, watch for symbol recurrence

**Step 1**: `tail -10 scratch/agent/SOAK-RESULTS.md` for `m5step5v3_rate_5` through `_8` (the loop
drains up to 2 per iteration between iterations — likely only 2 of the 4 will have landed by next
read; that's fine, work with what's there). For each landed verdict:
- Confirm `runlog_bytes` stayed in the 50-70 MB band (5th/6th/7th/8th confirmation the s345 fix holds
  — flag any regression as itself a surprising, checkable finding).
- Check `last_pc_symbol`. The single most information-dense outcome to watch for: does ANY symbol
  from this batch match `allocOrEvictMaterialNode+944`, `processSceneNode` (any offset), or
  `trackResourceListWithMappingTables+1192` from rate_1/3/4? A repeat of any one of these — especially
  `processSceneNode`, which already has 3 distinct prior-session offsets (`+6668`, `+7640`, `+1424`)
  suggesting it may be a recurring ambiguous-attribution family rather than 3 unrelated singletons —
  would be the first real family candidate in this whole comparison.

**Step 2 — update the tally**: after step 1, you'll have 6-8 total data points across rate_1 through
rate_8. Recompute: overall crash rate (currently 3/4 = 75%), rate of family #3/#4 specifically
(currently 0/4), and whether any symbol now has ≥2 hits (currently 0 symbols do). If a symbol reaches
2+ hits, that's the discriminating threshold to escalate to a source-read (same technique s343 used
for `tickWrappingTimerAccumulatorList`'s `break 7` trap): grep
`~/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c` for the function, read around the byte offset,
classify as OOB index / null deref / div-mod trap, same triage categories as every other cataloged
family.

**Step 3 — budget-rule check**: this will be the 3rd iteration on `HYPOTHESIS-ID
m5-audio-destub-step5-crashrate-comparison` counting from s347 (s345/s346 don't count, per their own
notes). If this iteration produces another inconclusive "different symbol each time" result with no
2+-hit family, Iron Rule 8 requires a pivot preamble on the 4th: write the hypothesis/evidence table
explicitly into this file, and consider whether the highest-information-value next move is (a) a much
larger batch (8-16 more soaks) to get a real per-family rate at this sample size instead of drip-
feeding 4 at a time, or (b) closing step 5 as "post-title crash rate in this window is diffuse/
long-tailed, no dominant family found in first 8-run sample" and moving to M3 idiom-class audits per
the user directive's priority-3 fallback.

HYPOTHESIS-ID: m5-audio-destub-step5-crashrate-comparison (3rd iteration counting from s347; the NEXT
iteration after this one is the 4th and would trigger Iron Rule 8's block if still inconclusive with
no pivot preamble written).

## Environment notes (carried forward — see s327-347 for full detail)

- Regen paths: `/Users/williambuckley/Documents/Tools/N64Recomp` (`fixup_game_funcs.py`, untracked).
  Delete `RecompiledFuncs/*.c` before every `N64Recomp` run:
  `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`.
- Full regen order: `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py` ->
  `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml` ->
  `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` ->
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
  /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build -j8`.
- Current gate state (unchanged since s343): fixup regex at `fixup_game_funcs.py` ~line 263 is
  `r"0x8008E(?:C88)"` — matches ONLY `reapplyDisplayMode` (`0x8008EC88`, force-zeroed);
  `setDisplayMode` (`0x8008EB40`) stays unmatched/reversed. Verify via `funcs_23.c: audio gate patched
  x1` in the fixup report. No rebuild needed for this work unit unless step 2 lands a guard.
- Soak driver: `scratch/s73_post_a_scene/run_s327waitpump.sh <label>`, invoked with
  `env HOLD_S=<n> zsh scratch/s73_post_a_scene/run_s327waitpump.sh <label>` (`env` prefix required —
  project rule 10 / CLAUDE.md). It arms EVERY diagnostic env var unconditionally EXCEPT the 4
  heap-walker vars (s345 fix — `ROGUESQ_LOG_RS_MALLOC_WALK`/`_GUARD`/`ROGUESQ_LOG_RS_FREE_WALK`/`_GUARD`
  now default to 1 but are overridable by pre-exporting 0). Log lands at
  `scratch/s73_post_a_scene/<label>/run.log` — grep it, don't read it directly; check `runlog_bytes`
  before trusting a soak's post-processing to have actually finished. **`[keys]` lines land in the
  LAUNCHER's stdout/stderr (`scratch/agent/soak_results/<label>_launcher.log`), NOT in the game's own
  `run.log`.**
- `[vi-fs-decision]` is an always-on native instrument (`lib/rt64/src/hle/rt64_state.cpp`), not
  env-gated — free in every soak, no arming needed.
- `[CRASH][pc-symbol]` (host PC via `dladdr`, precise) and `[CRASH][last-guest-pc]` (a separately
  tracked guest checkpoint, `g_rs64_last_guest_pc`, updated at recompiled-function/jump boundaries —
  NOT necessarily the guest instruction under the exact host crash PC) answer different questions by
  design (`src/main/main.cpp:1740-1786`, s206). A mismatch between them across a crash is expected, not
  itself evidence of an instrument bug — always trust `pc-symbol` for "what function crashed."
- Any soak recipe testing for a SPECIFIC crash must check `last-guest-pc`/`pc-symbol` against that
  crash's own signature, not just "did `[CRASH]` fire" — RS64 has ~20+ independent, already-catalogued
  crash families that can fire nondeterministically at any point (s344's method-trap finding,
  `docs/CURRENT-TRUTH.md` Method traps section). `processSceneNode` specifically has at least 3
  distinct documented crash offsets across sessions (`+6668`, `+7640` pre-s295; `+1424` s347) and is
  flagged in its own s151 write-up as possibly nearest-symbol-misattribution-prone at large offsets —
  treat a `processSceneNode` hit at ANY offset as the same suspect family until proven otherwise, not
  as a fresh singleton each time.
- `rc=137` (SIGKILL at the loop's 600s hard cap) does NOT necessarily mean the GAME hung — it can mean
  the RECIPE's own post-processing didn't finish in time (s345's finding). Always check the launcher
  log's own `done wall=Ns` line and the run.log's byte size before reading a 600s timeout as a game-side
  stall.
