# NEXT work unit (s2430) — attribute the retail hangar image consumer

HYPOTHESIS-ID: m5-image-contract-gap

## Work unit

Run one independent retail-oracle capture for the unresolved hangar consumer,
with explicit phase-gated writer histograms for both exact image ranges. This
is the complete work unit; defer any port capture until the oracle selects the
writer set. Keep the port behavior unchanged: do not remap output, alter task
data, change gates, add guards, or change defaults.

## Competing hypotheses and discriminator

- H-RetailHangarConsumerPC: each exact range has one dominant/stable writer PC
  in the hangar phase.
- H-RetailHangarHelperSet: either exact range has multiple material writer PCs,
  so no single consumer identity is valid at this scope.
- H-RetailHangarNoWriter: valid controls pass but the phase-gated exact-range
  histograms are empty.
- H-RetailControlInvalid: the oracle misses its whole-RDRAM or title/hangar
  positive controls.

The discriminator is one oracle table combining whole-RDRAM, title/hangar VI
controls, exact hangar image-range writes (`0x167650..0x167C50` and
`0x1798B0..0x179A48`), and phase-gated writer-PC histograms for both ranges.
A one-PC histogram selects H-RetailHangarConsumerPC; a multi-PC histogram
selects H-RetailHangarHelperSet; valid controls with no exact writes select
H-RetailHangarNoWriter; missing positive controls select
H-RetailControlInvalid. Arm the whole-RDRAM watch first and require its
positive threshold before interpreting any null.

## Exact command

    env tools/oracle/build/rs64_oracle \\
      --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \\
      --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \\
      --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \\
      --secs 120 --watch-write 0x0:0x800000 \\
      --watch-write 0x167650:0x167C50 --watch-write 0x1798B0:0x179A48 \\
      --pc-hist-watch 1 --pc-hist-watch 2 --pc-hist-phase 0x006AB400:512 \\
      --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start

Require the whole-RDRAM positive threshold and title/hangar VI controls before
interpreting exact-range nulls. Record every PC in both shutdown histograms;
the following iteration must add execution watches for that complete set.
