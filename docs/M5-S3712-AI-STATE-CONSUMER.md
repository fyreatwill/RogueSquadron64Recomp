# M5 s3712 — post-return AI state consumer

The single build added a phase-gated host table at the `set_frequency` callback
and the first PCM consumer, `queue_samples`. The real-audio route and a
same-configuration `ROGUESQ_AUDIO_UCODE=0` control both reached title VI 1024
and hangar VI 512, and both passed the RSP source positive control.

Both arms produced 67 AI-state rows: the host callback retained `22047 Hz`,
and queued 384-sample buffers at that rate. The real arm produced 4,826
image-stage rows; the silent arm produced none. This selects `H-AIStateParity`
for the port host side effect and first consumer, and rules out an
audio-route-specific host-frequency divergence. It does not explain why only
the real arm reaches the image-stage path. The oracle retry's whole-RDRAM
control fired but did not reach the target 512 phase before its run ended.

Artifacts: `scratch/agent/s3436_m5_port_frequency_contract/run.log` and
`scratch/agent/s3712_silent/run.log`.
