# M5 s3727 — port callback parity table

## Work unit

One CMake build and one same-configuration paired port run used the existing
phase-gated callback table. The real arm used `ROGUESQ_AUDIO_UCODE=1`; the
silent control used `ROGUESQ_AUDIO_UCODE=0`. Both retained the validated
`ROGUESQ_M4_Y8000_WIDTH=512`, ungated LLE, LLE-solo, spin-yield,
missing-function-stub, autopilot, and phase settings. The first launch omitted
`ROGUESQ_LOG_PCM_BOUNDARY=1`, so it was not used for the discriminator; the
fixed retry enabled it before interpreting any null.

## Controls

Both retry arms reached title VI 1024 and hangar VI 512. The RSP-source
positive control fired 1,024 times in each arm; audio-task ABI activity fired
2,386 times in the real arm and 2,407 times in the silent arm. Neither log
contained a crash or abort marker. Host audio rows fired 2,048 times per arm.

## Target table

At hangar VI 512 (`0x006AB400`), the real arm produced 3,677
`m5-image-queue` rows and 269 bounded `pcm-boundary-consumer` rows; the latter
reached consumer ordinal `n=1792`, because only the first 256 and every 128th
consumer row are printed. The silent arm produced zero image-stage rows and
269 bounded consumer rows, reaching `n=1792` as well.

The real image rows used one stable host thread, while the consumer rows used
a different stable host thread. Image callback sequence numbers reached
5,477 and consumer rows reached 5,456. Their route ordinals overlapped the
same target stream (`image 529..2399`, printed consumers `528..2392`), and
queue depth ranged 0..3045 bytes for image rows and 741..3813 bytes for the
printed consumer rows. Every joined callback row reported `callback_order=1`.
The silent consumer stream used its own stable consumer thread and had no
image callback owner to compare.

## Result

This selects `H-CallbackQueueOwnership` at the measured port boundary: the
real-only image callback stream has a distinct, stable owner/thread and
sequence interleaving with the consumer stream, while the silent control has
the consumer stream but no image stream. It does not establish retail host
callback parity; the independent retail oracle can attribute guest audio-task
paths but cannot expose SDL queue ownership or host callback threads. The
remaining image discrepancy is therefore the image-task/output payload
contract, not a route-only or host-queue-presence explanation.

This is single-source port evidence for the ownership conclusion. The
independent retail line is limited to guest task activity as recorded in
`M5-S3726-CALLBACK-GROUND-TRUTH.md`.

ORIGIN: diagnostic-only callback/source/thread/queue fields in the existing
port table. No guest, RSP, task, audio-route, selector, clear, or payload
behavior changed.

Evidence: `scratch/agent/s3727_callback_real_retry/run.log` and
`scratch/agent/s3727_callback_silent_retry/run.log`.
