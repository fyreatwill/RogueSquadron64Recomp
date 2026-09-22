# Next work unit: join absent-source DMA to later-route task ownership

HYPOTHESIS-ID: m5-audio-source-ownership

S3686 selected `H-LaterRouteReuse`: 244/244 hangar source rows lacking a
same-generation stage row were followed by a same-pointer stage on a later
route ordinal/row. The next unit must determine whether the input DMA is
owned by that later route/task or is stale data carried across pointer reuse.

Competing hypotheses:

- H-LaterRouteOwnsInput: the absent source event's DMA/task fields join the
  later route's ABI/DMA row and its task object.
- H-StaleInputAcrossReuse: the source event remains tied to the earlier route
  or earlier task data while the later route only consumes the reused pointer.
- H-DmaJoinUnavailable: the source event cannot be joined to either route
  without contradictory or missing event identity.

Discriminating measurement: for every absent source row, retain source event,
route ordinal/row, task pointer, generation, DMA range/length/hash; find the
first later same-pointer stage and join its stage event and route to the
nearest matching `audtask-dma-row`/`audtask-abi` records. Report exact later
route/task joins, earlier-route joins, and missing/contradictory joins. A
dominant exact later-route/task join selects H-LaterRouteOwnsInput; a dominant
earlier-route join selects H-StaleInputAcrossReuse; missing/contradictory
identity selects H-DmaJoinUnavailable. Require the same positive controls:
retail whole-RDRAM, descriptor, source-span, title, hangar, and type-2
controls plus port phase/source-hook/ABI/DMA/source/stage controls.

Before running:

    ./submodule-patches/export.sh
    cmake --build build -j8
    env zsh scratch/agent/run_s3687_m5_absent_dma_owner_join.sh

Use one qualified concurrent capture, SIGKILL cleanup, and do not alter guest
state or add a mitigation. Batch all three join classes in one classifier;
do not use the ABI publication counter without a stable join key.
