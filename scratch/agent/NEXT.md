# NEXT work unit (s2441) — close the phase join for second-range writers

HYPOTHESIS-ID: m5-retail-second-range-writer

## Work unit

Run one bounded retail-oracle capture using the validated eleven-Start route.
Keep whole-RDRAM, title, hangar, and both exact image-range controls. Replace
the high-frequency candidate field dump with a phase-latched execution/store
table that records the exact second-range writer PC, `PREVIOUS_PC`/return
relation, live VI origin/width, and store address for every requested
candidate: `0x80007670,0x8001E2C0,0x8001FACC,0x8001FAF8,0x8001FD2C`, plus
`0x800078EC` and caller `0x8008F2CC`. Observation-only; no port change.

## Competing hypotheses and discriminator

- H-SecondRangeEntry: a requested candidate has hangar-phase execution and
  phase-latched exact stores with a stable caller/return relation.
- H-SecondRangeHelperOnly: only the lower helper path has exact stores, while
  candidate execution is separate or lacks a stable entry relation.
- H-SecondRangeUnattributed: exact second-range writes pass, but no requested
  PC joins to them in the phase-latched table.

The discriminator is one same-run hangar-keyed table joining candidate PC,
exact store address, VI phase, and caller/return relation. Candidate rows with
exact stores and a stable relation select H-SecondRangeEntry; only helper rows
select H-SecondRangeHelperOnly; zero candidate joins with valid controls select
H-SecondRangeUnattributed. The s2440 run selected only the lifetime portion of
the third case, so this unit must repair the phase join before interpreting it.

Require whole-RDRAM, title `0x00790400:1024`, hangar `0x006AB400:512`, and
exact-range totals before interpreting any null.
