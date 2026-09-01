# M5 Session 3520 — selector AI boundary qualification

The independent retail oracle ran first with whole-RDRAM and selector-span
positive controls and an execution watch at `0x80029E78`, phase-gated to the
512 hangar origin `0x006AB400`. Whole-RDRAM produced 10,012 writes, the
selector span produced 12 writes, and the execution watch fired once in the
hangar with `a0=0x5622`, `a1=0x8A0`, `a2=0x10`, `s1=0x80165ED0`, and
`v0=0x561F`.

Added a diagnostic hook to the port's native `osAiSetFrequency_recomp`
implementation, the host equivalent of the `0x80029D20..0x80029E7F`
routine. The first port attempt used a drifted route and crashed at
`0x8000834C` while VI width was 320; it produced no target-phase evidence.
The corrected qualified real-audio LLE/spin-yield/autopilot route reached
title 1024 and hangar 512 with both existing producer and selector-store
controls live. The new hook's positive control fired once during startup, but
it produced zero hangar rows. The selector stores still fired in hangar with
`s1=0x5622` and values `0x80171E70`/`0x80173CB0`.

This selects a port/retail execution-path difference at the AI boundary: the
retail instruction executes in hangar, while the port's corresponding host
primitive is only entered before the target phase. It does not yet identify
whether the difference is a missing port call, a caller/route difference, or a
wrong equivalence between the retail instruction and the host primitive. The
next measurement must identify which port callsites enter `osAiSetFrequency`
and compare them with the retail caller context.

ORIGIN: diagnostic-only oracle execution watch and port host witness; no
audio, selector, task, or output state was rewritten, skipped, or validated.

Evidence: `scratch/agent/s3520_selector_oracle.log`,
`scratch/agent/s3520_selector_port/run.log`, and
`scratch/agent/s3520_port_driver_control.log`.
