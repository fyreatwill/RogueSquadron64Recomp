# NEXT work unit (s1110)

HYPOTHESIS-ID: submit-phase-recovery

Recover the VI-1024 launch phase with the smallest recipe change, then stop
after one capture. Keep the s1109 generated-store and submit-boundary probes;
remove only `ROGUESQ_LOG_ALL=1` first, retaining all targeted controls.

Competing hypotheses:

* H-log-overhead: broad logging is slowing or perturbing the transition; the
  targeted-only recipe reaches VI 1024 and passes the E9 controls.
* H-input-route: the s1109 key schedule leaves the game on the width-640
  route; the targeted-only recipe still misses 1024, so a later recipe change
  must alter input timing/route.
* H-transient-state: neither targeted-only result reaches 1024, despite a
  positive store control, so the launch failure is nondeterministic or an
  external state issue rather than writer attribution.

Discriminator: VI width 1024 plus the four E9 provenance controls in the same
run. Reaching 1024 selects H-log-overhead; stopping at 640 with controls
positive selects H-input-route/H-transient-state and requires the next bounded
recipe audit. No A0 writer null is admissible without the phase control.

Exact command:

```sh
env PROBE_KEYS='6 11 16 21 26 31 36 41 46 51 56' ROGUESQ_LOG_SLOT_SP_GUARD=1 ROGUESQ_LOG_SUBMIT_BOUNDARY=1 ROGUESQ_LOG_SUBMIT_GATE_STORES=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/submit_boundary_writer_s1110 60 1.0
```

Check `run.log` for `vi_width=1024`, all four E9 controls, and
`phys=0x11A8A0`; kill any orphaned game with SIGKILL.
