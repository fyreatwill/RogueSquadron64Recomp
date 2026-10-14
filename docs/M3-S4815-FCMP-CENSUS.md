# M3 s4815 — float compare / NaN-branch idiom census

Tool: `tools/census_fcmp_unordered.py <rom>` (scans the ROM for COP1 S/D compares, opcode 0x11 fmt 16/17 funct 0x30-0x3F, and requires a bc1t/bc1f within 3 words as a code-shape filter).

Generated code: 2,820 `c1cs = a OP b` sites (float `<` 1654, `<=` 833, `==` 319; double `<=` 17, `<` 14, `==` 2). ROM scan, code-shaped: lt 1608+11, le 815+17, eq 311+2, ole 9 — same order of magnitude as the generated counts (ROM scan also sees overlays/data, so exact equality is not expected).

## Concern
N64Recomp `src/operations.cpp:105-140` lowers the unordered-bit forms (c.un, c.ueq, c.ult, c.ule, c.ngle, c.ngl, c.nge, c.ngt) to the SAME plain C compare as the ordered forms (c.un/c.ngle -> constant false). On a NaN operand they would yield 0 where MIPS yields 1.

## Result
Code-shaped sites with the unordered bit set: **0** of 3,000+ compares (every unordered-form match has no adjacent bc1t/bc1f, i.e. is data). The game uses only c.lt / c.le / c.eq (+9 c.ole.s). For these, C `<`,`<=`,`==` are false on NaN, same as the MIPS condition (R4300i would additionally trap on signaling use; retail never reaches it).

## Verdict
Class closed: no NaN-divergent compare lowering is reachable. No guard added. Caveats: single-source (static ROM scan, no runtime hit counter); a 3-word bc1 window can miss compares whose branch is farther away (would only undercount unordered sites; the unfiltered totals for them are all in data-looking density, ~20 each, uniform with random bytes).
