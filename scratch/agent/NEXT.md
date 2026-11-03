# NEXT: G1d wide-width census, iteration 2 of 2 — W values carried through memory
HYPOTHESIS-ID: g1d-wide-epsilon-audit

State (s6848): direct screen-width reads are classified (docs/G1D-WIDTH-CENSUS.md, tools/g1d_wcensus.py). One new flipper
fixed (emitColorFillRect, apply_s6848_ovlwrap). The census's taint stops at stores, so values derived from W and parked in
memory are unaudited.

Hypotheses: H-mem-closed (no stored W-derived value reaches a fixed-epsilon compare or a 10/12-bit pack) vs H-mem-flip
(one does, like s6846 but through a field).
Method (offline, at most one build):
1. From the census sinks, list the store destinations of W-derived values: HUD layout floats (800FD6B4..800FE330 ->
   fields 0x40/0x70/0x1C0/0x1F0/0xA0 of the HUD struct), initHudStruct +0x54/+0x58, screen struct +0x18 centre writer.
2. grep RecompiledFuncs for loads of those (base, offset) pairs (lwc1/lw off(reg) in the same functions or their callees),
   follow each to compares/packs with tools/g1d_wcensus.py's taint logic (add a "field source" mode to the tool).
3. Classify as in the census. Fix any flipper with a W <= 640 bit-identical apply script + same-build A/B on the 21:9
   route (scratch/s6848/port_ovl.sh pattern; ROGUESQ_ASPECT=21:9).
Expected: 0 flippers -> close the class (CURRENT-TRUTH item 2 -> closed list) and move to the next ladder rung / owner
judgement items; N flippers -> fixes + A/B.
