# Next work unit (s4405): compare the two direct title/hangar AI edges

HYPOTHESIS-ID: m5-selector-decode-boundary

The regenerated callsite probe is now present at both direct generated edges.
The qualified route is title `0x00790400:1024` followed by hangar
`0x006AB400:512`; `0x00790800` remains out of scope. Session 4404 observed
`0x80091CB8` in title and no callsite row in hangar, while AI-boundary and
setup controls were live in both phases.

Competing hypotheses:

- H-reapply-edge-is-phase-specific: `0x80091CB8` is the live title edge and
  the hangar path uses `0x80091BAC` or another phase-specific setup route.
- H-hangar-callsite-filter-gap: the direct edge is live in hangar but the
  phase/key filter or row budget misses it; the existing boundary/setup rows
  will remain live, and widening only the callsite diagnostic will expose it.
- H-title-only-startup-edge: `0x80091CB8` is startup/title-only and neither
  direct edge is entered by the hangar selector path; hangar boundary/setup
  rows are from a host-equivalent path without these generated edges.

Discriminating measurement: one phase-gated run with both direct callsite
labels, the positive control, AI-boundary, setup-contract, and task/image
controls. A hangar row at `0x80091BAC` selects H-reapply-edge-is-phase-
specific; a hangar row at `0x80091CB8` selects the same hypothesis with the
existing edge; no hangar callsite row despite live boundary/setup controls
selects H-title-only-startup-edge unless a widened callsite row budget changes
that result, which selects H-hangar-callsite-filter-gap.

Exact commands:

1. Verify both generated probe calls:
   `rg -n -C 3 "rs64_m5_selector_ai_callsite|80091BAC|80091CB8" ../N64Recomp/RecompiledFuncs/funcs_24.c`
2. Build:
   `cmake --build build --config Debug --target RogueSquadron64Recomp`
3. Run the qualified capture:
   `zsh scratch/agent/run_s4402_m5_title_selector_witness.sh`
4. Read only the summary and bounded callsite rows:
   `grep -E "^(control|title_790400|hangar_6AB400|caller|ai_boundary|crash|abort)=|m5-selector-ai-callsite" scratch/agent/s4402_m5_title_selector_witness/summary.txt scratch/agent/s4402_m5_title_selector_witness/port.log`

Do not add another field or repeat the retail payload census. If the current
85-second route is invalid, record the route failure rather than interpreting
callsite absence.
