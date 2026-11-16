# NEXT (s7426)
HYPOTHESIS-ID: env-default-drift

First fold scratch/agent/SOAK-RESULTS.md for s7425_nobw_levels (RS64_BYTE_WATCH-off build/ qualification, L1/L5/L10). rc!=0 ->
read its log, and if a crash came from the change, set ROGUESQ_BYTE_WATCH=ON back and rebuild before anything else.

Class CI (CURRENT-TRUTH Next steps item 1): class CH showed the compile options are as intended. Are the RUNTIME defaults? Offline.
1. Enumerate every getenv("ROGUESQ_*"/"RS64_*") in src/, lib/N64ModernRuntime/{librecomp,ultramodern}, lib/rt64/src (our patches),
   include/, and the fixup-injected code in ../N64Recomp/RecompiledFuncs + build/factor5_ucode. For each: the default when unset
   (the else value / the parse of a missing var) and how it is parsed (atoi vs e[0]=='1' vs presence: "0" meaning ON is a bug).
   Note rs64_env_cache.cpp may cache/override getenv.
2. Compare with the documented defaults: docs/OWNER-OPT-INS.md, CURRENT-TRUTH (CULL_SPIKE on, DD_FARMAX 32767, DD_FOG_ALT,
   QOS_ALL, RETINA, RENDER_TO_RAM=0, NO_SAVE_WRITE exported by runner.sh, WIDE_EARLY, G5G hangar cam default on).
3. Flag: documented default != compiled default; one var parsed two different ways in two places; a presence-test var where docs
   say "=0 disables"; vars read but undocumented that change behaviour (not just logging).
4. Positive control: a planted copy of a source with a flipped default and one with a presence test must both be flagged.
Hypotheses: H-consistent (every documented default = compiled default, parse styles agree) vs H-drift (>=1 mismatch; then say who it
affects: owner recipe or test only, and fix it or fix the doc).
Write tools/s7426_env_defaults.py. Exit 0 = consistent, 1 = drift, 3 = control failed.
