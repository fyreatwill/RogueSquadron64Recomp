# NEXT (s7577)
HYPOTHESIS-ID: gen-c-ub-audit

s7575 (div) and s7576 (float->int trunc) closed the RecompiledFuncs UB classes. The RSP microcode is also recompiled to C
(build/factor5_ucode/*.c, RSPRecomp output + tools/fixup_factor5_ucode.py) and built -O2 (CMakeLists RS64_UCODE_FLAGS, C++ TU with
an inline threshold raise, s6714). Same question for it: does -O2 exploit C/C++ UB in the emitted scalar/vector code?
1. Enumerate UB-capable emissions in the ucode C and the RSP:: vector templates (lib/N64ModernRuntime / src/rsp headers):
   left shift of a negative signed value or by >= width (UB in C++17), signed int overflow in accumulator / int32 arithmetic,
   int16 narrowing (implementation-defined, fine), out-of-range float casts (none expected). Count sites per pattern.
2. Static test, s7576 method: arm A = file as built, arm B = the suspect op replaced by a defined form (e.g. `(int32_t)((uint32_t)x << n)`);
   compile both at the ucode flags to asm and diff per function; plant a fold control (`int f(int x){return (x<<1)<0 ? 1 : (x<0);}`-style
   snippet clang folds). Suspects get a manual read.
3. If anything is folded: total rewrite in tools/fixup_factor5_ucode.py (or a new apply script), then one runtime arm
   (scratch/s7576/run.zsh template, L1/L4 dd2/L12, 150 s) comparing RDP output hash vs before, plus a control.
Hypotheses: H-safe (no exploited UB), H-folded (asm differs on UB grounds), H-visible (a folded op changes RDP output on a real frame).
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
