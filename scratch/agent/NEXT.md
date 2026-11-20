# NEXT (s7681)
HYPOTHESIS-ID: g6c-shield-hide-condition

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
s7680: the s7679 near release is inert in flight (L5 default 0 releases, control NEAR=99 4, tools/s7680_flight_release.zsh).
What is left is cosmetic and attract-only: L5 attract item sub 0x32 ("shield") is spawned at depth 38 and never calls
addNpcToVisibilityBucket, so the held stand-in still shows from depth 38 down to the 15 cut.
Work unit (offline first, at most ONE run): read the sub 0x32 handler (0x8003D518, RecompiledFuncs / ROM disassembly) and name
the condition that skips its addNpcToVisibilityBucket call (a hidden/flash flag, a timer, a parent link, or a cinematic mask).
Hypotheses: H-flag (a state byte/bit in the object says "do not draw": read it in the stand-in hold and exclude while it is set),
H-parent (shield draws only through its parent craft, so it never gets its own bucket call: exclude 0x32 from holds entirely),
H-depth (no signal exists: keep the 15 cut, close). Discriminator: log the named field for the shield item vs ordinary items on
the s7678 attract route (tools/s7678_attract_run.zsh, deterministic); a field that is constant on the shield and different on
every item that draws selects H-flag/H-parent. Fix behind the existing STANDINS (old = ROGUESQ_S7681_*=0), rescore with
tools/s7675_ghost_score.py (shield must become UNHELD or RELEASED at spawn, all other handoffs identical).
If H-depth, close G6c engineering; G6c then waits on the owner's look. Next rung: owner items (backlog 2-9, 20, 22).
One game at a time, SIGKILL only, <=2 CPU-heavy jobs, no repeat-hold soaks.
