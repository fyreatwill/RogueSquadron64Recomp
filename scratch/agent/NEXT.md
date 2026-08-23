# NEXT work unit (s2193) — isolate the logging-sensitive failure mode

HYPOTHESIS-ID: m5-a1-retail-writer-census

## Work unit

Run the self-contained three-arm, phase-gated schedule test from the repo
root. All arms use the same qualified image/LLE recipe and the same writer
control. `quiet` leaves optional logs unset, `noisy` sets `ROGUESQ_LOG_ALL=1`,
and `route` enables only `ROGUESQ_LOG_SLOT_DISPATCH`,
`ROGUESQ_LOG_EVENT_WIRING`, `ROGUESQ_LOG_AUDIO_RETURN`, and
`ROGUESQ_LOG_SP_TASKS`. The watchdog kills each arm with SIGKILL after the
second-origin phase plus 15 seconds, on a 180-second deadline, and exits
nonzero if an arm logs a crash marker.

Exact command:

```sh
zsh scratch/agent/run_s2193_m5_narrow_log_ab.sh
```

Parse the complete table after the run:

```sh
for arm in quiet noisy route; do
  echo "=== $arm ==="
  grep -a '\[m5-writer-parity-control\]' "scratch/agent/s2193_m5_narrow_log_ab/$arm.log" | wc -l
  grep -a '\[phase\] vi_width=640' "scratch/agent/s2193_m5_narrow_log_ab/$arm.log"
  grep -a '\[m5-writer-parity\]' "scratch/agent/s2193_m5_narrow_log_ab/$arm.log"
  grep -a -E '\[(CRASH|ABORT)\]|\[last-guest-pc\]|\[pc-symbol\]' "scratch/agent/s2193_m5_narrow_log_ab/$arm.log" | tail -12
done
```

## Competing hypotheses and discriminator

- H-LoggingOnlyThroughput: `route` matches quiet's crash/termination while
  `noisy` remains alive; broad logging changes throughput or log-lock timing,
  but the selected route-log categories do not create the live-loop outcome.
- H-NarrowRouteLogBoundary: `route` matches noisy's live loop or reaches
  `0x00696600`; a route-specific log category changes the post-first-origin
  boundary. If it reaches the second origin, retain all six target writer
  rows for that arm.
- H-SecondOriginStillAbsent: all three arms pass controls and the first 640
  phase but miss `0x00696600`; the second-origin route remains unresolved and
  no writer parity conclusion is permitted.
- H-CoverageFailure: any arm lacks its writer control or first 640 phase;
  reject the three-arm comparison rather than treating missing rows as nulls.

The discriminator is one same-iteration table per arm containing positive
control count, both 640 origins, termination/last-guest-PC outcome, and all
six target writer-PC sets at each observed origin. Do not add a port guard,
mitigation, task rewrite, or audio-default flip.
