# NEXT work unit (s2429) — ground-truth the unresolved hangar image consumer

HYPOTHESIS-ID: m5-image-contract-gap

## Work unit

Run one independent retail-oracle capture for the unresolved hangar consumer.
This is the complete work unit; defer any port capture until the oracle selects
the writer set. Keep the port behavior unchanged: do not remap output, alter
task data, change gates, add guards, or change defaults.

## Competing hypotheses and discriminator

- H-RetailHangarConsumerPC: retail exact image-range writes are attributed to
  one stable hangar PC whose execution and writes can be watched independently.
- H-RetailHangarHelperSet: the range is written by multiple helper PCs, so no
  single consumer identity is valid at this scope.
- H-RetailHangarNoWriter: exact hangar range writes are absent after valid
  whole-RDRAM, phase, and execution controls.
- H-RetailControlInvalid: the oracle misses its whole-RDRAM, title, hangar, or
  named-PC positive controls.

The discriminator is one oracle table combining whole-RDRAM, title/hangar VI
controls, exact hangar image-range writes (`0x167650..0x167C50` and
`0x1798B0..0x179A48`), and execution watches for every writer PC attributed in
those ranges. A valid single-PC attribution selects H-RetailHangarConsumerPC;
a valid multi-PC attribution selects H-RetailHangarHelperSet; valid controls
with no exact writes select H-RetailHangarNoWriter; missing positive controls
select H-RetailControlInvalid. Arm the whole-RDRAM watch first and require its
positive threshold before interpreting any null.

## Exact command

    env tools/oracle/build/rs64_oracle \\
      --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \\
      --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \\
      --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \\
      --secs 120 --watch-write 0x0:0x800000 \\
      --watch-write 0x167650:0x167C50 --watch-write 0x1798B0:0x179A48 \\
      --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start

Require the whole-RDRAM positive threshold and title/hangar VI controls before
interpreting exact-range nulls. Record every PC attributed in each exact range;
the following iteration must add execution watches for that complete set.
