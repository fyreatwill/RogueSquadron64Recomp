# NEXT work unit (s2439) — isolate the retail hangar caller relation

HYPOTHESIS-ID: m5-retail-hangar-caller

## Work unit

Run one bounded retail-oracle capture with the validated eleven-Start route.
Keep the whole-RDRAM, exact image-range, title, and hangar controls. Watch both
the actual `jal` callsite `0x8008F2CC` and callee/store-helper entry
`0x800078EC`, but phase-gate the field table only to title and hangar. Use
`--pc-field-dump 0x8008F2CC` and the exact `--store-field-dump
2:0x800078EC`; do not field-dump the high-frequency callee. Observation-only;
no port change.

## Competing hypotheses and discriminator

- H-HangarCallerSamePath: the hangar caller and exact-store callee rows share
  the phase-local tuple and return relation.
- H-HangarCallerToOtherPath: the hangar caller reaches `0x8008F2CC`, but its
  tuple or return relation differs from the exact-store rows.
- H-HangarCallerUnreached: controls pass but no hangar caller row exists.

The discriminator is one same-run hangar-keyed table joining caller field rows
to exact-store callee rows. A matching tuple/return relation selects
H-HangarCallerSamePath; a nonmatching caller with valid callee rows selects
H-HangarCallerToOtherPath; zero caller rows with valid controls selects
H-HangarCallerUnreached.

## Exact validation

Use the existing oracle binary and recipe shape, changing only the phase
field buckets and removing the high-frequency callee field dump:

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 120 --watch-write 0x0:0x800000 --watch-write 0x167650:0x167C50 --watch-write 0x1798B0:0x179A48 --watch-pc 0x8008F2CC,0x800078EC --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 --pc-field-dump 0x8008F2CC --store-field-dump 2:0x800078EC --hit-cap 200 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150

Require whole-RDRAM positive control, title `0x00790400:1024`, hangar
`0x006AB400:512`, and exact-range totals before interpreting nulls.
