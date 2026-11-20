# NEXT (s7721)
HYPOTHESIS-ID: sweep-scoring-audit

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay green.

s7720 closed the hollow-GREEN list: s7384 (114/114 MULTI reviewed, 0 RACE) and s7557 (every default-on lever has a
PROJECT-OVERVIEW row) are GREEN, tools/gate_sweep_allowed_red.txt is empty, and the sweep's two new false-positive HOLLOWs
(s7392 reviewer prose "10 fails", s7558 "tags 34 open/undoc 0") have HOLLOW_OK rows.

Remaining hole, seen in s7720's own control: HOLLOW_KEYS is a fixed vocabulary. A gate printing `missing=3`, `stale=2`,
`race=1`, `need_fix=4`, `unmatched 7`, `defects=1` with rc 0 still scores GREEN.
Unit (ONE offline pass, no game run):
1. `env RS64_SWEEP_OUTDIR=scratch/s7721/out python3 tools/s7651_gate_sweep.py --jobs 2` (capture every gate's full output once).
2. Offline: enumerate every `<word>[=: ]<n>` / `<n> <word>` count token across all outputs; list each distinct key word with
   the gates and max value. Classify each key: OPEN-CLASS (a nonzero means unfinished work), INFO (sizes/totals), CONTROL.
3. Add every OPEN-CLASS key missing from HOLLOW_KEYS; rerun the scorer offline on the captured outputs; review each newly
   flagged gate by hand (HOLLOW_OK with a reason, or fix the tool / its rows).
Hypotheses: H-covered (no rc-0 gate prints a nonzero open-class key outside HOLLOW_KEYS), H-gap (>=1 does).
Positive control: plant an output line `SUMMARY missing=3` and `race=1` for a swept tool in the offline rescore: both must read HOLLOW.
Close: sweep ends 0 RED 0 HOLLOW. Then the slug is done; next take an owner item or G-rung per ITERATION 3c.
Owner defaults: never flip.
