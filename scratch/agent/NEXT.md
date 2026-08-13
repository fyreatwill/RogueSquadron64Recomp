# NEXT work unit (systematic pre-chain wild-pointer consumer audit)

HYPOTHESIS-ID: m3-prechain-wild-pointer-audit

The s790 reachability repeat passed its controls but crashed in
`viRetraceHandlerThread` at `0x380000004` before VI 1024. Do not add a guard
from this crash or infer a parser result.

## Competing hypotheses

- H-shared-consumer: the `0x380...` fault family has a common generated/runtime
  consumer idiom before VI 1024. Prediction: source enumeration finds multiple
  sites that dereference or index guest-derived wild pointers, including the
  s790 path, with matching existing diagnostics.
- H-independent-consumers: s790 is another unrelated pre-chain failure.
  Prediction: the audit finds no shared consumer or value path across s785,
  s786, s787, and s790.
- H-writer-unresolved: the value is written upstream but current source cannot
  name the writer. Prediction: all consumers see already-corrupt state and
  existing traces lack a writer attribution.

## Discriminating measurement

One bounded source audit before any build or run. Enumerate every active
generated/runtime consumer of guest-derived pointers or indices capable of
producing the `0x380...` fault shape, then map each to the s785-s790 crash
records and existing positive controls. Do not change code.

## Exact audit

1. Search the active generated tree and runtime for `0x380`, wild-pointer
   guards, guest-address conversion, and array/index consumers; record bounded
   source windows and call sites.
2. Compare those sites with the four crash signatures and the s789 RT64
   writeback origin; distinguish shared consumers from independent callers.
3. If no shared consumer is identified, record H-independent-consumers and
   choose the highest-information writer probe. No mitigation is allowed.

Expected outcomes: a source-and-trace match selects H-shared-consumer; disjoint
consumers select H-independent-consumers; only already-corrupt inputs with no
writer attribution select H-writer-unresolved. A missing active source blocks
classification rather than justifying a guard.
