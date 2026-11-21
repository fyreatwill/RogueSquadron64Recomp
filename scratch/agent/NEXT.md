# NEXT (s7731)
HYPOTHESIS-ID: owner-looks-or-new-report

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report, then any
new SOAK-RESULTS.md lines.
If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay green. After any src/ or lib/ edit run the gate sweep
(`python3 tools/s7651_gate_sweep.py --jobs 2`, ~10+ min: run it in the background).

Closed, do not repeat: s7726/s7727 Objective-C over-release; s7728 false/no + LOG_ALL splits; s7729 unmodelled-site
classification; s7730 empty values (stripped at launch in rs64_settings_apply; census VALUES include "").

Candidate bounded item if nothing above applies: values the census still does not probe that an owner could plausibly type:
"off", "true"/"on" (t/o first letter), " 1" / "1 " (whitespace from a settings file edited by hand; check whether
rs64_settings_parse_line trims). Hypotheses: H-agree (every reader of a name reads them the same way, even if "off" = on
everywhere: a doc issue, not a split) vs H-split (some name's readers disagree). Discriminator: add the values to VALUES in
tools/s7714_truth_census.py (one run), count unreviewed SPLIT; for each split, fix the minority reader and give a live
same-run control as s7730 did (pre-fix binary arm vs post-fix arm, plus a known-good value arm). If H-agree but "off" reads
as ON for owner-facing opt-ins (OWNER-OPT-INS names), consider teaching env parsing that "off"/"false"/"no" = 0 at launch
(the s7730 strip is the place) — only with a census control and never flipping a default.
