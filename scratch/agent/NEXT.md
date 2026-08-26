# NEXT work unit (s2497) — audit image-to-buffer handoff

HYPOTHESIS-ID: m5-generated-image-downstream-join

## Single work unit

Perform one bounded static provenance audit of the image-stage-to-PCM-buffer
handoff. Enumerate every generated callsite of `osAiSetNextBuffer_recomp` and
the named callers feeding `queue_samples`, then trace the phase-10 image
destinations (`0x166450..0x169150`, `0x1798B0..0x179A48`) through the existing
task-data and DMA fields. Use the s2496 positive controls and the independent
retail `0x800078EC` writer only as ground truth; do not infer identity from
ordering and do not change behavior.

## Competing hypotheses and discriminator

- H-handoff-explicit: a generated callsite or task-data field explicitly
  carries the image destination/ordinal into the PCM consumer.
- H-handoff-reconstructed: the handoff has no explicit image identity, but a
  stable buffer slot/length/hash relation can be established at one named
  boundary.
- H-handoff-absent: the image-stage destination is not used by the PCM
  consumer path; the matching addresses are independent consumer inputs.

The discriminator is one exhaustive static table with caller PC, callee,
buffer-address source expression, task-data source, image destination/range,
and whether ordinal or destination identity survives to `queue_samples`.
An explicit identity selects `H-handoff-explicit`; a unique stable relation
with no explicit field selects `H-handoff-reconstructed`; no reachable
relation selects `H-handoff-absent`. Do not add a runtime field unless this
table names one earliest boundary and each outcome would split the hypotheses.

## Exact commands

```sh
rg -n "osAiSetNextBuffer_recomp|queue_samples|rs64_audio_join_pcm|166450|169150|1798B0|179A48|task_data|data_ptr" \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
  src lib tools/oracle scratch/agent/s2496_m5_first_image_consumer
```

Write the table and conclusion to
`scratch/agent/s2497_m5_image_handoff_audit/audit.md`. If the static table
names one earliest boundary, prepare the next iteration's single phase-keyed
port/oracle capture there; this iteration is static-only and needs no build.
