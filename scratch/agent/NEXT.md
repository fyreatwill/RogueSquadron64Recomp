# NEXT: execute M5 plan Step 4 at the remaining hangar gate boundary
HYPOTHESIS-ID: m5-audio-destub

The design inventory is complete. Step 1 and the declared-size staging change
already have prior qualified evidence; do not repeat those runs. The next
bounded M5 unit is Step 4's remaining hangar gate/value boundary, centered on
the retail-live `0x80094648` consumer/writer family. Before building, read the
Step 4 row in `docs/M5-AUDIO-PLAN.md` and arm all existing phase/PCM/task
controls.

Competing hypotheses:

- H-gate-suppresses: the port's gate/value at the `0x80094648` boundary
  suppresses legitimate hangar audio service or slot progress.
- H-gate-legitimate: retail also reaches this boundary with the observed value
  and the missing hangar PCM/slot result has another downstream cause.
- H-port-input-diverges: the gate consumer is equivalent, but an upstream
  port input differs before the consumer; the writer and source field can be
  named without changing behavior.

Discriminating measurement: one batched build/run with phase-gated retail
write/PC/value attribution for the `0x80094648` family and matching port entry,
gate branch, task/slot, and PCM rows. The whole-RDRAM oracle and title/hangar VI
transitions must fire. Retail value/order matching the port selects
H-gate-legitimate; a retail-vs-port value/order mismatch at the named writer
selects H-gate-suppresses or H-port-input-diverges; missing controls invalidate
the run. No gate skip or force-value mitigation is authorized by a row count.

Exact starting commands:

    cmake --build build -j8
    zsh scratch/agent/s4264_gate.sh

Adapt the recipe only by adding the Step 4 writer/value controls and use
SIGKILL for cleanup. Report the comparison in the session entry; do not spend
a separate build on each counter.
