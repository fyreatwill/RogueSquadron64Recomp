# NEXT work unit (s1170)

HYPOTHESIS-ID: indirect-callback-idiom-census

Perform one bounded static census of the generated indirect-callback
invocation idiom after s1169's valid `musyxSynthFrame` handoff. Do not build,
run, or add a mitigation in this unit.

Competing hypotheses and discriminator:

- H1: another callback-table `LOOKUP_FUNC` site has a malformed guest-frame
  handoff or target address; the complete site table contains an unbalanced
  `$sp`/`$ra` setup or a target that does not match companion symbols.
- H2: every callback-thread/audio callback site has the same balanced runtime
  ABI and valid target registration; the remaining fault is inside a
  downstream `musyxSynthFrame` operation class.
- H3: the source census cannot distinguish callback dispatch from unrelated
  dynamic lookup sites; the table has unresolved sites or target identities,
  so it is unevaluable and must not be used to justify a guard.

The discriminating measurement is one complete table covering every generated
`LOOKUP_FUNC`/`get_function` callback invocation in `viRetraceHandlerThread`,
the audio callback families, and every callback-table target observed in the
current state poll. Each row must include caller guest PC, lookup target
expression, `$sp` adjustment, `$ra` save/restore evidence, call ABI, and
companion-symbol match. H1 requires at least one malformed row; H2 requires
all in-scope rows balanced and matched; H3 is the outcome if any in-scope row
cannot be classified.

Exact commands:

    rg -n "LOOKUP_FUNC|get_function\(" ../N64Recomp/RecompiledFuncs/funcs_*.c
    sed -n '29890,30030p' ../N64Recomp/RecompiledFuncs/funcs_4.c
    rg -n "0x8011A8A4|0x8011A8A8|0x8009123C|callback" ../N64Recomp/RecompiledFuncs/funcs_*.c ../rogue_squadron64/symbol_files
    rg -n "viRetraceHandlerThread|musyx|callback" ../N64Recomp/symbols ../rogue_squadron64/symbol_files

Record the row counts, unresolved rows, and companion-symbol matches in the
next ledger entry. If the census is balanced, the following unit should audit
the complete downstream operation idiom in `musyxSynthFrame`, not add a
single-site skip.
