# NEXT (s7732)
HYPOTHESIS-ID: owner-looks-or-new-report

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report, then any
new SOAK-RESULTS.md lines.
If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay green. After any src/ or lib/ edit run the gate sweep
(`python3 tools/s7651_gate_sweep.py --jobs 2`, ~10+ min: run it in the background, and do not build while it runs: CPU cap 2).

Closed, do not repeat: s7726/s7727 Objective-C over-release; s7728 false/no + LOG_ALL splits; s7729 unmodelled-site
classification; s7730 empty values; s7731 on/off words (normalised at launch to 0/1, kKeepWords for letter-mode readers,
census intent + letter-scan gates).

Candidate bounded item if nothing above applies: "=0 reads ON". s7731 maps `off` to "0", which only helps where "0" reads
off. The census signature shows presence readers where "0" reads ON (e.g. ROGUESQ_ASPECT sig unset=0 "0"=1: main.cpp
`as || fullscreen` opt-in window opens on ASPECT=0; OSMEM_MB tf reader "0"=1). Hypotheses: H-mode (the name is a value, not
a switch, so =0 has no off meaning: doc nothing) vs H-trap (OWNER-OPT-INS or README tells the owner `NAME=0` turns it off,
or the name is an owner switch, and some reader reads "0" as on). Discriminator: one pass over the census models listing
names whose some tf reader has sig["0"]==1 and sig[None]==0, crossed with OWNER-OPT-INS/README text containing `NAME=0`;
for each H-trap name, a same-binary live arm (`NAME=0` vs unset vs `NAME=1`) and a fix of the minority reader. Gate it in
tools/s7714_truth_census.py with a planted control as s7731 did.
