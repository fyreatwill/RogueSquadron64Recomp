# NEXT work unit (s1174)

HYPOTHESIS-ID: musyx-downstream-ground-truth-pointer-origin

Add a one-instruction post-step snapshot in the retail oracle after the
attributed write to physical `0x001496F8`, then rerun the calibration. The
current callback is before the MIPS store, so its `DebugMemRead32` value is not
the value written by that instruction.

Competing hypotheses and discriminator:

- H1: stepping the triggering instruction and reading the field immediately
  afterward exposes a changed, valid KSEG0 voice-array base; the next `0x88`-
  stride voice/sample watch can be defined.
- H2: the post-step snapshot is still `0xFFFFFFFF` or otherwise invalid; the
  callback timing/API cannot expose the store and a different ground-truth
  readout is required.
- H3: stepping perturbs the debugger path or breaks accounting, shown by a
  missing whole-RDRAM positive control or a read/write count mismatch; no
  pointer conclusion is allowed.

The discriminating measurement is the value printed after stepping the exact
instruction attributed to `0x8008F0EC`, together with the whole-RDRAM threshold
and separate per-watch read/write totals.

Exact commands:

    apply_patch tools/oracle/rs64_oracle.c
    ./tools/oracle/build.sh
    ./tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 10 --watch-write 0x0:0x800000 --hit-cap 10000 --watch-write 0x1496F8:0x1496FC --detail-watch 1 --watch-read 0x1496F8:0x1496FC --detail-watch 2 --press 6:start --hold-ms 150 --vi-trace

Require the whole-RDRAM threshold/removal, a write attribution, and the
post-step snapshot before using any pointer value.
