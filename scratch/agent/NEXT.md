# Next work unit: M5 target-buffer identity versus family execution edge

HYPOTHESIS-ID: m5-retail-writer-port-edge

Use s3768's fixed boundary: the generated port contains the retail writer
bodies, but no family write joined either target buffer in the qualified s3767
capture. Determine whether those bodies execute with a different
destination/route or do not execute in the target phases. Do not suppress or
replace the clear.

Competing hypotheses:

- `H-M5-RetailWriterFamilyExecutesSameTarget`: all three family classes
  execute in a target phase and write the clear-associated buffer.
- `H-M5-RetailWriterFamilyExecutesOtherObject`: family execution is present,
  but its destination or route identity differs from the clear-associated
  target buffer.
- `H-M5-RetailWriterFamilyAbsentTargetEdge`: positive controls and both target
  phases pass, but one or more family classes produce no target-phase edge.

Discriminator: one phase-scoped table keyed by the three family classes
(`rs_strncpy`, texture-LUT zeroing, texture-record population), recording
execution count, destination range, phase, route ordinal, and relation to the
`0x8008F2CC` clear. Same-target, other-object, and no-target rows split the
hypotheses. The run must retain the oracle whole-RDRAM positive control and
both title/hangar phases.

Before building, verify the current fixup anchors and existing positive
controls:

`rg -n '80007670|8001E2C0|8001F|800078EC|8008F2CC' RecompiledFuncs src docs | head -200`

`rg -n 'rs_strncpy|initTextureLUTAndAllocBuffers|loadTextureToMemory|m5_writer_parity' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_{2,6}.c tools`

`grep -a -E '\[oracle\] (watch write|done:)|\[vi\].*origin=0x00(790400|6ab400)' scratch/agent/s3767_m5_postclear_order/oracle.log | tail -80`

The implementation must be one regeneration-safe batch instrument, one build,
and one concurrent oracle/image/silent run. Positive-control failure or a
missing target VI invalidates that arm rather than producing a null result.
