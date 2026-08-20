# NEXT work unit (s2036)

HYPOTHESIS-ID: m5-c88-common-route-focus

## Work unit

Run one fresh unset-C88 route using the preflighted, width-relative
`tools/regress.sh` harness. Keep forced LLE, opt-in audio, and spin yield; do
not change a game writer or repeat the C88 value arm. Use a width-640-relative
eleven-Start schedule so the wrapper tests input after the observed route
enters VI 640, while `regress.sh` records Accessibility/window preflight.

## Competing hypotheses and discriminator

- **H1 — stale boot-relative schedule:** the phase-relative schedule reaches
  VI 1024 (and preferably VI 512) with live `s2006-svc` and reapply controls.
  The prior VI-640 result was a timing/route-wrapper artifact.
- **H2 — common port route failure:** preflight is valid, scheduled keys and
  post-640 `[host-start]` edges are live, and the service/reapply controls are
  live, but VI 1024 is still absent. The C88 value comparison remains closed.
- **H3 — GUI/input harness failure:** preflight is denied, or the scheduled
  width-relative keys produce no post-640 host Start edge. Do not interpret
  the VI result until the harness is repaired.

The discriminator is one table from `env.txt` and `run.log`: preflight input /
visual status, width-relative key rows, post-640 host Start edges, final VI
width, `s2006-svc` entry/exit count, and `reapplyDisplayMode` entry/exit count.
H1 requires the VI-1024 anchor; H2 requires all controls plus a 640-only
terminal route; H3 is selected by a missing preflight or input positive
control.

## Command

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp

env -u ROGUESQ_M5_C88_VALUE \
REGRESS_SECS=150 REGRESS_INTERVAL=0.6 \
REGRESS_KEYS='640@1:start 640@3:start 640@5:start 640@7:start 640@9:start 640@11:start 640@13:start 640@15:start 640@17:start 640@19:start 640@21:start' \
REGRESS_LABEL=s2036_c88_route \
ROGUESQ_LLE_FORCE=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 \
ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 \
ROGUESQ_LOG_PCM_SANITY=1 \
  zsh tools/regress.sh scratch/agent/s2036_c88_route 150 > scratch/agent/s2036_c88_route_driver.log 2>&1
```

Use only bounded `rg`, `grep -c`, `tail`, and `verdict.json` reads after the
run. If H2 is selected, keep C88 unset and design a new common-route probe;
do not repeat the same value A/B.
