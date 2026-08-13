# Iteration 841 substitution

1. The planned late ordinary parser-range probe could not run to its
   discriminator because the game aborted in the renderer before the late
   population was reached.

2. This iteration's evidence: the initial recipe, the corrected recipe with
   the established post-title input schedule, and the reduced-trace retry all
   reached VI 1024 and fired the boot E9 control path, then aborted at
   `drawIndexedTri` with the same `G_CYC_COPY` assertion and last guest PC
   `0x8000834c` at 165.5–167.8 seconds. All three had zero task-570+ parser
   records. The first run's omission was corrected; the repeat abort is the
   measured blocker, not a precedent.

3. The single experiment that would refute this blocking explanation is a
   source-complete audit of every `drawIndexedTri`/`G_CYC_COPY` path that
   identifies a legitimate late copy-cycle triangle or proves the assertion
   is unrelated to the target phase; that audit is the next work unit.
