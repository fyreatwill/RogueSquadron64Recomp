# NEXT (s7650)
HYPOTHESIS-ID: mk8-census-attribution

G6a/G6b/G6c and the G5 looks wait only on the owner (docs/OWNER-OPT-INS.md). If the owner reports, take that first.

s7649: tools/s7648_mk8_census.py pinned rt64_render_context.cpp:2088-2147 ([g1d-tex]/[g1d-cmd], gated by LOG_G1D_CMD)
to rs64_s7541_span (defined at 1884). Its FN regex misses some definitions (multi-line signatures, member functions,
lambdas), and D ("gated") is inferred from the enclosing function, so a misattributed site's D label is unproven.
Work unit (offline, bounded):
1. Make the attribution brace-aware: track brace depth from each FN match and only attribute to a function whose
   body still contains the line. For sites with no enclosing match, report as UNATTRIBUTED and classify by hand.
2. Add a planted control: an ungated `& 0x7FFFFFu` site placed after a gated function inside an unmatched definition
   must come out unclassified (today it would inherit the gated function's D).
3. Rerun `-v` and diff the attributions against s7648. Every site that changes function: re-read it and reclassify (D / D* / behaviour).
Hypotheses: H-cosmetic (re-attribution changes names but every site is still gated: 0 behaviour) vs H-hidden (>=1
ungated default-on key/bound at 8 MB surfaces -> fix it with a dd4 same-run control).
Rules: never touch build/saves; one game at a time; SIGKILL only.
