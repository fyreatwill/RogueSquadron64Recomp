# NEXT (s7777; s7776 closed the dangling NPC-slot table as H-unused)
HYPOTHESIS-ID: dangling-global-heap-ptr-class
First (any of these outranks the rest): `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers
in docs/OWNER-REVIEW-QUEUE.md, new SOAK-RESULTS lines.

Generalise s7776 into a class audit (ITERATION item 3 model: enumerate the whole idiom class, classify every member, close it).
Class: resident .data/.bss words that hold an rs_malloc pointer and outlive the block (the slot table *0x80130BB0 was one:
freed with the menu heap, never cleared, never read until re-init). Enumerate, one instrument, one run:
1. Static: every resident global word written from an rs_malloc return (sw of v0 after jal rs_malloc / wrappers) -> list of
   (global, writer fn, readers). Use objdump of the elf + the 59-site pattern from s7776 (tools/s7776_tblwatch_score.py header).
2. Runtime: at each overlay swap (s7528 pre/post lines) and each rs_free, check every listed global: does it point into a
   freed / reused block (s7480 freed map in src/main/upstream_compat.cpp)? For each dangling one, mark the word in the s7484
   bitmap (as s7776 does for 0x80130BB0) and count reads while dangling.
Hypotheses: H-all-unused (every dangling global is re-inited before its next read -> class CLOSED), H-latent (some global is read
while dangling -> name the reader, decide retail bug vs ours with the oracle), H-ours (a dangling global exists only because
our heap/overlay timing differs from retail).
Positive control: 0x80130BB0 must appear in the dangling list during the menu phase (s7776 window t=15-75 s on route_long).
Run: `zsh tools/s7774_slot_run.zsh <name> ROGUESQ_S7776_TBLWATCH=1 <new flag>` (300 s owner route, save read-only).
