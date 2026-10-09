# Next work unit (s4342): witness the static branch-state candidates

HYPOTHESIS-ID: m5-step9-branch-state-runtime-witness

s4341 corrected the static boundary: `0x8009C88C` is the filter callsite inside
`updateVoiceChannelParamsLarge`, while C904 is the `decodeAndFillVoiceBlock`
entry. C904's only external object data source is the word at
`object+0x1A0+cursor_index`, where the cursor comes from `+0x11C8`; decoded
stack halfwords then supply the actual C88C filter arguments. Retail C904 rows
still use `branch_state=0x0010/0x3108` by `s1`.

Competing hypotheses:

- H-port-table-field: the counterpart is in the object-backed bit-table word
  selected by `+0x11C8`.
- H-port-selector-field: the counterpart is one of the decoded stack halfwords
  supplied as C88C `a0/a1`.
- H-retail-DMA-field: an earlier DMA/ROM-loaded producer populates the table,
  so C904 cannot expose a direct counterpart.

Discriminator: one phase-gated co-located witness at the actual C88C filter
callsite recording cursor/index, selected table word, and decoded stack `a0/a1`.
A value family following retail `0x0010/0x3108` selects table versus selector;
only matching source-range provenance selects the DMA hypothesis. The host
positive control, title VI 1024, hangar VI 512, and filter controls must fire.

Run requirements:

1. Build all candidate fields in one instrument and run one qualified
   in-process-autopilot capture; do not use the external field-key route.
2. Positive controls must visibly fire in the same run.
3. Do not add a guard or alter decoder/RSP/AI behavior.
