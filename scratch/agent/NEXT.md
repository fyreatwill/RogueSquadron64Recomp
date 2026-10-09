# Next work unit (s4341): identify the port counterpart of retail branch state

HYPOTHESIS-ID: m5-step9-branch-state-field-mapping

s4340 passed the port host positive control, title VI 1024, hangar VI 512, and
255 C88C rows. Its all-generated-scalar-store census found zero writes to
physical `0x20..0x30`. The independent 75-second retail oracle passed its
whole-RDRAM control (10,000 callbacks), title/hangar VI controls, and exact
low-range watch, which also found zero writes. Therefore port `s1+0x22` is not
the semantic counterpart of retail C904 branch state. The external field-key
arm remains route-invalid.

Competing hypotheses:

- H-port-table-field: the port's branch-state counterpart is a different
  offset in the object/table loaded by `decodeAndFillVoiceBlock`.
- H-port-selector-field: the counterpart is derived from the C88C branch
  selector or descriptor arguments rather than loaded from `s1+0x22`.
- H-retail-DMA-field: retail's nonzero C904 field arrives in a DMA/ROM-loaded
  block, so no scalar writer should be expected in either runtime's low range.

Discriminator: one bounded static/data-flow table over the generated
`decodeAndFillVoiceBlock` body and its C88C call arguments: enumerate every
load/store offset based on `s1`, every branch-selector/descriptor load, and the
four argument values retained at C88C. Join those candidates to the retained
retail C904 tuples by `s1=1/2` and phase. A candidate whose port value follows
retail `0x0010/0x3108` selects H-port-table-field; a selector/descriptor value
does so selects H-port-selector-field; only a DMA-loaded candidate with a
matching source range selects H-retail-DMA-field. If no candidate qualifies,
the next step is a single new runtime witness at the best static load, not
another low-range writer census.

Run requirements:

1. Use `rg` plus bounded `sed` windows; inspect only the generated C88C helper,
   its direct callees, and the retained retail C904 rows.
2. Do not build or run until the candidate table has explicit outcomes for all
   three hypotheses.
3. Do not add a guard, alter decoder/RSP/AI behavior, or use the external
   field-key route.
