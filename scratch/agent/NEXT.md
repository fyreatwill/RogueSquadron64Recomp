# NEXT: idiom-class audit — uncached getenv() in per-frame paths (host cost / lock contention)
HYPOTHESIS-ID: hot-getenv-audit
Context (s7065): the transition-stall thread is CLOSED (retail 3072-sample audio wait). Every G5 item awaits the owner. Host
samples of the game thread showed getenv() (-> __findenv_locked, a process-wide lock shared with RT64/SDL threads) called per
frame from patched setupCameraMatrices, streamTerrainGridCellsByDistance and osRecvMesg (factor5MutexAcquire), ~25 samples/288 s on
MAIN; RecompiledFuncs carries 2182 getenv references. Small, but it is a whole idiom class and it is ours.
Hypotheses:
 H-few: only a handful of sites call getenv per call (not cached in a static); fix those in their apply/fixup scripts, done.
 H-many: dozens of hot sites; add one cached-env helper (rs64_env_cached(name) -> static table) and convert by script.
 H-none-hot: the sampled sites already cache and the samples are first-call or a different path (then close with the census).
Method, offline first: grep-enumerate every getenv( in N64Recomp/RecompiledFuncs/*.c, src/, lib/N64ModernRuntime; classify each
as cached (static init / s_on<0 guard) vs per-call; for per-call ones, name the function and whether it is per-frame (callers in
the s7065 sample trees: scratch/s7065/smp_*.txt, tools/s7065_sample_yields.py). Then fix per-call hot sites in the owning
tools/apply_*.py / fixup script (regen-safe), rebuild, one hold (scratch/s7065/run.zsh <name> 6 + tools/s7065_sample_loop.zsh) and
show getenv samples on MAIN drop to 0 with fps unchanged. Positive control: the s7065 baseline count (~25/288 s).
Hard rules: diagnostics/edits in generated code go through tools/fixup_*.py / apply scripts; one game run at a time; SIGKILL.
