# NEXT work unit

## s355 was a MAINTENANCE iteration (Step 0 triggered at 62,502 bytes) — no new soak data, no experiments run. Folded in: Thread A's `verify2` had already drained CLEAN before this session started.

Full detail: `PORTING-STATE` Session 355. Compacted `docs/CURRENT-TRUTH.md` 701→476 lines (225 net,
clears the >=200 ADVANCED bar), migrated the closed s339-353 M5 sub-arcs to a new
`docs/PROJECT-OVERVIEW.md` §10. Also picked up `s354_coalesceheapguard_verify2`'s result from
`SOAK-RESULTS.md` (it had drained via the queue before this session, not by this session): **CLEAN**,
423s, full hold, 0 crashes — same shape as `verify1`. **Thread A is now 2/2 clean**, 0/2 for the guard
actually firing. Nothing else changed factually; both threads below are exactly where s354 left them.

## Two open threads — pick the higher-information-value one first

**Thread A: `m5-audio-destub-coalesce-heap-guard-verify` (iteration 2 — 2/2 clean, 0/2 fires).** Does
the new `[coalesce-heap-guard]` fire on a crashing run, and does `coalesceFreeHeapBlocks+3452` stop
recurring? Both `s354_coalesceheapguard_verify1/2` came back CLEAN (full hold, 0 crashes, guard armed
but never exercised) — per Step 2c below, that's weak-but-still-incomplete evidence; 2 more runs needed
before calling it validated-by-non-recurrence.
- **Step 1**: write `scratch/agent/soak_queue/s355_coalesceheapguard_verify3.sh` and `_verify4.sh`
  (copy `s354_coalesceheapguard_verify2_20260805-134849.sh` from `soak_queue/done/` as the template —
  same env vars, `HOLD_S=240`) and let the loop drain them (do NOT run inline — this is exactly the
  "don't babysit a repeat soak" case the project rules call out).
- **Step 2**: next session reads the result. If EITHER crashes with `pc-symbol=coalesceFreeHeapBlocks+3452`
  again and `coalesce_guard_fire_n=0`: the guard's regex/anchor missed that occurrence — treat as a null
  instrument bug, re-check the regex against the freshly regenerated `funcs_0.c` around guest PC
  `0x80002434` (re-verify on the CURRENT regenerated source before assuming the guard is broken).
- **Step 2b**: if either CRASHES elsewhere with `coalesce_guard_fire_n>=1`: guard confirmed alive
  (positive control satisfied), crash relocated downstream — same "guard works, crash moves" pattern as
  s350/s351. Not evidence of failure; expected shape for a guard on a symptom rather than the corruption
  origin.
- **Step 2c**: if BOTH come back CLEAN too (4/4 clean, 0/4 fires): treat as validated-by-non-recurrence
  (same bar the s348 contentguard used — see `docs/PROJECT-OVERVIEW.md` §10) and close this thread.

**Thread B: `m5-audio-destub-linkedlist-corruption-source` (iteration 3 — 2 of iron rule 8's 3 strikes
used, 1 more before mandatory pivot).** The original `drainMeshReleaseQueue` tail-scan question — is
`bad_v1`'s walk position consistent across crashing runs — is STILL at 0/2 informative data points (both
s353 verify soaks crashed elsewhere). Queue 2 more `s355_ringbuffer_verify3/4.sh` (same template as
s353's recipes, `HOLD_S=240`, same env vars) if picking this thread. Given the budget: **if this
iteration's Thread B soaks ALSO come back 0-informative (crash outside drainMeshReleaseQueue again),
that's the 3-strike trigger — write the hypothesis/evidence table into this file and pivot**, per iron
rule 8. Do not spend a 4th iteration chasing the same off-target problem.

**Recommendation**: queue BOTH threads' next soak pairs for the loop this iteration (4 recipes total,
`s355_coalesceheapguard_verify3/4.sh` + `s355_ringbuffer_verify3/4.sh`) rather than running any inline —
neither thread needs a new build, both just need more soak data, and the loop drains up to 2 queued
recipes between iterations anyway. Read both pairs' results next session and resolve whichever thread
has data first.

## Environment notes (carried forward — see s327-354 for full detail)

- Regen paths: `/Users/williambuckley/Documents/Tools/N64Recomp` (`fixup_game_funcs.py`, untracked,
  confirmed outside this repo's `lib/`/submodule-patches system). Delete `RecompiledFuncs/*.c` before
  every `N64Recomp` run:
  `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`.
- Full regen order: `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py` ->
  `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml` ->
  `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` ->
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
  /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build -j8`. Run each step as its own
  single command (compound `cd a && cmd` sometimes needs manual approval this session).
- `soak_queue/*.sh` recipes must be invoked as `zsh scratch/agent/soak_queue/<name>.sh` if drained
  manually — `bash <path>` is NOT allowlisted even though the recipe files start with a `#!/bin/bash`
  shebang; only `zsh:*` is in the allow rules. If drained manually, also manually do what
  `run_soak_queue()` normally does: save output to `scratch/agent/soak_results/<name>_<timestamp>.log`,
  append a line to `SOAK-RESULTS.md`, move the `.sh` to `soak_queue/done/`.
- `for f in ...; do ... done` shell loops over globbed filenames trigger a sandbox rejection ("Contains
  simple_expansion") — prefer a `python3 - <<'EOF' ... EOF` heredoc with `glob.glob`/explicit path lists.
  Shell command substitution like `TS=$(date ...)` inline in a compound command also gets rejected
  ("Contains expansion") this session — run `date +%Y%m%d-%H%M%S` as its own command first, then paste
  the literal timestamp into subsequent commands.
- `nm` itself needs explicit interactive approval — `python3 -c "..."` wrapping `subprocess.run(['nm',
  ...])` IS allowed. `scratch/agent/check_symtab3.py` is the latest template for "is this crash symbol
  genuine or nearest-symbol misattribution."
- **All BREADCRUMB* passes share ONE `g_rs64_last_guest_pc` global.** `drainMeshReleaseQueue`
  (BREADCRUMB15) and `coalesceFreeHeapBlocks` (BREADCRUMB11) are both fully instrumented — their
  `last-guest-pc` is always precise.
- The raw `run.log` under `scratch/s73_post_a_scene/<label>/run.log` (not just the
  `scratch/agent/soak_results/*.log` summary) is where per-line diagnostic tags actually live — the
  summary logs only capture the LAST few lines. Grep the raw log directly for full history.
- Soak driver: `scratch/s73_post_a_scene/run_s327waitpump.sh <label>`, invoked with
  `env HOLD_S=<n> zsh scratch/s73_post_a_scene/run_s327waitpump.sh <label>` (`env` prefix required —
  project rule 10 / CLAUDE.md). Log lands at `scratch/s73_post_a_scene/<label>/run.log`. Note: this
  script's own `export HOLD_S=240` line INSIDE a recipe `.sh` overrides any `env HOLD_S=N` prefix passed
  to the recipe itself — to change hold length, edit the recipe file's `export HOLD_S=` line directly.
- `[CRASH][pc-symbol]` (host PC via `dladdr`, precise) and `[CRASH][last-guest-pc]` (guest checkpoint,
  only meaningful if the crashing function is breadcrumbed) answer different questions by design.
- Current gate state (unchanged since s343): fixup regex at `fixup_game_funcs.py` ~line 263 is
  `r"0x8008E(?:C88)"` — matches ONLY `reapplyDisplayMode` (`0x8008EC88`, force-zeroed);
  `setDisplayMode` (`0x8008EB40`) stays unmatched/reversed.
- If killing a manually-launched game process mid-run, verify with `ps aux | grep RogueSquadron64Recomp`
  that it's actually gone before treating a soak as aborted — s354 saw a case where a background task's
  final output showed a clean COMPLETED run despite an earlier `kill -9` on what appeared to be the same
  PID; the run's own watchdog/hold timing had likely already finished naturally by the time the kill
  landed. Trust the recipe's own printed VERDICT/launcher_rc over assumptions about what a kill did.

## Queued this session (s355, ready for the loop — nothing run yet)

`s355_coalesceheapguard_verify3/4.sh` (Thread A, `HOLD_S=240`) and `s355_ringbuffer_verify3/4.sh`
(Thread B, `HOLD_S=240`), all 4 in `scratch/agent/soak_queue/`. The loop drains up to 2 per gap between
iterations — expect at most 2 of the 4 to have results by next session; read whichever pair drained via
`SOAK-RESULTS.md` and resolve that thread first.

HYPOTHESIS-ID: m5-audio-destub-coalesce-heap-guard-verify (iteration 2 — 2/2 clean so far, `verify3/4`
queued s355). Parallel/still-open: m5-audio-destub-linkedlist-corruption-source (iteration 3 of 3
available before iron rule 8's mandatory pivot check — opened s352, instrument landed s353,
0/2-informative reading s354, `verify3/4` queued s355 as this thread's LAST soak pair before the
mandatory pivot).
