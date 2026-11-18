# NEXT (s7601)
HYPOTHESIS-ID: guest-ram-byte-swizzle-census

Class GX closed s7600 (249 units, 0 open, 0 oob, controls 3/3; tools/s7600_gx_census.py).

Class BS = host code (src/, librecomp/src, ultramodern/src, lib/rt64/src; skip tests/tools/gui) that accesses guest RAM
through the byte-swapped host view (rdram / RDRAM / g_rdram_for_submit / MEM_B/MEM_H/MEM_W macros) with a multi-byte or
sub-word access. Contract on this little-endian host: byte at guest addr A is rdram[A ^ 3]; halfword at A is
*(uint16_t*)(rdram + (A ^ 2)) (A 2-aligned); word at A is *(uint32_t*)(rdram + A) (A 4-aligned); multi-word spans via
memcpy need a per-word swap or a documented byte-reversed consumer.
Per site classify: ok-byte (^3), ok-half (^2), ok-word (aligned, no xor), ok-macro (MEM_*), swapped-consumer (bulk copy
whose consumer swaps, named), gated (diagnostic, gate named), BAD (wrong xor for the width, missing xor on a byte/half,
xor on an aligned word, or unaligned word read) -> must be 0 on default paths.
Hypotheses: H-clean (every default-path access uses the right swizzle), H-bad (some default-path site uses the wrong one:
silent wrong value), H-gated (only diagnostics are wrong).
Tool: tools/s7601_bs_census.py --controls (plant `rdram[a]` byte read with no ^3, and a `*(uint16_t*)(rdram + (a ^ 3))`
half read, into a copy of dpc_bridge.cpp; drop one row; all must be OPEN/BAD).
Runtime witness for any BAD default-path row: same-run A/B (fixed vs old under an env switch) on the value it reads, with a
known-value positive control (a guest word at a fixed address whose retail value is known, e.g. from the oracle).
Never touch build/saves; never clear ROGUESQ_NO_SAVE_WRITE.
