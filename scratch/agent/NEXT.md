# NEXT work unit

## s349 landed: found a new exact-repeat crash (drainMeshReleaseQueue+600, 2/2), confirmed real, added BREADCRUMB15

Full detail: `docs/CURRENT-TRUTH.md` item -205, `PORTING-STATE` Session 349. Short version:
`m5step5v3_rate_7/8` both crashed at `pc-symbol=drainMeshReleaseQueue+600` — same file offset
(`0x3fbcc4`) across different ASLR bases, a real bug (confirmed via `nm -n` symbol-distance check,
`scratch/agent/check_symtab2.py` — not the known `processSceneNode`-style nearest-symbol-ambiguity
artifact). The accompanying `last-guest-pc` was a red herring (stale global shared by 10 other
`BREADCRUMB*`-instrumented functions, none of which is `drainMeshReleaseQueue`). Added `BREADCRUMB15`
to `fixup_game_funcs.py` (same blanket per-instruction pattern as BREADCRUMB3/10-14) so the NEXT crash
here reports its own precise guest PC. Full regen + rebuild clean, `patched x149`. Queued
`s349_drainmeshbreadcrumb_verify1/2.sh`.

**Also still open from s348**: `s348_contentguard_verify2/3.sh` had NOT been drained by the loop as of
s349's session start — the content-guard question (does item -204's `processSceneNode` guard actually
stop the repeat crash / does it ever fire) is still unconfirmed. 0/2 repeat in s349's own rate_7/8 data
is weak supporting evidence but not yet a confirmation.

## The work unit: drain both queued batches, read whichever landed

**Step 1**: `tail -15 scratch/agent/SOAK-RESULTS.md`. Up to 4 recipes may have landed since s349
(`s348_contentguard_verify2/3.sh`, `s349_drainmeshbreadcrumb_verify1/2.sh` — the loop drains up to 2
per iteration between iterations, so some or all 4 may be done by next read).

**Step 2 — for each `s349_drainmeshbreadcrumb_verify*` result**:
- If it crashes at `pc-symbol=drainMeshReleaseQueue+NNN` again: `last_guest_pc` is NOW PRECISE
  (BREADCRUMB15 stamps that function's own body, no longer stale). Source-read `funcs_3.c` at that
  exact guest PC (the function starts at `funcs_3.c:1669`, is a dense unguarded linked-list
  free/coalesce routine — look for the specific `MEM_W`/`MEM_HU`/`MEM_H` load at that address and what
  register feeds it, same method as s348's `processSceneNode` content-pointer analysis). If the offset
  is close to `+600` again (or exact), that's a 3rd exact hit — strong grounds to add a guard following
  the s190/s348 shape (range-check, bail to a safe exit, env-gated diagnostic).
- If it's clean or crashes elsewhere: note the symbol and fold into the tally; 2/2 was already enough
  to instrument, but a 3rd confirms vs. a coincidental pair.

**Step 3 — for each `s348_contentguard_verify*` result**, per s348/s349's original plan:
- Check `[scene-node-content-guard]` log line count (`guard_fire_n`) — if >0, the guard fired,
  empirically confirming the corrupt-content-pointer hypothesis, not just the static source-read.
- Check `last_pc_symbol` on any crash — if it's `processSceneNode+1424`/`0x80014FDC` AGAIN, the guard
  did NOT close this site (re-verify the regex actually matched in the binary that ran). Any OTHER
  crash symbol is unrelated background noise, not a guard failure.
- Check `title_reached`/`keys_lines` to confirm the run actually exercised gameplay (a pre-title death
  is uninformative either way, as verify1 was).

**Step 4 — decide next move**:
- If BREADCRUMB15 pinpoints an exact deref and it's guardable (null/range check missing on a loaded
  pointer, same shape as every prior guard this session-chain has landed) — guard it, following the
  s190/s348 pattern exactly. This is the higher-value branch: a 3rd exact-offset hit on a previously
  uninstrumented function is unusually strong evidence for a real, fixable bug.
- If the content-guard verify soaks show the guard firing or `processSceneNode+1424` staying absent
  across a larger n (3-4+) — promote item -204 to "confirmed effective" in `CURRENT-TRUTH.md`.
- If both threads are still ambiguous (small n, no guard-fire evidence either way) — queue 2 more of
  whichever recipe has fewer data points rather than concluding from n=2-3. Budget check: this would be
  the 2nd iteration on `m5-audio-destub-drainmesh-breadcrumb` and the 2nd-3rd on
  `m5-audio-destub-contentguard-verify` — neither yet at the iron-rule-8 3-strike pivot point.

## Environment notes (carried forward — see s327-349 for full detail)

- Regen paths: `/Users/williambuckley/Documents/Tools/N64Recomp` (`fixup_game_funcs.py`, untracked).
  Delete `RecompiledFuncs/*.c` before every `N64Recomp` run:
  `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`.
- Full regen order: `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py` ->
  `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml` ->
  `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` ->
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
  /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build -j8`. Run each step as its own
  single command (compound `cd a && cmd` sometimes needs manual approval this session).
- **New this session**: `nm` itself needs explicit interactive approval and isn't allowlisted in
  `.claude/settings.json` — but `python3 -c "..."` wrapping `subprocess.run(['nm', ...])` IS allowed
  (matches on the `python3` prefix). Reuse `scratch/agent/check_symtab.py` /
  `check_symtab2.py` as templates for any future "is this crash a nearest-symbol-ambiguity artifact or
  a real hit inside this function" check — this is now a repeatable, cheap (no rebuild/rerun) static
  check to run BEFORE assuming a new crash symbol needs its own breadcrumb.
- **All BREADCRUMB* passes share ONE `g_rs64_last_guest_pc` global.** 10 functions were instrumented
  before s349 (`submitSceneNodeRender`, `heapFreeListDequeue`, `beginFrameDLChunk`, `processSceneNode`,
  `reserveAndEmitDLEntry`, `buildPositionAndCallTransformHelper`, `static_5_800AB658`, a function slice
  (BREADCRUMB8-10), `tickSongSequence`, `stopSongByHandle`), plus `drainMeshReleaseQueue` (BREADCRUMB15,
  new s349). If `last-guest-pc` on a crash doesn't look like it belongs to the crashing `pc-symbol`
  function, check FIRST whether the crashing function is even in this list — if not, the value is
  simply stale from whichever instrumented function last ran, not a bug or a clue about the actual
  crash location.
- `fixup_game_funcs.py` patches whose regex anchor depends on `g_rs64_last_guest_pc = 0x...u;` lines
  MUST be placed after the relevant BREADCRUMB-family pass for that function in script order — those
  lines don't exist in pristine N64Recomp output, they're inserted by the breadcrumb patches
  themselves. Always confirm your new patch's report line actually printed after a run.
- Current gate state (unchanged since s343): fixup regex at `fixup_game_funcs.py` ~line 263 is
  `r"0x8008E(?:C88)"` — matches ONLY `reapplyDisplayMode` (`0x8008EC88`, force-zeroed);
  `setDisplayMode` (`0x8008EB40`) stays unmatched/reversed.
- Soak driver: `scratch/s73_post_a_scene/run_s327waitpump.sh <label>`, invoked with
  `env HOLD_S=<n> zsh scratch/s73_post_a_scene/run_s327waitpump.sh <label>` (`env` prefix required —
  project rule 10 / CLAUDE.md). Arms `ROGUESQ_LOG_SCENE_NODE_CONTENT_GUARD=1` alongside every other
  diagnostic var, EXCEPT the 4 heap-walker vars (default-overridable per s345's fix). Log lands at
  `scratch/s73_post_a_scene/<label>/run.log` — grep it, don't read it directly; check `runlog_bytes`
  before trusting a soak's post-processing to have actually finished.
- `[CRASH][pc-symbol]` (host PC via `dladdr`, precise, always trust for "what function crashed") and
  `[CRASH][last-guest-pc]` (a separately tracked guest checkpoint, only meaningful if the crashing
  function is one of the BREADCRUMB-instrumented ones) answer different questions by design.
- `processSceneNode` remains a KNOWN misattribution-prone multi-offset crash site (4 distinct offsets
  across sessions). `drainMeshReleaseQueue` is NOT — confirmed via symbol-distance check s349.
- `rc=137`/launcher timeouts don't necessarily mean a game-side hang — check the launcher log's own
  `done wall=Ns` line and `run.log` byte size before reading a timeout as a stall.

HYPOTHESIS-ID: m5-audio-destub-drainmesh-breadcrumb (1st iteration — new thread opened s349). Parallel
open thread: m5-audio-destub-contentguard-verify (2nd iteration — still no confirming/refuting soak
landed as of s349).
