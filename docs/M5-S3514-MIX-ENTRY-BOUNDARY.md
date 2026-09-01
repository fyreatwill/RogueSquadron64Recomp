# M5 Session 3514 — mixer-entry boundary qualification

The independent retail oracle ran with whole-RDRAM and selector-store controls
plus execution coverage of `0x80090E04..0x80091034`. Whole-RDRAM recorded
2,589,720 writes; selector stores recorded five writes at each writer PC; and
`musyxMixActiveVoices` entry `0x80090E04` was live in title (344 executions).
The selector load and writer each had 1,960 executions. This qualifies the
retail boundary and its controls.

The port build added a regeneration-safe witness at `0x80090E04`. Its
real-audio arm used LLE/spin-yield/autopilot but crashed at 20.9 seconds in
the known audio-thread `fillSampleStreamRange` family
(`last-guest-pc=0x8000834C`) before any target VI, mixer row, or selector row.
The required silent-control retry reached only VI 320/640, with no title or
hangar phase, mixer row, selector row, crash, or abort.

This selects no parity, divergence, later mutation, or capture invalidity for
the cross-runtime mixer tuple: the retail boundary is live, but neither port
arm reached a comparable phase. It rules out only the claim that this join is
currently runnable on those two arms. The next route work must address the
pre-title blocker or qualify a new target-phase arm; zero port rows are not
evidence.

ORIGIN: diagnostic-only oracle and port execution witnesses; no audio state,
selector, task field, or output value was rewritten, skipped, or validated.

Evidence: `scratch/agent/oracle_s3514_m5_new_boundary.log`,
`scratch/agent/s3514_m5_mix_entry/port.log`, and
`scratch/agent/s3514_m5_mix_entry_silent/port.log`.
