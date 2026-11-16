# NEXT (s7477)
HYPOTHESIS-ID: injected-guest-call-register-clobber

Class EE (M3 idiom-class audit, s282-s288 model): port patches that call a GUEST function from inside generated code
(e.g. `findAndZeroTableSlotMatching(rdram, ctx);` inside a `/* PATCH: ... */` block) clobber the caller-saved registers
($v0,$v1,$a0-$a3,$t0-$t9,$at, hi/lo, FPRs) that the surrounding generated code still reads. s7476 found one: s4889 saved only
$a0 and turned the MusyX voice count 17 into 1 (class ED). Enumerate the whole class and close it.

0. Fold the s7476_canary_flight soak verdict (SOAK-RESULTS.md) into the ledger first (pass = plant DETECTED, 0 non-plant
   tail-hits, 0 `[s7476-ss]` slack_store).
1. Enumerate (offline, one script tools/s7477_injected_call_audit.py): in /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c,
   every line containing `PATCH` that also contains `<guestfunc>(rdram, ctx)` where guestfunc is a RECOMP_FUNC name, plus
   fixup/apply scripts emitting such calls (grep tools/*.py for `(rdram, ctx);` inside emitted strings).
2. Classify each site: which regs the callee writes (parse its generated body for `ctx->rN =`), which regs the code after the
   site reads before writing (scan forward in the caller to the next call/return), and which the patch saves/restores.
   Live-and-clobbered-and-not-restored = BUG. Dead or restored = SAFE.
3. Fix every BUG site in its fixup script (save/restore), with an =0 switch only where behaviour visibly changes; rebuild;
   one boot + the s7476 point watch/ALLOC_CALLERS as a smoke control.
Hypotheses: H-class-single (s4889 was the only live clobber) vs H-class-multi (more sites; each is a latent wrong-argument bug).
Discriminator: the audit table's BUG count, with a positive control = the audit must flag s4889 when run on the pre-fix body
(use OLD_CALL text from tools/apply_s4889_first_dereg.py) and pass it on the fixed body.
