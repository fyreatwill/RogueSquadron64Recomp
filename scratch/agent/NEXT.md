# NEXT: classify live-only patches; make scratch full-regen reproduce live RecompiledFuncs
HYPOTHESIS-ID: regen-path-repair

No owner authorization needed (see UNBLOCK.md). Work ONLY in ../N64Recomp/scratch_s4648/ (copy of s4204-fresh + repointed fixup copy;
harness in scratch/s4648/).
1. Build the exact list of patches present in live RecompiledFuncs but with no source in fixup_game_funcs.py (`diff -rq` of scratch fixup output vs live).
   Classify each as diagnostic-only or behavior-changing (s4563, s4296, s4580, s4571c, s4572 first).
2. Backport behavior-changing ones into fixup_game_funcs.py. Vendor a copy of the script into this repo's tools/ and commit (the ledger cannot track
   ../N64Recomp). Diagnostics: backport or declare dropped in CURRENT-TRUTH.
3. Success: scratch fixup completes rc=0 and behavioral patches match live (`diff -r` modulo declared-dropped diagnostics).
   NEVER run N64Recomp/fixup over ../N64Recomp/RecompiledFuncs.
