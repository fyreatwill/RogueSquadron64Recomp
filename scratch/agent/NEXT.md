# NEXT work unit (s2440) — identify the retail second-range writer path

HYPOTHESIS-ID: m5-retail-second-range-writer

## Work unit

Run one bounded retail-oracle capture using the validated eleven-Start route.
Keep whole-RDRAM, title, hangar, and both exact image-range controls. Watch
the unresolved second-range candidates `0x80007670,0x8001E2C0,0x8001FACC,
0x8001FAF8,0x8001FD2C` plus the joined first-range callsite `0x8008F2CC`;
use one phase-gated field table and one exact-store table. Observation-only;
no port change.

## Competing hypotheses and discriminator

- H-SecondRangeEntry: one candidate has hangar-phase execution and fields that
  identify the second-range destination, with a stable return/caller relation.
- H-SecondRangeHelperOnly: candidates execute, but only a lower helper has
  exact second-range stores and no stable semantic entry relation appears.
- H-SecondRangeUnattributed: exact second-range writes pass while no candidate
  is phase-relevant.

The discriminator is one same-run hangar-keyed table joining candidate PC,
exact second-range store address, phase, and return/caller relation. A
candidate with phase rows and exact stores selects H-SecondRangeEntry; only
helper rows selects H-SecondRangeHelperOnly; zero candidate rows with valid
controls selects H-SecondRangeUnattributed.

Require whole-RDRAM, title `0x00790400:1024`, hangar `0x006AB400:512`, and
exact-range totals before interpreting any null.
