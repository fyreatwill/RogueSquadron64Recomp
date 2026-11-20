# NEXT (s7693)
HYPOTHESIS-ID: after-regen-ub-gates-s7693

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
G6c is owner-judged (s7691 sheet; s7692 re-holds 6/6 clean). No owner-free G-rung is open.
Work unit: CURRENT-TRUTH Next-steps item 18 after-regen UB gates were last run before the s7672-s7690 G6c fixups
(apply_s7672..s7690 scripts in RS64_REPLAY). Rerun: tools/s7575_ir_calls.sh + `tools/s7575_break_census.py --controls --ir D`
(and the item-19 rerun-after-change censuses whose trigger text names fixup/apply changes; see PROJECT-OVERVIEW).
Hypotheses: H-clean (rc 0, census counts unchanged vs s7575 except the new hook bodies, every new site classified) vs
H-new (a G6c hook introduced an unclassified UB call/break site -> classify, guard or prove dead, commit).
Controls: --controls must report 10/10. Offline only; no game run needed. <=2 CPU-heavy jobs.
