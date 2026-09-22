# M5 s3714 — post-PCM drain qualification

The retail oracle passed its whole-RDRAM positive control with 23,005 writes.
At the 512 hangar phase it observed 4,335 executions each of
`osAiSetNextBuffer`, `__osAiDeviceBusy`, and the success branch, with zero
reject-branch executions. No named `osAiGetStatus` or `osAiGetLength` call was
observed by the targeted execution watches.

The rebuilt port pair launched real audio first and then the silent
`ROGUESQ_AUDIO_UCODE=0` control. Both arms reached title 1024 and hangar 512;
phase and RSP/source controls were active. In the hangar phase:

| arm | set-next rows | raw queue depth | image-stage rows | nonzero PCM rows | get-status/length |
|---|---:|---|---:|---:|---:|
| real | 114 | 741–3813 bytes | 471 | 0 | 0 |
| silent | 29 | 741–4581 bytes | 0 | 0 | 0 |

The corrected pair is the result; an earlier arm-order attempt was invalid
because silent crashed at 320 and real never reached 512. The port result
selects `H-AudioDrainDivergence` at the host queue/cadence boundary. It does
not identify the queue consumer that causes the difference, and it provides no
retail queue-depth parity claim. The absence of target status/length calls
rules out those guest shims as the measured drain discriminator.

ORIGIN: diagnostic-only oracle and host queue observations. No mitigation was
added; the legitimate producer remains `osAiSetNextBuffer` and the unresolved
boundary is the host audio consumer/callback cadence.
