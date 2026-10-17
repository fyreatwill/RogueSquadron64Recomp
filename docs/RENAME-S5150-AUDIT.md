# Generated-symbol audit — Session 5150

Candidate: `__osIdCheckSum = 0x8002F3EC`

The bounded rename helper reported `already-synchronized` and made zero
edits. The generated tree contains a named body in `funcs_8.c`, beginning at
`0x8002F3EC`; its return sequence ends at `0x8002F450`. The companion symbol
file places `__osRepairPackId` at `0x8002F454`, giving an exact `0x68` span.
The overlay table independently records `__osIdCheckSum` with
`rom_size = 0x68`. The generated tree contains no independent caller beyond
the definition.

Conclusion: the semantic name and exact body span agree, but the generated
function already has that name. Preserve it; no rename is warranted.

Competing hypotheses resolved:

- H-generated-name-correct: confirmed, with the existing name already
  synchronized.
- H-host-wrapper: ruled out by the generated body and direct span evidence.
- H-span-mismatch: ruled out by the body end, companion boundary, and overlay
  span agreeing.
- H-unproven: ruled out by the generated body and two independent span
  records; the absent independent caller does not create a rename case.
