# M5 Session 3488 — audio-disabled selector-writer route

The rebuilt port used the prescribed LLE-only, ungated, spin-yield route with
`ROGUESQ_AUDIO_UCODE=0`, the existing title phase gate, and the selector-writer
controls. The run reached title origin `0x00790400` at VI width 1024 after
12.0 seconds, then captured 95 frames across the 60-second gated window. The
whole-RDRAM/schema controls and the selector-writer control fired; the port
emitted 1,024 bounded rows at `0x80091074`. It also reached the later 512-wide
hangar phase. There were zero `[CRASH]` and `[ABORT]` markers.

The silent arm dispatched 72 audio tasks as `musyx_stub`; the real image-stage
marker was absent as expected for this arm. This selects the route-specific
audio blocker from Session 3487: disabling the audio image removes the
pre-title `fillSampleStreamRange` failure and restores the writer target.

The retained retail capture has 533 title writer rows, while this port capture
has 1,024. Their separate animated runs cannot be joined by ordinal, so the
writer-input/value hypotheses remain open. The port rows include the known
normal values and one `0x8018DD30` selector row; that observation is descriptive
only and is not treated as a cross-runtime divergence.

ORIGIN: the run is diagnostic-only; the audio selector and task-writer hooks
observe dispatch, registers, and values without rewriting, skipping, or
validating task fields.

Evidence: `scratch/agent/s3488_m5_audio_disabled/run.log` and the independent
retail capture `scratch/agent/s3487_oracle_writer.log`.
