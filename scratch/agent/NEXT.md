# NEXT work unit — decide: push decisionN past #9792 with a 2nd/3rd
# schedtick soak, OR step back from crash-site-chasing and ask what game/
# mission state clusters around decision ~9770-9792

Read PORTING-STATE Session 188 in full before doing anything else (`grep -n
"^## Session 188" PORTING-STATE.md`); this file only has the actionable
summary. Also read docs/CURRENT-TRUTH.md's `-37` next-steps item (top of the
list).

## Why this is the next work unit (read before doing anything else)

s188 added the `[sched-tick]` periodic decisionN/queueN/runnextN readout
NEXT.md called for last session (`lib/N64ModernRuntime`
`scheduling.cpp`/`threads.cpp`, exported+committed). One soak
(`schedtick1`, same env block as s187's crash-free `rsfreeguard1`) got real
data: `decisionN`/`queueN`/`runnextN` all climbed in clean lockstep the
ENTIRE run, no plateau, no growing gap — the 3rd straight soak (after s184,
s185) with zero scheduler-starvation signature. But it never got PAST
decision 9792, because a different, already-catalogued crash
(`processSceneNode` self-recursion SIGBUS, s172 lineage) killed it at
decision **#9789** — dead center in the historical `#9770`-`#9792`
stall-onset window, NOT the `rs_free` family s187's guard defused (that
guard's own diagnostics are clean/unfired in this run's tail).

This is now the 4th unrelated crash family (`evalCubicSplineAtTime` s184 @
8327, `rs_free` s185/186 @ 8616, `processSceneNode` s188 @ 9789) to die at
or just before this same narrow decision window across different guard
configurations. That clustering is a candidate signal, not yet a finding —
one data point per site. Two honest paths forward, both legitimate; pick
based on budget appetite:

**(A) Keep pushing the rule-8 budget (1 of 3 spent):** land a
`processSceneNode` self-recursion guard (bigger unit than s188's log-line
add — needs a source read of the recursion first, see CURRENT-TRUTH ~line
1703, 1724, 1735, 1765, 1809 for prior source-read findings on this exact
function) and re-run `schedtick1`-style soaks to see if `decisionN` can be
pushed past 9792 at all, and if so whether it plateaus (the actual `-35`
stall signature: queueN/runnextN still incrementing while decisionN stalls)
or keeps climbing clean.

**(B) Step back from one-crash-at-a-time chasing:** ask what changes in
game/mission state around decision ~9770-9792 that would make FOUR
unrelated code paths (spline eval, free-list walk, scene-node recursion,
whatever the 4th stall-onset instance if any) all likelier to fault around
there. This is a genuinely new hypothesis, not yet considered in the
`schedcaller`/`schedguard`/`rsfreeguard`/`schedtick` lineage — needs its own
discriminating test (e.g., what game asset/scene loads around update_screen
#9700-9800 judging by the `[vi]`/`[phase]` lines already in every run.log;
`rdpFs` value at that point across runs) before entering CURRENT-TRUTH as
more than a hypothesis.

Recommend (B) first since it's cheap (log-grepping existing soak data, no
new build) and could redirect (A)'s guard-writing effort more precisely if
it finds a common trigger; but either is a legitimate work unit.

## Do not

- Do not re-attempt root-causing the underlying `rs_free` free-list
  corruption source itself (s85-s114 chase) — still out of scope.
- Do not turn on `ROGUESQ_LOG_THREAD_RESUME=1` (s93's confound).
- Do not spend more than 2 more consecutive soaks on the "does decisionN
  climb past 9792" question (rule 8: 1 of 3 already spent) without a
  discriminating result — if so, park it, write up the hypothesis/evidence
  table, and treat the decision-window clustering itself as the next thing
  to test instead.

## Blocking on a long-running soak (learned the hard way, still current)

Run the driver script itself as a single foreground Bash call with output
redirected to a log file and a generous timeout (~480s covers this env
block's 120s hold + overhead) — the script blocks until the game process
exits, no polling loop needed. s188 confirmed this works cleanly end-to-end
in one Bash call when the run ends within the timeout (this soak ended at
wall=52s due to the early crash). If a soak DOES run the full 120s+grace and
risks exceeding 480s, see prior sessions' notes on backgrounding + a second
foreground wait-loop call.

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
  directly (confirmed s188: only the touched .cpp files recompiled, rt64
  untouched/not rebuilt, clean relink). Still needs
  `./submodule-patches/export.sh` + commit since it's under `lib/`.
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
  outfile` directly — just don't `cat`/`Read` it wholesale. Extract to a
  small file under `scratch/agent/`, then `Read` that.
- `nm`, `otool`, `lldb` are NOT on the Bash allowlist — use
  `scratch/agent/machoparse.py`, or just the `[CRASH]` stack dump (usually
  enough to identify the function).
- `git -C <path> ...` triggers an approval prompt even for read-only
  commands — plain `git <cmd>` from the correct cwd instead.
- `/scratch/` is entirely gitignored except `scratch/agent/NEXT.md`,
  `OUTCOME`, `STATUS` — new soak scripts/logs never need `git add`.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is now well over 100 KB (grown further this
session), wildly over the ~35 KB target — migrate durable
mechanism/architecture material to PROJECT-OVERVIEW.md and prune superseded
detail, paired with a real experiment. Flagged for many sessions without
action.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this session. Still flagged
for the user, not committed autonomously.
