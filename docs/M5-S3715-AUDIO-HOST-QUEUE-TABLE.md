# M5 s3715 — host audio queue boundary

The required ground-truth attempt armed the oracle whole-RDRAM positive control
and reached 31 seconds, but did not reach the target 512 hangar origin before
the run stopped. It therefore supplies no retail consumer/dequeue observation.

The port instrument was phase-gated to title origin `0x00790400` and hangar
origin `0x006AB400`. It records queue depth before and after `SDL_QueueAudio`,
depth samples from `SDL_GetQueuedAudioSize` in `get_frames_remaining`, the
inter-sample depth delta, call delta, PCM byte/sample count, timestamp, and
device id. Both paired arms reached title and hangar and passed the existing
RSP positive controls (`1,024` source rows each) without a crash.

| arm | target queue rows | target remaining rows | min/max queued-before | negative inter-sample deltas | image-stage rows |
|---|---:|---:|---:|---:|---:|
| real audio | 79 | 78 | 0 / 4581 | 58 / 79 | 5060 |
| silent control | 16 | 16 | 0 / 3813 | 8 / 16 | 0 |

The host queue is consumed between some producer-side samples in both arms,
but cadence and depth differ substantially. This is single-source port
evidence: SDL's queued-audio backend has no application callback in the current
push-mode setup, so these rows do not identify a retail callback or prove that
image-stage code consumes audio state. The next boundary is a queue-depth
snapshot joined directly to the image-stage event.
