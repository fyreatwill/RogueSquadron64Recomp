# Next work unit

HYPOTHESIS-ID: m3-mul-census

WORK UNIT: perform one complete static census of generated `mul` annotations
against the retail ELF, including raw decode, emitted host lowering, and
per-function conservative CFG reachability. Do not change runtime behavior or
generated output.

Competing hypotheses:

* H-mul-correct: every decoded `mul` has the expected signed 32-bit product
  lowering and destination.
* H-mul-unsupported: a reachable nonzero-destination `mul` is missing or has
  the wrong signedness/width, identifying a recompiler defect.
* H-mul-data: every apparent mismatch is data-like/unreachable or writes
  `$zero`, so no live translation defect is selected.

DISCRIMINATING MEASUREMENT: one table must enumerate every generated `mul`
annotation, independently decode the raw ELF word, record the destination and
source registers plus the generated expression, and include CFG reachability.
Positive control: select the first decoded nonzero-destination row and require
its raw word, annotation, and host lowering to agree in the same run. A live
nonzero mismatch selects H-mul-unsupported; otherwise select H-mul-correct or
H-mul-data as applicable.

Exact commands:

    rg -n '\\bmul\\b' ../N64Recomp/RecompiledFuncs/funcs_*.c
    rg -n 'mult|mul|signed|32-bit' docs tools | head -100

Implement one bounded `tools/census_mul.py` if no complete raw-decode /
lowering / reachability table exists, run it once against
`../rogue_squadron64/build/roguesquadron.elf`, and write the result under
`docs/`.
