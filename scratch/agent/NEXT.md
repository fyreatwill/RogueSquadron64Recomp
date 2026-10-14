# Next work unit (M5 task-contract audio-route A/B)

HYPOTHESIS-ID: m5-task-contract-audio-route

WORK UNIT: run the existing same-build image-versus-silent A/B with the task
contract/lifetime, route-order, and PCM controls enabled. This is a new route
discriminator after s4855's image-route startup crash; do not treat either
single-arm absence as a contract result.

Competing hypotheses:

* H-task-contract-audio-dependent: both arms qualify title/hangar and route,
  but task-contract/lifetime rows or their joins differ with audio enabled.
* H-task-contract-route-common: both qualified arms have coherent matching
  task-contract/lifetime rows, so the boundary is not audio-route specific.
* H-task-contract-unreached: both arms have positive route/SP/PCM controls but
  no task-contract/lifetime rows.
* H-route-invalid: either arm lacks title/hangar or the required phase-gated
  route/SP/PCM positive controls.

DISCRIMINATING MEASUREMENT: for each arm, require title and hangar VI gates,
phase-5 `sp-complete-enter/return` and `action-dequeue`, and nonzero PCM source
and consumer rows. Only then compare task-contract/lifetime row counts and
their task identity/route joins between `ROGUESQ_AUDIO_UCODE=1` and `=0`.
Audio-dependent rows select H-task-contract-audio-dependent; matching coherent
rows select H-task-contract-route-common; absent rows in both qualified arms
select H-task-contract-unreached; missing controls select H-route-invalid.

Exact commands:

    zsh tools/run_m5_yield_ab.sh
    grep -aE '^\[(m5-task|m5-route-order|phase|pcm|CRASH|ABORT)' \
      scratch/agent/m5_yield_ab/*.log | tail -300

The script launches both arms from `build/`, uses SIGKILL cleanup, and already
contains the title/hangar phase gates and task-contract/lifetime logging. If
either arm is route-invalid, record the missing control and pivot; do not infer
a task-contract defect.
