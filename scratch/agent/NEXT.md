# Next work unit (s4310): replay the validated port route for the free/read join

HYPOTHESIS-ID: m5-audio-destub-sequence

State (s4309): the first port join attempt was route-invalid: three variants
stalled or crashed before VI 512, with the final wrap-shadow route remaining at
VI 640 until its watchdog. The adjacent-range positive control fired, but no
target read/write rows were captured. Independent retail evidence still passed
both controls and VI 512,
and the value-aware oracle logger confirmed the first hangar consumer row
`0x8008FCE8: 0x17D9E0 -> 0x8017D9F8` plus the retail-specific read order. The
port table differs, but the exact lifetime/consumer fault is still open.

Competing hypotheses:

- H-free-before-consumer: the port's selected stream-node block is already in
  the retail-equivalent post-free state when the first synth read occurs; the
  divergence is caused by a later consumer traversal or overlay dispatch.
- H-port-reuse-before-consumer: port cache/level work reuses or republishes the
  block before the first synth read, so the first divergent read is downstream
  of a port-only lifetime ordering difference.
- H-retail-reclaims-different: retail and port both free the block, but the
  allocator/cache writer sequence between free and first synth read differs;
  the first consumer read is only the observable boundary.

Discriminator: one clean port VI-512 run with the existing phase-gated target
read positive control, value-aware read rows, selected writer ordinal, and a
join to the exact `rs_free`/stream-node free event. Record the first target
read and every selected write between the free and that read. A clean block
snapshot matching the retail post-free values before the first read selects
H-free-before-consumer; any port-only write/reuse before it selects
H-port-reuse-before-consumer; matching free but different intervening writer
sequence selects H-retail-reclaims-different. A missing control, no VI 512,
or a crash before the joined boundary is invalid. Do not add a guard or skip.

Before any build, inspect the existing port free/read join and confirm its
positive-control and phase-gating fields. Batch all three hypotheses in one
instrument/build/run; do not make an A/B arm or mitigation.

Expected command family: reconstruct the exact successful s4307 recipe from
`scratch/agent/s4307_read_join_512/run.log` and its seeded-save route, retain
`ROGUESQ_LOG_S4306=1`, `ROGUESQ_LOG_S4307=1`, and `ROGUESQ_LOG_RS_FREE=1`, run
from `build/`, kill with SIGKILL, and capture under
`scratch/agent/s4310_port_free_read_join/`. A missing positive control or no
VI 512 is invalid; do not add a guard or skip.
