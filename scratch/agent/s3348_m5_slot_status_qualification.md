# Session 3348 — M5 slot/status qualification

The Debug target rebuilt successfully. The existing extended
Start/spin-yield recipe was run from `build/` with the whole control matrix.
It reached title VI 1024 at 14.5 s and hangar VI 512 at 26.3 s, so the
target phase was valid.

Positive controls fired in the same run: tick/jal/exit and swap controls,
title and hangar phase transitions, repeated audio-task dispatch, and the
PCM/audio activity already used by the qualification recipe. The wrapper left
the game process alive after capture returned; it was SIGKILLed, and no crash
marker was used as evidence.

In VI-512, the port emitted slot/status activity through `slot-byte`,
`slot-sb`, `drain-slots`, and repeated `drainAudioAndFinalizeSpeechBuffer`
rows. The four named retail consumer PCs (`0x80094648`, `0x8009B600`,
`0x8009B85C`, and `0x8009BDE8`) had zero log hits. This selects
`H-PortConsumerUnreached`: the port-side slot/status path is active, but the
named consumer edge was not reached or is not represented by the current
consumer probe. This does not identify the missing caller or authorize a
behavior change.

Evidence: `scratch/agent/soak_results/s1949_menu_input_yield_20260830-235420/run.log`.
