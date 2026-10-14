# Next work unit (M5 task-contract boundary)

HYPOTHESIS-ID: m5-task-contract-boundary

WORK UNIT: qualify the phase-gated M5 task-contract boundary using the existing
task-contract logger, after s4854 found the port-load logger itself unreached.
Run one instrumented game with `ROGUESQ_LOG_M5_TASK_CONTRACT=1`,
`ROGUESQ_LOG_M5_TASK_LIFETIME=1`, `ROGUESQ_LOG_M5_ROUTE_ORDER=1`, PCM boundary
logging, and the established autopilot. Do not change runtime behavior.

Competing hypotheses:

* H-task-contract-legitimate: task-contract rows have coherent task identity,
  lifetime, and route/completion joins while all positive controls fire.
* H-task-contract-mismatch: task identity or lifetime fields disagree with
  route/completion payloads while all positive controls fire.
* H-task-contract-unreached: the task-contract controls are absent even though
  route/SP/PCM controls are positive.

DISCRIMINATING MEASUREMENT: in the same phase, require task-contract and
task-lifetime rows plus `sp-complete-enter/return`, action-dequeue, and
nonzero PCM source/consumer rows. Coherent task fields and matching route
metadata select H-task-contract-legitimate; a field/payload mismatch with all
controls positive selects H-task-contract-mismatch; absent task-contract rows
with positive controls select H-task-contract-unreached. A task row alone is
not a positive control.

Exact commands:

    zsh scratch/agent/run_s4855_task_contract.sh
    grep -aE '^\[(m5-task|m5-route-order|phase|pcm|CRASH|ABORT)' \
      scratch/agent/soak_results/s4855_task_contract/*.log | tail -300

Use the same title/hangar phase gates and SIGKILL watchdog as the prior recipe.
If the control is absent, do not infer a task-contract defect; record the exact
missing control and pivot.
