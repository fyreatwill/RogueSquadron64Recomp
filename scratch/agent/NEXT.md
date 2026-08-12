# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

Run item -421's already-built E9-alignment discriminator from a logged-in,
GUI-capable macOS session:

    env BUDGET_S=2400 zsh scratch/agent/s670_postsec2_pulse_freeroll.sh

Do not change or rebuild the instrument. `ROGUESQ_LOG_DL_SYNC=1` and
`ROGUESQ_LOG_DL_SYNC2=1` are already in the recipe. The s673 headless context
could not initialize SDL (`The video driver did not add any displays`); the
harness now fails fast with exit 3 when that occurs.

## Competing hypotheses

- **H-e9-walker-misaligned:** naive `e9_a/e9_b` hits are coincidental payload
  bytes caused by its fixed eight-byte stride.
- **H-e9-not-translated:** E9 exists on real command boundaries, but the
  translator/dispatcher does not produce runner `syncs` for it.
- **H-mixed:** the post-sec2 population contains both task shapes.

## Discriminating measurement

After one recovery-active attempt reaches section 2 and logs a few hundred
post-sec2 tasks, match `[dl-sync-probe2] e9_aligned` to `[dl-sync-probe]`
`e9_a/e9_b` by task number (`s_n`/`#N`). Positive control: normal VI/game
progress plus nonzero probe2 task output in the same run.

- `e9_aligned ~= 0` where naive E9 is nonzero: walker-misaligned confirmed.
- `e9_aligned` tracks naive E9 broadly: not-translated confirmed; next inspect
  the runner's E9 dispatch path.
- Mixed result: classify by task shape (`tris`, `cmds_a/b`, `end_a/b`).

Do not rerun item -422, productize `DROP_GARBAGE_CIMG`, or chase packTlut.
