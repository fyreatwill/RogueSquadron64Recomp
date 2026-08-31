# Session 3369 — independent retail status-03 worker contract

## Capture

The corrected run used the retail ROM under the debugger-enabled mupen64plus
oracle with Rice video, the validated Start schedule, a whole-RDRAM write
watch, the complete physical voice-status range `0x154620:0x168DB0`, and
execution watches for the status-03 publisher, worker, clear/republish sites,
and shutdown scan. The status-range writer histogram was enabled in the same
run. Output: `scratch/agent/s3369_m5_status03_worker_contract/fixed/oracle.log`.

The whole-RDRAM control produced 36,645,693 writes. The run completed normally
after 75.2 seconds / 4,472 VI and reached the target hangar phase, VI 512 at
origin `0x006AB400` (542 phase VI rows in the phase histogram).

## Results

| Watch | Result |
|---|---:|
| `0x8009B30C` status-03 publication | 0 executions |
| `0x8009B7CC` streaming status-03 republish | 4 executions; 2 target-phase entries |
| `0x8009B7EC` worker status-zero clear | 4 executions; 2 target-phase entries |
| `0x8009B600` service worker dispatch | 6,089 executions |
| `0x8009BDE8` accumulator | 2,326 executions |
| `0x8009BCF8` shutdown scan | 1 execution |

The first target-phase clear row was at 48.8 s, with `prev_pc=0x8009B7E8`,
`v0=0`, `s1=0x80153420`, and `v1=3`. A later target-phase republish row was
at 74.1 s, with `prev_pc=0x8009B7C8`, `v0=4`, `s1=0x80153420`, and `v1=2`.
The worker execution histogram independently reports the same transfer sites:
`0x8009B7EC <- 0x8009B7E8` and `0x8009B7CC <- 0x8009B7C8`, three samples each
in the bounded previous-PC summary.

## Interpretation

This selects `H-RetailStatus03Reaped`: the named service worker does execute
in hangar and reaches the status-zero store for a status-03 slot. It refutes
`H-RetailStatus03Gate` for the observed retail route and provides no support
for `H-RetailStatus03OtherPath`. The zero count at `0x8009B30C` means this
capture did not observe the status-03 publisher, not that the publisher is
dead; the independent static audit identifies it as a legitimate status-02
stop-path store.

This is two-line evidence: the oracle attributes live retail execution and
stores, while the generated-source census in `s3249_m3_status03_audit.md`
identifies the same PCs and their state transitions. No wait, slot, or status
behavior change is authorized. The next discriminator is the matching port
worker/clear contract on the already qualified hangar route.
