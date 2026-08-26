# NEXT work unit (s2431) — execute-watch retail hangar image writers

HYPOTHESIS-ID: m5-image-contract-gap

## Work unit

Run one independent retail-oracle capture with execution watches for every PC
selected by s2430, phase-gated to the hangar origin. Keep port behavior
unchanged: do not remap output, alter task data, change gates, add guards, or
change defaults.

## Competing hypotheses and discriminator

- H-RetailHangarSemanticEntry: `0x800078EC` and/or a named helper executes in
  the hangar phase, providing an execution-level candidate for the image
  consumer.
- H-RetailHangarStoreHelpers: only the `0x8001FAxx`/`0x8001FBxx`/adjacent
  helpers execute in the phase, so the range attribution is a lower-level
  store family rather than a single semantic consumer.
- H-RetailHangarExecutionGap: valid phase controls pass but the complete
  selected PC set has no hangar execution hits, so writer attribution alone is
  insufficient to identify an executable consumer.
- H-RetailControlInvalid: the oracle misses whole-RDRAM or title/hangar
  positive controls.

The discriminator is one oracle table combining whole-RDRAM, title/hangar VI
controls, exact-range write counts, and phase-gated execution hits for the
complete selected set: `0x800078EC`, `0x80007670`, `0x8001E2C0`,
`0x8001FACC`, `0x8001FADC`, `0x8001FAE4`, `0x8001FAEC`, `0x8001FAF0`,
`0x8001FAF8`, `0x8001FB10`, `0x8001FB14`, `0x8001FBE4`, and `0x8001FD2C`.
Any hangar execution hit selects the corresponding semantic/helper class;
zero selected-PC hits with valid controls selects H-RetailHangarExecutionGap.
Arm the whole-RDRAM watch first and require its positive threshold before
interpreting any null.

## Exact command

    env tools/oracle/build/rs64_oracle \
      --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
      --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
      --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
      --secs 120 --watch-write 0x0:0x800000 \
      --watch-write 0x167650:0x167C50 --watch-write 0x1798B0:0x179A48 \
      --pc-hist-watch 1 --pc-hist-watch 2 --pc-hist-phase 0x006AB400:512 \
      --watch-pc 0x800078EC --watch-pc 0x80007670 --watch-pc 0x8001E2C0 \
      --watch-pc 0x8001FACC --watch-pc 0x8001FADC --watch-pc 0x8001FAE4 \
      --watch-pc 0x8001FAEC --watch-pc 0x8001FAF0 --watch-pc 0x8001FAF8 \
      --watch-pc 0x8001FB10 --watch-pc 0x8001FB14 --watch-pc 0x8001FBE4 \
      --watch-pc 0x8001FD2C --pc-phase-log-width 0x006AB400:512 \
      --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start
