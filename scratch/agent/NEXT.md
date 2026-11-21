# NEXT (s7733)
HYPOTHESIS-ID: owner-looks-or-new-report

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report, then any
new SOAK-RESULTS.md lines.
If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay green. After any src/ or lib/ edit run the gate sweep
(`python3 tools/s7651_gate_sweep.py --jobs 2`, ~10+ min: run it in the background, and do not build while it runs: CPU cap 2).

Closed, do not repeat: s7726/s7727 Objective-C over-release; s7728 false/no + LOG_ALL splits; s7729 unmodelled-site
classification; s7730 empty values; s7731 on/off words; s7732 "=0 reads ON" (ASPECT fixed at launch, 17 others reviewed in
ZERO_ON_REVIEWED, gate zero_on_check).

Candidate bounded item if nothing above applies: dead reader text in the truth census. s7732 found that
tools/fixup_factor5_ucode.py:228 (`_new_cap`, ASPECT `wide`) is modelled as a live ASPECT reader, but its replace anchor
`_old_cap` matches nothing since s6762 (src/rsp/dpc_bridge.cpp:213 cap = 65536 always). Hypotheses: H-dead (more apply/fixup
REPLACEMENT texts whose anchor matches nothing in the current generated tree are counted as readers, so census SPLIT/agree
verdicts include dead code) vs H-live (that one is alone). Discriminator: one pass over every tools/apply_*.py / fixup_*.py
site the census models, test whether the replacement text (or its anchor) occurs in the generated output it targets
(build/factor5_ucode/*.c, RecompiledFuncs/, src/rsp/*.cpp); planted control: a fake site with an anchor that cannot match must
be flagged. For each H-dead site: drop the dead replace from the script (regen-safe: it is a no-op today) or class it DEAD in
the census so it stops voting. Gate it in tools/s7714_truth_census.py.
