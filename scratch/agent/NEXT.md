# NEXT: identify the level-10 transition failure

HYPOTHESIS-ID: g1-mission-coverage

Work unit: compare the level-10 post-selector transition state and writer
sequence against the successful level-11 control, using existing logs first and
one batched probe/change only if the comparison identifies a concrete state
boundary. Do not count level 10 as coverage.

Competing hypotheses:

- H1 (rejected): the route only needed earlier post-selection input. Moving the
  first `a/sl/sr` event from 95 s to 64 s produced the same result in five of
  five attempts.
- H2: a later writer overwrites the selected mission or transition state after
  `[lvsel]`, despite the selector's final `cursor=10/res=0xA` witness.
- H3: level 10 enters a level-specific flight origin absent from the current
  `0x620400/0x690400` allowlist; the level-11 origin sequence is not universal.
- H4: level 10 is genuinely stuck in its loading/viewer transition at
  `0x006A2900`/`0x00644D00`, independent of selector and input timing.

Discriminator: name the first divergent post-selector state/write between
level 10 and level 11, then toggle or witness that state in one run. H2 predicts
a selector/mission-state write before the divergence; H3 predicts stable
level-10 flight frames at a new origin; H4 predicts no transition writer and
continued `0x006A2900`/`0x00644D00`. The positive controls are `[lvsel]` in
both runs and level-11's `mission_t=86s` / 300-second hold; missing either
makes the comparison unevaluable.

Exact evidence checks before any build/run:

```sh
rg -n '\[lvsel\]|^\[phase\].*origin=0x|mission_t|nomission' scratch/agent/m6/g1_lvl10c/fail_att*.log scratch/agent/m6/g1_lvl11a/run.log | tail -240
rg -n 'gCurrentLevel|level.*table|006A2900|00644D00|620400|690400|transition' src docs scratch/agent | head -240
```

Only after this discriminator is repaired and level 10 reaches flight should
the next unit consume level 10 `a/b`, then levels 12..18.
