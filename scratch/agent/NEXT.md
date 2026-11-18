# NEXT (s7606)
HYPOTHESIS-ID: host-guest-call-census

Class FR closed s7605 (tools/s7605_fr_census.py, 0 open, controls 6/6, witness 11/11; recomphook_get_return_double fixed).
Next idiom class HC: host code that CALLS a guest (recompiled) function. Enumerate every LOOKUP_FUNC(...)(rdram, ctx), direct
call of a generated *_recomp / recomp_func_t* / get_function() target, and thread-entry/callback dispatch in src/ + librecomp
+ ultramodern (grep 'LOOKUP_FUNC\|recomp_func_t\|get_function\|run_thread_function\|(rdram, &' ).
Contract per call: (a) fresh ctx -> r29 inside a guest stack, 8-aligned, with >=16 bytes of o32 arg area below the caller's
frame; FR=0 + f_odd = &f0.u32h; r31/gp sane or never read; (b) reused ctx (callback from inside a stub) -> every register the
host stub relies on after the call (r2 result, caller's r4-r7, sp) is saved/restored or not used again; (c) args a0-a3
sign-extended 32-bit (class RX contract); (d) the target is a real function entry, not a mid-function address.
Per site verdict: ok (named contract), ok-diag (env-gated), BAD.
Hypotheses: H-clean, H-bad-gated, H-bad-live (a default-path callback clobbers state the host stub then uses).
Tool: tools/s7606_hc_census.py --controls: (1) plant a fresh ctx call without r29 -> OPEN; (2) plant a fresh ctx without
f_odd init -> OPEN; (3) drop a row -> OPEN; (4) plant a reused-ctx call followed by a read of ctx->r4 -> OPEN.
Second source: witness .cpp (as tools/s7605_fr_witness.cpp) or a runtime count of each live call site at L1.
Never touch build/saves; never clear ROGUESQ_NO_SAVE_WRITE.
