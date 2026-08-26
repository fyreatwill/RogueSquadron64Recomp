# NEXT work unit (s2442) — phase-locate the second-range helper caller

HYPOTHESIS-ID: m5-second-range-caller-boundary

## Work unit

Run one bounded, observation-only retail-oracle capture using the validated
eleven-Start route. Keep the whole-RDRAM positive control, title
`0x00790400:1024`, hangar `0x006AB400:512`, and exact ranges
`0x167650:0x167C50` and `0x1798B0:0x179A48`. Watch execution at the lifetime
caller candidate `0x8002BEEC`, the helper `0x800078EC`, and the known caller
`0x8008F2CC`; add a phase-gated field table only for `0x8002BEEC` and the
bounded exact-store table for `0x800078EC`. No port change.

## Competing hypotheses and discriminator

- H-SecondRangeSemanticCaller: `0x8002BEEC` executes in hangar with a stable
  `PREVIOUS_PC`/return relation and context matching the exact-store helper.
- H-SecondRangeHelperDirect: the helper writes in hangar, but
  `0x8002BEEC` has no hangar execution/context row.
- H-SecondRangeOtherCaller: both execute, but the helper's hangar stores join
  a different stable caller relation.

The discriminator is one same-run hangar-keyed table joining the exact-store
helper's `PREVIOUS_PC`, the `0x8002BEEC` execution/field row, and the
`0x8008F2CC` caller row. A matching stable `0x8002BEEC` row selects
H-SecondRangeSemanticCaller; helper stores with no such row select
H-SecondRangeHelperDirect; a different stable caller relation selects
H-SecondRangeOtherCaller. Do not interpret any null until all controls and
both exact-range totals pass. The store-field phase latch was zero in s2441,
so treat it as supplemental and use the live phase histogram as the writer
control.

## Exact command shape

Use `tools/oracle/build/rs64_oracle` with the established core, retail ROM,
Rice video, `--secs 120`, `--hit-cap 200`, `--watch-write 0x0:0x800000`, both
exact-range watches, `--watch-pc 0x8002BEEC,0x800078EC,0x8008F2CC`,
`--pc-phase-log-width 0x006AB400:512`, `--pc-field-dump 0x8002BEEC`,
`--store-field-dump 2:0x800078EC`, `--pc-hist-watch 1`,
`--pc-hist-watch 2`, `--pc-hist-phase 0x006AB400:512`, `--vi-trace`, and
the eleven-Start schedule. Run under a shell-native watchdog and SIGKILL.
