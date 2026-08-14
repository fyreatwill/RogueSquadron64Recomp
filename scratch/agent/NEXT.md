# NEXT work unit (s1139)

HYPOTHESIS-ID: m4-retail-oracle-stall

Run one bounded debugger-off retail-oracle audit with the same `iter974-armB2`
core, ROM, and eleven-Start schedule, using VI polling as the positive
progress control and `--oracle-emulator 1`:

```sh
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --secs 180 --oracle-debugger 0 --oracle-emulator 1 --vi-poll \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
```

Competing hypotheses and the discriminating measurement:

- H-debugger-watch-overhead: debugger-off VI polling advances beyond width 320;
  debugger/watch callbacks are the stall source.
- H-mode-independent-core-stall: debugger-off VI polling also stays at width
  320; debugger/watch overhead is ruled out and the core scheduling/state-path
  boundary remains open.
- H-input/state-path: VI polling remains at width 320 while the scheduled
  inputs are accepted; the state-path boundary remains the live explanation.

Record the first nonzero VI, every later width/origin change, whether the poll
thread remains active through 180 seconds, and the final process result. With
debugger disabled, do not treat absent debugger callbacks or watch counts as
evidence; `--vi-poll` is the required control.

Record the first and last polled VI timestamps, every width/origin transition,
the final emulated-frame count, and process state if output stops. Do not add
the M4 target watch or infer ownership from a pre-shaded run.
