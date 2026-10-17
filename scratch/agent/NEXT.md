# Next: the 2 uncovered j/jal targets (bounded M3 residual from s5348)

s5348 closed direct j/jal into overlay-aliased VMAs (84/84 lookup, 0 direct). Two call sites
target addresses covered by no section: `jal 0x8334B334` at 8009D978 (.ovl run 2738) and
`j 0x80000000` at 800A5130. Hypotheses: H1 both sit in data misclassified as code (dead);
H2 one is live code with a wrong target (relocation/overlay-base issue); H3 reachable only from
an overlay never loaded on the qualified route.
Discriminator: identify the containing function via syms/rogue_squadron.syms.toml and the
generated C in N64Recomp/RecompiledFuncs; grep callers of that function (LOOKUP_FUNC/direct).
No callers or a function inside a data/pad region => H1 (close). Live callers => check whether
the instruction decodes sanely in context (jal inside a real prologue/epilogue vs inside a table).
Positive control: run the same lookup for a known-live function (menuOverlayInit 800C58A0) with the
same commands. Do not touch lib/. Use tools/audit_overlay_alias_calls.py --generated for counts.
Afterwards the M3 idiom list is essentially exhausted: pivot to the sweep revisit rules in ITERATION.md.

HYPOTHESIS-ID: uncovered-jal-targets
