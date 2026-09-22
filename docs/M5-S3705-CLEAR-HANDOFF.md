# M5 session 3705 — clear-to-DMA handoff qualification

The one-build paired run used the real-audio and silent arms with the phase,
DMEM, static-call, source-writer, task, and descriptor controls enabled. Both
arms reached the 512 hangar VI and the target clear probe fired at caller
`0x8008F2CC` with `dst=0x801797B0`, `len=0x298`, and zero value. The real arm
reported the clear at route ordinal 525; its later source-range output rows
were at ordinals 669–670 and included `0x1798B0..0x179930` with zero payload
and zero post-DMA bytes. The silent arm had no source-DMA rows, as expected
for the control route.

The run confirms the clear is earlier than the qualified output handoff and
does not select whether the producer used a different object or whether the
expected object was cleared before consumption. The planned writer-setup probe
did not fire because its injection is absent from the generated `funcs_23.c`
used by this build; its null is therefore unevaluable, not evidence of no
allocation. The static disassembly independently shows the clear receives the
fresh `rs_malloc(0x298)` result stored at `0x8015689C`.

Retail remains the independent second line: its qualified source-span census
has writers at `0x80007670`, `0x8001E2C0`, the `0x8001F...` family, and
`0x800078EC`, with a live whole-RDRAM positive control. No guest or RDRAM
behavior changed.

ORIGIN: diagnostic-only clear/DMA ordering; the observed writer is the
legitimate `0x800078EC` zero-fill, and no mitigation was added.
