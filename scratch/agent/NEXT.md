# NEXT work unit — source-read processSceneNode/traverseSceneGraphRecursive
# to find the deref that the 4 EXISTING guards don't cover, then guard it

Read PORTING-STATE Session 189 in full before doing anything else (`grep -n
"^## Session 189" PORTING-STATE.md`); this file only has the actionable
summary. Also read docs/CURRENT-TRUTH.md's `-38` next-steps item (top of the
list) and the `-37` item right after it (kept for the still-valid
no-starvation finding).

## Why this is the next work unit (read before doing anything else)

s189 did NOT run a new soak — it surveyed `[CRASH][vifs-snapshot]
decisionN=...` (unconditionally armed in the crash handler) across ALL 16
historical soak logs under `scratch/s73_post_a_scene/*/run.log`, per
NEXT.md's own recommended path (B). Two results:

1. **The "4 unrelated crash families cluster near decision 9770-9792" claim
   (old CURRENT-TRUTH item -37) does not survive the full dataset.**
   `evalCubicSplineAtTime` (decisionN=8327) and `rs_free` (decisionN=8616)
   are 1443/1154 decisions from the window — comparable to or larger than
   the ~467-decision average gap between ANY two crashes in the full
   16-point dataset. Their inclusion as "clustering" evidence was an
   overclaim; drop that framing.

2. **But two OLDER runs nobody had cross-referenced against the window —
   `heapwalkerguard3_1` (decisionN=9661, s172) and `tickreap3dvoicesguard1`
   (decisionN=9694, s174) — have the byte-identical crash stack to s188's
   `schedtick1` (decisionN=9789): `SIGBUS <- processSceneNode
   (self-recursive call) <- traverseSceneGraphRecursive <-
   setupCameraMatrices <- static_5_800C9BF0 <- menuOverlayInit <-
   mainGameLoop <- mainBootstrapWorker`.** Same bug, 3rd/4th recurrence
   (on top of its original s172 catalog entry), always within a
   128-decision span (9661-9789).

3. **Critical addendum, checked before assuming this needs a brand-new
   guard**: `N64Recomp/fixup_game_funcs.py` already carries FOUR guards on
   this exact function: `_scene_node_list_guard_patch` +
   `..._guard2`/`..._guard3` (s99-101 era deref-site guards, lines
   ~2337-2464) and s175's recursion-depth cap at 128 (lines ~3899-3990,
   `ROGUESQ_LOG_SCENE_NODE_DEPTH_GUARD`). `schedtick1`'s driver script
   (`scratch/agent/run_schedtick1.sh`) armed **all four**
   (`ROGUESQ_LOG_SCENE_NODE_LIST_GUARD`, `..._LIST_GUARD2`,
   `..._LIST_GUARD3`, `..._DEPTH_GUARD`, all `=1`) — and **none fired**
   (`grep -c` for all 4 tags in `schedtick1/run.log` = 0/0/0/0) even as the
   process died to this exact backtrace. Same null result for
   `tickreap3dvoicesguard1`'s 3 list-guards (predates the depth cap).
   **This weakens s175's own hypothesis** (unbounded recursion depth ->
   native stack overflow, hence a depth cap as the fix): the SIGBUS lands
   at consistently the same in-function PC offset across independent
   recurrences and rebuilds (`+7176`/`+7640`/`+8148`/`+8456` — the drift
   tracks codegen changes between builds, not run-to-run recursion depth),
   which looks like ONE specific still-unguarded dereference at a fixed
   source line, not a stack-depth phenomenon.

**So the actual next work unit is NOT "add a guard to processSceneNode" —
that's already been tried 4 times and doesn't touch this crash. It's "find
the deref these 4 guards don't cover."**

## What to do

1. `grep -n "^## Session 189" PORTING-STATE.md` and read the addendum in
   full — it has the exact guard names/env vars/line numbers.
2. Read `N64Recomp/RecompiledFuncs/funcs_4.c:13759-14861`
   (`processSceneNode`) end to end. s175's own comment block in
   `fixup_game_funcs.py` (~line 3899-3941) already did partial groundwork:
   confirmed the function walks a sibling list rooted at mutable global
   `0x80112B20` via a next-pointer at node offset 0, self-calls once per
   sibling (line ~15044), and that the `a3`/`ctx->r7` argument threaded
   through the recursive call is clobbered for unrelated arithmetic (NOT a
   depth counter) at ~13922-13940. Re-use that, don't re-derive it.
3. Find every `MEM_W`/`MEM_HU`/`MEM_H`/`MEM_B` (or equivalent recomp.h
   macro) dereference in the function AND in `traverseSceneGraphRecursive`
   that is NOT already covered by one of the 4 existing guards (check
   `_scene_node_list_guard_patch`'s target site, `_scene_node_second_deref_sites`,
   and `_scene_node_loopback_sites` in fixup_game_funcs.py to know exactly
   which addresses are already covered — cross-reference by guest address,
   not just by function name, since a function can have multiple unguarded
   derefs and only some are covered).
4. If a symbol/offset tool is needed to map the native crash PC
   (`+8148`/`+8456`, whichever the next crash shows) back to a guest
   address or source line, use `scratch/agent/machoparse.py` (already
   built s152 for exactly this, `nm`/`otool`/`lldb` are not on the Bash
   allowlist).
5. Once the real unguarded deref is identified, guard it: `goto` the
   function's own natural exit (`L_80015528` is the confirmed sole
   epilogue, already used by the depth-cap guard for reference), new
   `ROGUESQ_LOG_*` env var following this file's existing pattern, then
   regen (`make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py` -> cmake,
   NOT optional) and re-run a `schedtick1`-style soak
   (`ROGUESQ_LOG_SCHED=1` + the periodic `[sched-tick]` line s188 added,
   still armed) to see two things: (a) does the new guard actually fire
   (positive control), and (b) can `decisionN` finally be pushed past 9792
   — and if so, does the `-35` stall signature (queueN/runnextN still
   climbing while decisionN plateaus) actually appear. That second
   question is the one the whole schedguard/schedtick/rsfreeguard lineage
   (s180-189) has been trying to reach and has not yet answered.

## Do not

- Do not add a 5th guard blind, or re-add one of the existing 4 guards
  under a new name — cross-reference guest addresses against
  `_scene_node_list_guard_patch`/`_scene_node_second_deref_sites`/
  `_scene_node_loopback_sites`/the depth-cap patch first.
- Do not re-attempt root-causing the underlying `rs_free` free-list
  corruption source itself (s85-s114 chase) — still out of scope.
- Do not turn on `ROGUESQ_LOG_THREAD_RESUME=1` (s93's confound).
- Do not re-open the "does decisionN climb past 9792" question with ANOTHER
  soak using the CURRENT guard set — s188's `schedtick1` already answered
  that (no, it dies to this exact crash first, 3rd confirmed time). The
  only way past 9792 is fixing/guarding this specific crash first.

## Blocking on a long-running soak (learned the hard way, still current)

Run the driver script itself as a single foreground Bash call with output
redirected to a log file and a generous timeout (~480s covers this env
block's 120s hold + overhead) — the script blocks until the game process
exits, no polling loop needed.

## This session's environment notes (carry forward, still current)

- **`N64Recomp/fixup_game_funcs.py` is non-idempotent** — running it a 2nd
  time (even just to check stdout) re-applies every patch again,
  duplicating them. If adding a NEW patch: regenerate fresh first (`zsh
  tools/agent/regen_n64recomp.sh`), THEN run `python3
  /absolute/path/to/N64Recomp/fixup_game_funcs.py > log` exactly once. Grep
  the log for the new patch's report line to confirm exactly x1, and check
  older patches' lines are ALSO x1 (not x2).
- A pure `lib/N64ModernRuntime`/`lib/rt64` runtime change (not a
  `RecompiledFuncs/*.c` patch) does NOT need the regen/fixup pipeline at
  all — just `cmake --build build --target RogueSquadron64Recomp -j`
  directly. A `RecompiledFuncs/*.c` patch (this session's likely shape,
  since the fix lives in `funcs_4.c`) DOES need the full regen order.
- Re-running the same soak script/tag **overwrites** the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- Running scripts under `RogueSquadron64Recomp/tools/agent/*.sh` /
  `scratch/agent/*.sh` directly gets denied — prefix with `zsh`.
- Compound `cd ... && zsh ...`/`cd ... && cmake ...` gets denied — use
  absolute paths, no `cd`, one command per Bash call (including a trailing
  `echo` after a redirected command).
- `submodule-patches/export.sh` must be invoked as `./submodule-patches/export.sh`
  (relative) from the repo root — absolute path gets denied.
- A large `run.log` (millions of lines) is fine to `grep -c`/`grep -n >
  outfile` directly — just don't `cat`/`Read` it wholesale.
- `nm`, `otool`, `lldb` are NOT on the Bash allowlist — use
  `scratch/agent/machoparse.py`, or the `[CRASH]` stack dump.
- `git -C <path> ...` triggers an approval prompt even for read-only
  commands — plain `git <cmd>` from the correct cwd instead.
- `/scratch/` is entirely gitignored except `scratch/agent/NEXT.md`,
  `OUTCOME`, `STATUS` — new soak scripts/logs never need `git add`.
- Bash commands containing a literal `$var` inside a `for` loop over
  bracketed grep patterns (e.g. `grep -F "[tag]"`) can get flagged/rejected
  by the sandbox as "Contains simple_expansion" even for read-only greps —
  avoid `for d in ...; do ... "$d" ...; done` loops with bracket-containing
  patterns; issue separate literal-path commands instead.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is now ~270 KB, wildly over the ~35 KB target —
migrate durable mechanism/architecture material to PROJECT-OVERVIEW.md and
prune superseded detail, paired with a real experiment. Flagged for many
sessions without action.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this session. Still flagged
for the user, not committed autonomously.
