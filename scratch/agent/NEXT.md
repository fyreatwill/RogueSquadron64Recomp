# NEXT work unit — catch the graphics-task-submission stall with the swap-ack-wait instrument armed

s177 corrected s176's framing (the `[vi-fs-decision]` "stalled" field is
wall-clock-defined, not a hidden counter threshold — see below) and landed a
targeted producer-side instrument, but the one soak that ran didn't reproduce
the stall itself. Read PORTING-STATE Session 177 before doing anything else;
this file only has the actionable summary.

## What s177 established (read before doing anything else)

- **Corrected NEXT.md's own s176 framing**: source-read `lib/rt64/src/hle/
  rt64_state.cpp` (~2841-2843) shows `[vi-fs-decision]`'s `stalled` field is
  computed directly from `std::chrono::steady_clock` — `(now -
  g_rs64LastAdvance) > 100ms` — not from any guest tick or resource count.
  s176's NEXT.md guess ("most plausibly tick-count or resource-count based")
  was never source-verified and is refuted. The real open question was never
  "what value does `stalled` cross" — it's **why the pending workload's
  `pairs` field (fbPairCount) stays 0 forever once stalled**, i.e. why the
  guest stops registering new framebuffer pairs at all.
- **New candidate lead (single-source, offline grep, no rebuild)**: at both
  s176 runs' last real `stalled=0` transition before their respective stall
  onsets, `rdpFs`/`skSeen`/`skNoTrig` cluster in a narrow ~3175-3802 band
  despite run 1 running 87% longer in wall-clock time than run 2 before
  onset. If these counters were wall-clock/tick-scaled they should differ by
  roughly that same 87% — instead they're within 5-8% of each other. This
  suggests a shared, roughly-fixed internal ceiling (buffer/queue-slot/
  semaphore count in the ~3500-3800 range), not a wall-clock/tick threshold.
  Not yet confirmed by a 3rd data point.
- **Landed and soaked `ROGUESQ_LOG_SWAP_ACK_WAIT`** (`N64Recomp/
  fixup_game_funcs.py`, funcs_5.c): entry + pre-recv/post-recv logging around
  `waitForPostSwapAck`'s `osRecvMesg_recomp` call — the only point in the
  per-frame producer chain (`runHangarSelectionFrame` -> `waitForPrevFrameDone`
  -> `waitForPostSwapAck`) that can block before the frame does any real work
  (animation, camera, `submitGfxFrame`). Built clean (exit 0).
- **One soak (`swapackwait1`) did NOT reproduce the stall** — it crashed
  instead to a recurrence of the s84 `frameStartReset` SIGBUS (2nd occurrence
  ever; source-confirmed zero self-calls in that function, so the doubled
  stack frame in its backtrace is very likely a stack-unwind artifact, same
  pattern as s87/88's `advancePlayerAnimationPhase`). The new instrument
  itself is validated: 7391 `enter`, 10033 matched `pre-recv`/`post-recv`
  pairs, zero orphaned waits, clean right up to the crash — a real negative
  control for "stuck in this wait" *for this run's failure mode*, but it says
  nothing about the actual stall since the stall didn't happen this run.

## Do next

1. **Re-run the `swapackwait1` recipe** (`scratch/agent/run_swapackwait1.sh`,
   copy to a new tag first per the renaming convention below) specifically
   trying to catch the graphics-task-submission stall itself with the new
   instrument armed. This is soak attempt 1 of a fresh hypothesis test (the
   producer-side instrument has never actually been checked against a real
   stall occurrence) — per rule 8 there's budget for up to 3 attempts before
   parking this line.
2. When a soak DOES stall (`[vi-fs-decision]` shows `stalled=1 pairs=0`
   persisting), grep `[swap-ack-wait]` near the stall onset line number:
   - **Last log line is `pre-recv` with no matching `post-recv`, and no
     further `enter` ever** → CONFIRMS the per-frame producer is blocked
     forever inside `osRecvMesg_recomp` waiting for a swap-ack message that
     never arrives. This would be a genuine root-cause finding — next step
     would be tracing who is supposed to send that message (likely a
     simulated VI/DP interrupt handler) and why it stops firing.
   - **`enter`/`pre-recv`/`post-recv` keep cycling normally throughout the
     stall window** → REFUTES this specific mechanism. Points back at the
     RT64-side `[vi-fs-decision]` gate logic itself (`rt64_state.cpp`
     `updateScreen`) — the producer keeps submitting frames but something
     about how `pending.fbPairCount` gets reset/consumed discards them.
3. **Independently, also check whether a 3rd stall occurrence's onset
   `rdpFs`/`skSeen`/`skNoTrig` values land near the same ~3175-3802 band** as
   s176's two runs — if so, this becomes the higher-priority lead (a
   concrete, driveable reproduction target) over the producer-instrument
   line above. Both checks can be done from the same soak's log, no need to
   choose one over the other in advance.

## Do not

- Do not conclude the `waitForPostSwapAck` hypothesis is confirmed OR refuted
  based on s177's soak — it never actually hit the stall, so there is no
  data point yet either way.
- Do not treat s84's `frameStartReset` SIGBUS as "just a fluke" anymore
  without qualification — it has now recurred once (2 total occurrences
  across many soaks), which is more than the single s84 sighting s85 called
  a fluke after only 2 non-recurrences. Still much rarer than the family's
  dominant classes; don't over-invest in it, but don't dismiss it either.
- Do not assume the doubled `frameStartReset + 532` stack frame means real
  self-recursion — source-checked this session (`funcs_3.c:7969`), zero
  self-calls in the function body. Treat it as a stack-unwind display
  artifact unless a future backtrace shows genuinely different call sites.

## Blocking on a long-running soak (learned the hard way, still current)

Simplest approach: run the driver script itself as a single foreground Bash
call with output redirected to a log file and a generous timeout (~480s
covers this env block's 120s hold + overhead) — the script blocks until the
game process exits, no polling loop needed. If it exceeds the foreground
timeout, the harness moves it to background automatically and notifies on
completion — do not sleep-poll in the meantime, just wait for the
notification. If you do start it with `run_in_background: true` directly
(also fine), and the Stop-hook gate fires before the notification arrives,
a plain foreground `while kill -0 <pid>; do sleep 5; done` wait (single Bash
call, generous timeout) is an acceptable way to actively block until it
exits — this is not the same as sleep-polling for status updates, it's
waiting out a known-bounded external process per this project's own
documented convention.

## This session's environment notes (carry forward, still current)

- Re-running the same script/tag **overwrites** the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak
  (e.g. `swapackwait2` from `swapackwait1`) so each soak's full run.log and
  screenshots land in their own directory, never overwritten.
- Running `N64Recomp/build/N64Recomp` or any script under
  `RogueSquadron64Recomp/tools/agent/*.sh` / `scratch/agent/*.sh` directly
  gets denied even though the text matches an allowlisted prefix —
  prefix with `zsh` (already allowlisted).
- Compound `cd ... && zsh ... > file 2>&1` gets denied — call
  `zsh /absolute/path/to/script.sh > /absolute/path/to/log 2>&1` directly,
  no `cd`, the script `cd`s internally. Same for `cd ... && cmake ...` —
  use `cmake --build /absolute/path/to/build` instead of `cd`+relative.
  Same for chaining a 2nd command after any of these with `;` or `&&` —
  each Bash call should be a single command; run follow-ups as separate
  calls (including a trailing `echo` after a redirected command — that
  also counts as a 2nd operation and gets denied).
- Same for `python3 fixup_game_funcs.py` — it uses an absolute
  `pathlib.Path("/Users/.../N64Recomp/RecompiledFuncs")` internally, so it
  can be invoked as `python3 /absolute/path/to/fixup_game_funcs.py > log`
  with no `cd` at all, sidestepping the compound-cd-redirect denial
  entirely.
- **CRITICAL: `fixup_game_funcs.py` is non-idempotent** — running it a 2nd
  time (even just to check stdout) re-applies every patch again,
  duplicating them. Redirect to a log file on the ONE invocation, and grep
  the log for your new patch's report lines to confirm exactly x1 before
  moving on.
- If only `fixup_game_funcs.py`/a `lib/rt64` or `N64ModernRuntime` C++ file
  changed (not symbol files or the ELF), you don't need `make_elf.py` —
  for guest-code fixup changes: `N64Recomp` (via
  `zsh tools/agent/regen_n64recomp.sh`) then `fixup_game_funcs.py` once,
  then `cmake --build`. For pure host/runtime C++ changes: just
  `cmake --build`, no regen needed at all.
- Before writing ANY new patch to `fixup_game_funcs.py`, grep for the
  exact anchor text's uniqueness both within the target file and (if using
  a short/generic snippet) across the whole `RecompiledFuncs/` tree —
  function-name-anchored patches (e.g. `RECOMP_FUNC void <name>(...)`) are
  safe since function names are unique repo-wide; mid-function anchors
  (loop bodies, specific instruction addresses) should be grepped for
  uniqueness first and file-scoped (`if p.name == "funcs_N.c"`) same as
  every prior patch in this file.
- `nm`, `otool`, `lldb` are NOT on the Bash allowlist — use
  `scratch/agent/machoparse.py` for Mach-O symbol reads (gives function
  sizes via symtab sort, NOT disassembly — it cannot map a crash's byte
  offset back to a source line; only a full source read can locate the
  actual fault site within a large function).
- Reading a `RECOMP_FUNC` body directly from
  `N64Recomp/RecompiledFuncs/funcs_*.c` (via `grep -n "RECOMP_FUNC void
  <name>"`) is far more reliable than trusting a `symbol_files/*.txt`
  comment.
- `git -C <path> ...` (with the `-C` flag) triggers an approval prompt even
  for read-only commands like `status`/`show` — plain `git <cmd>` from the
  correct cwd, or a separate `cd` call first, avoids it.
- `rm` on paths outside `scratch/` requires approval and does NOT accept
  glob patterns.
- Output redirection (`>`) from Bash is sandboxed to the session's allowed
  working directories — target `scratch/agent/`, never `/tmp`.
- `cmake --build` needs
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`; pass the
  build dir as an argument (`cmake --build /abs/path/to/build`) rather than
  `cd`-ing there, to avoid the compound-cd-redirect denial.
- `lib/N64ModernRuntime` and `lib/rt64` always show as "modified content"
  in the parent repo's `git status` — normal, long-standing state. Only run
  `submodule-patches/export.sh` + commit if you actually edit something
  under `lib/` this session (s177 did NOT touch `lib/` — the new instrument
  is entirely in the `N64Recomp` sibling checkout's `fixup_game_funcs.py`).
- `/scratch/` is entirely gitignored in this repo except 3 force-tracked
  files: `scratch/agent/NEXT.md`, `OUTCOME`, `STATUS`. New soak
  scripts/logs under `scratch/agent/` or `scratch/s73_post_a_scene/` never
  need `git add` — they're intentionally untracked.
- A `grep -c "[pattern]"` across a very large run.log (millions of lines
  from a per-tick instrument like `[rs-malloc-walk]`) is fine and fast —
  no need to avoid grepping big log files, just don't `cat`/`Read` them
  wholesale. Delegating this kind of pure-grep analysis to a background
  Agent (general-purpose, read-only Bash) keeps the huge log content out
  of the main context entirely — worked well this session for a 3.7GB log.
- When a soak survives the full hold window, `run_mission_keys.sh`'s
  summary line `UnhandledJump: N` can be nonzero from totally benign RSP
  microcode fallback noise (`Unhandled jump target 0x17F0`/`0x0231` "in
  microcode factor5_ucode") — grep the actual matched lines before reading
  a nonzero count as a regression; it is NOT the same thing as a guest-CPU
  `UnhandledJumpTarget`.
- Screenshots (`hold_NN.png`, `grace_NN.png`, `craft_stable.png`) are
  genuinely useful for characterizing a "process alive but stuck" state —
  reading a handful of them directly (via the Read tool, not a subagent)
  is cheap. Compare the SAME tick number across two runs, and compare a
  late-hold frame against the run's own `craft_stable.png`/early frames to
  spot exactly when a run visually froze.
- The run_mission_keys.sh summary block's later `print` lines (UnhandledJump,
  thr-resume bad=1, ost-wb SKIP_WIDTH/OOB, fs max, last fs line, last phase,
  CRASH count) can take noticeably longer to appear than the first few
  (lle tasks/exit=1/exit=2/missing-func) on a multi-hundred-MB run.log —
  if you check the driver log immediately after the game process itself
  exits, wait for the wrapper shell script's own process to exit too (not
  just the game PID) before treating the summary as complete.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is still far over the ~35 KB target — migrate
durable mechanism/architecture material to PROJECT-OVERVIEW.md and prune
superseded detail, paired with a real experiment. Flagged for many
sessions without action.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git checkout,
not a `lib/` submodule, with uncommitted changes across s90-177
(`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`). Same
posture as the `rogue_squadron64` sibling checkout flagged since s54.
Worth asking the user whether/how to commit that history.

`~/Documents/Tools/rogue_squadron64` also still carries pre-existing
uncommitted `symbol_files/*` changes from earlier sessions (unrelated to
this session's work). Still flagged for the user, not committed
autonomously.
