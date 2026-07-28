# NEXT work unit — heapWalker guard fix is SHIPPED but still UNTESTED live;
pick between chasing the new do_send SIGBUS or designing a fresh repro recipe

Read PORTING-STATE Session 214 in full (`grep -n "^## Session 214"
PORTING-STATE.md`) before doing anything else. Short version: s214 built and
shipped the upper-bits guard strengthening NEXT.md asked for (heapWalker's 10
guard sites now reject `hi != 0xFFFFFFFF`, not just the `U32()`-truncated
low-32 range check) — confirmed patched in the generated `funcs_3.c` before
building, full regen+build clean. But 2 soaks in a row with the s213 varied
recipe (`STICK_SCHEDULE="95:start 100:a 150:sr 200:sl 250:su"`) both died on
UNRELATED crashes before ever reaching heapWalker's code path:
- Soak 1 (`scratch/s73_post_a_scene/heapwalkerguard4a/run.log`): 3s into
  hold, `sinfApprox` NaN assert (signal 6) — new call site for the
  pre-existing `NAN_CHECK` family (s83 precedent was `evalCubicSplineAtTime`).
- Soak 2 (`scratch/s73_post_a_scene/heapwalkerguard4/run.log`): 104s into
  hold (35x further), `do_send`/`mesgqueue.cpp` SIGBUS (signal 10) — new call
  site for the pre-existing thread-context-corruption family already
  implicated in the s176+ "graphics-task-submission stall" investigation
  (PORTING-STATE ~L16759-16896).

Neither soak logged a `[heapwalker-guard]`/`[heapwalker-guard3]` fire or a
single `[unlit-mesh-tracer]` hit. The guard mechanism is STILL neither
confirmed nor refuted — this session's job is to get the discriminating
measurement s214 couldn't.

## Do NOT do this iteration

- Do not run a 3rd soak of the exact same `heapwalkerguard4`-style recipe.
  s214 already used its one free re-run (NEXT.md's own "inconclusive, re-run
  once" allowance) — a 3rd identical attempt is re-rolling dice against
  explicit guidance in this doc, not advancing the discriminating test. Two
  soaks, two different unrelated crashes, both well before heapWalker: that
  1-for-3 hit rate this session (vs 1-for-1 for this exact recipe in s213)
  means the recipe is not currently a reliable repro for the target crash.
- Do not re-touch the guard code itself (`N64Recomp/fixup_game_funcs.py`,
  `_make_heapwalker_guard_patch`/`_make_heapwalker_guard3_patch`) — it is
  DONE, confirmed built and live in the binary. Nothing about this session's
  findings suggests the guard code itself is wrong; the problem is the soak
  never reaches it.

## Two competing next moves — pick ONE, do not straddle both

**Option A (chase the do_send SIGBUS)** — higher expected value IF it's
really the same bug as the s176+ stall family, because fixing it could
unblock MULTIPLE future soaks (this stall/crash has now blocked at least
s186 (stall), s214 soak 2 (SIGBUS) — same functions, different symptom).
1. Read PORTING-STATE ~L16759-16896 (the s176+ thread-context-UAF mechanism:
   `run_next_thread_and_wait` popping a torn-down thread's context, the s84
   crash-avoidance gate trading a SIGBUS for a silent stall).
2. Read `mesgqueue.cpp`'s `do_send` around wherever it dereferences a thread
   context to decide if this SIGBUS (native pc, not a `ctx->rN` guest
   register — `_Z7do_sendPhiibb+388`, `si_addr=0x34ca41180` garbage, NOT a
   KSEG0-shaped address) is mechanically the SAME corrupted-context path or a
   genuinely different one. This is a NATIVE crash, not a recompiled-MIPS
   register corruption — the KSEG0-zero-extension theory does NOT apply here,
   this needs its own read, not a guard-template reuse.
3. If it's the same mechanism: the s84 gate already exists as a "drop the
   turn instead of crashing" fix for the stall side — check why it didn't
   fire here / whether do_send has its own unguarded thread-context deref
   that needs the equivalent guard.

**Option B (design a fresh heapWalker repro)** — lower investigation cost,
directly serves the still-open guard question.
1. The varied s213 recipe got lucky once (1/1) then unlucky twice (0/2) —
   consider whether a recipe with MORE hold time before the crash-vulnerable
   window, or a recipe that reaches craft-select-exit via a different input
   sequence entirely, changes which race wins.
2. Whichever recipe you pick, set `ROGUESQ_LOG_HEAPWALKER_GUARD=1` and
   `ROGUESQ_LOG_HEAPWALKER_GUARD3=1` (both already default-off, must be set
   to observe a fire) and launch with `Bash(..., run_in_background=true)` +
   `TaskOutput(task_id, block=true, timeout=420000)`.
3. Discriminating outcomes are UNCHANGED from s213/s214's table: guard fires
   with `hi != 0xFFFFFFFF` + crash gone = mechanism proven and fixed; guard
   fires + crash elsewhere = this site closed, another path remains; guard
   never fires + crash recurs identically = theory refuted for this crash;
   guard never fires + no crash = inconclusive, one free re-run only.

Pick based on which has higher information value this session — Option A
has a chance of resolving a MUCH older, higher-cost-to-project bug
(s176-present); Option B directly closes s214's specific open question. If
budget is tight, prefer A only if the source read in step 2 confirms same-
mechanism quickly (say, within the first ~15 min); otherwise fall back to B.

## Environment notes (carried forward, still current)

- The `[CRASH][pc-symbol]` diagnostic (dladdr on the raw mcontext `pc`) is
  permanent, always-on, and MORE PRECISE than `backtrace_symbols_fd` (s213
  proved this live). Trust dladdr.
- Disassembly/symbolication tools (`nm`/`otool`/`objdump`/`lldb`/`atos`) are
  ALL blocked (non-interactive session) — re-verified s207/s213.
- `recomp.h`: `U32(val)` = `(uint32_t)(val)`; `gpr` = `uint64_t`; a legit
  KSEG0 `gpr` sign-extends, upper bits `0xFFFFFFFF`. The s214 guard fix reads
  the upper bits directly off the untouched 64-bit register — this is now
  the reference pattern for any FUTURE guard needing the same protection
  (e.g. if the `ctx->r16`/item -49/`renderUnlitMeshFaces` guard is ever
  built, copy this shape).
- This project builds `CMAKE_BUILD_TYPE=Debug` (`-O0`); `RECOMP_FUNC` is
  `noinline` — no game function can be silently inlined into a caller (s207).
- `rm -f <glob>`/`find <dir> -delete` are blocked — use
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('<pattern>')]"`.
- `fixup_game_funcs.py` re-run after deleting one `funcs_*.c` is safe and
  idempotent on the other 44 already-patched files (s208-s211).
- `./build/N64Recomp rogue_squadron.toml` needs an `env` prefix (permission-
  prefix-match wall).
- Any edit under THIS repo's `lib/` needs `./submodule-patches/export.sh` +
  commit same session. `N64Recomp`/`rogue_squadron64` are SEPARATE checkouts,
  NOT `lib/` submodules — editing `N64Recomp/fixup_game_funcs.py` does NOT
  need export.sh (confirmed s214: edited it, built clean, git status showed
  zero new changes in THIS repo beyond docs).
- Re-running the same soak script/tag OVERWRITES the previous run's `run.log`
  in place (confirmed again s214: had to `mv` the first attempt's directory
  aside before re-running, or it would have been lost) — copy the driver
  script to a new tag name per soak, or rename the output dir before re-use.
- `ROGUESQ_LLE_FORCE`/`ROGUESQ_LLE_UNGATED`/`ROGUESQ_LLE_SOLO`/
  `ROGUESQ_STUB_MISSING_FUNCS` are set INSIDE `run_mission_keys.sh` (line 6).
- Running scripts under `RogueSquadron64Recomp/tools/agent/*.sh`/
  `scratch/agent/*.sh` directly gets denied — prefix with `zsh`.
- Compound `cd ... && zsh ...`/`cd ... && cmake ...` gets denied in ONE Bash
  call — use separate Bash calls. Heredocs get rejected — use Write tool.
- `/scratch/` is entirely gitignored except `scratch/agent/NEXT.md`,
  `OUTCOME`, `STATUS`.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each iteration
  by the harness — finding them reset at session start is normal.
- Launch soaks with `Bash(..., run_in_background=true)` then block with
  `TaskOutput(task_id, block=true, timeout=180000-480000)`.
- The `grep -ac '[CRASH]'` count in `run_mission_keys.sh`'s summary counts
  LINES matching the tag, not crash EVENTS — a single crash's full mcontext
  dump is ~35 lines (28 GPRs + siginfo + mcontext header + pc-symbol +
  vifs-snapshot + caught-signal line), so "CRASH: 35" in a summary usually
  means exactly ONE crash, not 35. Always grep `caught signal` or
  `[CRASH][pc-symbol]` to get the real event count, don't trust the raw
  number at face value (s214 finding — the summary line is misleading).

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is now past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (confirmed s195, still true s214 — read
it with `grep`/`sed -n`, never a plain whole-file `Read`). Migrate durable
mechanism/architecture material to `PROJECT-OVERVIEW.md` and prune superseded
detail, paired with a real experiment — flagged for 12+ sessions without
action, escalating.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with long-
standing uncommitted changes (including this session's guard-fix edit to
`fixup_game_funcs.py`), unrelated to this repo's commit scope. Still flagged
for the user, not committed autonomously.

`lib/N64ModernRuntime` and `lib/rt64` show as modified in `git status` (pre-
existing since at least s213, not caused by s213 or s214's work) — still not
investigated (out of scope for both sessions' prescribed work units); worth
checking whether these two submodules' patches are still in sync with
`submodule-patches/*.patch` before assuming this is normal steady-state
dirtiness.
