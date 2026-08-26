# NEXT work unit (s2427) — trace the retail title writer's exact store range

HYPOTHESIS-ID: m5-image-contract-gap

## Work unit

Use the retail oracle to watch the exact title guest-store range observed in
s2424 (`0x169730:0x169B30`) plus its adjacent field range and the existing
image ranges, while retaining whole-RDRAM, title, hangar, and candidate-PC
controls. This is a ground-truth-only run: do not change the port, task data,
output ranges, gates, guards, dispatch, or defaults.

## Competing hypotheses and discriminator

- H-RetailTitleExactWriter: `0x80015BC8` writes the exact `0x169730` title
  range with a phase-local histogram, matching the port guest-store identity.
- H-RetailTitleDifferentRange: the candidate executes but does not write the
  exact title range; writes are attributed to another PC or another range.
- H-RetailAdjacentOnly: the candidate writes only the adjacent/task-related
  range, leaving the exact port title range to another writer.
- H-ControlsInvalid: the whole-RDRAM or title/hangar phase control fails.

The discriminator is the same-run phase-keyed writer-PC histogram for
`0x169730:0x169B30`, the adjacent/task-related range, and the two existing
image ranges, joined to candidate execution rows. An exact `0x80015BC8` hit
selects H-RetailTitleExactWriter; valid controls with candidate writes only
elsewhere select H-RetailTitleDifferentRange; candidate writes only to the
adjacent range select H-RetailAdjacentOnly; any missing positive control
selects H-ControlsInvalid.

## Exact command

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 120 --hit-cap 10000 --watch-write 0x0:0x800000 --watch-write 0x169730:0x169B30 --watch-write 0x178D80:0x178F80 --watch-write 0x167650:0x167C50 --watch-write 0x1798B0:0x179A48 --watch-pc 0x80015BC8,0x8000F3A0 --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x006AB400:512 --pc-hist-watch 1 --pc-hist-watch 2 --pc-hist-watch 3 --pc-hist-watch 4 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150 --vi-trace > scratch/agent/s2427_m5_retail_title_writer/oracle.log 2>&1

Require whole-RDRAM threshold, both VI phases, and nonzero candidate-PC
execution before interpreting target-range nulls.
