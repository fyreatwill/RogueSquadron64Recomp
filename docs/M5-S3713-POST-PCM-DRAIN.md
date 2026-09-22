# M5 s3713 — post-PCM drain qualification

The same-build paired route ran real audio and the silent `M_AUDTASK` control
with title (`1024 @ 0x00790400`) and hangar (`512 @ 0x006AB400`) phase gates.
Both arms reached both transitions, passed RSP controls, and were SIGKILLed
cleanly.

At hangar, real audio emitted 43 phase-gated `set-next` drain rows and raw SDL
queue depth 0–4581 bytes. Silent emitted 132 rows and depth 741–4581 bytes.
The adjusted buffered field showed the same divergence. Neither arm called
guest `get-status` or `get-length` in the target phase.

Both arms emitted PCM source and host-consumer joins, but every sampled hangar
row had zero PCM (`fnv=0xF59C39C5`, `nz=0`). Only real audio emitted
image-stage rows. This selects `H-AudioDrainDivergence` at the measured host
boundary; `H-AudioDrainNotConsumed` remains open because the guest status and
length consumers were not reached. This is single-source port evidence: raw
and adjusted depth are two fields from the same host, not independent retail
observations.

The phase-reset instrument is controlled by `ROGUESQ_LOG_M5_AUDIO_DRAIN`. The
paired recipe is `scratch/agent/run_s3436_m5_port_frequency_contract.sh`.
