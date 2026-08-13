# NEXT work unit (E9 callback/task ownership audit)

HYPOTHESIS-ID: m3-e9-callback-task-ownership

Run one bounded source/telemetry audit before any parser-loss experiment.
Trace the exact caller and task-serial lifetime for:

- `src/main/main.cpp` `rs64_e9prov_aligned(task_serial, dl_ptr, e9_aligned)`;
- `src/rsp/dpc_bridge.cpp` `rs64_e9prov_aligned`, `rs64_e9prov_task_begin`,
  and `rs64_e9prov_task_end`;
- the LLE task mutex/threads around `rs64_run_lle_gfx` and any path that can
  overwrite global `g_e9prov` between callback and task end.

Competing hypotheses:

- H-callback-same-task: callback and task end share the same serial, but the
  selected `do_probe` path does not call the callback for the nonzero walker
  rows.
- H-global-overwrite: another LLE task overwrites global `g_e9prov` between
  the walker callback and task end, causing the missing aligned rows.
- H-serial-mismatch: callback receives a different task serial than the
  task-end owner, so the existing equality check discards it.

Discriminating measurement: source inspection must prove one of those call
paths, or add one rate-limited callback record containing passed task,
`g_e9prov.task`, `guestE9`, and the task-end serial. A callback with matching
serial but no task-end field selects H-callback-same-task; a differing current
serial selects H-global-overwrite or H-serial-mismatch. Missing callback
records with a proven caller selects H-callback-same-task. Do not change game
logic or parser accounting.

Exact audit commands:

    rg -n 'rs64_e9prov_aligned|rs64_e9prov_task_(begin|end)|g_e9prov|do_probe|g_lle_task_mutex|rs64_run_lle_gfx' src lib/rt64
    sed -n '880,990p' src/main/main.cpp
    sed -n '330,390p;920,1010p' src/rsp/dpc_bridge.cpp
    sed -n '1040,1070p' src/main/main.cpp

If source inspection cannot discriminate, make one build with the callback
record, run `zsh scratch/agent/s790_postsec2_reachability.sh` once with the
existing VI-1024 gate and positive controls, and evaluate only the callback
serial rows. Use the normal build pipeline for source changes; no mitigation.
