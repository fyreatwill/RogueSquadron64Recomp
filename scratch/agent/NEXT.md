# Next work unit: M5 route-state/source-use join (safe targeted census)

HYPOTHESIS-ID: m5-route-state-not-source

Resolve whether exact fields `0x128C92` and `0x128CD0..0x128CD3` are image
source state or only route/control metadata. The s3748 native host writer-PC
watch closed the remaining arbitrary host-writer class; do not repeat it and
do not alter `0x800078EC`.

Competing hypotheses:

- `H-RouteStateNotSource`: target phases read/use the fields as control
  metadata, but no read/use is joined to the source-DMA payload; the image
  producer is a separate object.
- `H-RouteStateSourceKey`: a phase-gated read/use of an exact field selects or
  keys the source object, and its value can be joined to the subsequent source
  DMA despite no host write.
- `H-RouteStateStale`: the fields are read/use state, but remain stale/zero and
  do not control the source route; a different handoff carries the producer.

Discriminator: one build must capture the complete phase-scoped table of exact
field reads/uses, their host/guest PCs and values, route identity, and the next
source-DMA row, with a positive control for the read-fault/instrument path and
the independent retail exact-field write watches retained. A read/use joined
to source-DMA selects `H-RouteStateSourceKey`; target-phase reads with no
source join select `H-RouteStateNotSource`; reads that remain zero/stale and
do not affect source-DMA select `H-RouteStateStale`. Missing oracle control,
port positive control, or either target phase is unevaluable.

Ground truth before building: inspect the oracle exact-field hit PCs and the
existing port route/source-DMA call edges; do not infer a read from a field
snapshot. Do not use a whole-generated-load rewrite. First identify the exact
guest load sites from the existing disassembly/ROM evidence, then add only
those bounded hooks through the regeneration-safe fixup script. Batch the
read/use and source-DMA joins in one real/silent qualified run plus the oracle
control. Kill every arm with SIGKILL from `build/`.
