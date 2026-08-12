# NEXT work unit (after s696: three unqualified provenance rerolls)

HYPOTHESIS-ID: m3-recovery-latch-readiness

Do a bounded recovery-latch writer/readiness audit before any further
`m3-e9-provenance-cap` reroll. Do not alter the E9 tracer or enqueue another
identical 600-second provenance recipe.

## Competing hypotheses

- **H-game-route:** the current route legitimately never emits the recovery
  FULL_SYNC/address `0x0076B768`; the section-2 prerequisite is stochastic
  game state, not an observer defect.
- **H-observer:** the recovery write/emission occurs but the current runtime
  marker misses it; this contradicts s692's three live marker classes and
  needs independent retail evidence before being revived.
- **H-runtime-divergence:** retail reaches the recovery write on the same
  phase-gated path while recomp does not, identifying an emulation/control-flow
  divergence upstream of the E9 provenance target.

## Discriminating measurement

First use `tools/oracle/README.md`'s whole-RDRAM write watch as a positive
control; it must fire at the documented rate. Then arm physical `0x0076B768`
and run the documented phase-gated retail path. A retail hit while recomp's
three markers remain absent supports H-runtime-divergence; no retail hit after
the path demonstrably reaches the equivalent phase supports H-game-route;
whole-RDRAM-only activity or failure to reach the phase is unqualified and
must not be used to revive H-observer. If retail cannot reach that phase, stop
before adding a runtime instrument and record the exact reachability limit.

## Commands

    sed -n '1,240p' tools/oracle/README.md
    rg -n '0x0076B768|recovery-silent|rdp-fullsync|fs-slot' scratch/agent/s692_recovery_latch_audit.sh scratch/agent/s670_postsec2_pulse_freeroll.sh
    tail -20 scratch/agent/SOAK-RESULTS.md
