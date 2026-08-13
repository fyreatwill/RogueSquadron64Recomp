# NEXT work unit (s862)

HYPOTHESIS-ID: m3-coalesce-entry-state

Add one behavior-neutral, regeneration-safe entry probe to
`coalesceFreeHeapBlocks`, carrying its four incoming block bases and the
global free-list head. Batch the probe with computed-next values at both
guarded reads, then run one existing phase-gated capture after the retail heap
watch positive control. Do not add a guard or alter game values/control flow.

Competing hypotheses:

- H-heap-entry-state: an incoming base or computed next pointer is outside the
  expected RDRAM heap range; this identifies the state/writer boundary.
- H-heap-valid: all captured bases and computed next pointers are valid, so the
  recurring host symbol is not explained by this idiom.
- H-heap-unreached: the coalescer entry control does not fire in the 1024 phase;
  the family belongs to another phase or attribution path.
- H-probe-invalid: the retail or port positive controls fail, making the run
  unevaluable.

Discriminating measurement: in the same run, the retail whole-RDRAM and heap
watch controls, the existing phase/E9 controls, and bounded coalescer entry
rows must all fire. Invalid entry or computed-next values select
H-heap-entry-state; all valid rows select H-heap-valid; no entry rows select
H-heap-unreached; failed controls select H-probe-invalid.

Exact commands:

1. Add the single batched probe to `../N64Recomp/fixup_game_funcs.py`, then
   regenerate in order: `make_elf.py` -> N64Recomp -> fixup.
2. Build `RogueSquadron64Recomp` Debug once.
3. Run the retail oracle with its whole-RDRAM and heap-region controls, then
   run the existing phase-gated port recipe from `build/`, using SIGKILL and a
   non-hidden capture filename. Keep all passive breadcrumb env vars armed.
4. If the capture is valid, record the control counts and classify every
   coalescer row; queue any repeat soak rather than running it interactively.
