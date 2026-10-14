# Resume next work unit

HYPOTHESIS-ID: m5-qualified-route-startup-contract

Checkpoint close-out: the s4826 corrected boundary audit found valid, identical task state at both
`osSpTaskStartGo` and pre-conversion enqueue in both arms, with positive
controls firing and no rejected pointer. The intermittent `0x400128d47` crash
was absent; the pair stopped at the VI-640 gate with 64 SP completions each.

No experiment is to be rerun in this checkpoint iteration. The instrument and
its s4826 result are already committed in `439e38f9`; resume by running the
single capture below in the next iteration and preserve both logs.

Single bounded work unit: obtain one native crash-path capture while retaining
the boundary witnesses. Competing hypotheses:

* H-common-host-after-enqueue: the fault is in a host operation after the
  validated enqueue boundary; select if a crash run shows the same boundary
  rows followed by a native stack outside task conversion.
* H-request-state: request-only changes scheduler state after the validated
  boundaries; select only if a crash run shows an arm-specific state transition
  before the fault.
* H-route-instability: the crash is an intermittent startup condition that is
  absent on qualified runs; retain if both arms reach the gate without a crash
  and no boundary divergence appears.

Discriminating measurement: a single phase-gated pair with the boundary flag,
crash handler output, and host thread stack capture enabled; require the task
validity positive control in both arms. A native crash stack after matching
start/enqueue rows selects H-common-host-after-enqueue; an arm-specific state
row selects H-request-state; another clean gate-qualified pair selects
H-route-instability. Do not rerun Step 1.

```sh
env ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_TASKSUBMIT_STACK=1 zsh tools/run_m5_yield_ab.sh
grep -a -E '\[m5-host-boundary|\[CRASH\]|si_addr|spTaskSchedulerThread' scratch/agent/m5_yield_ab/default.log scratch/agent/m5_yield_ab/request-only.log
```

Expected discriminator: matching start/enqueue rows followed by a native
post-boundary stack selects H-common-host-after-enqueue; an arm-specific state
transition selects H-request-state; another clean gate-qualified pair with no
boundary divergence retains H-route-instability.
