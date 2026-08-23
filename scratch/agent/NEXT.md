# NEXT work unit (s2192) — test logging cadence as the second-origin boundary

HYPOTHESIS-ID: m5-a1-retail-writer-census

## Work unit

Run the two-arm, phase-gated schedule test from the repo root. The arms use
the same qualified image/LLE recipe and the same writer probe; the only
difference is broad `ROGUESQ_LOG_ALL=1` in `noisy` versus unset in `quiet`.
The helper control must fire in each arm. The watchdog kills each arm with
SIGKILL after the second-origin phase plus 15 seconds, on a 150-second
deadline, and exits nonzero if either log contains a crash marker.

Exact command:

```sh
zsh scratch/agent/run_s2192_m5_log_all_ab.sh
```

Parse both complete tables after the run:

```sh
for arm in noisy quiet; do
  echo "=== $arm ==="
  grep -a '\[m5-writer-parity-control\]' "scratch/agent/s2192_m5_log_all_ab/$arm.log" | wc -l
  grep -a '\[phase\] vi_width=640' "scratch/agent/s2192_m5_log_all_ab/$arm.log"
  grep -a '\[m5-writer-parity\]' "scratch/agent/s2192_m5_log_all_ab/$arm.log"
done
```

## Competing hypotheses and discriminator

- H-LogCadenceBoundary: quiet reaches `640 @ 0x00696600` while noisy exits
  after `0x00696100`; broad logging cadence is the route boundary.
- H-LoggingIndependentBoundary: both arms pass controls and reach the first
  640 phase but stop before `0x00696600` with the same `get_function(0)` /
  `slotDispatcherIter` boundary; broad logging is not the discriminator.
- H-PhaseReachableBoth: both arms reach `0x00696600`; logging is not the
  boundary and the two complete six-target origin tables select the writer
  parity result.
- H-CoverageFailure: either arm lacks its writer-control or 640 phase control;
  reject the pair rather than treating missing rows as nulls.

The discriminator is one same-iteration table per arm containing positive
control count, both 640 origins, the crash/last-guest-PC outcome, and all six
target writer-PC sets at each origin. Do not add a guard, mitigation, task
rewrite, or audio-default flip.
