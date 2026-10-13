# RESUME — next work unit: qualify a mission-route driver for the compiled overlay-0x2C splice

HYPOTHESIS-ID: factor5-overlay-0x2c-splice

The s4773 build/run qualified the resident 0x2C image and reached VI 512, but
the existing s4753 key recipe stayed on hangar origin `0x006AB400`. It never
produced mission origin `0x00690400` or a direct `res=0x2C` row, so the splice
effect is still unevaluable. Do not repeat the same hangar-only recipe.

Competing hypotheses and discriminating measurement:

- H2C-real-image: on a mission-origin task, the compiled image supplies the
  missing `TexrectGen` implementation and removes the DL restart loop.
- H2C-route-unrelated: mission-origin tasks arrive, but the restart loop
  persists.
- H2C-output-neutral: the loop ends, but mission ship/HUD output is unchanged.
- H2C-route-absent: the new driver still cannot reach mission origin; the
  image effect remains unevaluable and the route recipe is the blocker.

DISCRIMINATING MEASUREMENT: one new phase-gated run must first show the
positive VI-512/mode control and then mission origin `0x00690400`; only after
that compare `res=0x2C`, 0xBD, overlay-arrival, DL-restart, and ship/HUD rows
against the already-spliced binary. Mission origin plus no restart selects
H2C-real-image; mission origin plus restart selects H2C-route-unrelated; a
clean loop with unchanged output selects H2C-output-neutral; no mission
origin selects H2C-route-absent.

Commands:

```sh
# Existing compiled/spliced source and binary are qualified; do not recompile.
# Start from the s4753 driver, changing only the input schedule/route trigger.
env PROBE_PHASE_WIDTH=1 PROBE_KEYS_FROM_PHASE=1 zsh scratch/agent/<new-mission-route-driver>.sh
```

Do not change callback deregistration or add a shutdown mitigation. If the
compiler remains blocked, write BLOCKED.md with the exact denied command and
the one allow-rule change needed.
