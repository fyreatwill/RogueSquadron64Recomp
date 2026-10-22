# NEXT: repair the level-10 G1 route discriminator

HYPOTHESIS-ID: g1-mission-coverage

Work unit: inspect the level-10 route/phase evidence and make the smallest
recipe change that distinguishes a legitimate level-10 loading path from a
selector overwrite before flight. The repaired `a/b` pair launched and passed
`[lvsel]` in all five internal attempts per arm, but both ended
`allattempts-failed` at `nomission`; observed origins were only
`0x006A2900` and `0x00644D00`. Do not count this as coverage.

Competing hypotheses:

- H1: `0x006A2900`/`0x00644D00` are the legitimate level-10 load path and the
  recipe needs level-specific input or a later origin/phase gate.
- H2: the forced selector is overwritten after `[lvsel]`, so the observed path
  is not level 10 and the route needs a selector-state witness.
- H3: level 10 reaches a flight origin not recognized by the hard-coded
  `0x00690400` gate; the harness needs a level-specific mission-origin map.
- H4: the route is genuinely stuck in loading/viewer; a bounded rerun with the
  corrected gate will reproduce it as a new G1 route failure, not a crash.

Discriminator: correlate `[lvsel]`'s `cursor=10/res=0xA` with every subsequent
VI origin and selector-state line until flight. H1 predicts a stable level-10
loading-to-flight sequence after the route/input correction; H2 predicts a
selector/state change away from 10; H3 predicts a stable, previously unknown
flight origin; H4 predicts persistent `0x006A2900`/`0x00644D00` with no flight.
The positive control is `[lvsel]` itself; missing it makes a run unevaluable.

Exact evidence checks before any build/run:

```sh
rg -n '\[lvsel\]|origin=0x|flight|mission|level' scratch/agent/m6/g1_lvl10[ab]/fail_att*.log | tail -200
rg -n 'FORCE_SAVE_MISSION|MISSION_RE|006A2900|00644D00|690400' scratch/agent docs
```

Only after this discriminator is repaired and level 10 reaches flight should
the next unit consume level 10 `a/b`, then levels 11..18.
