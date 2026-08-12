# NEXT work unit (after s692 recovery-latch readiness audit)

HYPOTHESIS-ID: m3-e9-provenance-cap

Run one ordinary single-instance command-word capture now that s692 restored
and independently validated its required recovery control. Do not alter the
decoder, the LLE marker, or the recovery route.

## Competing hypotheses

- **H-legitimate-open-chain:** the eight retained frames describe a valid
  display-list/branch chain; their captured command words are valid commands.
- **H-inline-data-dispatch:** the repeated dispatcher return fetches inline
  data as commands; captured words expose a pointer/data family.
- **H-state-corrupt:** a corrupted saved frame or command source feeds the
  dispatcher; captured words/PCs are unstable or implausible.

## Discriminating measurement

Run the existing phase-gated, recovery-reroll recipe once to a qualified
section-2 latch and score `[e9-prov-frame]` rows only after the first
`addr=0x0076B768`. Positive controls in that same log: four boot
`[e9-prov]` controls plus both `rdp-fullsync` and `fs-slot` observations of
the recovery cell. Valid, stable opcode/operand families support
H-legitimate-open-chain; repeatable data-shaped words support
H-inline-data-dispatch; incoherent or changing target/PC/word joins support
H-state-corrupt. If the recovery control is absent, record it as unscorable;
do not interpret cap rows.

## Command

    env BUDGET_S=2400 TARGET_PULSED=1 SEC2_SETTLE_S=8 POST_PULSE_HOLD_S=15 MAX_HOLD_S=45 zsh scratch/agent/s670_postsec2_pulse_freeroll.sh
