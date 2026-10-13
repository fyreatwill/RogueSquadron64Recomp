# Next work unit — phase-gate the 0x2C route-selection input

HYPOTHESIS-ID: ovl2c-real-splice

The boot-relative long key-mash arm crashed in the scheduler before phase
entry, while the direct driver reached only hangar origin `0x006AB400`. Use
the same key sequence phase-relative to the hangar VI 512 control, so input
does not perturb boot, with one run at `ROGUESQ_OVL2C_DROP=0`,
`ROGUESQ_DLWALK=1`, `ROGUESQ_LOG_E9_PROVENANCE=1`,
`ROGUESQ_LOG_TASKSUBMIT=1`, and `ROGUESQ_LOG_PHASE=1`. Run from `build/`,
SIGKILL cleanup, and classify only a later VI 512 origin `0x00690400`; do not
rebuild unless the binary is missing. The concrete arm is
`PROBE_PHASE_WIDTH=512 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1` with the
existing 6-second Start / 9-second A cadence from `s4751_run.sh`.

Competing hypotheses and discriminator:

- Hphase: the boot-time crash was input timing; hangar-gated keys reach mission
  and emit `res=0x2C`.
- Habsent: the gated route also has zero `res=0x2C`; the route still does not
  exercise the overlay and splice correctness remains unevaluable.
- Hbad: a gated 0x2C marker is followed by a crash or DL runaway, selecting an
  ABI/image integration defect over a content comparison.

DISCRIMINATING MEASUREMENT: one hangar-gated run with batched route/task/DL
logs. Reaching mission origin with `res=0x2C` splits Hphase from Habsent;
crash/runaway after a 0x2C marker splits Hbad from a usable splice route. The
s4759 direct-driver result is the positive control, not an answer to this
discriminator.
