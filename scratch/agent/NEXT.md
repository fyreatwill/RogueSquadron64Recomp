# NEXT work unit (s1040)

HYPOTHESIS-ID: retail-attract-phase-path

Run one new retail-oracle cadence discriminator with both arms in the same
iteration: eleven 150 ms Start pulses at the documented five-second cadence
versus eleven 150 ms Start pulses at a one-second cadence. Keep the
whole-RDRAM watch as the positive control and keep the freelist watch disarmed
until a 512 hangar-origin VI is observed.

## Competing hypotheses and discriminator

* `H-retail-cadence-sensitive`: a rapid Start cadence is required by the
  attract/title state machine; the one-second arm changes VI phase while the
  five-second arm does not.
* `H-retail-window-sensitive`: only the documented timing window works; the
  five-second arm changes phase while the one-second arm does not.
* `H-retail-schedule-independent`: neither cadence changes phase; both remain
  at width 320/origin `0x006dd280`.

Discriminating measurement: compare each arm's first independent `--vi-poll`
width/origin transition and final VI count. A transition to 512, especially
origin `0x6abxxx`, makes it safe to arm the bounded freelist watch in a
follow-up unit. The whole-RDRAM callback count must reach 10,000 in both arms,
and all eleven Start pad edges must be visible.

## Exact commands

Use the validated debugger-on, pure-interpreter core and repository ROM. Run
both arms concurrently for 60 seconds, with `--vi-trace --vi-poll --pif-trace`
and `--watch-write 0x0:0x2000000 --hit-cap 10000`. Use these schedules, varying
only cadence:

* five-second arm: `6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start`
* one-second arm: `6:start,7:start,8:start,9:start,10:start,11:start,12:start,13:start,14:start,15:start,16:start`

Use `--hold-ms 150` for both arms. Record ROM identity, callback removal,
Start pad words, VI transitions, and final VI count.
