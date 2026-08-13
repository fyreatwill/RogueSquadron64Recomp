# NEXT work unit (systematic allocation/grid crash-idiom audit)

HYPOTHESIS-ID: m3-prechain-allocation-grid-idiom

The s787 repeat passed provenance controls but reached only VI 640 and aborted
in RT64 `findTileCopyId` before the 1024 gate. This is the third consecutive
pre-chain failure across distinct families (s785 Metal barrier, s786 grid
allocation, s787 framebuffer tile-copy). Do not run another reachability soak
yet and do not add a guard from any one crash.

## Competing hypotheses

- H-grid-writer-corruption: one game-side allocation/grid writer corrupts state
  later consumed by several crash families. Prediction: a complete enumeration
  finds a shared unchecked pointer/size/index idiom and a common upstream value.
- H-renderer-only: the distinct failures are independent host/runtime consumers.
  Prediction: the allocation/grid enumeration has no shared game-side idiom;
  only RT64 host sites differ.
- H-stale-generated-view: the apparent allocation/grid class is incomplete
  because the active generated funcs are outside this checkout or stale.
  Prediction: source inventory cannot map the named functions/PCs to a current
  generated artifact, so no complete classification is possible.

## Discriminating measurement

One bounded source audit, before any build: inventory every allocation/grid
pointer, size, index, and host-consumer site reachable from the three observed
families; classify each as guarded, proven-valid, or unclassified; and record
the writer and legitimacy of every wild value. H-grid-writer-corruption wins
only if two independent lines (source idiom enumeration plus an existing trace
or address/value record) identify a shared writer. H-renderer-only wins if the
complete current source inventory shows disjoint, valid game inputs and only
host consumers. H-stale-generated-view wins if the required generated source
is absent or cannot be tied to the active build; then stop and request the
artifact path rather than inventing a guard.

## Exact audit

1. Locate active generated `funcs_*.c` and its fixup/build provenance with
   `find`, `rg`, and the build manifest; do not read the whole generated tree.
2. Enumerate `allocAndInitGridCellArray`, its callers, and all sibling grid/
   allocation idioms; separately inspect RT64 `findTileCopyId` call sites.
3. For every candidate, capture the guest address/value writer and classify
   legitimate versus wild. No code change or mitigation is allowed unless a
   writer is identified.
4. If the active generated source is unavailable, record that concrete result
   and stop the audit as blocked; do not substitute a reactive runtime patch.

No build or run is part of this unit unless the audit discovers a bounded,
source-backed diagnostic change and its positive control can be specified.
