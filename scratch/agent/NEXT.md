# NEXT (s7735)
HYPOTHESIS-ID: owner-looks-or-new-report

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report, then any
new SOAK-RESULTS.md lines.
If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay green. After any src/ or lib/ edit run the gate sweep
(`python3 tools/s7651_gate_sweep.py --jobs 2`, ~10+ min, background, no build while it runs: CPU cap 2).

Closed, do not repeat: s7726-s7733 census passes; s7734 compiled-tree reader census (0 HIDDEN after fixing LOG_ALL s4159,
DD_CAPX_TOG s6548, M5_B40_VALUE ""; controls PASS).

Candidate bounded item if nothing above applies: wire tools/s7734_compiled_reader_census.py into tools/s7651_gate_sweep.py
(offline step, rc must be 0; skip when ../N64Recomp absent), then prove the regen chain reproduces the s7734 compiled text:
`tools/regen_replay.sh <copy of pristine>` then `tools/regen_verify.sh` (docs/REGEN-VERIFY.md) and rerun the s7734 census on the
replayed tree. Hypotheses: H-replays (the three edited scripts emit exactly the hand-synced compiled lines: census 0 HIDDEN on the
replayed tree) vs H-drift (a step re-writes one of them, e.g. fixup_live_replay's `_b` anchor not matching the vendored text, so
the replayed tree carries the old B40 form). Planted control: replay with the old fixup_live_replay.py must give B40 HIDDEN again.
The 14 NOREF (was ORPHAN) rows (FORCE_UNLOCK/-1 sentinels, POOLX/FARCLIP numbers, SPANFORCE presence "0" -> on) are numeric or diagnostic
readings with no modelled script site; SPANFORCE=0 forcing spans on is the only on/off-looking one (diagnostic, dd>1 forces it anyway).
