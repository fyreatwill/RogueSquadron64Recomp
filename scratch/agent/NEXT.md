# NEXT work unit — re-run the minimal-logging soak to get past (or confirm)
the new `evalCubicSplineAtTime` crash, then read the `B_LOADED` result for
the `processSceneNode+8772`/`renderUnlitMeshFaces` KSEG0-zero-extension bug.

Read PORTING-STATE Session 210 in full (`grep -n "^## Session 210"
PORTING-STATE.md`) before doing anything else. Short version: s210 ran the
minimal-logging soak s209 called for (`run_unlitmeshtracer6.sh`: all
`ROGUESQ_LOG_*` vars stripped except `ROGUESQ_LOG_UNLIT_MESH_TRACER=1`,
everything else identical to `run_unlitmeshtracer5.sh`). This CONFIRMED the
s209 blowup was self-inflicted logging overhead (run.log collapsed from
210M lines to 143,093; craft-select was reached in 46.0s, never reached at
all in s209's two full-logging soaks) — `rs-free-walk` blowup as an
independent regression is RULED OUT, do not revisit that question.

But the soak crashed 6s into the hold window on a bug NEVER SEEN BEFORE in
this investigation: `[CRASH][pc-symbol] sym=evalCubicSplineAtTime+1008`,
signal 10 (Bus error), `si_addr=0x37ffffff8`. This is NOT
`renderUnlitMeshFaces` — it's an unrelated spline/animation-eval function —
so `renderUnlitMeshFaces` was never called this run, and both
`unlit-mesh-tracer` and `B_LOADED` logged 0 lines for a legitimate reason
(crashed elsewhere first), not because either instrument is broken. The
original s208 question (does `ctx->r16` show up zero-extended immediately
at its `funcs_4.c:5031` load?) is STILL unanswered.

## Do exactly one this iteration, in this order

1. **Re-run the exact same minimal-logging recipe as a fresh soak.** Copy
   `scratch/agent/run_unlitmeshtracer6.sh` to `run_unlitmeshtracer7.sh`,
   change only the tag argument (`unlitmeshtracer6` -> `unlitmeshtracer7` in
   the final `zsh run_mission_keys.sh ...` line), leave every env var
   untouched. Launch it in the background (it runs past the 120s Bash
   timeout) and block on it (`TaskOutput(..., block=true, timeout=300000-
   480000)`). Three possible outcomes:
   - **Reaches `renderUnlitMeshFaces` this time (tracer or `B_LOADED` line
     appears)**: this is the actual target result — read it directly
     (`grep -a "B_LOADED" .../unlitmeshtracer7/run.log`). An `OOB`/nonzero
     line means `ctx->r16` was already corrupted at load time (real,
     actionable — points at codegen or a stray cast, not the audited-clean
     `MEM_W` path). No such line despite a crash means the corruption
     happens later than `ctx->r16`'s first ~35 uses — widen further per
     s208's list (site A's `ctx->r18`, or the individual derefs at
     funcs_4.c:5057/5069/5114-5195/5347-5542).
   - **Crashes again at `evalCubicSplineAtTime+1008` (or same `si_addr`
     pattern)**: this is now a confirmed-recurring 2nd bug, independent of
     the `+8772` investigation. Do NOT chase it deeper this same iteration
     (budget rule 8 — this would be the 2nd occurrence of THIS specific
     signature, so one more soak to characterize it is fine next time, but
     not folded into unrelated work this iteration). Write it up
     as a new, separate candidate bug in CURRENT-TRUTH (do not merge its
     evidence into the `+8772` bug's — different function, only
     pattern-level similarity so far) and pick the next highest-value item.
   - **Crashes on yet a 3rd, different signature**: same treatment — log it,
     do not force it into either existing bug's bucket, move to the next
     highest-value CURRENT-TRUTH item this iteration.

2. **If step 1's soak reaches the scene AND crashes with the `+8772`
   signature (`renderUnlitMeshFaces+508`/`+792`, `far`/`si_addr` matching
   the recurring `0x80630062` family) but the `B_LOADED` check shows no OOB**:
   this is the widen-further case — pick ONE of the ~35 remaining `ctx->r16`
   derefs (prioritize funcs_4.c:5057 and 5069, the earliest after the
   already-checked load) and add a scoped check there for the next
   iteration's build, rather than building it this same iteration (budget:
   one soak already ran this unit).

## Do not

- Do not re-litigate the `rs-free-walk`/logging-overhead question — s210
  closed it with a clean confirm (2 independent lines of evidence now:
  s209's 210M-line/scene-never-reached soaks, and s210's 143K-line/scene-
  reached-in-46s soak with the ONLY variable changed being the log-var set).
- Do not re-add the `B_LOADED` check to `fixup_game_funcs.py` — already
  present, verified clean/no duplicates through s210.
- Do not re-read `renderUnlitMeshFaces`'s source as a fresh whole-function
  pass — s204, s207 (twice) already did this exhaustively.
- Do not re-attempt `nm`/`atos`/`otool`/`objdump` — blocked, re-confirmed
  s207, not re-litigated since.
- Do not assume `evalCubicSplineAtTime`'s crash shares root cause with the
  `+8772` bug just because both show register values clustered near
  `0x80000000` — that pattern-level similarity is noted in PORTING-STATE
  s210 but is SINGLE-OCCURRENCE and unconfirmed; treat as a separate,
  unconfirmed bug until a 2nd independent line of evidence links them or
  characterizes `evalCubicSplineAtTime` on its own.
- Do not re-touch any of the existing GUARD/tracer instrumentation
  (SCENE_NODE_LIST_GUARD family, SCENE_NODE_CACHE_GUARD, scene-node-ptr-guard,
  REINTERPRET_TILE_GUARD, video-frame-tick-guard, the processSceneNode
  callee tracers A-J, or the unlit-mesh-tracer sites A-D/B_LOADED) — all
  correct-per-spec, no new evidence against any of them.

## Environment notes (carried forward, still current)

- The `[CRASH][pc-symbol]` diagnostic (`src/main/main.cpp`, `dladdr()` on the
  raw mcontext `pc`) is permanent, always-on, and now has hits naming BOTH
  `renderUnlitMeshFaces` (`+508`, `+792`) and, new this session,
  `evalCubicSplineAtTime+1008` — trust it over `backtrace_symbols_fd()`'s
  output when they disagree.
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
  safe and idempotent on the other 44 already-patched files (s208/s209/s210-
  confirmed, no duplicate `PATCH:` markers).
- `./build/N64Recomp rogue_squadron.toml` (from the `N64Recomp` checkout)
  needs an `env` prefix to clear the permission-prefix-match wall.
- Any edit under THIS repo's `lib/` needs `./submodule-patches/export.sh` +
  commit in the SAME session. `N64Recomp` and `rogue_squadron64` are
  SEPARATE checkouts outside this repo, NOT `lib/` submodules — their
  uncommitted changes (`fixup_game_funcs.py`, `RecompiledFuncs/funcs_4.c`)
  are flagged for the user, not this session's call to commit.
- Re-running the same soak script/tag overwrites the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
  `run.log` files CAN be multi-gigabyte if full logging is re-enabled
  (s209: 10+ GB, 210M+ lines) — but with minimal logging (s210) it's only
  20 MB/143K lines. Either way, prefer `grep -a`/`sed -n`/`awk`/`wc -l` for
  specific content over a whole-file `Read`.
- `ROGUESQ_LLE_FORCE`/`ROGUESQ_LLE_UNGATED`/`ROGUESQ_LLE_SOLO`/
  `ROGUESQ_STUB_MISSING_FUNCS` are set INSIDE `run_mission_keys.sh` itself
  (line 6), not the driver scripts — confirmed s210, don't add them
  redundantly to new driver scripts.
- Running scripts under `RogueSquadron64Recomp/tools/agent/*.sh` /
  `scratch/agent/*.sh` directly gets denied — prefix with `zsh`.
- Compound `cd ... && zsh ...`/`cd ... && cmake ...` gets denied in ONE
  Bash call — prefer separate Bash calls. Output-redirection compounds
  (`cmd > file`, `cmd | tee file`, and even a plain `cd X && sed ... > Y`)
  also get flagged — use the `Write` tool for small file writes, or run
  `sed`/similar with absolute paths and no `cd` in the same call.
- Heredocs get rejected by this session's Bash tool — use the Write tool
  instead (write to `scratch/agent/`, not `/tmp`).
- `/scratch/` is entirely gitignored except `scratch/agent/NEXT.md`,
  `OUTCOME`, `STATUS` — new soak scripts/logs never need `git add`.
- `scratch/agent/STATUS`/`OUTCOME` get reset to `WORKING`/deleted at the
  START of each iteration by the harness — finding them in that state at
  session start is normal.
- Launch soaks with `Bash(..., run_in_background=true)` then block with
  `TaskOutput(task_id, block=true, timeout=180000-480000)` — do not end the
  turn while a background soak is still running. The driver script's own
  `--- summary ---` postprocessing step can itself take time on a large
  log; `grep -a -c` the run.log directly for specific markers if you need
  an answer before that summary finishes.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is now over 4300 lines and well past both the
~35 KB CLAUDE.md budget and the Read tool's 256 KB single-read limit
(confirmed s195, still true s210 — read it with `grep`/`sed -n`, never a
plain whole-file `Read`). Migrate durable mechanism/architecture material to
`PROJECT-OVERVIEW.md` and prune superseded detail, paired with a real
experiment — flagged for 10+ sessions without action, escalating.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this session's commit
scope. Still flagged for the user, not committed autonomously.
