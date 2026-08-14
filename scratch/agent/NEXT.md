# NEXT work unit (s1042)

HYPOTHESIS-ID: retail-attract-phase-path

Run one new retail-oracle duration discriminator with both arms in the same
iteration for 120 seconds: eleven 150 ms Start pulses at 1,6,11,...,51
seconds versus the documented 6,11,...,56-second schedule. Keep the
whole-RDRAM watch as the positive control and keep the freelist watch disarmed
until a 512 hangar-origin VI is observed.

## Competing hypotheses and discriminator

* `H-retail-late-window-sensitive`: the early and documented schedules diverge
  once the run lasts long enough to reach the known late attract transition.
* `H-retail-duration-limited`: both schedules remain at width 320 through 120
  seconds, so the earlier null was a horizon limitation rather than an input
  timing discriminator.
* `H-retail-phase-path-independent`: both schedules reach the same non-320
  phases at the same relative time and origin.

Discriminating measurement: compare each arm's first independent `--vi-poll`
width/origin transition, transition time, and final VI count. A 512 transition
with origin `0x6abxxx` identifies the hangar and makes it safe to arm the
bounded freelist watch in a follow-up unit; `0x690xxx` is attract demo and is
not sufficient. The whole-RDRAM callback count must reach 10,000 in both arms,
and all eleven Start pad edges must be visible.

## Exact commands

Use the validated debugger-on, pure-interpreter core
`/Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib`
and repository ROM `rogue_squadron.z64`. Run both arms concurrently for 120
seconds:

```sh
tools/oracle/build/rs64_oracle --core CORE --rom rogue_squadron.z64 --secs 120 \
  --oracle-debugger 1 --oracle-emulator 0 --vi-trace --vi-poll --pif-trace \
  --watch-write 0x0:0x2000000 --hit-cap 10000 --hold-ms 150 \
  --press '1:start,6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start'
```

The comparison arm uses the documented schedule:
`6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start`.
