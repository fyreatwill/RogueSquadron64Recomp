# NEXT work unit (s1043)

HYPOTHESIS-ID: retail-attract-phase-path

Run one same-build/same-run retail-oracle discriminator for the documented
6,11,...,56-second schedule: compare eleven 150 ms Start-only pulses with
eleven 150 ms simultaneous Start+A pulses. Keep the whole-RDRAM watch as the
positive control and keep the freelist watch disarmed until an independent VI
poll reports a 512 phase with hangar origin `0x6abxxx`.

## Competing hypotheses and discriminator

* `H-retail-start-state`: Start-only is insufficient because the retail path
  requires A confirmation; the Start+A arm reaches a 512 hangar-origin phase.
* `H-retail-input-state-independent`: both arms stay at width 320/origin
  `0x006dd280`, so adding A does not explain the duration-independent attract
  path.
* `H-retail-attract-demo`: an arm reaches width 512 with origin `0x690xxx`,
  identifying the attract demo rather than the hangar and leaving input-state
  handling unresolved.

Discriminating measurement: compare each arm's first `--vi-poll` width/origin
transition, transition time, and final VI count. A 512 transition at
`0x6abxxx` selects `H-retail-start-state` and permits a bounded freelist-watch
follow-up; identical width-320 traces select `H-retail-input-state-independent`;
`0x690xxx` selects `H-retail-attract-demo`. The whole-RDRAM callback count must
reach 10,000 in both arms, and every scheduled Start edge must be visible.

## Exact commands

Use the validated debugger-on, pure-interpreter core
`/Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib`
and repository ROM `rogue_squadron.z64`. Launch both commands concurrently
for 120 seconds, with distinct capture paths:

```sh
tools/oracle/build/rs64_oracle --core CORE --rom rogue_squadron.z64 --secs 120 \
  --oracle-debugger 1 --oracle-emulator 0 --vi-trace --vi-poll --pif-trace \
  --watch-write 0x0:0x2000000 --hit-cap 10000 --hold-ms 150 \
  --press '6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start'
```

The comparison arm uses the same schedule with simultaneous A, expressed as
two events at each timestamp:
`6:start,6:a,11:start,11:a,16:start,16:a,21:start,21:a,26:start,26:a,31:start,31:a,36:start,36:a,41:start,41:a,46:start,46:a,51:start,51:a,56:start,56:a`.
