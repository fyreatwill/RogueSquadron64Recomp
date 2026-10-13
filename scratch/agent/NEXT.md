# Next work unit

HYPOTHESIS-ID: mission-phase-correctness

Work unit: obtain an unpaused mission-frame capture after fixup 24, using one
direct game process and a phase-gated VI control. The s4752 repeated-key recipe
paused the scene before the ship/HUD comparison.

Before building anything, retain these competing hypotheses and discriminator:

- H1: absent ship/HUD is entirely the dropped 0x2C billboard-sprite work.
- H2: terrain ribbons or other non-0x2C geometry remain independently wrong.
- H3: the capture is not in the mission phase.

DISCRIMINATING MEASUREMENT: launch the rebuilt binary once, send the existing
s4724 key schedule only through the mission-launch edge (stop before the next
Start press), wait for and log VI origin `0x00690400` at width 512, then capture
several unpaused frames. H1 predicts terrain/sky without ship/HUD and stable
0x2C-drop activity; H2 predicts an additional terrain/non-sprite divergence;
H3 predicts no `0x00690400` phase. Positive controls are the VI-512 transition,
mission origin, and no-crash log. Do not add runaway counters or use the
duplicating `tools/probe.sh` wrapper; use the direct one-process driver from
s4752, with SIGKILL cleanup.

Exact starting command shape:
`env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1 ./build/RogueSquadron64Recomp`
Drive Start at 6,12,18,24,30,36,42 seconds and A at 9,15,21,27,33,39,45
seconds, then stop input; phase-gate on the log line containing
`vi_width=512` and `origin=0x00690400` before capturing.
