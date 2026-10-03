# Next work unit: M5 source-route producer boundary after exact-load closure

HYPOTHESIS-ID: m5-source-route-producer-boundary

The nine exact candidate loads are closed as non-owners of the `0x80128C70`
route object. Move one boundary upstream: identify the next port-side
producer/read class that can explain why qualified real-audio source DMAs
carry zero payload while retail writes the source span. Do not repeat the
closed candidate list, the invalid `0x80019CD8` hook, or alter `0x800078EC`.

Competing hypotheses:

- `H-PortSourceProducerAbsent`: the next bounded census has no nonzero value
  or source-object handoff before the real source DMA.
- `H-PortSourceProducerPresent`: a bounded producer supplies a nonzero value
  or object that is then consumed by the source DMA.
- `H-PortSourceJoinMismatch`: the producer is present, but its route/task
  identity does not join to the qualified source-DMA rows.

Discriminator: before building, census the existing bounded port-side source
producer/read candidates documented by the latest M5 source-boundary note,
including real/silent arms and independent retail whole-RDRAM/source-span
watches. One build must carry every candidate and its source-DMA join, with a
same-run positive control for every hook family. A nonzero producer joined to
real source DMA selects `H-PortSourceProducerPresent`; producer rows with no
matching route/task identity select `H-PortSourceJoinMismatch`; no producer
rows after controls and both phases selects `H-PortSourceProducerAbsent`.
Missing controls or either target phase is unevaluable.

Ground truth before building: ask the retail oracle for the same producer
class and arm a whole-RDRAM positive control first. Add only bounded hooks
through the regeneration-safe fixup script. Run real and silent arms from
`build/` with the validated explicit AUTOPILOT schedule, then kill every arm
with SIGKILL.
