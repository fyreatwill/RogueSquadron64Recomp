# NEXT: G3c(a) four-arm mission edge table
HYPOTHESIS-ID: g3c-edge-fade-phase-c6390

The widescreen route gate is now validated. Run one bounded four-arm table
(retail, draw-distance=2, aspect 16:9, and combined) from the same build, with
framebuffer dumps and the mission-phase gate fixed per route. Do not score
title, hangar, or transition captures.

Competing hypotheses:

- H-edge-fog: draw-distance exposes a terrain boundary because haze/fog start
  and end remain at retail distances; dd2 and combined have excess edge pixels,
  while retail and aspect-only remain near their controls.
- H-edge-grid: the terrain cell footprint itself is the exposed boundary;
  dd2 and combined show the same blocky edge independent of aspect, with a
  stable geometric edge score and no corresponding fog-ramp evidence.
- H-edge-aspect: widening the frustum exposes a side edge; aspect-only and
  combined increase edge excess relative to their same-dd controls, while
  retail and dd2 do not.

DISCRIMINATING MEASUREMENT: compare `tools/g3c_edge_score.py` on mission-phase
framebuffer dumps from all four arms, using 0x00690400 as `MISSION_RE` for
retail/dd2 and 0x00639238 as `MISSION_RE` for aspect/combined. The positive
control is the harness `fbrun-control OK` plus a reached mission origin and
nonzero terrain score in every arm. A result is selectable only if the four
arms reach their expected origin and hold with zero VI stalls/crash markers;
otherwise fix the gate/route before interpreting pixels.

Exact commands (run concurrently, `ROGUESQ_NO_PKILL=1`):

    env ROGUESQ_NO_PKILL=1 ROGUESQ_G1B=1 LEVEL=1 TITLE_ORIGIN=0x00790400 MISSION_RE=690400 TAG_SUFFIX=_s6390_retail HOLD_S=180 XENV_EXTRA='' zsh scratch/agent/g1_level_coverage_common.zsh > scratch/agent/s6390_edge_retail.out 2>&1
    env ROGUESQ_NO_PKILL=1 ROGUESQ_G1B=1 LEVEL=1 TITLE_ORIGIN=0x00790400 MISSION_RE=690400 TAG_SUFFIX=_s6390_dd2 HOLD_S=180 XENV_EXTRA='ROGUESQ_DRAW_DISTANCE=2' zsh scratch/agent/g1_level_coverage_common.zsh > scratch/agent/s6390_edge_dd2.out 2>&1
    env ROGUESQ_NO_PKILL=1 ROGUESQ_G1B=1 LEVEL=1 TITLE_ORIGIN=0x00639238 MISSION_RE=639238 TAG_SUFFIX=_s6390_edge_aspect HOLD_S=180 XENV_EXTRA='ROGUESQ_ASPECT=16:9' zsh scratch/agent/g1_level_coverage_common.zsh > scratch/agent/s6390_edge_aspect.out 2>&1
    env ROGUESQ_NO_PKILL=1 ROGUESQ_G1B=1 LEVEL=1 TITLE_ORIGIN=0x00639238 MISSION_RE=639238 TAG_SUFFIX=_s6390_edge_combined HOLD_S=180 XENV_EXTRA='ROGUESQ_ASPECT=16:9 ROGUESQ_DRAW_DISTANCE=2' zsh scratch/agent/g1_level_coverage_common.zsh > scratch/agent/s6390_edge_combined.out 2>&1

After all four finish, inspect only each `summary`, `[phase] vi_width=` rows,
and mission-phase dumps; score each dump directory with:

    python3 tools/g3c_edge_score.py scratch/agent/m6/g1_lvl1_s6390_<arm>/fbd

If all four gates pass, the next session may interpret the arm table and
produce owner-viewable before/after frames. If any gate fails, report the
route datum and do not infer a visual cause.
