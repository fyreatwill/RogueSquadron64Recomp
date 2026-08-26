# NEXT work unit (s2415) — link sequence-key identity to PCM/task identity

HYPOTHESIS-ID: m5-sequence-pcm-link

## Work unit

Run one bounded, observation-only reducer over the valid retained image logs
from s2412 and s2413. Parse each selected class-5/7 identity row, its key-on
event/ordinal/row, and every later `[audio-join-pcm]` source/consumer record in
the same phase/origin. Produce one complete table keyed by capture, stage
event, key-on event, key-on ordinal/row, PCM event, PCM ordinal/row, address,
and event delta. Do not change task data, audio, gate, fallback, dispatch, VI,
output behavior, the nonzero predicate, or the 64-event identity window.

## Competing hypotheses and discriminator

- H-SequencePcmLegitimate: the selected key-on identity is followed by PCM
  source/consumer records with the same phase/origin and ordinal/row, in both
  captures.
- H-KeyonOnly: the sequence legitimately identifies the key-on event, but the
  PCM records use a separate identity or range; same-identity PCM joins are
  absent or non-stable.
- H-GlobalPcmCollision: later PCM records match only by phase/origin or global
  event order and do not preserve the key-on ordinal/row.
- H-NoDownstreamRelation: the selected key-on relation does not survive the
  complete PCM/task table or is route-invalid in either capture.

The discriminator is the one combined per-row table. A stable same-identity
PCM source and consumer join after the selected key-on in both valid captures
selects H-SequencePcmLegitimate; key-on-only rows with stable phase/origin but
no ordinal/row PCM join select H-KeyonOnly; only broad phase/origin matches
select H-GlobalPcmCollision; a missing control or empty/unstable table selects
H-NoDownstreamRelation. Do not interpret a zero-valued PCM tuple as a match
without its event and ordinal/row identity.

## Exact inputs and command

Inputs:

- `scratch/agent/s2412_identity_join/image_retained/run.log`
- `scratch/agent/s2413_identity_join/image/run.log`

Create `scratch/agent/s2415_sequence_pcm_link/reduce.py` if needed, then run:

`python3 scratch/agent/s2415_sequence_pcm_link/reduce.py scratch/agent/s2412_identity_join/image_retained/run.log scratch/agent/s2413_identity_join/image/run.log`

Required controls in each input: title `1024 @ 0x00790400`, hangar
`512 @ 0x006AB400`, and a key-on positive-control marker. Write the complete
table and summary under `scratch/agent/s2415_sequence_pcm_link/`.
