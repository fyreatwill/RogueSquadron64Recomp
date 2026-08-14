# NEXT work unit (s1044)

HYPOTHESIS-ID: m4-zero-shade-accumulator-origin

Perform one bounded offline reconstruction of the Factor 5 shade producer from
the captured M4 stage rows and the exact RSP accumulator rules. Do not change
runtime code or add a mitigation. Locate the saved stage-10/11/12 capture,
extract complete triplets, and compute the four lanes before `vmadh v6,v4,v0`,
after the accumulator high-half/saturation step, and after `vge v6,v6,v29[1q]`.
The checker must include a synthetic positive control that reaches 0x8000 so a
zero result cannot be mistaken for a dead parser or bad extraction.

## Competing hypotheses and discriminator

* `H-accumulator-saturation`: 0x8000 appears only after the accumulator
  high-half/saturation step, selecting saturation as the sentinel origin.
* `H-v4-v0-arithmetic`: 0x8000 is already present before saturation, selecting
  ordinary `v4`/`v0` arithmetic as the origin.
* `H-v29-selection`: no pre-saturation endpoint exists, but the final `vge`
  selects a matching 0x8000 lane from the DMEM-0x60 threshold vector.

Discriminating measurement: classify the first stage at which any real row
contains 0x8000, and verify the synthetic control reaches the expected stage.
Pre-saturation, post-saturation, and threshold-only outcomes select the three
hypotheses above; no endpoint in real rows leaves the numeric origin open.

## Exact commands

```sh
rg -n "stage-(10|11|12)|vmadh|vge|0x8000" scratch/agent logs docs
rg -l "stage-10" scratch/agent logs | head -20
sed -n 'START,ENDp' <the_selected_capture>
```
