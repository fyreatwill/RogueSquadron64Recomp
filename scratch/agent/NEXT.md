# Next work unit (s4404): locate the title AI-boundary consumer call chain

HYPOTHESIS-ID: m5-selector-decode-boundary

The qualified port route is `0x00790400 -> 0x006AB400`; the absent
`0x00790800` bucket is not part of this unit. Session 4403 widened both host
filters: the AI-boundary witness fired in title and hangar, while the separate
AI-callsite witness fired zero times in both phases.

Competing hypotheses:

- H-consumer-is-hooked-boundary: the existing callsite hook is on the direct
  downstream path from `0x80029E78`/`0x80091CB8`, and a phase-scoped rerun with
  a corrected join will produce rows.
- H-consumer-is-different-callsite: the boundary witness is live, but the
  zero-row hook names a different or unreachable generated callsite; source
  inspection will identify the actual downstream target.
- H-boundary-is-terminal: the boundary is a selector-return/setup edge with no
  downstream consumer on the qualified route; source inspection will show the
  path terminates or branches away before publication.

Discriminating measurement: inspect the generated functions and existing hook
call sites around `0x80029E78`, `0x80091CB8`, and the zero-row callsite hook,
then add one phase-keyed downstream witness that records the first consumer
PC/arguments and joins it to the already-live task/image rows. A row at the
hooked PC selects H-consumer-is-hooked-boundary; a different downstream PC
selects H-consumer-is-different-callsite; no downstream row with a proven
fall-through/return selects H-boundary-is-terminal. Do not build until the
source read names these alternatives and the join key.

Exact commands:

1. `rg -n -C 12 "80029E78|80091CB8|rs64_m5_selector_ai_callsite|selector_ai" RecompiledFuncs src/main`
2. Read only the bounded generated-function windows; enumerate every direct
   call/return edge from the boundary hook to the candidate consumer.
3. Write the competing route table and the exact phase/task join into NEXT.md
   before making any instrumentation change.

The s4403 capture is at
`scratch/agent/s4402_m5_title_selector_witness/`; its positive control,
title/hangar phase counts, task/image joins, and zero-row callsite result are
the baseline for the next unit.
