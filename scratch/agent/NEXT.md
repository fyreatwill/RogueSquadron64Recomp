# NEXT (s7413)
HYPOTHESIS-ID: aligned-load-store-macro-semantics

s7412 closed class BV (tools/s7412_int_emission.py: 14,687 emitted integer forms, 0 MISM, CONTROL PASS, div guards = s7085).
Class BW: aligned load/store macros. recomp.h MEM_W/MEM_H/MEM_HU/MEM_B/MEM_BU (incl. the RS64_BYTE_WATCH MEM_B variant),
LD/SD (ld/sd, ldc1/sdc1 64-bit: hi word at +0), include/rsp_dpc_macros.h MEM_WU override, and the store forms
(MEM_W(off,base) = v etc). Rdram is word-swizzled (guest byte a at host a^3, half at a^2).
1. Offline, like s7411/s7412: harvest every emitted load/store statement shape from ../N64Recomp/RecompiledFuncs
   (lb lbu lh lhu lw lwu ld sb sh sw sd lwc1 ldc1 swc1 sdc1; skip diagnostic-prefix lines as s7412 harvest does), compile the
   real header with -include include/rsp_dpc_macros.h, compare against a byte-wise big-endian model (sign/zero extension
   into the 64-bit GPR; store writes only its width; neighbouring bytes untouched), every alignment legal for the op, plus
   KSEG0/KSEG1 bases (0x80../0xA0.. addresses -> same physical byte).
2. Positive control: mutant header per macro (swizzle ^3 -> ^1, sign vs zero extension swapped) must MISM in its own op only.
3. Hypotheses: H-equal (0 MISM) / H-ext (a sign/zero-extension error, e.g. lhu sign-extending) / H-swz (wrong lane for some
   alignment or the KSEG1 alias) / H-width (a store touching a neighbour byte).
