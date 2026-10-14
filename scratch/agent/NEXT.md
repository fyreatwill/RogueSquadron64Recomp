# Next work unit

HYPOTHESIS-ID: m3-hi-lo-move-census

WORK UNIT: perform one complete static census of generated HI/LO move
instructions (`mfhi`, `mflo`, `mthi`, `mtlo`) against the retail ELF, then
classify every site as correctly lowered, unsupported/trapping, or data-like.
Do not change generated output or runtime behavior.

Competing hypotheses:

* H-hilo-correct: every decoded HI/LO move has the expected generated register
  transfer or HI/LO write, so this translation class needs no fix.
* H-hilo-unsupported: one or more live-destination sites lower to `do_break`
  or otherwise omit the HI/LO operation, identifying a recompiler defect.
* H-hilo-data: all apparent mismatches are data-like/unreachable or write
  `$zero`, so no live translation defect is selected.

DISCRIMINATING MEASUREMENT: one table must enumerate every generated
`mfhi`/`mflo`/`mthi`/`mtlo` annotation, independently decode the raw ELF word,
and record the generated lowering plus destination/source register. The
outcome is H-hilo-correct if all live sites match; H-hilo-unsupported if any
reachable live site omits or traps the operation; otherwise H-hilo-data if
all mismatches are data-like/unreachable or zero-destination sites.

Exact commands:

    rg -n '\\b(mfhi|mflo|mthi|mtlo)\\b' ../N64Recomp/RecompiledFuncs/funcs_*.c
    python3 tools/census_unhandled_cpu.py --source ../N64Recomp/RecompiledFuncs --elf ../rogue_squadron64/build/roguesquadron.elf --output docs/M3-S4846-UNHANDLED-CPU-CENSUS.md

If the generic census does not provide HI/LO lowering and reachability rows,
write one bounded `tools/census_hilo_moves.py` that produces that complete
table in the same work unit; do not split the census across iterations.
