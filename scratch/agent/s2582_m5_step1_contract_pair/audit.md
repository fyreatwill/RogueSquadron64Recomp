# s2582 M5 Step 1 contract checkpoint

The unchanged Debug build passed the required independent retail control before
the port arms: the oracle reported the 10,000 whole-RDRAM callback threshold,
nonzero VI, title `0x00790400 @ 1024`, and hangar `0x006AB400 @ 512`.

The silent and image arms were run with the same driver and phase gates. Both
reached title and hangar. The image arm positively executed the Factor 5 image
stage and generated two DMA ranges per observed task; the silent arm generated
neither. Both arms nevertheless had zero task output/yield fields and matching
PCM boundary rows whose sampled buffers were zero (`fnv=F59C39C5`, `nz=0`). No
slot, voice, or reaping rows appeared in either arm. The image arm had no crash;
the silent arm reproduced the known wild-ROM PI-DMA crash in `recomp::do_rom_read`
from guest PC `0x80001B08`.

| phase | arm | ABI rows | image stages | audio returns | PCM source/consumer |
|---|---:|---:|---:|---:|---:|
| title 1024 | silent | 0 | 0 | 260 | 45 / 45 |
| title 1024 | image | 0 | 2922 | 260 | 45 / 45 |
| hangar 512 | silent | 0 | 0 | 259 | 47 / 47 |
| hangar 512 | image | 0 | 1798 | 258 | 43 / 43 |

The driver summary counted 1,351 silent and 1,111 image task rows overall;
phase filtering above is by the row's `width` field. The image log also
contained 2,323 generated DMA-range rows overall (the range rows do not carry a
phase field). The image-only execution edge proves the image arm is not merely
an unreachable route, but it does not close the output/PCM contract. This
selects `H-ContractGap` at the current observable boundary. It does not
authorize an output remap, task-field change, gate change, or mitigation. The
next unit must obtain independent retail writer/value evidence for the
zero-valued contract boundary.

Artifacts: `driver.log`, `silent.log`, `image.log`, and `oracle.log` in this
directory.
