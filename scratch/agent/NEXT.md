# Next work unit (s4407): map the indirect hangar AI boundary entry

HYPOTHESIS-ID: m5-selector-decode-boundary

Session 4406 found exactly two generated calls to `0x80029D20`, at
`0x80091BAC` and `0x80091CB8`; both were already instrumented. The qualified
route passed the control, reached title `0x00790400` and hangar `0x006AB400`,
and retained 2,313 task/image joins plus 256 filter joins. The raw witness
observed `0x80091CB8` once in title and neither direct edge in hangar, while
the hangar AI boundary and `ai-return` setup remained live.

Competing hypotheses:

- H-indirect-or-aliased-entry: hangar reaches the live boundary through an
  indirect dispatch, overlay alias, or generated target body not represented by
  a direct `jal` edge.
- H-hangar-callsite-filter-gap: a direct edge is live in hangar but the
  phase/key filter or row budget misses it; the exhaustive two-edge scan is
  incomplete only at the host witness.
- H-title-only-boundary-path: hangar's live boundary/setup-return rows do not
  represent entry through `0x80029D20` in the qualified route.

Discriminating measurement: enumerate the generated function body/aliases for
`0x80029D20`, identify the first uninstrumented entry or indirect dispatch
that can reach the boundary, add one bounded regeneration-safe witness there,
and run the same phase-gated route. A hangar entry row selects
H-indirect-or-aliased-entry; a direct-edge row after a host filter repair
selects H-hangar-callsite-filter-gap; live boundary/setup-return controls with
no entry row select H-title-only-boundary-path.

Exact commands:

1. Enumerate target body and aliases:
   `rg -n -C 8 "80029D20|80029E78|rs64_m5_selector_ai_boundary" ../N64Recomp/RecompiledFuncs ../N64Recomp/fixup_game_funcs.py src/main/upstream_compat.cpp`
2. Add one entry/dispatch witness through the regeneration-safe probe script,
   rebuild with `cmake --build build --config Debug --target RogueSquadron64Recomp`.
3. Run the qualified capture:
   `zsh scratch/agent/run_s4402_m5_title_selector_witness.sh`
4. Read only the summary and bounded rows:
   `grep -E "^(control|title_790400|hangar_6AB400|task_joins|filter_joins|caller|ai_boundary|crash|abort)=|m5-selector-(ai-callsite|caller|ai-boundary|setup-contract)" scratch/agent/s4402_m5_title_selector_witness/summary.txt scratch/agent/s4402_m5_title_selector_witness/port.log`

Do not add another field or repeat the retail payload census. If the current
85-second route is invalid, record the route failure rather than interpreting
caller absence.
