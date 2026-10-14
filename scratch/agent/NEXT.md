# Next work unit

HYPOTHESIS-ID: m3-next-complete-idiom-census

WORK UNIT: perform one complete static census of the next unclosed generated
translation class: valid CPU instructions that currently fall through
N64Recomp's generic `do_break` path. Do not modify generated output or
implement a recompiler fix in this iteration.

Competing hypotheses:

* H-unhandled-data: every generic-trap site in the selected opcode class is
  data-like or unreachable, so no live translation defect is exposed.
* H-unhandled-live: at least one valid nonzero-destination site is reachable
  in the generated CFG, selecting a real missing lowering for follow-up.
* H-decoder-disagreement: the generated annotation or raw word disagrees with
  Rabbitizer/source decoding at one or more sites, selecting a decoder or
  input-provenance issue instead.
* H-fixup-interference: a valid site is lowered before the fixup pass and is
  changed to `do_break` by a post-processing rule, selecting a fixup audit.

DISCRIMINATING MEASUREMENT: enumerate every selected-class source instruction
and every corresponding generated `do_break`, independently decode the raw
word, classify CFG reachability, and compare pristine output against the live
output and `fixup_game_funcs.py`. H-unhandled-data yields zero reachable
nonzero destinations; H-unhandled-live yields one or more; H-decoder-
disagreement yields a raw/annotation mismatch; H-fixup-interference yields a
pristine assignment replaced by fixup. Any missing stage alignment is a
route-gap, not a conclusion.

Exact commands:

    rg -n 'Unhandled instruction|emit_do_break|binary_ops|unary_ops|conditional_branch_ops' ../N64Recomp/src ../N64Recomp/include
    python3 tools/census_unhandled_cpu.py --source ../N64Recomp/RecompiledFuncs --elf ../rogue_squadron64/build/roguesquadron.elf
    python3 tools/classify_unhandled_cpu.py --source ../N64Recomp/RecompiledFuncs
    git diff -- ../N64Recomp/src ../N64Recomp/RecompiledFuncs tools/fixup_game_funcs.py

No game build/run is needed. If the named census scripts do not exist, create
them as the bounded engineering change before running the census; keep the
no-behavior-change constraint explicit.
