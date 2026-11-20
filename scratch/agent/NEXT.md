# NEXT (s7716)
HYPOTHESIS-ID: default-on-label-audit

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report, then
scratch/agent/CONTRACT-CARRY.md if it exists. If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay 8/8.

truth-census-coverage is CLOSED (s7715: 708 modelled, residue = pass-ons/foreign/no-decision, do NOT iterate the parser).
Both label defects it found (s7714 AUDIO_UCODE, s7715 M5_C88_VALUE) share one idiom: a setting whose DEFAULT was flipped to
on ("unset = on, =0 restores old") while its diagnostic labels kept the generic `e && e[0] && e[0] != '0'` test, so logs
name the wrong arm for unset. Close that idiom class in ONE pass (an idiom-class audit, not a parser change):
1. Enumerate default-on names: docs/debug-trace-env-vars.md + docs/OWNER-OPT-INS.md rows saying unset/default on or "=0
   restores", plus the s7714 census names whose behaviour site signature starts with 1 (unset on).
2. For each, grep EVERY reader incl. the 31 census "passed on" sites (the reader may hand e to a helper, like
   rs64_s7715_c88_label): `grep -rn 'getenv("NAME")' src lib/rt64/src lib/N64ModernRuntime tools/*.py`.
3. Classify each reader: behaviour / label-agrees / LABEL-WRONG (unset prints off). Fix every LABEL-WRONG in src/ like s7715
   (helper + S7716_*=0 old); vendored-fixer labels need a matching funcs_*.c mirror (s7714 precedent).
Hypotheses: H-two (AUDIO_UCODE and C88 were the only ones), H-more (other flipped defaults carry stale labels).
Positive control: the audit must flag the pre-s7715 C88 label (`git show HEAD~1:src/main/upstream_compat.cpp`) as LABEL-WRONG.
Runtime witness for any fix: one boot per arm printing the label (unset, =0 control, old-label env).
Standing check after any src/ or lib/ change: `python3 tools/s7651_gate_sweep.py --jobs 2`. Owner defaults: never flip.
