# RESUME — next work unit: make mission entry deterministic (stop mashing keys)

HYPOTHESIS-ID: factor5-overlay-0x2c-splice

s4774: 0/4 drivers (probe.sh phase-gated, s4753 winctl x2) reached mission origin 0x00690400 on the spliced
binary; all stopped at hangar 0x006AB400 with res=0x2C=0. Wall-clock Start/A mashing is not a route.

Hypotheses:
- Hroute-timing: mission entry needs a hangar-state-gated press (react to hangar origin, then press once, observe).
- Hroute-splice: the splice changes hangar->mission flow (weak: s4759 reached mission once while spliced).
- Hroute-menu: needs a specific menu selection (right/down), not Start/A only.

DISCRIMINATOR: once VI-512 hangar origin is logged, send ONE key per 4 s with a screenshot after each and read the
screens to learn the menu state; then script the true sequence. Alternative: grep for the hangar->mission transition
in code and force it with a debug env. Do not recompile; do not repeat mashing.
