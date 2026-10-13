# Next work unit — identify the 0x2C-producing route

HYPOTHESIS-ID: ovl2c-real-splice

The repaired binary is already built and the s4753 direct driver reached the
positive control, but its batched provenance log recorded zero `res=0x2C`
dispatches. Use the existing long key-mash arm in
`scratch/agent/s4751_run.sh` as the route-selection experiment, with one run
at `ROGUESQ_OVL2C_DROP=0`, `ROGUESQ_DLWALK=1`,
`ROGUESQ_LOG_E9_PROVENANCE=1`, `ROGUESQ_LOG_TASKSUBMIT=1`, and
`ROGUESQ_LOG_PHASE=1`. Run from `build/`, SIGKILL cleanup, and phase-gate the
summary on VI 512 origin `0x00690400`; do not rebuild unless the binary is
missing.

Competing hypotheses and discriminator:

- Hroute: the long key-mash reaches the DMEM `0x153==0x2C` task that the
  direct driver missed; it predicts at least one `res=0x2C` marker and a
  phase-7 task record.
- Habsent: the route also has zero `res=0x2C`; this rules out the input arm as
  the needed discriminator but says nothing about splice correctness.
- Hbad: a 0x2C marker is followed by a crash or DL runaway, selecting an ABI/
  image integration defect over a content comparison.

DISCRIMINATING MEASUREMENT: one run with the long key-mash arm and batched
route/task/DL logs. `res=0x2C` present vs absent splits Hroute from Habsent;
if present, runaway/crash vs bounded completion splits Hbad from a usable
splice route. The s4759 direct-driver result is the positive control, not an
answer to this next discriminator.
