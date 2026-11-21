# NEXT (s7734)
HYPOTHESIS-ID: owner-looks-or-new-report

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report, then any
new SOAK-RESULTS.md lines.
If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay green. After any src/ or lib/ edit run the gate sweep
(`python3 tools/s7651_gate_sweep.py --jobs 2`, ~10+ min, background, no build while it runs: CPU cap 2).

Closed, do not repeat: s7726-s7732 census passes; s7733 DEAD filter (76 dead Python reader texts, s7714+s7716 filter,
`--dead`, controls PASS; fixup_factor5_ucode `_old_cap` removed as a proven no-op).

Candidate bounded item if nothing above applies: the census models SCRIPT text, never the compiled tree.
s7733 example: ROGUESQ_S4562_PAUSE's apply_s4562 texts are dead; the live reader at ../N64Recomp/RecompiledFuncs/funcs_24.c:10823
carries a later `if (!e) e = "4"; /* s4786 default */`, so unset ARMS the hold. Hypotheses: H-covered (every getenv in the
compiled tree models to the same signature as some live script/host reader of that name, so script-text modelling is enough)
vs H-hidden (some compiled readers differ, like S4562: a later rewrite changed the reading and no modelled site shows it).
Discriminator: one pass, `t.model_site` over every `getenv("ROGUESQ_*")` line in RecompiledFuncs/*.c + build/factor5_ucode/*.c
(C, not .py), compare each signature to the set of modelled signatures of the same name (s7714 load_sites). Planted control:
a copy of funcs_24.c text with the s4786 default line stripped must model differently from the real one (unset 0 vs 1).
For each H-hidden name: read it (grep PORTING-STATE for the session that added the rewrite, e.g. `s4786`) and either class it
(deliberate default, reviewed) or fix the script text that still claims the old reading. If generated readers vote, gate it
in tools/s7714_truth_census.py (generated sites as voters; skip if ../N64Recomp absent, as the DEAD filter does).
Note: PORTING-STATE ~155700 shows s4786 made the S4562 default deliberate (env-unset default check, RELEASED at reinit), so it is likely "reviewed: deliberate default"; the pass is about finding any OTHER hidden name.
