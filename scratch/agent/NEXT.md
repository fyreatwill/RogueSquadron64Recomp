# NEXT (s7771)
HYPOTHESIS-ID: jal-interior-target-census
First (any of these outranks the rest): `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers
in docs/OWNER-REVIEW-QUEUE.md, new SOAK-RESULTS lines. The rename sweep is CLOSED (s7770 census called=0; the stop gate blocks
a NEXT.md naming it).

Unit (offline, no game run, one bounded idiom-class audit, ITERATION item 3 model): every jal whose target is NOT a function
start in the ELF (and so not a generated function entry), classified. s7770's objdump pass found 5 of 1787 targets (0x80007064,
0x800AF6AC, 0x800E9B10, 0x800EA01C, 0x8334B334), but objdump prints the exception block as data, so redo it from raw words:
1. Extend tools/s7770_placeholder_census.py (or a sibling tools/s7771_jal_target_census.py) to scan every 4-aligned word of
   each code section (.text + each .ovl.* separately, since overlays share VMA 0x800A5130), and for each jal target report:
   section of the call site, whether the target is an ELF symbol start, in which section, and the enclosing symbol + offset.
2. Classify each non-start target, hypotheses: H-data (the call-site word is data decoded as code: past the enclosing
   function's real end, or no valid neighbours), H-ovl (target is a start in a DIFFERENT overlay than the one mapped when the
   call site runs: harmless, the call site's own overlay is what counts), H-interior (a real call into the middle of a
   function: N64Recomp must emit a lookup/stub for it; check the generated tree for what it does - a wrong body would be a
   live defect), H-split (the ELF merges two functions, like redispatch+send_mesg).
3. For every H-interior row, find the generated call (grep the caller's funcs_*.c for the target address) and say whether the
   runtime reaches a correct body. Controls: a planted jal to a mid-body address must classify H-interior; a known clean call
   (jal __osEnqueueThread) must classify start.
Outcome: 0 H-interior -> class CLOSED; any H-interior with a wrong generated body -> fix via a fixup script (regen order
make_elf -> N64Recomp -> fixup_game_funcs -> cmake) and same-run control.
