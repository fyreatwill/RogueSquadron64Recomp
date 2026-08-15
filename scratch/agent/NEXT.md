# NEXT work unit (s1173)

HYPOTHESIS-ID: musyx-downstream-ground-truth-pointer-origin

Fix the oracle's watch accounting so a read watch is distinguished from a
write watch, then run one short calibration arm that captures the first
post-store read of retail `0x001496F8`. Use that value to define the next
voice-array/sample-field range; do not infer it from the pre-store callback.

Competing hypotheses and discriminator:

- H1: a distinct post-store read exposes a valid KSEG0 voice-array base; the
  target range can be mapped and the next retail writer watch is actionable.
- H2: the field is written but no post-store read occurs before the retail
  width-320/origin `0x006dd280` stall; the current oracle path cannot map the
  dynamic array and needs a different ground-truth readout.
- H3: the watch callback flags or address semantics remain unusable, shown by
  a read/write count mismatch in the positive-control calibration; no origin
  conclusion is allowed.

The discriminating measurement is the first callback after the attributed
`0x001496F8` write whose flags contain READ, plus separate per-watch counts.
H1 is a valid pointer value; H2 is a clean post-store-read zero before the
stall; H3 is any callback/accounting mismatch or failed whole-RDRAM control.

Exact commands:

    apply_patch tools/oracle/rs64_oracle.c
    ./tools/oracle/build.sh
    ./tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 10 --watch-write 0x0:0x800000 --hit-cap 10000 --watch-write 0x1496F8:0x1496FC --detail-watch 1 --watch-read 0x1496F8:0x1496FC --detail-watch 2 --press 6:start --hold-ms 150 --vi-trace

Require the whole-RDRAM threshold/removal, a write attribution, and a
separately identified read callback before using any pointer value.
