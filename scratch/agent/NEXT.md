# NEXT work unit (s1041)

HYPOTHESIS-ID: retail-attract-phase-path

Run one new retail-oracle first-input timing discriminator with both arms in
the same iteration: eleven 150 ms Start pulses at 1,6,11,...,51 seconds versus
the documented 6,11,...,56-second schedule. Keep the whole-RDRAM watch as the
positive control and keep the freelist watch disarmed until a 512 hangar-origin
VI is observed.

## Competing hypotheses and discriminator

* `H-retail-first-input-sensitive`: an early Start is required to arm the
  attract/title transition; the 1-second arm changes VI phase and the
  documented arm does not.
* `H-retail-documented-window-sensitive`: only the documented timing works;
  the documented arm changes phase and the early arm does not.
* `H-retail-phase-path-independent`: neither schedule changes phase; both stay
  at width 320/origin `0x006dd280`.

Discriminating measurement: compare each arm's first independent `--vi-poll`
width/origin transition and final VI count. A transition to 512, especially
origin `0x6abxxx`, makes it safe to arm the bounded freelist watch in a
follow-up unit. The whole-RDRAM callback count must reach 10,000 in both arms,
and all eleven Start pad edges must be visible.

## Exact commands

Use the validated debugger-on, pure-interpreter core
`/Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib`
and repository ROM `rogue_squadron.z64`. Run both arms concurrently for 60
seconds:

```sh
tools/oracle/build/rs64_oracle --core CORE --rom rogue_squadron.z64 --secs 60 \
  --oracle-debugger 1 --oracle-emulator 0 --vi-trace --vi-poll --pif-trace \
  --watch-write 0x0:0x2000000 --hit-cap 10000 --hold-ms 150 \
  --press '1:start,6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start'
```

The comparison arm uses the documented schedule:
`6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start`.
