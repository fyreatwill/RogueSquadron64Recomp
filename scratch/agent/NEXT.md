# Resume next work unit

HYPOTHESIS-ID: m3-conditional-move-fixup-audit

WORK UNIT: audit the fixup/regeneration path for the statically reachable
nonzero-destination conditional move at `funcs_49.c:0x800A2B64` (and its
duplicate source context). Do not modify generated output or implement a fix
in this iteration.

Competing hypotheses:

* H-cmov-unsupported: N64Recomp deliberately emits `do_break` because the
  instruction is unsupported or intentionally treated as an invalid/data word.
* H-cmov-fixup-loss: the source annotation is valid MIPS `movn`, but a fixup or
  post-processing rule replaces the conditional assignment with `do_break`.
* H-cmov-regeneration-drift: the current generated file is stale or differs
  from the configured regeneration input, so the live output cannot identify
  the responsible stage without a clean replay comparison.

DISCRIMINATING MEASUREMENT: trace this exact guest PC through the current
generated comment, the source ELF/disassembly or N64Recomp input annotation,
`fixup_game_funcs.py`, and the generated output. The origin is selected by a
reproducible replay: unsupported selects if pristine N64Recomp already emits
`do_break`; fixup-loss selects if pristine output has the assignment but the
fixup changes it; regeneration-drift selects if the replay input/output does
not contain the site or differs before fixup. If the stages cannot be aligned,
record route-gap and do not patch.

Exact commands:

    sed -n '1,260p' docs/M3-S4840-MOVZ-MOVN-REACHABILITY.md
    rg -n '0x800A2B64|movn|do_break|fixup_game_funcs' ../N64Recomp tools patches
    sed -n '1,260p' tools/fixup_game_funcs.py
    git diff -- ../N64Recomp/RecompiledFuncs/funcs_49.c tools/fixup_game_funcs.py

No game build/run is needed unless the replay itself requires it; this is a
static provenance audit. Keep the no-behavior-change constraint explicit.
