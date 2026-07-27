# RS64 Recomp — session rules

Read `docs/CURRENT-TRUTH.md` before doing ANY work. `PORTING-STATE.md` is the
append-only log; ~two dozen of its conclusions are superseded — never act on it
without checking CURRENT-TRUTH. Project overview: `docs/PROJECT-OVERVIEW.md`.
Autonomous-operation contract: `tools/agent/ITERATION.md`. Setup rationale:
`docs/AUTONOMY-PLAN.md`.

`AGENTS.md` is the ORIGINAL upstream author's guidance (Windows paths,
PowerShell, `E:\Projects\...`). It is historical context, not instructions for
this macOS port — CURRENT-TRUTH wins wherever they disagree.

The loop is runner-agnostic (`tools/agent/runner.sh`): `RUNNER=claude` (default,
`LOOP_MODEL` picks the model), `RUNNER=grok`, `RUNNER=codex`, or `RUNNER=custom`
with `RUNNER_CMD`. The Stop-hook gate in `.claude/settings.json` is a Claude
Code feature — codex and grok never run it, so `loop.sh` also runs
`tools/agent/stop_gate.sh --verify` after every iteration whatever the runner,
and re-invokes with the unmet condition. **If you add a contract rule, put it in
`stop_gate.sh`, not in the hook config, or it will only apply to Claude.**

Hard rules:
- Regen order: `make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py` -> `cmake`.
  The fixup step is NOT optional. Hand-edits to generated code go in the fixup
  scripts (`tools/fixup_*.py`) or they die at the next regen.
- NEVER run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. `lib/` carries months of uncommitted patches. They are
  mirrored in `submodule-patches/*.patch`; `./submodule-patches/apply.sh`
  restores them, `./submodule-patches/export.sh` refreshes them. **Any edit
  under `lib/` must be followed by `export.sh` + a commit in the same session.**
- Kill the game with SIGKILL, not SIGTERM. Run it from `build/` with the ROM
  beside it. Metal rebuilds need
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`.
- A null result without a same-run positive control is not a result.
- No cross-run A/B on animating scenes — phase-gate on VI transitions.
- Capture once, analyze many: prefer one dump flag re-analyzed offline over
  three counters each costing a build-run cycle.
- One game run at a time. Parallelism goes into offline analysis and docs only.
- The ledger is the only memory. Work done outside this repo's ledger either
  gets written into PORTING-STATE.md or it did not happen. Keep CURRENT-TRUTH
  under ~35 KB — migrate durable material to PROJECT-OVERVIEW.md and prune.
- End every working session by updating `PORTING-STATE.md` +
  `docs/CURRENT-TRUTH.md` and committing.
