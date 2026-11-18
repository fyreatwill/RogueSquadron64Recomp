# NEXT (s7585)
HYPOTHESIS-ID: host-memory-growth-audit

s7584 closed class UI (uninitialized host stack/heap reads, H-clean, plant 7 fired). The rename sweep is CLOSED (s6868: 139 remaining
address names are shape-only) — do not take it. Next: class LK, host memory growth (leaks / unbounded caches) in long play.

Hypotheses: H-flat (footprint plateaus after the first mission load; every cache is bounded), H-leak (footprint grows linearly per
mission load / hangar re-entry: something allocated per scene is never freed), H-cache (growth in flight with no scene change: RT64
texture/pipeline/framebuffer caches or a diag ring growing per frame).
Discriminator, ONE run each route, sampled from outside the process (no rebuild):
1. Owner recipe L4 dd4 16:9 FPS60, HOLD 600 (tools/g1e_owner_quiet_arms.zsh, ALLOW_SLOW=1), plus the s7469 hangar abort/re-entry route
   on build/ (scratch/s7584/hangar.zsh with GD=build, drop MallocScribble/PLANT; 4 loads, 3 re-entries).
2. A sampler beside each run: every 10 s `footprint -p <pid> --summary` (or `vmmap --summary <pid>` phys_footprint) + `ps -o rss=`;
   at t=300 s and at the end `leaks <pid>` (summary lines only; needs MallocStackLogging=lite in the env for backtraces of leaked
   blocks). Pid from tools/rs64_game_pid.zsh.
3. Positive control: ROGUESQ_S7578_PLANT is C-only and not a leak; add plant 8 to tools/s7578_ubsanc_plant.h (malloc 1 MB x 64 at
   startup, drop the pointers) and confirm `leaks` reports >= 64 MB leaked in a build_autoinit run (that dir already force-includes the
   header), or plant a leak via an env-gated malloc in src/main (build/) if leaks cannot see the C plant.
Outcomes: slope per load/re-entry > ~5 MB -> H-leak (name the allocator from leaks' stacks, fix); slope in steady flight -> H-cache
(name the cache, bound it); flat with control firing -> H-flat, class closed.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves (the s7584 hangar script uses GAMEDIR's own saves copy).
