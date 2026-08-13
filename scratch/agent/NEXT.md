# NEXT work unit (oracle PIF input verification)

HYPOTHESIS-ID: m3-postsec2-lle-control

s766 established that the retail oracle itself runs and its whole-RDRAM watch
fires (11,774,702 writes / 4,195 VI), but the documented Start schedule did
not produce any 640, 1024, or 512 VI transition. The next unit is a short
oracle PIF trace, not a port build or target watch.

## Competing hypotheses

- H-input-reaches-pif: scheduled scancode-40 Start presses appear in PIF reads
  as Start bits, so the 320-only result is a game/phase timing divergence.
- H-input-not-mapped: the frontend logs injections but the input plugin does
  not deliver Start to the emulated controller; the phase result is
  H-retail-undriven-only.
- H-rom-or-config-mismatch: PIF sees Start, but the ROM/config differs from
  the documented setup and follows a different state machine.

## Discriminating measurement

Run the oracle with `--pif-trace`, a whole-RDRAM positive control, and a short
Start schedule. PIF reads containing the Start bit at the scheduled presses
select H-input-reaches-pif; no Start bit despite logged injections selects
H-input-not-mapped; correct Start bits with a continued 320-only trace selects
H-rom-or-config-mismatch. Do not add runtime instrumentation until this split
is made.

## Command

    tools/oracle/build/rs64_oracle \
      --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
      --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
      --secs 25 --pif-trace --vi-trace --watch-write 0x0:0x800000 \
      --press 6:start,11:start,16:start,21:start

Record PIF button words, positive-control hit count, and VI transitions.

ORIGIN for the closed 6w change: OVL1C_1E7C `jal 0x1ED4` sets r31=`0x1E8C`;
OVL1C_1ED4 saves `$ra→$30`; OVL1C_1F04 `jr $30` is the legitimate return.
