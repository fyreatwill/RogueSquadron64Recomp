# M5 Session 3711 — AI-frequency call/return qualification

The existing phase-gated frequency driver was corrected to enable both the
selector AI-boundary and AI-return witnesses. One Debug build was used for the
qualified route; a route-flake retry that stopped before title was discarded.
The valid run reached title VI 1024 and hangar VI 512, fired the RSP positive
control and 4,766 image-stage rows, and emitted no crash or abort marker.

At the hangar phase the port recorded one complete AI row:

    pc=0x80029E78 a0=0x5622 s1=0x80165ED0 v0=0x561F
    return input=0x561F result=0x561F

The independent retail ground-truth captures passed their whole-RDRAM control,
reached hangar, and recorded the same `a0=0x5622` input and `v0=0x561F`
actual-frequency result. The retail ELF audit independently explains the
value as the rounded NTSC DAC-rate contract (`48681812 / 2208 = 22047`).

This selects `H-AIFrequencyReturnParity` and refutes
`H-AIFrequencyReturnDivergence` and `H-AIFrequencyProducerState` at the
measured call/return boundary. The image-task discrepancy therefore remains
downstream of this AI-frequency result. No audio, selector, task, clear, or
payload state was rewritten.

ORIGIN: diagnostic-only host AI entry/return observations, paired with
independent retail execution/value evidence. The legitimate writer is
`osAiSetFrequency` at `0x80029D20`; its actual-frequency result is preserved.

Evidence: `scratch/agent/s3436_m5_port_frequency_contract/run.log`,
`docs/M5-S3520-SELECTOR-AI-BOUNDARY.md`,
`docs/M5-S3533-SELECTOR-AI-RETURN.md`, and
`docs/M5-S3534-AI-FREQUENCY-CONTRACT.md`.
