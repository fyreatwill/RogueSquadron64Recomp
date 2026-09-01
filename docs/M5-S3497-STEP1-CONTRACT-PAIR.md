# M5 Session 3497 — Step 1 same-build contract pair

The existing phase-gated Step 1 driver ran the independent retail oracle
preflight, then launched silent (`ROGUESQ_AUDIO_UCODE=0`) and default image
(`factor5_ucode_b`) arms from the same build. The oracle whole-RDRAM positive
control reached 10,000 callbacks and both title `0x00790400`/1024 and hangar
`0x006AB400`/512 phases.

Both port arms reached title and hangar without crash or abort:

| signal | silent | image |
|---|---:|---:|
| audio dispatch | 50 | 50 |
| task ABI rows | 668 | 668 |
| DMA-range rows | 0 | 1,359 |
| image-stage rows | 0 | 2,738 |
| audio-return rows | 294 | 296 |
| audio route rows | 951 | 960 |
| SP route rows | 951 | 960 |
| PCM source/consumer rows | 84 / 84 | 85 / 85 |
| title / hangar phase | 1 / 1 | 1 / 1 |
| crash / abort | 0 / 0 | 0 / 0 |

The independent oracle control and both port phase controls were positive.
The image arm demonstrably executes the image task's DMEM/DMA and image-stage
path, while the silent control does not. Both arms still publish zero-valued
PCM in sampled rows and neither reports slot allocation, so this does not
close the downstream audio contract or prove audible output.

This selects the Step 1 image-task-progress hypothesis at the dispatch/task
boundary and clears the route-qualification blocker for the selector-load
comparison. It does not select selector parity or source divergence.

Evidence: `scratch/agent/s3497_m5_step1_contract_pair/driver.log` and the
three captured arm/oracle logs in that directory.

ORIGIN: diagnostic-only task, DMA, route, PCM, and phase observations; no
audio state, task field, selector value, or output was rewritten, skipped, or
validated.
