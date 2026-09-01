# M5 Session 3531 — selector setup source/return contract

The Debug build completed successfully. A corrected real-audio/LLE/solo,
spin-yield, canonical-autopilot run reached title VI 1024 and hangar VI 512;
all existing selector controls and the new setup-contract positive control
fired.

The phase-keyed port table observed the complete title setup sequence:
`reapply-entry` entered with `a0=0x80165ED0`, `a1=0x12`; the mutex path
preserved the selector context; the AI call loaded `a0=0x5622`; and the AI
return reported `v0=0x5622`. In hangar, the AI-return row again reported
`v0=0x5622` with `s1=0x80165ED0`; downstream entry, allocation, and
selector-store witnesses remained live.

The independent retail run was attempted with whole-RDRAM and target-write
controls plus execution watches, but could not start because the configured
`libmupen64plus.dylib` is absent. The port contract is therefore qualified,
but retail source/value parity is unevaluable in this session. This is
single-source evidence and does not select `H-SetupWriterSourceParity` versus
`H-SetupWriterSourceDivergence`.

ORIGIN: diagnostic-only setup-entry, mutex, AI-call/return, phase, positive,
and downstream observations. No audio, selector, task, or output state was
rewritten.

Evidence: `scratch/agent/s3531_selector_setup_contract/run.log` and
`scratch/agent/s3531_selector_setup_contract/oracle.log`.
