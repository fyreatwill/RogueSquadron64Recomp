# NEXT (s7934)
HYPOTHESIS-ID: g5-owner-looks-standing
s7933 closed the retained-input class's last source: the manifest now also cites every scratch file a gate's traced run read
(build/gate_sweep_cache.json), --check prints `s7933 sweep-trace ... missing=0` (pinned in S7932_RETAIN).
0. `python3 tools/crash_reports.py --since 2026-11-25` first; a new report outranks everything. Fold new SOAK-RESULTS lines;
   a freeze_arms>0 verdict is a G5c datum (tools/s7920_hold_class.py on its ring).
1. Take the top open, not-owner-gated item of CURRENT-TRUTH "Next steps", or a "single-source" label a second line could
   settle; else the first unclosed rung of ITERATION.md 3c.
   Candidate: gate_trace.py's documented gap - os.stat/os.path.exists raise no audit event, so a gate whose verdict depends
   only on a path EXISTING is neither cache-keyed nor (now) manifest-protected by its trace. Census: grep tools/s7*.py run by
   the sweep for os.path.exists/isfile/getsize on scratch/ paths that are never opened; each hit -> ensure the path is a
   literal in the manifest scan or add an open; expected small (0-3), close the class with a planted control.
