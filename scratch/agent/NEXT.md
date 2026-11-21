# NEXT (s7730)
HYPOTHESIS-ID: owner-looks-or-new-report

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report, then any
new SOAK-RESULTS.md lines.
If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay green. After any src/ or lib/ edit run the gate sweep
(`python3 tools/s7651_gate_sweep.py --jobs 2`, ~10+ min: run it in the background).

Closed, do not repeat: s7726/s7727 Objective-C over-release; s7728 false/no + LOG_ALL splits; s7729 unmodelled-site
classification (81 classed, census exits 1 on any new unclassified reader).

Candidate bounded item if nothing above applies: the empty-value ("") splits from s7729's side probe for the SHELL route
(settings files are fixed): ROGUESQ_ASPECT main.cpp:14498 (`e || fullscreen`), ROGUESQ_OSMEM_MB main.cpp:14860 (`e ? 1 : 0`),
HWBP_ADDR main.cpp:12003. Hypotheses: H-harmless (an empty value takes the same path as unset at every reader: e.g. ASPECT ""
falls to 4:3) vs H-split (one reader takes the opt-in branch with an empty string). Discriminator: make those 3 readers use
`e && *e`, then add "" to VALUES in s7714_truth_census.py and require 0 unreviewed SPLIT; live run `env ROGUESQ_ASPECT= ` vs
unset, compare the [g1d] aspect lines (same run positive control: ROGUESQ_ASPECT=16:9 arm). Owner defaults: never flip.
