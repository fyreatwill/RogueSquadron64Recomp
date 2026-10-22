# NEXT: identify the level-10 transition-dispatch writer

HYPOTHESIS-ID: g1-mission-coverage

Work unit: add one batched, phase-gated diagnostic for the concrete boundary
already found in existing logs: the first section-4 DMA after `[lvsel]` and the
following `cineBody`/level-state transition. Run level 10 and level 11 controls
in the same build, with all counters enabled, and do not count level 10 as
coverage.

Competing hypotheses:

- H1 (rejected): the route only needed earlier post-selection input. Moving the
  first `a/sl/sr` event from 95 s to 64 s produced the same result in five of
  five attempts.
- H2: a later writer overwrites the selected mission or transition state after
  `[lvsel]`, despite the selector's final `cursor=10/res=0xA` witness.
- H3: level 10 uses a level-specific flight origin and the current origin
  allowlist is incomplete.
- H4: level 10 is genuinely stuck in its loading/viewer transition at
  `0x006A2900`/`0x00644D00`, independent of selector and input timing.
- H5: the level-10 cinematic dispatch is delayed or skipped because the
  section-4 overlay call reaches a different overlay/state path; stale
  `curOvl=1`/`STAR` is the immediate symptom.

Discriminator: capture the first post-section-4 `cineBody` caller/argument,
`gCurrentLevel`, `curOvl`, `cineState`, and VI origin in both arms. H2 predicts
`gCurrentLevel` or a transition-state overwrite before the missing dispatch;
H3 predicts a stable level-10 origin distinct from `0x00690400` after a real
flight handoff; H4 predicts no dispatch and continued `0x006A2900`/`0x00644D00`;
H5 predicts section-4 DMA plus stale `curOvl=1`/`STAR` with a missing or
misrouted `cineBody` call. Positive controls are `[lvsel]` in both arms,
section-4 DMA in both arms, and level-11 `mission_t=86s`/300-second hold.

Evidence consumed this iteration: five level-10 attempts reproduce the
stale-state/no-immediate-`cineBody` sequence; the level-11 control shows the
reset/dispatch sequence and reaches flight. The next diagnostic must name the
writer/caller, not merely add another phase field.

Exact preflight/build/run commands:

```sh
rg -n '\[lvsel\]|^\[phase\].*origin=0x|mission_t|nomission' scratch/agent/m6/g1_lvl10c/fail_att*.log scratch/agent/m6/g1_lvl11a/run.log | tail -240
rg -n 'gCurrentLevel|level.*table|006A2900|00644D00|620400|690400|transition' src docs scratch/agent | head -240
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Run the corrected level-10 arm and level-11 control with
`ROGUESQ_LOG_LEVEL=1` and `ROGUESQ_LOG_PHASE=1`, capturing from `build/` and
SIGKILLing only after the phase-gated transition or a 30-second unchanged-origin
stall. A named writer/state selects H2; a new stable flight origin selects H3;
no writer plus stale state selects H4/H5 and moves the next probe to the overlay
dispatch caller. Only after level 10 reaches flight should the next unit consume
level 10 `a/b`, then levels 12..18.
