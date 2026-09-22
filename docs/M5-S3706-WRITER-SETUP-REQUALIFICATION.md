# M5 Session 3706 — producer-object join requalification

The regeneration fixup was repaired with an idempotent s3423/s3424 hook for
`funcs_23.c` and `funcs_2.c`, then one Debug build ran the real-audio and silent
arms concurrently. Both arms reached VI 512 and fired the setup positive
control, all five setup-step rows, and the existing RSP/DMEM/source controls;
neither arm logged a crash or abort.

In the real arm, both target setup rows at `0x8008F2CC` had
`a0=0x801797B0`, `a2=0x298`, `s0=0x12`, and `s1=0x561F`. The five setup-step
rows retained the same `s1`, `t0=1`, and `t1=0`. The clear call then logged
`dst=0x801797B0`, `len=0x298`, and zero value at route ordinal 523. The same
run's final source-span writer was the zero-valued `0x800078EC` fill (384
stores, ending at physical `0x17992C`), and later input-DMA rows had zero
payload with no later nonzero writer. The silent arm matched the setup tuple
but emitted no image source DMA, as expected for the control.

This selects `H-ClearTooEarly` at the measured boundary: the producer and
clear use the same object, and the legitimate clear is the final observed
writer before the first qualified output DMA. `H-DifferentProducerObject` is
refuted for this call; `H-ProducerAfterClear` is refuted for the captured
source range. The producer's semantic reason for producing zero remains open.

ORIGIN: diagnostic-only producer-object join. The observed writer is the
legitimate `0x800078EC` zero-fill; no mitigation or guest-state change was
added.

Evidence: `scratch/agent/s3692_m5_input_payload_writer/{real,silent}.log`,
the independent retail writer census in the s3697/s3700 evidence, and the
same-build setup positive controls.
