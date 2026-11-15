# NEXT (s7420)
HYPOTHESIS-ID: recompfuncs-parser-agreement

Class CC (CURRENT-TRUTH Next steps item 1). s7419 found `re.match(r'RECOMP_FUNC void (\w+)\(')` misses the 3
`__attribute__((weak)) RECOMP_FUNC` headers (isCinematicActive, setRngSeed, findAndUnlinkSmallestEntry), so rows after them are
attributed to the previous function. Fixed in s7418/s7419 only.
1. `grep -ln "RECOMP_FUNC" tools/*.py` -> for each parser: its header regex, whether it reads full-line and/or mid-line
   `// 0xADDR:` comments, how it handles delay-slot duplicate comments and fixup-inserted lines, and whether it EDITS code (fixup_*,
   apply_*) or only reads (audits).
2. Reference split: tools/s7419_dis_agree.rabbit() (weak-aware). For each parser, run its own split (import or copy its regex) over
   ../N64Recomp/RecompiledFuncs and diff the (function -> addr set) map against the reference: mis-attributed rows / functions.
3. For EDITING tools: intersect mis-attributed functions with the tool's target list; if a target is hit, show the generated line
   it edits (or fails to edit) and fix the regex in that fixup (regen order: fixups live in tools/fixup_*.py).
Hypotheses: H-clean (only the 3 weak headers differ, no fixup target among them, audits unaffected) / H-split (a parser
mis-attributes a target or an audit verdict row). Control: a planted `__attribute__((weak)) RECOMP_FUNC void zz_plant(` header in a
temp copy of one funcs_N.c must move rows in each un-fixed parser's split.
Re-run tools/s7419_dis_agree.py --controls and tools/s7418_opcode_residue.py (rc 0) after any shared-parser change.
