# NEXT work unit (s1137)

HYPOTHESIS-ID: m4-retail-oracle-stall

Run one bounded oracle stall audit using the known-good `iter974-armB2` core,
the same retail ROM, plugins, and documented Start schedule, but with only the
whole-RDRAM positive-control watch and `--vi-trace` (no M4 target watch). Keep
the 180-second horizon and capture the process state if output stops after the
last press. Do not change the port probe or infer anything about the candidate
record range.

Competing hypotheses and discriminating outcomes:

- H-core-deadlock: the debugger core stops advancing at a repeatable emulated
  time while the positive control has already passed.
- H-ROM-path-stall: the core continues but the retail state machine remains at
  width 320 after the schedule; a longer/independent progress signal advances.
- H-launch-instrument-fault: removing the target watch changes the stall and
  the positive control or VI trace progresses beyond the prior stopping point.

Discriminator: final positive-control count, last VI/press timestamp, and
whether the no-target arm advances beyond the prior width-320 stop.

Expected command shape (resolve the configured oracle core/ROM paths from
`tools/oracle/README.md`):

```sh
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --secs 180 --watch-write 0x0:0x800000 \
  --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
```
