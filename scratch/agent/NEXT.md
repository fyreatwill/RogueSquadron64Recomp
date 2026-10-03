# Next work unit: M5 clear ordering and caller

HYPOTHESIS-ID: m5-clear-ordering-caller

Use the existing source-span writer rows and retail oracle to join the known
zero-fill writer `0x800078EC` to its caller and ordering before image input DMA
`0x1798B0 -> DMEM 0xCB0`. Do not suppress or replace the clear.

Competing hypotheses:

- `H-M5-ClearIsExpected`: the writer's caller/order matches the route's
  legitimate preparation and retail timing.
- `H-M5-ClearIsWrongOrder`: the clear runs after a legitimate producer or at
  the wrong route boundary, explaining the zero input.
- `H-M5-JoinMismatch`: the clear/source-DMA join is not the image-task object,
  or phase/ordinal alignment fails.

Discriminator: identify the caller/return chain for `0x800078EC` in the
existing generated symbols and join its phase-5 writer rows to the input-DMA
ordinals; compare the same physical source range and timing in the retail
oracle. `H-M5-ClearIsExpected` requires a matching preparation/order;
`H-M5-ClearIsWrongOrder` requires a legitimate producer or route event before
the clear followed by zero input; `H-M5-JoinMismatch` requires a failed source,
task, or phase join. If static caller mapping is insufficient, build one
instrument with caller, clear, source-DMA, and oracle controls in one run.
Require the oracle whole-RDRAM positive control and title/hangar phases.

Exact commands:

`grep -a -E '^\[(field348-writer|m5-input-dma|audtask-image-stage|audtask-image-dma-join|audtask-join)' scratch/agent/s3762_m5_step1_silent_repeat/image.log | grep 'phase=5 width=512' | tail -200`

`grep -a -E '^(oracle_gate|silent_hangar|image_hangar)' scratch/agent/s3762_m5_step1_silent_repeat/driver.log`
