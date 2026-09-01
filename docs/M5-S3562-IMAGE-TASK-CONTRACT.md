# M5 session 3562 — image-task output contract remains open

The independent retail preflight was unavailable: this checkout has the
oracle frontend and binary but not its documented debugger core or retail ROM.
No retail null is used as evidence.

The existing full target rebuilt successfully. A same-build image/silent pair
was route-invalid in this environment: both arms passed 320/640 startup
activity but timed out before the required 1024 phase. Their target-phase
contract rows are therefore unevaluable. The image arm was then retried
standalone with the identical witness batch. This fixed run reached title
`0x00790400`/1024 at 16.2 seconds and hangar `0x006AB400`/512 at 25.4 seconds,
captured 65 frames, and had no crash marker.

The standalone image arm had positive controls live: the two target VI
transitions, 2,589 image completion-call rows, 10,271 image-stage rows, 7,773
DMA-range rows, 98 PCM source rows, 98 PCM consumer rows, 530 audio-return
rows, 1,024 task-lifetime rows, and the explicit downstream-store positive
control. The image-task summaries reported:

| phase | stage rows | nonzero stage rows | source matches | consumer matches | stage-only | consumer-only observed |
|---|---:|---:|---:|---:|---:|---:|
| title 1024 | 1,059 | 0 | 0 | 0 | 1,059 | 13 |
| hangar 512 | 1,060 | 0 | 0 | 0 | 1,059 | 0 |

The stage destinations were valid but zero-valued. Separately, title PCM
source/consumer rows matched each other by address and FNV, while the image
stage rows did not join either endpoint. Title also showed 13 consumer-only
PCM rows and downstream slot/key-on rows. Thus the image task reaches its
completion and DMA machinery, but its observed output does not join the PCM
contract. This selects `H-ImageTaskOutputGap` at this discriminator; it does
not yet identify the legitimate writer or prove that the zero output is
incorrect. The next probe follows the first producer of the image-stage
destination.

The evidence is single-source port evidence for this iteration. The failed
pair is recorded only as route-invalid and is not used for animated A/B
comparison.

ORIGIN: diagnostic-only phase, task, DMA, completion, PCM, slot, and output
observations; no game state, task field, output, gate, slot, PCM, or writeback
behavior was changed.
