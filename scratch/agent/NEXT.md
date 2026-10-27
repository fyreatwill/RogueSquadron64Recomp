# NEXT: G3c(a) widescreen mission-phase census
HYPOTHESIS-ID: g3c-edge-fade-phase-c6389

The s6389 edge comparison was not interpretable for widescreen: its corrected
arms reached the 796-wide title/hangar phase but never reached mission origin.
Do one bounded route-validation unit before collecting another edge table.

Competing hypotheses:

- H-aspect-route-gate: the widescreen route reaches mission but uses a
  different mission origin; updating `MISSION_RE`/the phase gate will expose
  the same flight route and make the edge comparison valid.
- H-aspect-route: the aspect arm changes a game-side transition or allocation
  and genuinely fails before mission; the origin sequence will stop before any
  mission-equivalent phase even with the correct title gate.
- H-harness-arm: the route is live but the autopilot schedule is consumed at a
  different phase; a phase-relative schedule or the observed origin sequence
  will distinguish this from an aspect runtime failure.

DISCRIMINATING MEASUREMENT: one retail control and one `ROGUESQ_ASPECT=16:9`
run, both with `ROGUESQ_LOG_PHASE=1`, recording the complete VI origin/width
sequence and whether a stable mission-origin phase is reached. Positive control
is the retail sequence ending at `0x00690400` plus a 120-second hold with zero
VI stalls. H-aspect-route-gate predicts a stable widescreen mission origin and
clean hold after correcting the gate; H-aspect-route predicts no mission
origin; H-harness-arm predicts mission origin after moving the key schedule to
the observed widescreen phase. Do not score edge pixels until this gate passes.

Exact commands after the build is current:

    env LEVEL=1 TITLE_ORIGIN=0x00639238 TAG_SUFFIX=_s6390_aspect HOLD_S=120 XENV_EXTRA='ROGUESQ_ASPECT=16:9' zsh scratch/agent/g1_level_coverage_common.zsh
    env LEVEL=1 TAG_SUFFIX=_s6390_retail HOLD_S=120 XENV_EXTRA='' zsh scratch/agent/g1_level_coverage_common.zsh

Inspect only `[phase] vi_width=... origin=...`, `keys.log`, and the summary;
use SIGKILL for cleanup. If aspect reaches mission, the following unit must
rerun the four-arm edge table with that mission origin as the phase gate.
