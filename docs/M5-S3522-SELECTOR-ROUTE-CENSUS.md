# M5 Session 3522 — selector route census

The generated tree was enumerated before the runtime capture. There are
exactly two direct references to `0x80029D20` / `osAiSetFrequency_recomp`:
`0x80091BAC` in `initAudioSubsystem` and `0x80091CB8` in
`reapplyAudioConfig`. Their only generated callers are
`setDisplayMode` (`0x8008EA78`) and `reapplyDisplayMode` (`0x8008EBC0`).
Both direct calls are unconditional once their enclosing function is entered.

Added the regeneration-safe `tools/apply_s3522_m5_selector_route.py` witness
at both enclosing caller entries. It logs a startup control and phase-gated
title/hangar caller rows without changing guest state. The Debug target built
successfully.

The first port attempt omitted the validated route settings and stalled at VI
640. The corrected attempt used real audio, LLE ungated/solo, spin-yield,
missing-function stubs, and the canonical autopilot, but crashed before title
at `fillSampleStreamRange+932` / guest PC `0x8000B650`. Thus the port caller,
known-call, and new route rows are absent for a route-invalid capture; this is
not evidence that the callers are absent in hangar.

The independent retail run was valid. Its whole-RDRAM control fired 10,012
times, the physical selector span `0x00149758..0x00149760` fired 12 times,
and the hangar-phase execution watch at `0x80029E78` fired once from
`0x80029E64`, with `a0=0x5622`, `a1=0x8A0`, `a2=0x10`, `s1=0x80165ED0`, and
`v0=0x561F`.

The static census rules out an unenumerated direct generated caller at this
scope, but the runtime discriminator remains unevaluable until a real-audio
port run reaches hangar. No audio, selector, task, or output state was
rewritten.

ORIGIN: the new route-entry witness is diagnostic-only; it observes caller
registers and phase, and performs no guest-memory or control-flow mutation.
