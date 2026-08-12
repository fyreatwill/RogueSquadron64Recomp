# NEXT work unit (after s697: retail target watch is phase-unqualified)

HYPOTHESIS-ID: m3-recovery-latch-readiness

Do a bounded retail-oracle boot-reachability audit before any further
`m3-e9-provenance-cap` reroll or recovery-cell target watch. Do not alter the
E9 tracer or enqueue another identical 600-second provenance recipe.

## Competing hypotheses

- **H-watch-perturbation:** debugger memory watches prevent retail boot from
  advancing; an unwatched `--vi-trace --pif-trace` arm reaches 640/1024 while
  the whole-RDRAM-control arm remains 320.
- **H-rsp-stall:** the currently selected retail RSP plugin fails a boot task;
  all otherwise-equivalent arms using it remain 320, while an installed
  alternative RSP plugin reaches 640/1024.
- **H-oracle-environment:** the phase failure persists across no-watch and
  alternative-RSP arms, so the oracle setup/ROM environment is not presently
  a valid retail witness. Do not interpret the recovery-cell zero in that
  state.

## Discriminating measurement

Build every available arm in one batch: (A) current RSP with no memory watch,
(B) current RSP plus the whole-RDRAM control watch, and (C) each installed
alternative RSP plugin with no watch. All use `--vi-trace --pif-trace` and the
same documented Start schedule. A/B splits H-watch-perturbation; C splits
H-rsp-stall. Each arm must show PIF Start transitions, and a successful arm
must reach a VI-width transition past 320 before it can qualify a later
`0x0076B768` target watch. If no arm crosses 320, record H-oracle-environment
and stop before adding a runtime instrument.

## Commands

    ls /opt/homebrew/lib/mupen64plus/*rsp*.dylib
    tools/oracle/build/rs64_oracle --help
    # Run A/B/C with --secs 70 --vi-trace --pif-trace and:
    # --press '6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start'
    # B alone adds --watch-write 0x0:0x800000.
