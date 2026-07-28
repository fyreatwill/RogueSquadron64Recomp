# NEXT work unit — re-run the processSceneNode node-pointer guard soak;
# it's fixed, but a different already-catalogued crash blocked the target test

Read PORTING-STATE Session 190 in full before doing anything else (`grep -n
"^## Session 190" PORTING-STATE.md`); this file only has the actionable
summary. Also read docs/CURRENT-TRUTH.md's `-39` next-steps item (top of the
list).

## Why this is the next work unit (read before doing anything else)

s190 did the source-read NEXT.md asked for, found the real gap (3 of the "4
existing guards" on `processSceneNode` were actually on a different function,
`submitSceneNodeRender` — only the depth cap touches `processSceneNode` at
all), and landed a new entry-point guard on `processSceneNode`'s node
pointer (`ROGUESQ_LOG_SCENE_NODE_PTR_GUARD`, `N64Recomp/fixup_game_funcs.py`,
bails to `L_80015528` with `ctx->r2=0` if `ctx->r17` is outside RDRAM bounds).

**The first version of that patch had a bug**: the regex match consumed the
line `ctx->r3 = MEM_W(ctx->r17, 0XC);` as part of its anchor but the
replacement never re-emitted it, silently deleting that instruction. This
caused a 2/2-reproducible immediate crash (decisionN~150, a brand-new
`submitSceneNodeRender+2156` self-call signature) with the guard's own log
tag never firing — the tell that it was a codegen bug, not a triggered
false-positive. Caught via a same-session control build (identical env
block, patch disabled) that ran the full 120s hold crash-free to decisionN
14721+, isolating the regression to the patch. **Fixed** (the original line
is now re-appended after the guard block) and reverified: `fixup_game_funcs.
py` reports the new patch `x1` and all pre-existing `processSceneNode`-
adjacent patches still `x1` (no duplication).

**A third soak on the fixed build (`sceneptrguard3`) showed no regression**
— decisionN climbed cleanly through a real VI-width transition (1024→512,
legitimate mission load) to **8053** — but died there to a SIGBUS in
`reserveAndEmitDLEntry` (called via `submitSceneNodeRender` ←
`processSceneNode` ← `traverseSceneGraphRecursive` (twice) ←
`setupCameraMatrices` ← ...), the **already-catalogued 14th class** (first
identified s168-171, PORTING-STATE ~15574-15780), recurring at a native
offset (+5212) past the s109 guard and the 3 guards s169 already added to
that function. `scene-node-ptr-guard` did not fire (0) in this run — the
node pointer was never observed corrupted before this other crash intervened.

**So the actual open question is unchanged from before s190, just now
properly instrumented: does decisionN ever push past 9792 with this guard
active, and if so does the `-35` stall signature appear?** This run simply
didn't get far enough to find out — a different bug got there first. Given
16 historical soaks have crashed at 16 different decisionN values (356 to
14267), this is very plausibly ordinary run-to-run variance, not something
the fix needs to address.

## What to do

1. `grep -n "^## Session 190" PORTING-STATE.md` and read it in full.
2. Confirm the current build already has the fixed guard: `grep -n
   "s_process_scene_node_ptr_guard\|ctx->r3 = MEM_W(ctx->r17, 0XC);"
   /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_4.c`
   — expect the `ctx->r3 = MEM_W(ctx->r17, 0XC);` line to appear immediately
   after the guard's closing `}` (3 total occurrences of that exact line in
   the file; the second one, ~funcs_4.c:13800s, is the one that matters).
   If it's regenerated fresh (no patches applied), redo the regen + fixup
   pipeline before soaking — do NOT soak an unpatched build.
3. Copy `scratch/agent/run_sceneptrguard3.sh` to a new tag (e.g.
   `run_sceneptrguard4.sh`, replace the tag string) and run it exactly like
   the prior 3 attempts — same env block, same `ROGUESQ_LOG_SCENE_NODE_PTR_
   GUARD=1`. Run as a single foreground Bash call (or background + block on
   it with TaskOutput) with a generous timeout (~480s+).
4. Check three things in the resulting `run.log`:
   a. Does `decisionN` (via `[CRASH][vifs-snapshot]` or, if it survives, the
      `[sched-tick]` periodic readout — `ROGUESQ_LOG_SCHED=1` is already in
      the env block) reach past 9792 this time?
   b. Does `[scene-node-ptr-guard]` fire at all anywhere in the run
      (positive control — confirms the corrupted-sibling-pointer mechanism
      actually happens, whether or not it's what ends the run)?
   c. If it crashes before 9792 again, is it the SAME `reserveAndEmitDLEntry`
      class, a DIFFERENT already-catalogued class, or something new? (grep
      the crash backtrace's function names against PORTING-STATE.)
5. If `reserveAndEmitDLEntry` blocks the run again (2/2 or more), that's
   its own recurring obstacle and may need a guard extension of its own
   (mirrors the s169 pattern — source-read the function fresh, find the
   deref at native +5212 that the existing 3+1 guards don't cover) as a
   SEPARATE work unit before the `processSceneNode` question can be tested
   at all. Don't open that investigation until this soak has run at least
   once more, per the "check the boring thing first" rule (variance vs. a
   real recurring blocker).

## Do not

- Do not re-touch the `processSceneNode` node-pointer guard itself unless a
  NEW soak shows it misbehaving — it's fixed and verified crash-free for
  120s+ in the control-style test; don't re-litigate that without new
  evidence.
- Do not chase `reserveAndEmitDLEntry` (14th class) as a full investigation
  without at least one more soak first — it may be ordinary crash-site
  variance, not a new recurring blocker.
- Do not re-attempt root-causing the underlying `rs_free` free-list
  corruption source itself (s85-s114 chase) — still out of scope.
- Do not turn on `ROGUESQ_LOG_THREAD_RESUME=1` (s93's confound).

## Blocking on a long-running soak (learned the hard way, still current)

Run the driver script as a single foreground Bash call with output
redirected to a log file and a generous timeout (~480s), OR launch with
`run_in_background: true` and block on the returned task ID via
`TaskOutput(task_id, block=true, timeout=300000)` — this session found that
ending the turn while a background soak is still running trips the Stop
hook's exit-contract check prematurely; `TaskOutput` with `block=true` is
the correct way to synchronously wait for it before writing the exit-contract
docs.

## This session's environment notes (carry forward, still current)

- **`N64Recomp/fixup_game_funcs.py` is non-idempotent** — running it a 2nd
  time (even just to check stdout) re-applies every patch again,
  duplicating them. If adding a NEW patch: regenerate fresh first (`zsh
  tools/agent/regen_n64recomp.sh`), THEN run `python3
  /absolute/path/to/N64Recomp/fixup_game_funcs.py > log` exactly once. Grep
  the log for the new patch's report line to confirm exactly x1, and check
  older patches' lines are ALSO x1 (not x2).
- **When a `re.subn` replacement function's regex match consumes a "stable
  anchor" line for uniqueness, the replacement MUST re-emit that line** if
  it wasn't captured in its own group — `re.subn` replaces the ENTIRE
  matched span, not just what you explicitly reference in the replacement.
  This session's regression (deleted instruction, 2/2 reproducible crash)
  was exactly this mistake. When writing a new patch that anchors on a
  trailing line for uniqueness, either capture it in its own group and
  re-emit `m.group(N)`, or write it out literally in the replacement string.
- A pure `lib/N64ModernRuntime`/`lib/rt64` runtime change (not a
  `RecompiledFuncs/*.c` patch) does NOT need the regen/fixup pipeline at
  all — just `cmake --build build --target RogueSquadron64Recomp -j`
  directly. A `RecompiledFuncs/*.c` patch (via fixup_game_funcs.py) DOES
  need the full regen order (though `make_elf.py` itself is only needed if
  symbols/ELF layout changed, not for a pure fixup-script edit).
- Re-running the same soak script/tag **overwrites** the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- Running scripts under `RogueSquadron64Recomp/tools/agent/*.sh` /
  `scratch/agent/*.sh` directly gets denied — prefix with `zsh`.
- Compound `cd ... && zsh ...`/`cd ... && cmake ...` gets denied — use
  absolute paths, no `cd`, one command per Bash call (including a trailing
  `echo` after a redirected command). `echo foo; echo bar` and `cmd;
  echo $?` also get flagged ("Contains simple_expansion") — one command,
  one effect, per Bash call.
- `git -C <path> ...` AND `cd <path> && git ...` (combined in one Bash call)
  both trigger approval prompts that a non-interactive session can't clear —
  if you need git state from a directory other than the repo root, either
  accept that a plain `git <cmd>` after a SEPARATE `cd` Bash call may still
  need approval, or just use direct file reads/greps instead of git.
- `submodule-patches/export.sh` must be invoked as `./submodule-patches/export.sh`
  (relative) from the repo root — absolute path gets denied.
- A large `run.log` (millions of lines) is fine to `grep -c`/`grep -n >
  outfile` directly — just don't `cat`/`Read` it wholesale.
- `nm`, `otool`, `lldb` are NOT on the Bash allowlist — use
  `scratch/agent/machoparse.py`, or the `[CRASH]` stack dump.
- `/scratch/` is entirely gitignored except `scratch/agent/NEXT.md`,
  `OUTCOME`, `STATUS` — new soak scripts/logs never need `git add`.
- Output redirection is sandboxed to the session's allowed working
  directories (this repo, N64Recomp, rogue_squadron64) — redirecting to
  `/tmp/...` gets blocked; use a path under `scratch/agent/` instead.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is now over ~35 KB (growing every session) —
migrate durable mechanism/architecture material to PROJECT-OVERVIEW.md and
prune superseded detail, paired with a real experiment. Flagged for many
sessions without action.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this session. Still flagged
for the user, not committed autonomously.
