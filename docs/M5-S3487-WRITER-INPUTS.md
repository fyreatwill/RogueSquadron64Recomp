# M5 Session 3487 — selector writer input capture

The planned join at `0x80091074` could not be qualified because the port did
not reach the title phase in either of two unchanged retries. Both runs used
the prescribed LLE/spin-yield route with `ROGUESQ_AUDIO_UCODE=1` and crashed in
`fillSampleStreamRange` from the audio thread at guest PC `0x8000B650`, before
the title origin `0x00790400` appeared. The first run and retry were captured
in `scratch/agent/s3487_port_writer.log` and
`scratch/agent/s3487_port_writer_retry.log`.

The independent retail preflight was valid: the whole-RDRAM control fired
12,029 times, the physical selector-word watch at `0x00149750` fired 2,029
times, and the `0x80091074` execution watch fired 3,096 times, including
title-phase rows. Retail rows included `v0=0x80171CE0`, `s1/a0=0x801772F0`,
and varying selector operands. This qualifies the ground-truth side but does
not provide the missing port join.

The regeneration-safe port hook was built successfully and is present in the
generated function containing `0x80091074`; it emitted zero rows in both
failed port runs. Therefore no writer-input or later-transform hypothesis is
selected. The blocking explanation remains route-specific audio failure, not
an absent writer, because the port never reached the phase gate.

**ORIGIN:** diagnostic-only writer-register/value observation at
`0x80091074`; it does not rewrite, skip, or validate task fields.
