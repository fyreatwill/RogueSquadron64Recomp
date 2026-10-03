# Next work unit: M5 Step 1 same-run contract comparison

HYPOTHESIS-ID: m5-step1-contract-gap

Use the completed s3762 same-build capture to identify the first downstream
contract edge that differs between the qualified image and silent arms. Do not
add instrumentation, add another task-data value field, or change an audio
gate until this comparison selects a missing edge.

Competing hypotheses:

- `H-M5-ImageStageOnly`: the only meaningful arm difference is the expected
  nonzero image-stage/DMA work; shared task completion, route, PCM, and target
  phase prove no downstream contract gap in the measured Step 1 rows.
- `H-M5-SilentContractEdge`: silent and image diverge at a measured task,
  return, slot, voice, or PCM edge despite both reaching target phases; that
  edge is the next de-stubbing boundary.
- `H-M5-RunAccounting`: the apparent difference is caused by row budgets,
  phase gating, or arm-specific sampling rather than behavior; control counts
  or ordinal alignment will fail before an edge can be selected.

Discriminator: compare `scratch/agent/s3762_m5_step1_silent_repeat/driver.log`
and both arm logs by phase and ordinal for dispatch, ABI/DMA, image-stage,
audio-return/route, slot/voice, and PCM source/consumer rows. Positive controls
are oracle whole-RDRAM=10000 plus title/hangar for oracle, image, and silent.
An image-stage-only difference selects `H-M5-ImageStageOnly`; a first shared
ordinal/phase edge selects `H-M5-SilentContractEdge`; missing controls or
budget truncation selects `H-M5-RunAccounting` and requires a redesigned
capture.

Exact commands:

`grep -a -E '^(oracle_gate|silent_hangar|image_hangar|.*=([0-9]+)|--- )' scratch/agent/s3762_m5_step1_silent_repeat/driver.log`

`grep -a -E '^\\[(audtask-|audio-|pcm-|slot-|filter-voice|phase)' scratch/agent/s3762_m5_step1_silent_repeat/{silent,image}.log | sed -n '1,240p'`
