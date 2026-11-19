# NEXT (s7642)
HYPOTHESIS-ID: owner-items-wait

G6a (rumble), G6b (F6 controls), G6c (stand-ins) and the G5 looks wait only on the owner (docs/OWNER-OPT-INS.md). If the owner
reports on any of them, take that first. Do NOT schedule a ladder-item-4 REVISIT or the rename sweep.

Work unit if no owner report: NEW host-side idiom class **TS = Thread Sanitizer over all of RT64** (s7641 instrumented only
plume_metal.cpp and found 1 live race there). Extend tools/s7641_tsan_build.sh into tools/s7642_tsan_rt64_build.sh: recompile
EVERY object of librt64 + libplume (compile_commands entries under lib/rt64/src, not contrib/ except plume) with
-fsanitize=thread into scratch/s7642/obj, build copies of those .a files, relink build/RogueSquadron64Recomp_tsan2. Run
tools/s7641_tsan_run.zsh (boot 45 s; also one forced-level flight arm, LEVEL=1 dd2, ~120 s, screen unlocked) and bucket reports
by (function pair, variable). Hypotheses: H-clean (only the known metal-cpp __block blind-spot class) vs H-defect (>=1 new race
pair in RT64 present/worker/texture-cache code). Positive control in the same build: ROGUESQ_S7641_CF=0 must bring back the
2 index reports. Classify every pair: real (fix, env-gated old arm) / blind spot (name the uninterpreted sync) / benign-by-design.
Rules: never launch under lldb; never touch build/saves; one game at a time; SIGKILL only; real binary untouched.
