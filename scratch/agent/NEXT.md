# NEXT (s7430)
HYPOTHESIS-ID: default-file-growth

First fold new scratch/agent/SOAK-RESULTS.md lines (s7428_audio_route_arms: rc 0 = F9 gate two-arm verified; 2 = VOID).

Class CM (CURRENT-TRUTH Next steps item 1): unbounded default-on file growth. An owner-recipe run (ROGUESQ_FPS60=1
ROGUESQ_DRAW_DISTANCE=4 ROGUESQ_ASPECT=16:9, no logging env) may create/append files in the exe dir (build/rs64_s6892.log,
other rs64_*.log / dumps, stderr capture) on every run.
Hypotheses: H-bounded (every default-on file is truncated per run or capped) vs H-growth (>=1 file appends across runs
without a cap, so build/ grows each session) vs H-hot (>=1 default-on write happens per frame, a G5c stall candidate).
1. Offline: grep src/, lib/N64ModernRuntime, lib/rt64 for fopen/ofstream/open( with write/append modes; classify each by gate
   (env opt-in / default-on), mode (w / a), cap, and call frequency. Planted control: an ungated "a" fopen in a scratch copy
   must be flagged.
2. Runtime, copied folder: run the owner recipe twice 60 s each (no keys), list new/changed files and sizes after each run
   (fs_usage or a before/after find -newer); a file growing between run 1 and run 2 = H-growth.
Write tools/s7430_file_growth.py. Exit 0 = H-bounded, 1 = growth/hot found, 3 = control failed.
Also open from s7429: the SDL_QUIT save flush ([s7429-quit] save flush=N) is not runtime-verified; if a quit injector works
(osascript 'tell application "System Events" to keystroke "q" using command down' with the game frontmost), check it.
