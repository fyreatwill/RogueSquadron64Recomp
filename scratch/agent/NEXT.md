# Next work unit: offline audit of unguarded indirect-call / jr-ra sites (M3 class "all")
HYPOTHESIS-ID: m3-unguarded-indirect-sites-all
Static/offline only (parallelizable; no game run). Enumerate every indirect jalr/jr (non-ra and ra) site in the generated recomp output, check which route through a guarded dispatch (fixup scripts / lookup helper) vs raw, classify raw sites by target-set provenance (jump table, vtable, overlay callback, unknown), and rank unknown-provenance ones by reachability on title->hangar->mission. Output: table in scratch/ + session entry. Only propose a runtime probe if a ranked site has a concrete defect hypothesis; any probe needs a same-run positive control. Do not touch plume (reopen only on new si_addr=0x58 SIGSEGV).
Human may still redirect (BLOCKED s5387 options b/c); see CURRENT-TRUTH open dependency.

## OWNER DIRECTION 2026-10-17 (see ITERATION.md item 3b): after this offline audit (max 2 iterations), pivot to M6 play-through endurance. Do NOT write BLOCKED.md for "no discriminator remains" - do M6.
