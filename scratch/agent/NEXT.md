# NEXT (s7411)
HYPOTHESIS-ID: unaligned-access-macro-semantics

s7410 closed class BT (callee-saved preservation across the FR=1 hand-asm routines; tools/s7410_csave_census.py + build_fsv).
Fold the queued s7410_fsv_levels soak (L4/L7/L12) if it ran: pass = rc 0 (CONTROL PASS + H-preserved per level).
Class BU: unaligned load/store macro semantics. ~820 emitted sites: do_lwl 207, do_lwr 203, do_swl 205, do_swr 204
(grep -ho 'do_[a-z]*(' ../N64Recomp/RecompiledFuncs/*.c). Recomp rdram is word-byteswapped (MEM_B uses addr ^ 3), so these
macros must re-derive the big-endian VR4300 semantics per (addr & 3) and must sign-extend the 32-bit result into the 64-bit GPR.
1. Offline (no game run): extract do_lwl/do_lwr/do_swl/do_swr (+ any ldl/ldr/sdl/sdr) from the real recomp.h, compile them
   against a 16-byte rdram window in a host harness, and compare against a reference written from the VR4300 manual
   (big-endian memory, LWL merges the high bytes, LWR the low bytes, result sign-extended) for every addr&3, random register
   and memory contents (>=1e6 cases per macro), also the lwl+lwr pair = unaligned word load identity and swl+swr pair =
   unaligned word store identity. Perturbed control: flip one byte lane in a copy of a macro -> must mismatch.
2. Census: per site, is it a paired lwl/lwr (same base, offsets k and k+3) or a lone one; lone sites need a semantic read.
3. Hypotheses: H-equal (all macros == reference on all inputs), H-lane (a lane/shift error at some addr&3 -> fix in recomp.h,
   export.sh if lib/), H-ext (missing/extra sign extension of the 32-bit result; visible only to 64-bit consumers -> census
   whether any site's result feeds a 64-bit op).
