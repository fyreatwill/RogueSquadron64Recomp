# Next work unit (M5 descriptor/task-contract boundary)

HYPOTHESIS-ID: m5-descriptor-task-contract

WORK UNIT: qualify the existing phase-gated descriptor control on the current
real-image route. Run one instrumented game with
`ROGUESQ_LOG_M5_DESCRIPTOR=1`, `ROGUESQ_LOG_M5_ROUTE_ORDER=1`, PCM boundary
logging, and the established autopilot. Do not change runtime behavior.

Competing hypotheses:

* H-descriptor-legitimate: the descriptor at `0x800377C8` is a valid task
  contract; descriptor layout, `OSTask` fields, and the completion route agree.
* H-descriptor-mismatch: the port descriptor/layout or task-field conversion
  disagrees at the target phase and the mismatch is a live contract defect.
* H-descriptor-unreached: the target descriptor control is absent even though
  route/SP/PCM controls are positive, so this boundary is unevaluable.

DISCRIMINATING MEASUREMENT: in the same phase, require
`m5-descriptor-control`, `m5-descriptor-start`, `m5-descriptor-compare`,
`sp-complete-enter/return`, and nonzero PCM source/consumer rows. H-descriptor-
legitimate requires matching task fields and `yield_match=1`/`payload_match=1`
where the control emits them. A field mismatch with all route controls positive
selects H-descriptor-mismatch; absent descriptor rows with positive route
controls selects H-descriptor-unreached. A descriptor row alone is not a
positive control.

Exact commands:

    cp scratch/agent/a10_retry_s4849.sh scratch/agent/run_s4853_descriptor.sh
    # Replace the A10 env with ROGUESQ_LOG_M5_DESCRIPTOR=1, retain the
    # route-order/PCM/phase/autopilot env, and use one default arm.
    zsh scratch/agent/run_s4853_descriptor.sh
    grep -aE '^\[(m5-descriptor|m5-route-order|phase|pcm|CRASH|ABORT)' \
      scratch/agent/soak_results/s4853_m5_descriptor/*.log | tail -300

Use the same title/hangar phase gates and SIGKILL watchdog as the prior recipe.
If the control is absent, do not infer a descriptor defect; record the exact
missing control and pivot.
