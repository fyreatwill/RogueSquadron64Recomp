# Next work unit: REVISIT external retail-entry boundary (sweep pivot)
HYPOTHESIS-ID: external-retail-entry-revisit

Why: the last 15+ session titles (s5013-s5027) all belong to the generated-symbol
renaming sweep, so per ITERATION.md this iteration is a REVISIT, not another
sweep step. s5027 (buildScaledFormatTextElement 0x800B3AFC) is committed;
docs/RENAME-S5027-AUDIT.md holds its gates. Do NOT resume the sweep.

Competing hypotheses (read CURRENT-TRUTH Next steps #2 and line ~281 first):
1. The boundary is an input/recipe gap (our recipe never reaches the qualified
   Rice route state), so a recipe change reaches it.
2. The boundary is a real runtime divergence reachable only via the oracle.
3. Boundary is design-dead (s4979 already closed one facet) and should be
   formally closed in CURRENT-TRUTH.

Discriminating measurement: check CURRENT-TRUTH's stated "genuinely new angle"
requirement (line ~261/519); pick one angle not in PORTING-STATE (grep it),
design the whole table in ONE instrument, run once. If no new angle exists,
go BLOCKED with that specific question or land an M5 de-stub from
docs/M5-AUDIO-PLAN.md instead.

Parked: normal MIPS patch qualification (needs a GCC toolchain).
