# NEXT work unit (s2681) — new M5 CPU renderer-to-AI destination/order join

HYPOTHESIS-ID: m5-cpu-renderer-ai-publication-join

## Work unit

Run one new, positive-controlled retail oracle capture to join the named
renderer/mixer output to the AI source and consumer. Do not repeat the ring,
shared-stack, filter, persistent-object, task-field, or image-vs-silent
censuses, and do not change runtime behavior.

## Competing hypotheses and discriminator

- `H-MORT-PCM`: a named CPU renderer/mixer writer publishes the PCM consumed by
  AI on the same destination span and ordered call sequence.
- `H-AI-source-gap`: renderer/mixer runs, but AI reads a different or
  unpopulated source; the missing edge is between them.
- `H-Host-only-gap`: retail has a valid renderer-to-AI join, so any port gap is
  after AI source publication and must not be fixed in the guest/RSP path.

The discriminator is one phase-keyed retail table containing whole-RDRAM
positive-control count, title/hangar route markers, `renderVoiceAudioBlock`,
`audioMixStereoBlock8`, every writer PC and payload span for the selected
candidate output ranges, `osAiSetNextBuffer`, `__osAiDeviceBusy`, and source
address/order/hash/nonzero polarity at each edge. A renderer/mixer writer that
matches the AI source and precedes its consumer selects `H-MORT-PCM`; distinct
or zero AI source selects `H-AI-source-gap`; a complete retail join with no
port join selects `H-Host-only-gap`. Missing whole-RDRAM control or target
phase invalidates the run.

## Ground-truth prerequisite

Use `tools/oracle/README.md` and the corrected local core path. Arm the
whole-RDRAM positive control first and require title plus hangar before
interpreting narrow nulls. No port instrumentation is authorized until this
oracle control passes.

## Exact commands

1. Launch the corrected retail oracle with whole-RDRAM watch, candidate output
   range watches, renderer/mixer and AI PC watches, VI trace, and the existing
   AUTOPILOT input; wait for positive control, title, and hangar.
2. Extract the complete writer/source/order table into
   `scratch/agent/s2681_mort_pcm_publication_join/`; do not run a port build
   unless the oracle discriminator identifies a new named edge.
3. Enqueue any validation soak rather than babysitting it; terminate the
   oracle/process group with SIGKILL.
