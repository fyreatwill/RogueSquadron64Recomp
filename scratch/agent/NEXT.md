# NEXT (s7612)
HYPOTHESIS-ID: host-static-of-guest-register

Class SN closed s7611 (tools/s7611_sn_census.py --controls --witness: 169 candidates 0 open, contracts C1-C6, controls 8/8,
witness PASS from scratch/s6995 aim logs, H-clean). Its declared scope gap is the next class.
Class RG: host static / thread_local / file-scope state holding a value taken from a guest REGISTER (ctx->rN, ctx->fN,
gpr[] arrays passed to hooks) and used on a LATER call: a guest pointer (sp-relative stack address, object pointer, list
head) or a guest scalar parked across calls, which goes stale when the guest frees/reuses the object, re-enters the
function from another thread, or a new stack frame lands at the same sp. Examples to expect: fixup-injected statics in
RecompiledFuncs (s7103 camfix s7103_* set at entry and consumed at exit; s6907 dp; s5839_obj; rs6673_actor), src hooks
taking `const uint64_t* gpr` (rs64_menu_worker_sent msg = gpr[29]+0x10), s7394fix, s6963 state keyed by ctx->r16.
Method: extend tools/s7611_sn_scan.py with a REG token set (ctx->r\d+, ctx->f\d+, gpr\[\d+\]) as a second taint source
(keep the SN set separate so SN stays closed), tools/s7612_rg_census.py with rows + proof regexes the same way.
Classify: fresh (set and consumed inside one guest call: entry/exit pairs; prove the exit clears or the entry overwrites
and no other function reads it), value (scalar used only for a log/edge), event (reset on a named edge), keyed (compared
against the live register before use), gated, BAD. For any default-on cross-call pointer: name what guarantees the object
is still live (or re-validated) at the later use.
Hypotheses: H-clean, H-bad-gated, H-bad-live.
Controls: (1) plant a static guest pointer from ctx->r4 dereferenced in a later call on a default path -> OPEN; (2) drop a
row -> OPEN; (3) remove the s7103 exit clear (s7103_in = 0) -> contract OPEN; (4) re-entrancy: plant an entry/exit pair
whose static is read by a different function -> OPEN.
Second source: runtime witness from existing logs if any entry/exit pair logs both ends; else a compiled witness
(tools/s7612_rg_witness.cpp) driving the real injected snippet shape with a re-used sp.
Never touch build/saves; never clear ROGUESQ_NO_SAVE_WRITE.
