# NEXT: idiom-class audit — host self-time of our own (non-guest) helpers on the game threads in flight
HYPOTHESIS-ID: host-selftime-audit
Context (s7066): hot getenv closed by an image-wide cache (src/main/rs64_env_cache.cpp). All G5 items await the owner.
Capture once, analyze many: scratch/s7066/on/smp_*.txt (289 x 1 s host samples, all threads, cache on, L6 dd1 4:3 FPS60, 365 s flight)
and scratch/s7066/off/ are already on disk. No build needed for the first half.
Hypotheses:
 H-diag: diagnostic leftovers (per-frame probe/ring/counter helpers, fprintf gates, atomics) hold a measurable share (>2%) of
   MAIN/[Game] 0 on-CPU self samples; fix the top class (gate by a cached static or compile out) and re-measure.
 H-guest: on-CPU time is dominated by generated guest functions and RT64/ucode work; our helpers < 1% -> close the class.
 H-runtime: ultramodern/librecomp glue (osRecvMesg, yield, MEM_* helpers) dominates our share -> audit that path instead.
Method: write tools/s7067_selftime.py: per thread, self samples by leaf symbol, excluding blocking leaves (__psynch_*, mach_msg*,
__semwait_signal, nanosleep, kevent), and bucket symbols as guest (RecompiledFuncs names / func_0x), ours (rs64_*, s6xxx/s7xxx
helpers, src/ functions), runtime (ultramodern/librecomp), RT64, libsystem. Positive control: the on vs off arms must show the
getenv bucket difference (~776 -> 0 libsystem getenv) in the same tool. Then fix the top "ours" class if H-diag, rebuild, one
hold with the sampler (scratch/s7066/both.zsh pattern), same-build =0 arm where a knob exists.
Hard rules: generated-code edits go through tools/fixup_*.py / apply scripts; one game run at a time; SIGKILL.
