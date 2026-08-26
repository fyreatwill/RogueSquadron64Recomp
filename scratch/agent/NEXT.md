# NEXT work unit (s2426) — test retail writes at the port image DMA ranges

HYPOTHESIS-ID: m5-image-contract-gap

## Work unit

Use the retail oracle to watch the exact title/hangar image-DMA destination
ranges observed in the fixed s2424/s2425 port capture, while also retaining
the whole-RDRAM, title, hangar, and candidate-PC controls. This is a
ground-truth-only run: do not change the port, task data, output ranges, gates,
guards, dispatch, or defaults.

## Competing hypotheses and discriminator

- H-RetailImageRangeWriter: retail writes one of the exact port image ranges
  in a target phase, with a candidate writer PC and phase-local histogram.
- H-RetailDifferentRange: retail candidate execution is valid, but writes no
  exact port image range while its phase/range activity remains elsewhere.
- H-RetailNoImageWrite: controls and candidate PCs are valid, but neither
  exact image range is written in title or hangar.
- H-ControlsInvalid: the whole-RDRAM or title/hangar phase control fails.

The discriminator is the same-run phase-keyed writer-PC histogram for exact
port ranges `0x167650:0x167C50` and `0x1798B0:0x179A48`, joined to candidate
execution rows. A target-range hit by a candidate PC selects
H-RetailImageRangeWriter; valid candidate/phase controls with only other-range
writes select H-RetailDifferentRange; valid controls with zero target writes
select H-RetailNoImageWrite; any missing positive control selects
H-ControlsInvalid.

## Exact command

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 120 --hit-cap 10000 --watch-write 0x0:0x800000 --watch-write 0x167650:0x167C50 --watch-write 0x1798B0:0x179A48 --watch-pc 0x80015BC8,0x8000F3A0 --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x006AB400:512 --pc-hist-watch 1 --pc-hist-watch 2 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150 --vi-trace > scratch/agent/s2426_m5_retail_image_ranges/oracle.log 2>&1

Require whole-RDRAM threshold, both VI phases, and nonzero candidate-PC
execution before interpreting target-range nulls.
