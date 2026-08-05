# NEXT work unit

## s348 landed a real fix: processSceneNode's repeat crash (2/6, exact PC match) is now guarded

`m5step5v3_rate_5` (CLEAN) and `_rate_6` (CRASH) landed. `rate_6` hit the discriminating result this
whole batch was designed to find: `pc-symbol=processSceneNode+1424` AND `last-guest-pc=0x80014FDC`,
BOTH fields byte-identical to `rate_3`'s crash (s347) — the first symbol in the comparison to cross
NEXT.md's own "2+ hits" escalation threshold. Source-read `funcs_4.c` at that guest PC and found an
unguarded "content pointer" (`ctx->r16`, loaded from `MEM_W(ctx->r17, 0X8)` — a FIELD of the already-
node-pointer-guarded `ctx->r17`) dereferenced with zero validation, at two load sites in the function
(entry `0x80014FD0`, loop-continuation `0x800153F8`). Added guards at both, mirroring the existing
s190 guard's shape exactly (range-check, bail to `L_80015528`, env-gated diagnostic under
`ROGUESQ_LOG_SCENE_NODE_CONTENT_GUARD`). Full regen + rebuild clean. Full writeup: `docs/CURRENT-TRUTH.md`
item -204, `PORTING-STATE` Session 348.

**Methodology trap hit and fixed this session, worth remembering**: `fixup_game_funcs.py`'s ~150
patches run in SCRIPT ORDER against one accumulating `text` variable per file, not against a final
fully-breadcrumbed view. A patch whose regex anchor includes a `g_rs64_last_guest_pc = 0x...u;` line
(which is INSERTED by a later BREADCRUMB-family pass, not present in pristine N64Recomp output) must
be placed AFTER that breadcrumb pass in the script, or `re.subn` silently returns `n=0` with no error
and no report line — a completely silent no-op. Always check the printed report list for your new
patch's own line after a "successful" (no-Python-error) fixup run; a missing report line at ANY point
in this script means the match failed, regardless of exit code.

## The work unit: drain the 2 queued content-guard verify soaks + m5step5v3_rate_7/8, check for a repeat

**Step 1**: `tail -10 scratch/agent/SOAK-RESULTS.md`. Up to 4 recipes are queued
(`s348_contentguard_verify2.sh`, `_verify3.sh`, `m5step5v3_rate_7.sh`, `_rate_8.sh`); the loop drains up
to 2 per iteration between iterations, so 2-4 may have landed by next read.

**Step 2 — for each `s348_contentguard_verify*` result**, check three things:
- `guard_fire_n` (grepped `[scene-node-content-guard]` count in the run log) — if >0, the guard fired,
  which EMPIRICALLY confirms the corrupt-content-pointer hypothesis (not just the static source-read).
  Print `guard_fire_sample` too and read what `bad_content`/`node` values it caught.
- `last_pc_symbol` on any crash — if it's `processSceneNode+1424` / `last-guest-pc=0x80014FDC` AGAIN,
  the guard did NOT close this site (check the regex actually matched in the build that ran — grep the
  built binary's own regen log, or just re-check `grep -c 'content-pointer validity guard' funcs_4.c`
  in `~/Documents/Tools/N64Recomp/RecompiledFuncs/` if still present — should show 2 hits). Any OTHER
  crash symbol is an unrelated pre-existing family, not a guard failure.
- `title_reached` / `keys_lines` — confirm the run actually exercised gameplay (unlike s348's own
  inline verify1, which crashed at `musyxSynthFrame+4652` before title and was uninformative for this
  question — if a queued verify also dies pre-title, it's similarly uninformative, note it and don't
  over-read it as either a confirm or refute).

**Step 3 — for each `m5step5v3_rate_7/8` result**: same as s347/s348's method — check `last_pc_symbol`
against the 3 now-tracked symbols (`allocOrEvictMaterialNode+944` 1/6, `processSceneNode+1424` 2/6 NOW
GUARDED, `trackResourceListWithMappingTables+1192` 1/6) and update the tally. Since `processSceneNode`
should no longer crash at `+1424` post-guard, a rate_7/8 hit there would itself be a signal the guard
build wasn't actually running (check binary timestamp/regen freshness first — boring explanation
before exotic).

**Step 4 — decide next move based on what lands**:
- Guard fires at least once + no `processSceneNode+1424` repeat across all landed data → promote item
  -204 from "not yet confirmed" to confirmed-effective in `CURRENT-TRUTH.md`, and consider whether
  `trackResourceListWithMappingTables+1192` (the other singleton) is worth the same idiom-class-audit
  treatment next, OR whether M5 step 5's crash-rate comparison is now well-enough characterized to
  close and move to M3 idiom-class audits per the user directive's priority-3 fallback.
  `HYPOTHESIS-ID m5-audio-destub-contentguard-verify` — 1st iteration if this is the session that
  checks it.
- Guard never fires and no repeat → still consistent with the fix (maybe the corrupting write that
  produces the bad content pointer is itself rare/nondeterministic) but weaker evidence; queue 2-3 more
  verify soaks rather than concluding either way from n=2-4.
- `processSceneNode+1424` DOES repeat post-guard → the regex match location may be wrong (guards
  compile+link but don't dominate the actual faulting path — re-check with a debugger-level trace or
  re-verify the guard's placement relative to the crash instruction in the rebuilt `funcs_4.c`) — this
  would be a real, reportable methodology finding, not just "try again."

## Environment notes (carried forward — see s327-348 for full detail)

- Regen paths: `/Users/williambuckley/Documents/Tools/N64Recomp` (`fixup_game_funcs.py`, untracked).
  Delete `RecompiledFuncs/*.c` before every `N64Recomp` run:
  `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`.
- Full regen order: `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py` ->
  `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml` ->
  `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` ->
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
  /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build -j8`. Note: `cd a && cmd` style
  compound commands sometimes require explicit approval this session (permission-matching quirk, not
  a project rule) — running each step as its own single command avoids the prompt.
- **New this session**: `fixup_game_funcs.py` patches whose regex anchor depends on
  `g_rs64_last_guest_pc = 0x...u;` lines MUST be placed after the relevant BREADCRUMB-family pass for
  that function in script order — those lines don't exist in pristine N64Recomp output, they're
  inserted by the breadcrumb patches themselves. Always confirm your new patch's report line actually
  printed after a run.
- Current gate state (unchanged since s343): fixup regex at `fixup_game_funcs.py` ~line 263 is
  `r"0x8008E(?:C88)"` — matches ONLY `reapplyDisplayMode` (`0x8008EC88`, force-zeroed);
  `setDisplayMode` (`0x8008EB40`) stays unmatched/reversed.
- Soak driver: `scratch/s73_post_a_scene/run_s327waitpump.sh <label>`, invoked with
  `env HOLD_S=<n> zsh scratch/s73_post_a_scene/run_s327waitpump.sh <label>` (`env` prefix required —
  project rule 10 / CLAUDE.md). Now arms `ROGUESQ_LOG_SCENE_NODE_CONTENT_GUARD=1` (new this session,
  next to the existing `ROGUESQ_LOG_SCENE_NODE_PTR_GUARD`/`_DEPTH_GUARD`) alongside every other
  diagnostic var, EXCEPT the 4 heap-walker vars (still default-overridable per s345's fix). Log lands
  at `scratch/s73_post_a_scene/<label>/run.log` — grep it, don't read it directly; check `runlog_bytes`
  before trusting a soak's post-processing to have actually finished.
- `[CRASH][pc-symbol]` (host PC via `dladdr`, precise) and `[CRASH][last-guest-pc]` (a separately
  tracked guest checkpoint) answer different questions by design — always trust `pc-symbol` for "what
  function crashed," and a MATCH on both together (as `rate_3`/`rate_6` showed) is unusually strong
  evidence of a real, fixed-address repeat bug, not misattribution noise.
- `processSceneNode` has now hit 4 distinct offsets across sessions (`+6668`/`+7640` pre-s295, `+1424`
  s347/s348 — now guarded at 2 load sites). Treat ANY future `processSceneNode` hit at a DIFFERENT
  offset as a still-open, separate site in this large (~1100-line) function, not automatically covered
  by this session's fix.
- `rc=137`/launcher timeouts don't necessarily mean a game-side hang — check the launcher log's own
  `done wall=Ns` line and `run.log` byte size before reading a timeout as a stall.

HYPOTHESIS-ID: m5-audio-destub-contentguard-verify (1st iteration — new thread opened s348 after the
prior slug `m5-audio-destub-step5-crashrate-comparison` closed with a landed fix, not another
inconclusive tally-update).
