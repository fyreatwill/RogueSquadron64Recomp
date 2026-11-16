# NEXT (s7428)
HYPOTHESIS-ID: config-env-precedence

First fold any new scratch/agent/SOAK-RESULTS.md lines.

Class CK (CURRENT-TRUTH Next steps item 1): s7427 closed env-policy ORDER (H-ordered after the rs64_g5b_tg_fix re-arm fix).
Open: settings that can come from a FILE as well as from ROGUESQ_* env. main.cpp:~13297 recomp::register_config_path(cwd);
librecomp recomp.cpp / mods.cpp read .json files; RT64 has its own user configuration (resolution, aspect, msaa, vsync...)
that RT64's init may load or default; build/saves holds the owner's save (never touch it).
1. Enumerate every file the game reads at boot (offline: grep fopen/ifstream/std::filesystem/json parse in src/, librecomp,
   ultramodern, rt64 src/hle+common; runtime: one boot with fs_usage -w -f filesys on the pid for ~10 s, or a DYLD-free
   open() trace via the existing env-cache style interposer if fs_usage is denied) -> list of (path, reader, keys).
2. For each key that an env var also controls (ROGUESQ_RESMULT, ASPECT, FULLSCREEN, WINDOW_*, MSAA, VSYNC, FPS60, ...):
   which is applied last, and does that match docs/OWNER-OPT-INS.md? A file value that beats an explicit env value, or a
   file written by one run that changes the next run's default = drift.
3. Positive control: a planted config file in a COPY of the game folder (never build/saves) with a key that the env also sets
   must be reported (offline: planted text into the parser model; runtime: run from the copied folder).
Hypotheses: H-env-wins (env always overrides, files hold only non-overlapping state) vs H-file-wins (>=1 overlapping key where
a file silently overrides env, or a run persists state that changes the next default). Name who is affected (owner recipe or
test-only) and fix.
Write tools/s7428_config_precedence.py. Exit 0 = env-wins, 1 = drift, 3 = control failed.
Reuse: tools/s7427_env_policy_order.py (call graph, functions()), tools/s7426_env_defaults.py (sources()).
