# NEXT: s6794 "not checked" - EXACT_EDGES fan on hangar/menus (seams) + its tri/frame-time overhead (G3 cinematic follow-up)
HYPOTHESIS-ID: g3-cinematic-sweep

State: s6794 exact-edge fan (ROGUESQ_EXACT_EDGES default on, =tog alternates off/on per 1 s epoch, on = odd second, logs
[exactedges]) fixed the AT THE MOVIES x=318 seam. s6796 showed it leaves the cw-1 right-edge column alone (H-same).
s6794 never checked the hangar/menus, nor the cost of emitting up to 6-vertex fans instead of 3-vertex tris.

Hypotheses:
- H-clean: hangar/menus show no seam change, frame time unchanged (fan cost negligible) -> close the exact-edge thread.
- H-improve: hangar/menus had shared-edge seams (lit 1 px lines inside flat fills) that vanish in on seconds.
- H-regress: on seconds add artefacts (slivers/overdraw lines at fan edges) or cost >5% host frame time.
Discriminator, ONE run: scratch/s6731/menus.sh route (title -> menus -> hangar SELECT YOUR CRAFT/LEVEL), copy it to
scratch/s6797/ with the s6796 timestamped cap() (times.txt "<n> <t0> <t1>" via zsh $EPOCHREALTIME) and
"ROGUESQ_EXACT_EDGES=tog". Score: per capture, count interior 1 px columns/rows whose colour differs from both neighbours
by >40 inside otherwise flat regions, split by arm (tools/g3_edge_tog_split.py's time filter). Frame cost: G1b per-VI
frame-time instrument split by [exactedges] epochs from run.log.
Positive control: the AT THE MOVIES seam detector must flag the x=318 line in off seconds (s6793/s6794 recipe) if the
detector is reused; otherwise inject a synthetic 1 px line into one capture and confirm the scorer counts it.
Outcomes: on == off and cost <5% -> H-clean, close; fewer lines on -> H-improve; more lines or cost -> H-regress (fix or gate).
