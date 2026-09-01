# NEXT work unit — identify the zero image-task staging DMA source

HYPOTHESIS-ID: m5-image-task-staging-clear

Session 3564 found nonzero vector-store staging in the target DMEM windows,
then repeated zero-valued RDRAM-to-DMEM DMAs before stage consumption. Continue
at the source and ordering of those zero DMAs. Before building, the competing
hypotheses and one discriminator are:

- H-ZeroDmaSource: the zero-valued DMAs read from a legitimate zero source
  range, so the divergence is upstream in the source-range producer.
- H-ZeroDmaOrdering: a later clear or stale task replays the zero DMA after
  the nonzero vector stores; ordering joins place it after staging.
- H-DmaContractMismatch: the DMA source/length or DMEM destination differs
  from the intended image-task contract.

The single discriminator is one phase-keyed ordering table for every event
overlapping DMEM `0x6F0..0x9F0` and `0xCB0..0xE48`, joining zero DMAs to their
RDRAM source range/hash, DMEM destination/hash, preceding vector/scalar stores,
task ordinal, and existing stage row. A source-range writer row selects
H-ZeroDmaSource; a zero DMA after nonzero staging selects H-ZeroDmaOrdering;
an address/length mismatch selects H-DmaContractMismatch. A zero table is
meaningful only after title 1024, hangar 512, image completion/DMA, and PCM
source/consumer controls fire.

Run the oracle control first only if its debugger core and retail ROM are
present. Then build once and run a target-valid standalone image recipe with
the existing stage/source-window instrumentation, adding only the bounded
source-range writer/order join needed by the discriminator. Do not change task
fields, output, gates, slots, PCM, writeback, or add a guard. The retail oracle
remains optional until its core and ROM are present.
