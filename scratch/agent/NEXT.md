# NEXT (s7579)
HYPOTHESIS-ID: gen-c-bounds-audit

gen-c-ub-audit is CLOSED (s7575 div, s7576 trunc, s7577 ucode, s7578 game-C null/wrapv: N arm 1 dead diag check, W arm
131 game funcs = diag counters / bounded fixup arithmetic, runtime -fsanitize=signed-integer-overflow on all 52 TUs at -O2
L1/L4/L12 with plant control). Next idiom class: HOST ARRAY BOUNDS in the fixup C. The fixup scripts put ~407 static
diagnostic/table arrays into RecompiledFuncs (pcs[npc++], rs5817_nm[k], s_prev[N], cnt[kind-10] ...). An out-of-bounds index
there writes host .bss next to other fixup state (a host-side corruption no guest watch can see). build_asan never
instrumented the generated C (s7467: C++ only), and ASan cannot see .bss neighbours inside one global anyway.
1. Reuse tools/build_ubsanc.sh with B=build_ubsanb and -fsanitize=bounds (array-bounds + local-bounds) added to the C flags
   (make the sanitizer list an env SAN=..., default signed-integer-overflow). Add a bounds plant to tools/s7578_ubsanc_plant.h
   gated by ROGUESQ_S7578_PLANT=2 (a[idx] with volatile idx = N on int a[N]).
2. Build-level control: nm -u on the RecompiledFuncs objects shows __ubsan_handle_out_of_bounds.
3. Run scratch/s7578/run.zsh pattern (GAMEDIR=build_ubsanb): p (plant=2), L1 dd4, L4 dd2, L12 dd4, HOLD 150, plus the owner
   hangar abort/re-entry route if time allows (scratch/s7326/run.zsh).
Hypotheses: H-clean (0 out_of_bounds outside the plant), H-diag-oob (a diagnostic table overruns: fix its bound in its
apply_*.py), H-game-oob (an OOB in a behaviour-changing patch, e.g. terrain window / s6905 tables: root-cause + fix).
Discriminator: grep "runtime error: index" in san_<arm>.* grouped by file:line; plant must report in arm p.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
