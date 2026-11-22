# NEXT (s7786; s7785 closed the s5660-hook fallout: H-none except s5661, store-hook register gate 0/188,965 bad)
HYPOTHESIS-ID: load-hook-reg-census
First (any of these outranks the rest): `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers
in docs/OWNER-REVIEW-QUEUE.md, new SOAK-RESULTS lines.

Question: do the LOAD-side diagnostic hooks report the address of the load they instrument? (Same class as s7784/s7785 for stores.)
Families: RS64_S7484_LD(pc, base, off, w) before MEM_W/H/B/D loads, rs64_s4307_synth_read, any rs64_* hook taking
U32(ADD32(ctx->rN, OFF)) before an lw/lh/lb/lbu/lhu/ld/lwc1/ldc1/lwl/lwr.
Hypotheses: H-clean (0 bad), H-mixup (some family reads the destination register, like s5660 read the value), H-hole (load forms,
e.g. lwl/lwr or $zero-based, that a family never hooks, like bzero's swl $zero).
Unit (offline): extend or clone tools/s7785_store_hook_reg_census.py as tools/s7786_load_hook_reg_census.py (per-function pc keying,
--controls with a destination-register mutant and an offset mutant), run on ../N64Recomp/RecompiledFuncs, fix any bad family in its
apply_* fixup (idempotent per site), rebuild, sweep --only the touched gates. Outcomes: bad=0 & no hole -> H-clean, close; bad>0 ->
name the fixup, list every recorded conclusion that read that hook (grep PORTING-STATE for its env var) as in s7785.
