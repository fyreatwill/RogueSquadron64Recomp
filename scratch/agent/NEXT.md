# NEXT work unit (s1109)

HYPOTHESIS-ID: submit-producer-boundary

The s1108 generated-store probe is landed and builds. Its A89F positive rows
prove the effective-address calculation and identify generated SP-loop stores,
but both captures were invalid for the planned discriminator: one remained at
VI width 320 and the Start-assisted retry stopped at width 640. No A0 row was
seen. Do one capture only: reach VI width 1024 first, then classify whether a
generated store covering physical `0x11A8A0` precedes a same-phase SP send.

Competing hypotheses:

* H-generated-writer: an instrumented generated store covers `0x11A8A0` and
  precedes a same-phase SP send.
* H-nongenerated-writer: VI/E9 controls are positive, repeated nonzero A0
  submit values remain, and no generated A0 writer row fires.
* H-observation-race: the capture does not reach VI 1024 or lacks aligned
  phase/order controls, so neither writer result is admissible.

Discriminator: VI width 1024 plus the existing E9 provenance controls and a
same-phase writer/submit ordering. A0 writer row selects H-generated-writer;
positive controls with zero A0 rows select H-nongenerated-writer; any missing
phase/E9 control is invalid and requires fixing the launch recipe.

Exact capture command (use a Start schedule only if needed to reach 1024;
do not change the probe or queue behavior):

```sh
env PROBE_KEYS='6 11 16 21 26 31 36 41 46 51 56' ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_SLOT_SP_GUARD=1 ROGUESQ_LOG_SUBMIT_BOUNDARY=1 ROGUESQ_LOG_SUBMIT_GATE_STORES=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/submit_boundary_writer_s1109 60 1.0
```

Check `run.log` for `vi_width=1024`, the four E9 controls, and
`phys=0x11A8A0`; kill any orphaned game with SIGKILL. If the recipe again
cannot reach 1024, record that as invalid and pivot to the smallest launch
recipe change that restores the phase control.
