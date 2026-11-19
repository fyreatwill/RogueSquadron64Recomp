# NEXT (s7643)
HYPOTHESIS-ID: owner-items-wait

G6a (rumble), G6b (F6 controls), G6c (stand-ins) and the G5 looks wait only on the owner (docs/OWNER-OPT-INS.md). If the owner
reports on any of them, take that first. Do NOT schedule a ladder-item-4 REVISIT or the rename sweep.

Work unit if no owner report: class TS-2 = Thread Sanitizer over the HOST runtime (ultramodern, librecomp, src/main/*.cpp/.mm,
src/rsp, PatchesLib host side), NOT RecompiledFuncs (guest code; too big, single game thread). s7642 closed RT64+plume H-clean
(CURRENT-TRUTH item 29). Copy tools/s7642_tsan_rt64_build.sh to tools/s7643_tsan_host_build.sh: select compile_commands entries
for libultramodern.a, liblibrecomp.a and the RogueSquadron64Recomp.dir objects (src/main, src/rsp, src/game...), keep the s7642
rt64/plume tsan objects too, relink build/RogueSquadron64Recomp_tsan3. Runs: boot 45 s (tools/s7642_tsan_run.zsh), boot with a
planted race positive control (add an env-gated ROGUESQ_S7643_PLANT=1 unsynchronised counter bumped from two host threads, e.g.
VI thread + main, default off), then L1 dd2 flight HOLD=120 via g1e_owner_quiet_arms (GAME=./RogueSquadron64Recomp_tsan3,
TSAN_OPTIONS exported). Bucket with tools/s7642_tsan_bucket.py. Hypotheses: H-clean (only Metal blind spots + plant) vs H-defect
(>=1 pair in VI/audio/input/event-queue/rumble/MESSAGE code). Classify each: real (fix, env-gated old arm) / blind spot / benign.
Rules: never launch under lldb; never touch build/saves; one game at a time; SIGKILL only; real binary untouched.
