# NEXT (s7549)
HYPOTHESIS-ID: class-gi-injected-static-guest-ptrs

Class GH CLOSED s7548 (tools/s7548_gh_census.py rc 0, --controls 10/10): src/main statics that capture guest values and deref
later are all in-flight / gated / base / host / refreshed / scalar. Residual: statics declared INSIDE the C that tools/fixup_*.py
and tools/apply_*.py inject into RecompiledFuncs (/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c has
~4387 `static` lines; e.g. the s6418 farclip block `static uint32_t org6418`). They run inside guest functions, so a captured
guest pointer there can be dereferenced on a later guest call after the object was freed.

Work unit: tools/s7549_gi_census.py (--controls), offline. Reuse s7548's engine (import tools/s7548_gh_census.py: File/census/
classify take arbitrary paths + override texts). Inputs: the generated funcs_*.c (patched tree, as built) — restrict to PATCH-tagged
regions, or run on whole files and attribute each static to the injecting script by its PATCH tag/`/* sNNNN */` comment.
Sources there: ctx->rN, MEM_*, any local tainted by them. Derefs: MEM_*(…, x) / TO_PTR with x derived from the static.
Classify as s7548 (H-diag auto; rules for H-gated / H-refresh / H-value / H-static-target / OPEN), with the rule proof in the
injecting script's text (`tools/x.py@@regex`). Controls: planted injected static + later MEM_W deref -> UNCLASSIFIED; deleted rule;
renamed gate -> DRIFT; real tree rc 0.
Hypotheses: H-value-only (injected statics hold scalars: cutoffs, counters, latches), H-refresh (pointers re-read per call),
H-stale (a default-on injected static holds a heap pointer across calls -> fix it in that apply script, =0 knob, two-arm qualify).
Runtime witness only if a row is OPEN.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
