# Next work unit (s4309): join the first post-free consumer read to the free boundary

HYPOTHESIS-ID: m5-audio-destub-sequence

State (s4308): independent retail evidence passed both controls and VI 512,
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

Expected command family: use the existing s4307/s4306 port recipe from the
seeded save, with the value-aware oracle diagnostic source retained only for
the independent retail comparison. Run from `build/`, kill with SIGKILL, and
capture the full log under `scratch/agent/s4309_port_free_read_join/`.
