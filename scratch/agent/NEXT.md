# NEXT work unit (s1111)

HYPOTHESIS-ID: submit-phase-recovery

Recover the VI-1024 launch phase with one bounded recipe change, then stop
after one capture. Keep the s1110 generated-store and submit-boundary probes;
compare the prior successful s1106 launch shape and change only its input
schedule/cadence while retaining all targeted controls.

Competing hypotheses:

* H-input-route: the s1110 key schedule leaves the game on the width-640
  route; the s1106 launch shape reaches 1024 with the same probes.
* H-transient-state: the s1106-shaped recipe still misses 1024 despite
  positive controls, so the launch failure is nondeterministic or external.
* H-probe-perturbation: the targeted instrumentation itself changes the
  route; the same recipe reaches 1024 only when the submit-boundary probe is
  removed.

Discriminator: VI width 1024 plus the four E9 provenance controls in the same
run. Reaching 1024 with the s1106-shaped schedule selects H-input-route;
stopping at 640 with controls positive selects H-transient-state. No A0
writer null is admissible without the phase control.

Exact command: recover the s1106 key/cadence values from its run recipe, then
run exactly one command of this form with only `PROBE_KEYS`/cadence changed:

```sh
env PROBE_KEYS='<s1106 keys>' ROGUESQ_LOG_SLOT_SP_GUARD=1 ROGUESQ_LOG_SUBMIT_BOUNDARY=1 ROGUESQ_LOG_SUBMIT_GATE_STORES=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/submit_boundary_writer_s1111 60 <s1106 cadence>
```

Before running, grep the s1106 recipe/log metadata to replace both
placeholders; do not use a stopwatch or cross-run animation comparison.
Check `run.log` for `vi_width=1024`, all four E9 controls, and
`phys=0x11A8A0`; kill any orphaned game with SIGKILL.
