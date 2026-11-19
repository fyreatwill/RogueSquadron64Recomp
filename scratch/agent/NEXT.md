# NEXT (s7673)
HYPOTHESIS-ID: hm-census-settings-row

s7672 fixed the G6c stand-in blink at spawn (ROGUESQ_S7672_HOLD). First: `python3 tools/crash_reports.py --since 2026-11-13`
(a NEW report outranks everything), then any owner report.
Unit: CURRENT-TRUTH Next steps item 23. `python3 tools/s7614_hm_census.py --controls` FAILs on one OPEN row,
src/main/rs64_settings.cpp `p.vars` (no member row; came in with s7663). Hypotheses: H-host (p.vars holds host strings/pointers only,
never guest memory -> add a 'host' row with the evidence), H-guest (it retains a pointer into rdram or a guest-derived buffer ->
real HM finding, fix ownership). Discriminator: read the struct and every store to p.vars (the census prints the member kinds);
guest-derived stores (TO_PTR/rdram+) select H-guest. Close when the census exits 0 with its 8/8 controls still PASS.
Then: G6c handoff polish if worth it (held stand-ins culled by their own view test while the real object is too = off-screen, not a
defect), or the next owner item. One game at a time, SIGKILL only, never touch build/saves, <=2 CPU-heavy jobs, no repeat-hold soaks.
