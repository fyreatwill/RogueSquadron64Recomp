# Next work unit (repair the A10 positive control)

HYPOTHESIS-ID: m5-a10-guard-class

WORK UNIT: repair and qualify the missing SP positive control in the s4851 A10
same-build pair, then run both default and guard-off arms in one invocation.
Do not change any guard or repeat the retail oracle. The s4851 retry already
reached title/hangar and passed writer, traversal, guard, and PCM controls, but
its `sp-complete` counter was zero in both arms; the next run must use an
existing live SP-task/completion marker or add one batch instrument and prove
it fires in both arms before interpreting A10 behavior.

Competing hypotheses:

* H-A10-legitimate: named writers publish in-range values, traversal is valid,
  and no guard suppresses required work; retain the guards.
* H-A10-suppression: a guard fires after a legitimate in-range write and the
  guard-off arm changes valid traversal or downstream audio behavior; only then
  is a narrowly identified relaxation eligible for a later work unit.
* H-A10-invalid: the port route misses target phase, publishes an invalid
  value, or lacks a positive control; the result is unevaluable and no guard
  change is authorized.

DISCRIMINATING MEASUREMENT: compare the corrected run's phase-scoped SP
control and both arm summaries/logs. A valid selection requires, in the same
phase, the port writer, in-range pointer/value, traversal or slot progress,
guard fire-by-site, PCM and SP controls, and title/hangar route controls. A
guard fire plus downstream default/rollback divergence selects
H-A10-suppression; valid controls with no guard fire selects H-A10-legitimate;
missing or invalid controls selects H-A10-invalid.

Exact evidence to preserve:

    sed -n '1,80p' scratch/agent/soak_results/s4849_m5_a10_guard_qualification_retry/verdict.txt
    for arm in default rollback; do grep -aE '^\\[(m5-a10|phase|pcm|CRASH|ABORT)' scratch/agent/soak_results/s4849_m5_a10_guard_qualification_retry/$arm.summary | tail -240; done

Before the next build/run, identify the SP marker and run a positive-control
check on the same binary/configuration. If the marker cannot be made positive,
stop with the exact missing control; do not infer guard behavior.
