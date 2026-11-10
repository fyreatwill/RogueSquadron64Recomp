# NEXT: owner reports first; otherwise the host-shim ABI census (librecomp/src libultra replacements)
HYPOTHESIS-ID: host-shim-abi-census
Context: the N64Recomp lowering series is CLOSED (s7082-s7087, docs/N64RECOMP-WARNING-CENSUS.md, 120/120 mnemonics
mapped). The generated code is now checked; the hand-written layer it calls is not. s7087 found one shim defect class by
accident (osGetCount_recomp zero-extended its u32 return; fixed, dead in this game). There are 128 `*_recomp` shims in
lib/N64ModernRuntime/librecomp/src/*.cpp and 17 in src/. Each one hand-decodes the o32 ABI.
Unit (offline, one tool + one host test, no game run needed unless a live defect is found):
1. Enumerate every `extern "C" void X_recomp(` in librecomp/src and src/; mark which ones the generated code actually calls
   (grep `X_recomp(rdram, ctx)` in ../N64Recomp/RecompiledFuncs/*.c; count call sites).
2. For each CALLED shim, pair it with its libultra prototype (ultramodern/include/ultramodern/ultra64.h, or the libultra
   headers if missing) and check: (a) argument registers: a0-a3 in order, 64-bit args in an EVEN pair (a2:a3) with the high
   word first, 5th+ args at sp+0x10, 0x14, ... (u64 on the stack 8-aligned); (b) casts: pointers (int32_t) before TO_PTR,
   s32 args sign-extended, u8/u16 masked; (c) return: 32-bit returns sign-extended into r2 (int32_t), u64 split r2=hi,
   r3=lo, each sign-extended (osGetTime_recomp is the model); (d) float args/returns (f12/f14, f0) if any.
3. Host test for the 64-bit split/join shapes (osSetTimer countdown a2:a3 + stack interval, osSetTime, osGetTime) with values
   >= 0x80000000 in each half.
Discriminator per shim: {matches, differs-unreachable (0 call sites or value range cannot trigger), differs-live}.
Positive control: osGetCount_recomp at the pre-s7087 text (`ctx->r2 = osGetCount();`, apply it to a copy) must be flagged
as a zero-extended u32 return; osGetTime_recomp must pass. Negative: mutate one shim's a2/a3 order in a copy -> exactly one
finding. A differs-live finding gets a fix in lib/ + ./submodule-patches/export.sh + a commit in the same session.
