# NEXT work unit (oracle runtime/configuration identity audit)

HYPOTHESIS-ID: oracle-runtime-or-rom-discrepancy

Session 782 completed the controlled no-press input-plugin A/B. The verified
input-SDL plugin was attached only in arm B, yet the no-input arm recorded
21,588,123 whole-RDRAM writes / 7,799 VI and the input arm 21,605,494 / 7,788;
both stayed at width 320/origin `0x6dd280` for 130 seconds. Input schedule and
input-plugin attachment are now refuted as phase discriminators.

## Discriminating measurement

Before changing the port runtime, perform a bounded effective-state audit of
the oracle launch against a stock Mupen64Plus CLI launch using the same retail
ROM, core/RSP/input plugin paths, ROM-database data path, `R4300Emulator=1`,
and fresh config directories. Record the generated configs plus startup logs,
then compare the effective Core and Input-SDL sections and loaded plugin list.
If a concrete difference is found, test only that difference in a fresh
130-second oracle run. If no effective-state difference exists, record that
the exact 320-only recipe reproduces across both frontends and return focus to
the M3 FULL_SYNC blocker.

## Controls

- Do not treat a config-save warning after shutdown as startup failure.
- Preserve the whole-RDRAM positive control and VI trace for any follow-up run.
- Do not change port runtime code during this oracle audit.
