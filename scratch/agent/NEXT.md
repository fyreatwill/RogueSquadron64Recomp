# NEXT work unit (s1138)

HYPOTHESIS-ID: m4-retail-oracle-stall

Run one bounded retail-oracle execution-mode audit with the same `iter974-armB2`
core, ROM, eleven-Start schedule, VI trace, and whole-RDRAM positive-control
watch, adding `--oracle-emulator 1`:

```sh
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --secs 180 --oracle-emulator 1 --watch-write 0x0:0x800000 --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
```

Competing hypotheses and discriminator:

- H-interpreter-stall: emulator 1 advances beyond width 320; the prior
  interpreter execution mode is the stall.
- H-mode-independent-core-stall: emulator 1 reproduces the post-56-second
  stop with positive control and presses intact; execution mode is ruled out.
- H-input/state-path: the mode change does not advance VI, but the press/control
  evidence remains healthy; the retail state-path boundary stays open.

Record the final control count, last VI and press timestamps, and process state
if output stops. Do not add the M4 target watch or infer ownership from a
pre-shaded run.
