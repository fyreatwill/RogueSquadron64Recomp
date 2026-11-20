# NEXT (s7717)
HYPOTHESIS-ID: setenv-after-static-init

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report, then
scratch/agent/CONTRACT-CARRY.md if it exists. If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay 8/8.

default-on-label-audit is CLOSED (s7716: tools/s7716_default_label_census.py gate, 0 LABEL-WRONG). Do not iterate it.

Idiom class to close in ONE pass: main.cpp applies ~38 auto-defaults with `setenv("ROGUESQ_X", v, 0)` (dd bundle s7037/s7258,
drain tick, ...). A reader that latches X in a NAMESPACE-SCOPE static initializer (global object ctor, `int g = []{..}()`,
`namespace { Init i; }`) runs BEFORE main, so it reads X unset and never sees the auto-default, unless it is re-read later.
Known handled instances: upstream_compat.cpp:587 S7239Init (DD_WIDEWIN_MERGE) re-run by rs64_s7258_merge_reinit;
g_rs64_s7030 forced to 1 by main.cpp after the setenv. Function-local statics (`static int m = -1; if (m < 0)`) are lazy and fine
iff first called after the setenv.
1. Enumerate every name main.cpp (and any other file) setenv's with overwrite 0 or 1; note the setenv's function and whether it
   runs before guest start.
2. For each, find every reader (s7716 census model_all gives sites) and classify: LAZY (function-local static / per-call),
   EAGER-REINIT (namespace-scope init with a reinit call after the setenv), EAGER-STALE (namespace-scope init, no reinit: the
   auto-default never reaches it = a real defect), or LAZY-EARLY (lazy but first called before the setenv, e.g. from another
   static init).
Hypotheses: H-clean (every eager reader has a reinit), H-stale (>=1 auto-default never reaches an eager reader).
Positive control: removing the rs64_s7258_merge_reinit call (planted text) must classify S7239Init as EAGER-STALE.
Runtime witness for any fix: one dd4 title boot printing the reader's latched value before/after (with =0 control).
Standing check after any src/ or lib/ change: `python3 tools/s7651_gate_sweep.py --jobs 2`. Owner defaults: never flip.
