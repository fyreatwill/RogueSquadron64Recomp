# M5 session 3702 — source producer and overwrite boundary

The required independent retail preflight was run before the port rebuild. Its
whole-RDRAM positive control reached 10,000 callbacks, reached title and
hangar, and its source-range writer histogram again included `0x80007670`,
`0x8001E2C0`, the `0x8001F...` family, and `0x800078EC`.

The port probe was changed only to remove the target-route gate from the
existing scalar-store witness for `0x1797B0..0x179930`. The paired real-audio
and silent arms were built together and both reached the title and hangar
controls. Each recorded 652 source-range stores. The port PCs included:

| writer PC | stores | nonzero store values |
|---|---:|---:|
| `0x80007670` | 172 | 30 |
| `0x8001E2C0` | 11 | 0 |
| `0x8001F...` family | 64 | 53 |
| `0x800078EC` | 384 | 0 |

The first three groups were observed before target-route publication. The
`0x800078EC` group was the later zero-fill. The existing RSP and DMEM controls
were live, and the qualified output-DMA rows still had zero source and
post-DMA payloads. The real and silent arms produced the same source census;
this is not an audio-arm discriminator.

These are two independent lines of evidence: retail attribution names the
same producer families, while the port's phase-independent guest-store probe
shows those producers actually execute. This refutes producer omission and
the descriptor/range mismatch at the measured boundary. It selects
`H-PrePhaseScalarProducer`: the source is legitimately produced, then the
`0x800078EC` zero-fill overwrites it before the output DMA. This is provenance
evidence only; no mitigation or guest/RDRAM state change was made.

Next discriminator: join the final source-range writer sequence to the first
512 output DMAs. A nonzero writer after the clear selects
`H-ProducerAfterClear`; only the clear selects `H-ClearIsFinal`.
