# NEXT (s7713)
HYPOTHESIS-ID: multi-reader-clamp-census

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report, then
scratch/agent/CONTRACT-CARRY.md if it exists. If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay 8/8.

s7712 found a defect class: one ROGUESQ_X read in several places with different clamps or defaults (DRAW_DISTANCE: apply_s6036
capped at 4 without UNSAFE, the dd bundle read the raw value; fixed in rs64_s7358_sanitize_env, [s7712-dd]). Close the CLASS
statically (an idiom-class audit, ITERATION item 3):
  tools/s7713_multireader_census.py: reuse the s7711 site finder (tools/s7711_optval_census.py) to list every ROGUESQ_X with >=2
  getenv sites; per site pull the clamp/default/parse idiom (atoi/atof/sscanf, min/max consts, default literal, "*e != '0'" vs
  pointer test). Flag X where the sites disagree on cap, floor, default or the =0 meaning. Each flag: classify as fixed upstream
  (sanitizer normalises first), harmless (diagnostic reader), or a defect -> normalise in rs64_s7358_sanitize_env like s7712.
Controls (same run): the pre-s7712 DRAW_DISTANCE pair (apply_s6036 cap 4 vs policy raw) with the sanitizer line masked -> must
flag; OSMEM_MB (recomp.cpp 4..16 vs upstream_compat 4..16) -> must agree.
Hypotheses: H-one (DRAW_DISTANCE was the only split), H-many (more splits exist), H-masked (splits exist but a sanitizer or
setenv upstream already makes every reader agree).
Standing check after any src/ or lib/ change: `python3 tools/s7651_gate_sweep.py --jobs 2`. Owner defaults: never flip.
