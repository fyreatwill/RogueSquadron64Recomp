# Next work unit (s4406): locate the alternate hangar AI caller

HYPOTHESIS-ID: m5-selector-decode-boundary

Session 4405 compared both generated direct edges. The qualified route is
title `0x00790400:1024` followed by hangar `0x006AB400:512`; `0x00790800`
remains out of scope. The raw witness observed `0x80091CB8` once in title,
neither direct edge in hangar, and live hangar AI-boundary/setup/source/mixer/
input/store-entry witnesses.

Competing hypotheses:

- H-alternate-hangar-caller: hangar reaches `0x80029D20` through a generated
  caller other than the two direct edges already instrumented.
- H-hangar-callsite-filter-gap: a direct edge is live in hangar but the
  phase/key filter or row budget misses it; existing boundary/setup rows remain
  live and a corrected witness exposes it.
- H-title-only-boundary-path: hangar's live boundary/setup rows do not come
  from a generated call to `0x80029D20` in the qualified route.

Discriminating measurement: static-enumerate every generated call to
`0x80029D20`, then add one bounded witness for the uninstrumented candidate
and run the same phase-gated route. A hangar row at a new candidate selects
H-alternate-hangar-caller; a direct-edge row after a filter repair selects
H-hangar-callsite-filter-gap; no candidate row with live boundary/setup
controls selects H-title-only-boundary-path.

Exact commands:

1. Enumerate callers:
   `rg -n -C 4 "jal.*80029D20|rs64_m5_selector_ai_callsite|80091BAC|80091CB8" ../N64Recomp/RecompiledFuncs/funcs_24.c`
2. Add the candidate witness through the regeneration-safe probe script,
   rebuild with `cmake --build build --config Debug --target RogueSquadron64Recomp`.
3. Run the qualified capture:
   `zsh scratch/agent/run_s4402_m5_title_selector_witness.sh`
4. Read only the summary and bounded rows:
   `grep -E "^(control|title_790400|hangar_6AB400|caller|ai_boundary|crash|abort)=|m5-selector-(ai-callsite|caller|ai-boundary)" scratch/agent/s4402_m5_title_selector_witness/summary.txt scratch/agent/s4402_m5_title_selector_witness/port.log`

Do not add another field or repeat the retail payload census. If the current
85-second route is invalid, record the route failure rather than interpreting
caller absence.
