# M5 s3558 — image versus silent audio contract qualification

The first launch used `ROGUESQ_AUTOPILOT=1`, which is not a valid schedule;
both arms stopped at VI 640 and that attempt was discarded. The fixed launch
used the validated in-process schedule, `ROGUESQ_LLE_FORCE=1`,
`ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`, `ROGUESQ_SPIN_YIELD=1`, and
`ROGUESQ_STUB_MISSING_FUNCS=1`, from the rebuilt `build/` binary. Image and
silent arms ran concurrently and were killed by `tools/probe.sh` after 75
seconds beyond the 1024 phase gate.

The independent retail preflight passed with `rc=0`, reached the whole-RDRAM
positive-control cap of 10,000 writes, and reached the hangar VI origin
`0x006AB400` at width 512. Both port arms reached title
`0x00790400`/1024 and hangar `0x006AB400`/512, with no crash or abort marker.

| phase-gated signal | image `factor5_ucode_b` | silent `musyx_stub` |
|---|---:|---:|
| dispatch | 80 | 80 |
| task ABI | 2,494 | 2,520 |
| DMA range/row | 7,773 / 2,494 | 0 / 2,520 |
| image-stage rows | 9,693 | 0 |
| audio return | 529 | 528 |
| audio route | 2,130 | 2,349 |
| SP-completion text rows | 3,882 | 3,996 |
| PCM source / consumer | 99 / 99 | 99 / 99 |
| target phases title / hangar | 1 / 1 | 1 / 1 |
| crash / abort | 0 / 0 | 0 / 0 |

Representative target rows show both arms returning `exit=1` and reaching
`sp-complete-enter`. The image arm's first PCM source and consumer rows have
`nz=768`; the silent arm's corresponding rows have `nz=0`. The image summary
reported 1,021 stage rows in title and 1,022 in hangar, only two nonzero stage
rows in each, and `source_matches=0`, `consumer_matches=0`. No named MORT row
or slot/status transition row appeared in this matrix; voice/filter audit
controls were present but do not establish a completed slot or MORT join.

This selects `H-ImageTaskContractGap` at the current discriminator: the image
task has real DMEM/DMA and completion activity, and the port PCM path is live,
but the image-stage destination relation does not join to the sampled PCM
buffers and the task/slot/MORT chain is not closed. It does not authorize a
writeback, gate, slot, or MORT behavior change. The silent arm remains a valid
same-build no-DMEM/DMA control.

Evidence is two-source for route validity (retail oracle plus both port phase
controls) and single-source for the detailed port audio contract. Logs:
`scratch/agent/s3558_m5_audio_contract/oracle.log`,
`scratch/agent/s3558_m5_audio_contract/image-fixed2/run.log`, and
`scratch/agent/s3558_m5_audio_contract/silent-fixed2/run.log`.

ORIGIN: diagnostic-only task, DMEM/DMA, completion, slot/voice, MORT, PCM,
and phase observations; no audio state, task field, output, or gate was
rewritten or skipped.
