# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

Build and run one same-task E9 dispatch-stage discriminator for item -421.
Do not change E9 behaviour or inject a sync. Add phase-budgeted counters/logs
at three existing stages, all gated by one new `ROGUESQ_LOG_E9_DISPATCH=1`:

1. RT64 interpreter immediately before dispatch when the decoded opcode is
   `0xE9` (positive control: also count all decoded commands and `0xE7`).
2. `GBI_F3DFACTOR5::fullSync_logged` entry.
3. `State::fullSync` entry plus the runner task number/counter snapshot already
   available around `[dl-sync-probe]`.

Scope/reset every budget at section 2 or the existing post-sec2 task phase;
include the task number in every stage so counts can be joined within one run.
Because this edits `lib/rt64`, export the submodule patch before committing:

    ./submodule-patches/export.sh
    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8
    env BUDGET_S=2400 zsh scratch/agent/s670_postsec2_pulse_freeroll.sh

Wire `ROGUESQ_LOG_E9_DISPATCH=1` into the recipe before the run. Preserve the
existing `ROGUESQ_LOG_DL_SYNC=1` and `ROGUESQ_LOG_DL_SYNC2=1` controls. Batch
all counters into this one build/run cycle.

## Competing hypotheses

- **H-e9-pre-dispatch-loss:** the authoritative interpreter never decodes the
  command-boundary E9 population seen by the diagnostic walker (control-flow
  or command-length model differs before map dispatch).
- **H-e9-map-or-handler-loss:** interpreter pre-dispatch sees E9, but the
  Factor5 `fullSync_logged` handler is not entered (map replacement/mismatch).
- **H-e9-post-handler-loss:** handler entry tracks pre-dispatch E9, but
  `State::fullSync` or runner `hist[0x29]` does not track it.

## Discriminating measurement

For each post-sec2 task, compare `e9_aligned`, interpreter E9, handler entry,
`State::fullSync`, and runner `syncs`. Positive control in the same run:
section 2 reached, thousands of interpreter commands decoded, nonzero E7, and
nonzero `e9_aligned`.

- Aligned E9 high, interpreter E9 near zero: H-e9-pre-dispatch-loss confirmed;
  next compare the authoritative interpreter's PC advances/control flow with
  `docs/F5-UCODE-REFERENCE.md`.
- Interpreter E9 high, handler near zero: H-e9-map-or-handler-loss confirmed;
  inspect Factor5 map lifetime/ucode switches.
- Handler high, `State::fullSync` or runner syncs near zero: H-e9-post-handler-loss
  confirmed; inspect the first diverging stage only.
- All stages track but `rdpFs` stays flat: the runner metric is not the missing
  sync witness; reframe -421 without landing a mitigation.

Do not rerun item -422, productize `DROP_GARBAGE_CIMG`, or add a synthetic
FULL_SYNC in this work unit.
