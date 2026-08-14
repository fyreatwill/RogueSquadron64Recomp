# NEXT work unit (s1039)

HYPOTHESIS-ID: retail-attract-phase-path

Run one new retail-oracle attract-path discriminator with both arms in the
same iteration: the verified eleven-pulse Start schedule versus the same
schedule with a sustained Start hold at each edge. Keep the whole-RDRAM watch
as the positive control and keep the freelist watch disarmed until a 512
hangar-origin VI is observed.

## Competing hypotheses and discriminator

* `H-retail-edge-only`: the attract transition consumes Start edges, so the
  existing pulse arm reaches a non-320 phase while the hold arm does not.
* `H-retail-level-only`: the transition requires a held Start level, so the
  hold arm changes VI phase while the pulse arm remains at width 320.
* `H-retail-path-independent`: neither input shape changes the phase; both
  remain at width 320/origin `0x006dd280`.

Discriminating measurement: compare each arm's independent `--vi-poll` first
width/origin transition and final VI count. A transition to 512 (especially
origin `0x6abxxx`) makes it safe to arm the bounded freelist watch in a
follow-up unit; unchanged 320 in both arms closes this input-shape family.
The whole-RDRAM callback count must reach 10,000 in both arms.

## Exact commands

Use the prescribed debugger-on, pure-interpreter core and fresh config dirs.
Run both arms concurrently, each with the same 60-second limit, 11 Start
times, `--vi-trace --vi-poll --pif-trace`, and the whole-RDRAM watch with
`--hit-cap 10000`; vary only the per-edge hold duration (150 ms pulse versus
2000 ms hold). Record ROM identity, callback removal result, VI transitions,
and pad words from both outputs. Do not arm the freelist watch in this unit.
