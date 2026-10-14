# Next work unit (M5 port-task-load contract boundary)

HYPOTHESIS-ID: m5-port-task-load-contract

WORK UNIT: qualify the broader phase-gated port-task-load contract on the
current real-image route. The exact descriptor target `0x800377C8` was absent
in s4853 despite positive route controls; do not repeat that target. Run one
instrumented game with `ROGUESQ_LOG_M5_PORT_LOAD=1`,
`ROGUESQ_LOG_M5_ROUTE_ORDER=1`, PCM boundary logging, and the established
autopilot. Do not change runtime behavior.

Competing hypotheses:

* H-port-load-legitimate: the task loaded at the port boundary has coherent
  fields and agrees with the route/completion contract.
* H-port-load-mismatch: the live port-task-load fields disagree with the
  route or completion payload while all positive controls fire.
* H-port-load-unreached: the broader port-task-load control is absent even
  though route/SP/PCM controls are positive.

DISCRIMINATING MEASUREMENT: in the same phase, require at least one
`m5-port-load` row plus `sp-complete-enter/return`, action-dequeue, and
nonzero PCM source/consumer rows. Coherent task fields and matching route
metadata select H-port-load-legitimate; a field/payload mismatch with all
controls positive selects H-port-load-mismatch; absent port-load rows with
positive controls select H-port-load-unreached. A port-load row alone is not a
positive control.

Exact commands:

    # Copy run_s4853_descriptor.sh to run_s4854_port_load.sh, replace the
    # descriptor env with ROGUESQ_LOG_M5_PORT_LOAD=1, and rename its OUT dir.
    zsh scratch/agent/run_s4854_port_load.sh
    grep -aE '^\[(m5-port|m5-route-order|phase|pcm|CRASH|ABORT)' \
      scratch/agent/soak_results/s4854_m5_port_load/*.log | tail -300

Use the same title/hangar phase gates and SIGKILL watchdog as the prior recipe.
If the control is absent, do not infer a task-contract defect; record the exact
missing control and pivot.
