# NEXT (s7351): idiom-class audit - class AB, typed load/store through a cast guest pointer
HYPOTHESIS-ID: host-typed-guest-access
Context: s7350 closed class AA (tools/s7350_overlap_census.py: 195 memcpy sites, 0 open, no defect).
Idiom: `*(uint32_t*)(rdram + a)`, `*reinterpret_cast<uint16_t*>(RDRAM + a)`, `((uint64_t*)p)[i]` where p/a is guest-derived and the
address alignment is not proven. Misaligned typed access is UB (alignment + strict aliasing); clang on arm64 may fuse into ldp/stp,
vectorise, or use it in std::atomic (which faults on misalignment).
Hypotheses: H-safe (address masked `& ~3` / `& 0x...FC`, or derived from a naturally aligned guest pointer field the MIPS code
itself loads with lw/ld, so it is aligned by construction), H-diag (only gated probes), H-ub (default-on cast access with an
unproven guest alignment: fix with a memcpy load or an alignment mask matching MIPS lw's address error behaviour).
Method: new tools/s7351_cast_census.py on the s7343 scope; reuse s7343 args_of()/ln_fn()/body_gated(), s7338 sites() C/P/G/D, s7344
CORE demotion. Site = a deref of a C-style or reinterpret_cast to a >1-byte integer/float pointer whose operand base is guest memory
(rdram / RDRAM / g_rdram_for_submit / ram / TMEM / DMEM). Classes: ALN (mask proves alignment), K (constant offset), MC (already
memcpy), H hand, B defect. Controls: planted `*(uint32_t*)(rdram + task->a)` ('?'), masked twin `& ~3u` (ALN), memcpy twin (not a
site), gated twin (G).
Runtime only if a B site gets fixed: standalone control, then `env SECS=260 zsh scratch/s7326/run.zsh s7351_dd8 ''`.
Exit: PORTING-STATE s7351, CURRENT-TRUTH item 27p -> closed/fixed, commit.
