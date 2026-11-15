# NEXT (s7409)
HYPOTHESIS-ID: fr0-odd-register-access

s7408 closed class BR (H-equal: FP->int macros identical in range on all 2^32 floats; 0 out-of-range live at 475 sites,
dd8 + dd1; tools/s7408_cvt_contract.py, build_cvt). Fold the queued s7408_cvt_levels soak (L5/L10/L15) if it ran.
Class BS: odd FPR access / FR mode. recomp_context has fpr f0..f31 plus `uint32_t* f_odd` and `mips3_float_mode`
(recomp.h ~478); CHECK_FR is an assert (compiled out in Release?). 145 f_odd uses in funcs_4/7/8/26/27/36/42/49.
Seen in s7408: transformAndEmitFaceVertices (hand asm, sets Status.FR via mtc0 and clears it with & 0xFBFFFFFF at exit)
WRITES odd destinations through ctx->f_odd[(7-1)*2] but READS `ctx->f7.fl` directly (CVT_W_S(ctx->f7.fl), mfc1 reads
f_odd). If f_odd aliases the high half of the even fpr in FR=0 and f7 is a separate slot in FR=1, a mixed read/write pair
can see two different registers.
1. Offline: read how librecomp sets f_odd and mips3_float_mode on cop0_status_write (lib/N64ModernRuntime/librecomp),
   and how the generator picks f_odd vs fN (../N64Recomp/src/cgenerator.cpp). Census every f_odd use and every plain
   odd fN.fl/u32l use per function, and which functions run with FR=1 (mtc0 Status with bit 26 set).
2. Model: VR4300 FR=1 has 32 independent 64-bit FPRs; FR=0 odd single-precision ops touch the high word of the even pair.
   Each function gives a row: consistent (all odd accesses through one view) / mixed (read via one view, write via the other).
3. Hypotheses: H-consistent (every function uses one view for each register, or the two views alias correctly at runtime),
   H-mixed-live (a function on the live path writes through f_odd and reads fN, or the reverse, with a different value
   seen; fix in the generator/fixup + export.sh if lib/ is touched), H-dead (mixed only in functions never called).
   Discriminator: the census rows plus, for any mixed function, a live check in a separate build dir comparing the two
   views at the read (positive control: a planted write to one view must show up in the other check).
