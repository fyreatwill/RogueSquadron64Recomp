# NEXT (s7404)
HYPOTHESIS-ID: direct-rcp-register-access

s7403 closed class BM (boot globals, H-none). Work unit, class BN: LIVE (non-replaced, s7401 live()) guest code that loads/stores
RCP / PI / SI / VI / AI / MI registers or PI-mapped cart space directly (KSEG1 0xA4000000-0xA4FFFFFF, 0xA0000000|x, 0xB0000000+),
bypassing the replaced libultra.
1. Extend tools/s7402_side_effects.py scan() idea (new tools/s7404_rcp_access.py): track lui/ori/addiu constants that are used as the
   BASE of a load/store (ignore lui values only stored as data: most game 0xB9xx/0xBAxx lui are GBI command words written to DLs).
   Also catch `or reg, reg, at` with at=0xA0000000 (KSEG1 conversion of a pointer). Rows: function, insn, register, R/W, LIVE tag.
2. For each live row: what the recompiled code does (grep RecompiledFuncs for the insn's MEM_* and librecomp's handling of
   >=0xA4000000 addresses: rdram mirror, intercept, or out-of-bounds) vs what hardware returns.
3. Hypotheses: H-none (no live direct access, or each is a harmless mirror e.g. KSEG1 rdram alias), H-mirror-bad (a register read
   lands in RAM and returns 0/stale where hardware returns status bits, e.g. a busy-wait that passes trivially or never ends),
   H-write-lost (a register write the game relies on is dropped). Static first; runtime only if a live register site exists:
   one counter at that site + a planted control, two arms only if a fix lands (default-on env, =0 old).
