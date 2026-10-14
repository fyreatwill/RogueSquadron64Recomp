# Next work unit (RESUME after interrupted close-out)

HYPOTHESIS-ID: m5-a10-guard-class

WORK UNIT: consume the queued s4849 A10 default-versus-guard-off soak and
classify the complete pointer/list/table guard class. This retry did not rerun
the soak: no verdict or result directory exists yet. Do not repeat the retail
oracle or rebuild unless the queue verdict exposes a specific missing control.

Competing hypotheses:

* H-A10-legitimate: named writers publish in-range values, traversal is valid,
  and no guard suppresses required work; retain the guards.
* H-A10-suppression: a guard fires after a legitimate in-range write and the
  guard-off arm changes valid traversal or downstream audio behavior; only then
  is a narrowly identified relaxation eligible for a later work unit.
* H-A10-invalid: the port route misses target phase, publishes an invalid value,
  or lacks the traversal/PCM controls; the result is unevaluable and no guard
  change is authorized.

DISCRIMINATING MEASUREMENT: compare `scratch/agent/soak_results/s4849_m5_a10_guard_qualification/summary.txt`
and both arm summaries/logs. A valid selection requires, in the same phase,
the port writer, in-range pointer/value, traversal or slot progress, guard
fire-by-site, PCM/SP controls, and title/hangar route controls. A guard fire
plus downstream default/rollback divergence selects H-A10-suppression; valid
controls with no guard fire selects H-A10-legitimate; missing or invalid
controls selects H-A10-invalid.

Exact commands if the loop has not consumed the recipe:

    tail -20 scratch/agent/SOAK-RESULTS.md
    sed -n '1,160p' scratch/agent/soak_results/s4849_m5_a10_guard_qualification/verdict.txt
    for arm in default rollback; do grep -aE '^\\[(m5-a10|phase|pcm|CRASH|ABORT)' scratch/agent/soak_results/s4849_m5_a10_guard_qualification/$arm.summary | tail -240; done

Resume condition: first verify whether the queue recipe has moved to
`scratch/agent/soak_queue/done/` and whether the result directory now exists;
if neither is true, let the queue run the existing recipe. Do not launch a
second copy from this iteration.

Do not remove or relax an A10 guard from this result alone. If the queue
recipe is absent or failed before its watchdog, document the exact missing
control and choose one replacement measurement rather than repeating a blind
soak.
