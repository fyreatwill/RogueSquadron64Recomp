# Next work unit: add a stable key to the DMA ownership witness

HYPOTHESIS-ID: m5-audio-source-ownership

S3687 selected H-DmaJoinUnavailable at the current logging boundary. The
absent-generation hangar source rows can be joined to later stages by pointer
and generation, but `audtask-dma-row` exposes neither generation, route, nor a
shared source event. Its task-local hash is not the source-span hash, and
cross-thread log order is not a valid owner key.

Competing hypotheses:

- H-LaterRouteOwnsInput: a DMA row carrying the source event/generation and
  later route key joins the absent source to the later stage/task.
- H-StaleInputAcrossReuse: the newly keyed DMA row joins the earlier source
  generation/route while the later stage only consumes the reused pointer.
- H-DmaKeyStillUnavailable: the emission boundary cannot carry a stable key or
  the rows remain contradictory/missing.

Discriminating measurement: add source event, task generation, and latest
route ordinal/row to the `audtask-dma-row` emission, preserving all existing
fields. Classify every absent-generation source row in one table by exact
later-route/task join, exact earlier-route join, or missing/contradictory key.
A dominant later join selects H-LaterRouteOwnsInput; a dominant earlier join
selects H-StaleInputAcrossReuse; missing/contradictory identity selects
H-DmaKeyStillUnavailable.

Exact commands:

    ./submodule-patches/export.sh
    cmake --build build -j8
    env zsh scratch/agent/run_s3688_m5_keyed_dma_owner_join.sh

Use one qualified concurrent capture, with retail whole-RDRAM, descriptor,
source-span, title, hangar, and type-2 controls plus port phase/source-hook/
ABI/DMA/source/stage controls. Kill both processes with SIGKILL. Do not alter
guest state or add a mitigation.
