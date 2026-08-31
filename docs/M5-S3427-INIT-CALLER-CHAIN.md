# M5 Session 3427 — initN64RspMixer caller chain

The first retail arm used stale address `0x80091898`, the delay-slot NOP. Its
whole-RDRAM control and phase gates fired, but the caller watch had zero hits,
so that arm was discarded. Generated-source enumeration found two actual JALs
to the function entry `0x8009189C`: `0x80091C58` and `0x80091D14`.

The corrected retail oracle passed its whole-RDRAM positive control at 10,000
writes and reached title 1024 and hangar 512. The caller watch fired twice,
both with `prev_pc=0x80091D14`; no `0x80091C58` execution was observed on this
driven route. The sampled tuple was `a0=0x80165ED0, a1=0x12, a2=0, v0=1`.

The first concurrent port pair was invalid because the image arm crashed at
boot before phase qualification. A retry qualified both silent and Factor 5
image arms: both reached title and hangar, had live init and audio ABI/DMA
controls, and emitted no crash or abort marker. Both arms had the same init
and pre-allocate tuples as Session 3426, but the init witness reported `ra=0`
in every sampled row at both phases. Thus the existing entry witness cannot
recover a direct caller from the recompiler context.

This selects a caller-site asymmetry at the observed route: retail executes
`0x80091D14`, while port caller identity is not recoverable from the current
entry witness. It does not select parity or prove the port count illegitimate.
No wait, slot, dispatch, clear, or PCM behavior was changed.

Evidence is in `scratch/agent/s3427_m5_init_caller_chain/`.
