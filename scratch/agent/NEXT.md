# NEXT work unit (s2416) — identify the title-to-hangar M5 handoff key

HYPOTHESIS-ID: m5-phase-transition-identity

## Work unit

Run one bounded, observation-only source audit over the existing s2412 and
s2413 logs. Enumerate every M5 task, DMA, PCM, slot, and key-on marker from the
selected title key-on event through the first hangar PCM records. Build one
complete table keyed by capture, event, phase, origin, ordinal/row, task/data
address fields, and event delta. Do not build or alter runtime code unless the
existing markers cannot supply the table; do not change task data, audio, gate,
fallback, dispatch, VI, output behavior, or the nonzero predicate.

## Competing hypotheses and discriminator

- H-PhaseTransitionKey: an existing task/DMA field or ordered event relation
  links the title key-on to the first hangar PCM records in both captures.
- H-TaskOrdinalKey: the link survives by task or DMA ordinal/row even though
  the VI origin changes.
- H-GlobalSequenceOnly: only broad event order links the records; no stable
  task/DMA identity survives the transition.
- H-NoHandoffKey: the complete existing-marker table has no stable relation in
  one or both captures.

The discriminator is one cross-capture table containing all candidate handoff
fields and the first five post-key-on PCM source/consumer records. A stable
field matching both captures selects its hypothesis; only event-order matches
select H-GlobalSequenceOnly; an empty or inconsistent table selects
H-NoHandoffKey. Do not interpret zero-valued payloads as identity.

## Exact commands

First inventory marker names without reading whole logs:

`rg -o '\\[(m5-[^]]+|audio-[^]]+|slot-[^]]+|keyon-[^]]+)\\]' scratch/agent/s2412_identity_join/image_retained/run.log scratch/agent/s2413_identity_join/image/run.log | sort | uniq -c`

Then inspect only bounded windows around the selected key-on events (s2412
event 5288, s2413 event 5321) and the first subsequent hangar-origin PCM
records. Write the complete table and summary under
`scratch/agent/s2416_phase_transition_identity/`.
