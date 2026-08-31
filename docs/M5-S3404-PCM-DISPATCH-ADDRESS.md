# M5 session 3404 — PCM dispatch address qualification

The prescribed 120-second retail oracle capture passed the same-run controls:
the whole-RDRAM watch recorded 10,040 writes, the `0x1935E0` PCM control
recorded 40 writes, and the route reached title 1024 and hangar 512. The
execution watch at `0x8002BEEC` still recorded zero hits and emitted no
`exec-prev` rows.

A corrective capture watched the adjacent known PCs in one run. It again
passed the whole-RDRAM control (10,040 writes), PCM control (40 writes), and
the target phases. `0x800078EC` executed 9,699 times; `0x800078E8`,
`0x8002BEE8`, and `0x8002BEEC` each executed zero times. Its only execution
histogram row was `exec-prev pc=0x800078ec prev=0x800078ec n=9699`.

This selects `H-Stale-2BEEC-Target` for the current oracle route: the presumed
`0x8002BEEC` dispatch address is not a live execution site in this same-run
qualification, while the producer loop is. It refutes the three caller-shape
hypotheses in `NEXT.md` at that address and does not identify the actual
producer dispatch path. The prior 2BEEC attribution must be reconciled before
adding port instrumentation. No runtime or audio behavior changed.

Evidence: `scratch/agent/s3403_retail_8002beec_caller/oracle-120.log` and
`oracle-corrective.log`.
