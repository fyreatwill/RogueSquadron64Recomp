# Next work unit

HYPOTHESIS-ID: m3-double-shift-census

WORK UNIT: perform one complete static census of generated 64-bit shift
instructions (`dsll`, `dsrl`, `dsra`, `dsll32`, `dsrl32`, `dsra32`, and their
variable forms) against the retail ELF, then classify each site by raw decode,
generated lowering, and conservative CFG reachability. Do not change runtime
behavior or generated output.

Competing hypotheses:

* H-dshift-correct: every decoded 64-bit shift has the expected width, count,
  signedness, and destination lowering.
* H-dshift-unsupported: a reachable nonzero-destination site traps or omits
  the decoded shift, identifying a recompiler defect.
* H-dshift-data: every apparent mismatch is data-like/unreachable or writes
  `$zero`, so no live translation defect is selected.

DISCRIMINATING MEASUREMENT: one table must enumerate every generated annotation
for the complete double-shift class, independently decode the raw ELF word,
record the generated expression and destination/source registers, and include
CFG reachability. Positive control: first choose a decoded nonzero-destination
site from the table and require its raw word and generated expression to agree
in the same run. H-dshift-unsupported requires at least one reachable live
mismatch; otherwise select H-dshift-correct or H-dshift-data as applicable.

Exact reconnaissance commands:

    rg -n '\\b(dsll|dsrl|dsra|dsll32|dsrl32|dsra32|dsllv|dsrlv|dsrav)\\b' ../N64Recomp/RecompiledFuncs/funcs_*.c
    rg -n 'double|64-bit|dshift' docs tools

If no existing census provides the full raw-decode/lowering/reachability table,
write one bounded `tools/census_double_shifts.py` and run it once against
`../rogue_squadron64/build/roguesquadron.elf`.
