# NEXT work unit (oracle configuration/ROM divergence)

HYPOTHESIS-ID: oracle-320-only-divergence

s768's 70-second run proved all 11 scheduled Start presses reach the retail
game (`0x7C4=0x10000000`) and the whole-RDRAM control fires, but VI remains
320-only. This conflicts with the documented phase timeline, so isolate the
oracle-side divergence before returning to port hypotheses.

## Competing hypotheses

- H-oracle-rom-mismatch: the ROM path/hash differs from the retail ROM used
  for the documented phase timeline.
- H-oracle-config-mismatch: the core/input/config/plugin setup differs in a
  way that preserves PIF Start reads but prevents phase advancement.
- H-oracle-observed-320: the documented timeline is not reproducible in this
  current oracle environment even with correct PIF delivery.

## Discriminating measurement

Run one same-run oracle identity/configuration check: print and record the ROM
hash, use the documented ROM path, materialize a fresh config directory, and
repeat the phase schedule with `--pif-trace --vi-trace` and the whole-RDRAM
positive control. A hash mismatch selects H-oracle-rom-mismatch; a matching
hash with a phase transition after fresh-config materialization selects
H-oracle-config-mismatch; a matching hash, positive control, Start words, and
320-only result selects H-oracle-observed-320. Do not add port instrumentation
until this split is measured.

## Command

    shasum -a 256 /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
    rm -rf /tmp/rs64-oracle-config-next
    mkdir -p /tmp/rs64-oracle-config-next
    tools/oracle/build/rs64_oracle \
      --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
      --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
      --configdir /tmp/rs64-oracle-config-next \
      --secs 70 --pif-trace --vi-trace --watch-write 0x0:0x800000 \
      --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start

Record the SHA-256, config path, PIF button words, positive-control hit count,
and VI transitions. Keep the corrected oracle trace source/build; do not
revert the `w0 || w1` trigger. The next run must have a positive-control hit
count and all three outcomes above must remain distinguishable.

ORIGIN for the s767 oracle fix: PIF trace output previously checked only
`w1`; the button word is observed as `0x10000000` in `0x7C4`.
