# Generated-symbol audit — Session 5149

Candidate: `__osSumcalc = 0x8002F390`

The bounded rename helper reported `already-synchronized` and made zero
edits. The generated tree contains a real body in `funcs_8.c`, beginning at
`0x8002F390`; its return sequence ends at `0x8002F3E8`. The companion symbol
file places `__osIdCheckSum` at `0x8002F3EC`, giving an exact `0x5C` span. The
overlay table independently records `__osSumcalc` with `rom_size = 0x5C`. A
generated caller at `0x800306B4` invokes the function directly.

Conclusion: the semantic name, exact body span, and independent caller all
agree, but the generated function already has that name. Preserve it; no
rename is warranted.

Competing hypotheses resolved:

- H-generated-name-correct: confirmed, with the existing name already
  synchronized.
- H-host-wrapper: ruled out by the generated body and direct caller.
- H-span-mismatch: ruled out by the body end, companion boundary, and overlay
  span agreeing.
- H-unproven: ruled out by two independent structural lines of evidence.
