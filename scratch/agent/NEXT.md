# Next work unit: recover the missing allocateDisplayListBuffer instruction window
HYPOTHESIS-ID: m3-assembly-patch-pipeline

Competing hypotheses:

1. The remaining seven-instruction-equivalent gap is recoverable from the
   original/generated entry and the assembly port can reach the known `0xE8`
   span with matching control flow.
2. The current `0xCC` result is only a size/layout difference; existing stores
   and branches already cover the complete behavior.
3. Available source is insufficient to prove the missing control flow, so the
   assembly override must remain disabled pending a new source artifact.

Discriminating measurement: locate the recovered/generated entry or an
independent disassembly for `0x80007D74..0x80007E58`, then compare every
branch target, load/store address, and call against `patches/heap_guard_asm.S`.
An exact source-backed `0xE8` match selects H1; a complete `0xCC` source-backed
entry selects H2; absent or ambiguous missing instructions selects H3 and
requires a human-provided source artifact. Do not pad or enable the override.
