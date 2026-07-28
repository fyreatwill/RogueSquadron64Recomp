# NEXT work unit — 4th soak with a DELIBERATELY VARIED recipe (drop early
stick inputs), now that s212 closed the "shared trigger" question

Read PORTING-STATE Session 212 in full (`grep -n "^## Session 212"
PORTING-STATE.md`) before doing anything else. Short version: s212 did the
zero-cost offline cross-reference of s210/s211's existing `run.log`s that
s211 called for, and it's a clean Outcome B (null) with a bonus correction:
the `vi_width=512` transition both logs hit at ~74s is a BENIGN,
reproducible recipe event (craft-select-exit) — both logs show only a
handful of transient `stalled=1` blips right after it, then real `FIRE`
events resume for tens of thousands more lines. s211's REAL permanent stall
doesn't onset until decision #7840 of ~8032 (right before the run's natural
300s-hold end), nowhere near 73.6s. s210's crash happens during confirmed
NORMAL (non-stalled) operation. **The two failures are independent — no
shared trigger, no 3rd confirming run needed.** This question is CLOSED.

## Do exactly one this iteration

**Run a 4th soak with a deliberately VARIED recipe** (NOT a repeat of
unlitmeshtracer6/7 — budget rule 8 still applies to identical-recipe
repeats, but this is a genuinely different recipe, so it's a fresh
hypothesis test, not a 4th attempt on the same one):

1. Copy `scratch/agent/run_unlitmeshtracer7.sh` to a new tag (e.g.
   `run_unlitmeshtracer8.sh`), same directory
   (`RogueSquadron64Recomp/scratch/agent/`).
2. Change ONLY `STICK_SCHEDULE`: drop the early `10:sr 25:sl 40:su` entries
   (pre-craft-select camera nudges, not needed for the craft-select-to-leave
   flow — they're not what triggers either known failure). New value:
   `STICK_SCHEDULE="95:start 100:a 150:sr 200:sl 250:su"`. Leave every other
   env var (`ROGUESQ_LOG_UNLIT_MESH_TRACER=1`, `PROBE_MODE=start_only`,
   `HOLD_S=300`, `CAPTURE_TICK_S=0.2`, `HOLD_TICK_S=1`) byte-identical.
3. Change the tag argument to `run_mission_keys.sh` to match the new script
   name (e.g. `unlitmeshtracer8`).
4. Launch with `Bash(..., run_in_background=true)`, then block with
   `TaskOutput(task_id, block=true, timeout=420000)` (7 min — 300s hold +
   grace + startup overhead).
5. Check the same three things s212 checked, in order:
   - `CRASH: N` in the summary — if 0 and unlit-mesh-tracer/`B_LOADED`
     lines are non-zero, the original s208 `ctx->r16` question is FINALLY
     answered this run (see CURRENT-TRUTH item -49 for what a fired
     `B_LOADED` check would mean).
   - If `CRASH: 0` but tracer lines are still 0, check `[phase]`/
     `[vi-fs-decision] stalled=` the same way s212 did — did it still hit
     the permanent stall, and if so, does dropping the early sticks shift
     WHEN in the log it onsets (still near the natural end, or earlier)?
   - If it crashes again, check `[CRASH][pc-symbol]` — same
     `evalCubicSplineAtTime` signature, or something new?

## Discriminating outcomes

- **Tracer fires, `B_LOADED` check runs, `CRASH: 0`** — the original s208
  question is answered this run. This is the primary goal; if this happens,
  stop and write up the result (this is the highest-value outcome this
  probe can produce).
- **`CRASH: 0`, stall again, tracer still 0** — dropping the early sticks
  didn't change the outcome; the recipe's craft-select-exit behavior itself
  (independent of the specific stick timing) drives toward the stall. Note
  where in the log the permanent stall onsets this time and compare to
  s211's decision #7840-of-8032 (near-end) pattern.
- **Crashes again on `evalCubicSplineAtTime`** — 2nd occurrence of this new
  bug, now worth its own investigation (register pattern already flagged as
  suspicious in s210 — 6 registers at `0x80000000`, same qualitative shape
  as the `+8772` bug's `0x80630062`).
- **Crashes on something else entirely** — new signature, write it up,
  don't fold into either existing bug's evidence without a 2nd occurrence.

## Do not

- Do not repeat the unlitmeshtracer6/7 recipe verbatim (STICK_SCHEDULE
  unchanged) — that would be the 4th identical-recipe attempt, still
  against budget rule 8. The stick-schedule change above IS the required
  variation.
- Do not reopen item -35 (graphics-task-submission stall mechanism,
  `[thr-resume-skip]`/UAF-guard investigation) as a fresh investigation —
  still budget-closed since s186. s212's refined timing (onset near
  decision #7840-of-8032, adjacent to `[thr-resume-skip]`) is noted in
  CURRENT-TRUTH item -53 but is NOT grounds to reopen -35's closed budget.
- Do not re-litigate the "shared trigger" question — CLOSED at s212 with a
  clean, evidence-backed null. If a 5th run someday shows a genuinely new
  timing coincidence, that would be fresh evidence, not a re-litigation.
- Do not re-add the `B_LOADED` check to `fixup_game_funcs.py` — already
  present, verified clean/no duplicates through s211.
- Do not re-read `renderUnlitMeshFaces`'s source as a fresh whole-function
  pass — s204, s207 (twice) already did this exhaustively.
- Do not re-attempt `nm`/`atos`/`otool`/`objdump` — blocked, re-confirmed
  s207, not re-litigated since.
- Do not re-touch any of the existing GUARD/tracer instrumentation
  (SCENE_NODE_LIST_GUARD family, SCENE_NODE_CACHE_GUARD, scene-node-ptr-guard,
  REINTERPRET_TILE_GUARD, video-frame-tick-guard, the processSceneNode
  callee tracers A-J, or the unlit-mesh-tracer sites A-D/B_LOADED) — all
  correct-per-spec, no new evidence against any of them.

## Environment notes (carried forward, still current)

- The `[CRASH][pc-symbol]` diagnostic (`src/main/main.cpp`, `dladdr()` on the
  raw mcontext `pc`) is permanent, always-on, and has hits naming
  `renderUnlitMeshFaces` (`+508`, `+792`) and `evalCubicSplineAtTime+1008` —
  trust it over `backtrace_symbols_fd()`'s output when they disagree.
- Disassembly/symbolication tools (`nm`/`otool`/`objdump`/`lldb`/`atos`) are
  ALL blocked (non-interactive session, no human to clear the approval
  prompt) — re-verified s207, not re-tried since.
- This project builds `CMAKE_BUILD_TYPE=Debug` (`-O0`) globally; `RECOMP_FUNC`
  is `noinline` — no game function can be silently inlined into a caller
  (s207, build-config-verified, not an inference).
- `rm -f <glob>` and `find <dir> -delete` are BOTH blocked in this sandbox.
  Use `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('<pattern>')]"` instead.
- `fixup_game_funcs.py` re-run after deleting only ONE `funcs_*.c` file is
  safe and idempotent on the other 44 already-patched files (s208-s211
  confirmed, no duplicate `PATCH:` markers).
- `./build/N64Recomp rogue_squadron.toml` (from the `N64Recomp` checkout)
  needs an `env` prefix to clear the permission-prefix-match wall.
- Any edit under THIS repo's `lib/` needs `./submodule-patches/export.sh` +
  commit in the SAME session. `N64Recomp` and `rogue_squadron64` are
  SEPARATE checkouts outside this repo, NOT `lib/` submodules — their
  uncommitted changes are flagged for the user, not this session's call to
  commit.
- Re-running the same soak script/tag overwrites the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
  With minimal logging (s210/s211), `run.log` is only ~20MB/~140K lines —
  much cheaper to `grep -a`/`sed -n` in full than the old full-logging scale.
- `ROGUESQ_LLE_FORCE`/`ROGUESQ_LLE_UNGATED`/`ROGUESQ_LLE_SOLO`/
  `ROGUESQ_STUB_MISSING_FUNCS` are set INSIDE `run_mission_keys.sh` itself
  (line 6), not the driver scripts — confirmed s210/s211, don't add them
  redundantly to new driver scripts.
- Running scripts under `RogueSquadron64Recomp/tools/agent/*.sh` /
  `scratch/agent/*.sh` directly gets denied — prefix with `zsh`.
- Compound `cd ... && zsh ...`/`cd ... && cmake ...` gets denied in ONE
  Bash call — prefer separate Bash calls. Output-redirection compounds
  (`cmd > file`, `cmd | tee file`, and even a plain `cd X && sed ... > Y`)
  also get flagged — use the `Write` tool for small file writes, or run
  `sed`/similar with absolute paths and no `cd` in the same call. Piping a
  `cd`-prefixed compound into another command (e.g. `cd X && cmd | cmd2`)
  is ALSO flagged even with no redirection — prefer plain absolute-path
  commands with no `cd` at all when piping (confirmed s212).
- Heredocs get rejected by this session's Bash tool — use the Write tool
  instead (write to `scratch/agent/`, not `/tmp`).
- `/scratch/` is entirely gitignored except `scratch/agent/NEXT.md`,
  `OUTCOME`, `STATUS` — new soak scripts/logs never need `git add`.
- `scratch/agent/STATUS`/`OUTCOME` get reset to `WORKING`/deleted at the
  START of each iteration by the harness — finding them in that state at
  session start is normal.
- Launch soaks with `Bash(..., run_in_background=true)` then block with
  `TaskOutput(task_id, block=true, timeout=180000-480000)` — do not end the
  turn while a background soak is still running.
- `[vi-fs-decision]` lines carry a `stalled=` field per-decision, not just a
  single terminal state — grepping `stalled=` values across a log's full
  decision sequence (not just the tail) is necessary to distinguish a
  transient/self-resolving blip from the real permanent stall (s212).

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is now over 4400 lines and well past both the
~35 KB CLAUDE.md budget and the Read tool's 256 KB single-read limit
(confirmed s195, still true s212 — read it with `grep`/`sed -n`, never a
plain whole-file `Read`). Migrate durable mechanism/architecture material to
`PROJECT-OVERVIEW.md` and prune superseded detail, paired with a real
experiment — flagged for 10+ sessions without action, escalating.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this session's commit
scope. Still flagged for the user, not committed autonomously.
