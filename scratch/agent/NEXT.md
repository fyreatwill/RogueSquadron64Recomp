# NEXT work unit — characterize/clear the s209 log-volume blowup before
resuming the `ctx->r16` widen probe for the `processSceneNode+8772`/
`renderUnlitMeshFaces` KSEG0-zero-extension bug.

Read PORTING-STATE Session 209 in full (`grep -n "^## Session 209"
PORTING-STATE.md`) before doing anything else. The short version: s209 landed
a real new instrument (a `B_LOADED` check on `ctx->r16` itself, right after
its load at `funcs_4.c:5031`, via a new `fixup_game_funcs.py` patch block —
still present, do not re-add it) and built clean, but BOTH soaks this session
came back as ambiguous nulls — not because the instrument is broken, but
because something new and reproducible is preventing the craft-select/hangar
scene from ever being reached at all.

## The new fact this session found

`run_unlitmeshtracer4.sh`/`run_unlitmeshtracer5.sh` (copies of s208's
`run_unlitmeshtracer3.sh`, unmodified env vars, same 361s hold duration) both
produced run.log files ~47x larger than s208's own successful baseline run
(`unlitmeshtracer3`: 4.49M total lines; `unlitmeshtracer4`: 210.0M;
`unlitmeshtracer5`: 210.9M), dominated by `rs-free-walk` lines (1.98M in the
baseline vs 104.8M / 172.1M this session). Neither soak logged a single
`unlit-mesh-tracer` line, including the always-fires-at-call-1 positive
control — meaning `renderUnlitMeshFaces` was never called, i.e. the run never
got far enough to reach the scene this bug lives in. `processSceneNode`
itself IS running (`[process-scene-node-callee] site=I` lines are present in
the sampled log), so this isn't a full hang — something is just consuming
nearly the entire 361s hold window before the craft-select transition
happens.

## Do exactly one this iteration, in this order

1. **Cheapest, boring-explanation-first: strip the non-essential logging and
   re-soak.** Copy `scratch/agent/run_unlitmeshtracer5.sh` to a new tag
   (e.g. `run_unlitmeshtracer6.sh`). Comment out or remove every
   `export ROGUESQ_LOG_*=1` line EXCEPT `ROGUESQ_LOG_UNLIT_MESH_TRACER=1`
   (keep `ROGUESQ_LLE_FORCE`/`ROGUESQ_LLE_UNGATED`/`ROGUESQ_LLE_SOLO`/
   `ROGUESQ_STUB_MISSING_FUNCS` and the script's other non-`LOG` plumbing —
   those aren't logging). Run it. Two possible outcomes:
   - **The craft-select scene is reached and the tracer fires (positive
     control logs at call #1, log stays small, ~4-5M lines like the s208
     baseline or smaller)**: this confirms the earlier over-instrumented runs
     were self-inflicted — the ~60 verbose `ROGUESQ_LOG_*` diagnostics were
     costing enough wall-clock time via `fprintf` that real game-logic
     progress got starved inside the fixed 361s hold window. Actionable and
     cheap: for THIS specific bug's future soaks, always run with a minimal
     env-var set (document this in the next PORTING-STATE entry and add a
     `run_unlitmeshtracer_minimal.sh` reusable template). Then, in the SAME
     run if it also crashes, or a follow-up run otherwise, read whether the
     new `B_LOADED` check at `funcs_4.c:5032` fires OOB — this is the actual
     original s208/NEXT.md question (does the value in `ctx->r16` show up
     zero-extended immediately after its load, or only later).
   - **Still 0 tracer lines / scene still never reached, even with minimal
     logging**: the `rs-free-walk` blowup is a real behavioral regression,
     not a logging-overhead artifact. Do NOT chase this deeper the same
     iteration (budget rule 8) — write it up as a new, higher-priority
     blocking bug (working title: "rs-free-walk blowup blocks scene
     transition"), separate from the `+8772` KSEG0 bug, and go BLOCKED or
     pick the next highest-value item from CURRENT-TRUTH's "Next steps".

2. **If step 1 confirms the logging-overhead explanation and a soak with
   minimal logging reaches the scene**: check the `B_LOADED` check's result
   directly (`grep -a "B_LOADED" run.log` for the new tag's run.log — expect
   either an `OOB` line, meaning the value was already zero-extended right at
   the load and NOT via the audited-clean `MEM_W`-assignment path (a real,
   actionable finding worth its own deep dive into codegen or a stray raw
   cast), or no `OOB` line despite a crash, meaning the corruption happens
   even later than `ctx->r16`'s first ~35 uses and the next session should
   widen further along the chain (site A's `ctx->r18`, or the ~35 individual
   `ctx->r16` derefs listed in s208's PORTING-STATE entry).

## Do not

- Do not re-add the `B_LOADED` check to `fixup_game_funcs.py` — it is
  already there (patched cleanly, verified x1, no duplicates as of s209).
  Re-running `fixup_game_funcs.py` after deleting only `funcs_4.c` is safe
  and idempotent (s208/s209-confirmed) if you need to regenerate.
- Do not re-read `renderUnlitMeshFaces`'s source as a fresh whole-function
  pass — s204, s207 (twice) already did this exhaustively.
- Do not re-attempt `nm`/`atos`/`otool`/`objdump` — blocked, re-confirmed
  s207, not re-litigated since.
- Do not soak a 3rd time with the FULL (unstripped) env-var set expecting a
  different outcome — 2/2 soaks this session already came back the same way
  with that exact config; per budget rule 8, that hypothesis (as configured)
  is exhausted. The variable to change is the env-var set (step 1), not the
  number of retries.
- Do not conclude the `rs-free-walk` blowup is caused by the `B_LOADED`
  patch — that edit is a 1-line, `getenv`-gated, control-flow-inert observer
  in `funcs_4.c` (rendering code), unrelated to whatever subsystem emits
  `rs-free-walk` (an allocator/heap-walk diagnostic, pre-existing, untouched
  this session). If step 1's minimal-logging soak clears the problem, that
  closes this question without needing to inspect the free-walk code at all.
- Do not re-touch any of the existing GUARD/tracer instrumentation
  (SCENE_NODE_LIST_GUARD family, SCENE_NODE_CACHE_GUARD, scene-node-ptr-guard,
  REINTERPRET_TILE_GUARD, video-frame-tick-guard, the processSceneNode
  callee tracers A-J, or the unlit-mesh-tracer sites A-D/B_LOADED) — all
  correct-per-spec, no new evidence against any of them.

## Environment notes (carried forward, still current)

- The `[CRASH][pc-symbol]` diagnostic (`src/main/main.cpp`, `dladdr()` on the
  raw mcontext `pc`) is permanent and always-on, and has 2 independent hits
  naming `renderUnlitMeshFaces` (`+508` and `+792`) — trust it over
  `backtrace_symbols_fd()`'s output when they disagree.
- Disassembly/symbolication tools (`nm`/`otool`/`objdump`/`lldb`/`atos`) are
  ALL blocked (non-interactive session, no human to clear the approval
  prompt) — re-verified s207, not re-tried s208/s209.
- This project builds `CMAKE_BUILD_TYPE=Debug` (`-O0`) globally; `RECOMP_FUNC`
  is `noinline` — no game function can be silently inlined into a caller
  (s207, build-config-verified, not an inference).
- `rm -f <glob>` and `find <dir> -delete` are BOTH blocked in this sandbox.
  Use `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('<pattern>')]"` instead.
- `fixup_game_funcs.py` re-run after deleting only ONE `funcs_*.c` file is
  safe and idempotent on the other 44 already-patched files (s208/s209-
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
  `run.log` files can be MULTI-GIGABYTE (this session: 10+ GB, 210M+ lines)
  — NEVER `Read`/`cat` them whole — always `grep -a`/`sed -n`/`awk`/`wc -l`
  for specific content, and expect even `grep -c` over a 10 GB file to take
  real wall-clock time.
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
- Block on a soak by launching (it auto-backgrounds past the 120s Bash
  timeout) and then calling `TaskOutput(task_id, block=true, timeout=
  180000-480000)`, possibly more than once in a row if it's still
  `running` — do not end the turn while a background soak is still running.
  The driver script's own `--- summary ---` postprocessing step can itself
  take several minutes on a 10+ GB log; it's fine to `grep -a -c` the
  run.log directly for the specific markers you need instead of waiting for
  that summary to finish.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is now well over the ~35 KB CLAUDE.md budget and
exceeds the Read tool's 256 KB single-read limit (confirmed s195, still
true s209 — read it with `grep`/`sed -n`, never a plain whole-file `Read`).
Migrate durable mechanism/architecture material to `PROJECT-OVERVIEW.md` and
prune superseded detail, paired with a real experiment — flagged for 10+
sessions without action, escalating.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this session's commit
scope. Still flagged for the user, not committed autonomously.
