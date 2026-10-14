# M3 s4817 — mult/multu/dmult/dmultu lowering census

Tool: `tools/census_mult.py`. Generated-code counts: mult 566, multu 104, dmult 50, dmultu 64.

Lowerings (lib/N64ModernRuntime/N64Recomp/src/cgenerator.cpp emit_muldiv; recomp.h DMULT/DMULTU):
- mult: `S64(S32(a))*S64(S32(b))`, lo=S32(r), hi=S32(r>>32): exact MIPS semantics.
- multu: `U64(U32(a))*U64(U32(b))`, then S32 of the halves: exact (sign-extended halves match MIPS).
- dmult/dmultu: `__int128` full product split into hi/lo: exact; a 128-bit product of two 64-bit values cannot overflow.

No trap, no UB, no host-dependent behaviour (unlike div/f2i). Class closed; no guard needed. Static, single-source (code inspection plus counts; no runtime counter).
