# Next work unit: record the input-DMA ownership boundary

HYPOTHESIS-ID: m5-audio-source-ownership

S3688 selected H-DmaKeyStillUnavailable at the output-DMA boundary. The
per-range `[audtask-dma-range]` record now exposes source event, task
generation, and latest route sequence/ordinal/row, and the positive control
shows nonzero values. However, 257/258 absent-generation hangar source rows
have no DMA range with the same source event and one has a contradictory key.
The input DMA callback must retain its own event and task/route snapshot before
later output DMAs overwrite the thread's last source event.

Competing hypotheses:

- H-LaterRouteOwnsInput: the input-DMA key joins the absent source to the
  later route/task.
- H-StaleInputAcrossReuse: the input-DMA key joins the earlier source
  generation/route while the later stage only consumes the reused pointer.
- H-InputDmaKeyStillUnavailable: the input-DMA boundary still produces
  missing or contradictory identity.

Discriminating measurement: add one monotonic input-DMA event and the current
task generation plus route publication key at `dma_rdram_to_dmem`, carry it
through the source witness, and classify every absent-generation source row in
one table by later-route/task join, earlier-route/task join, or
missing/contradictory key. A dominant later join selects H-LaterRouteOwnsInput;
a dominant earlier join selects H-StaleInputAcrossReuse; missing/contradictory
identity selects H-InputDmaKeyStillUnavailable.

Exact commands:

    ./submodule-patches/export.sh
    cmake --build build -j8
    env zsh scratch/agent/run_s3688_m5_input_dma_owner_join.sh

Use one qualified concurrent capture, with retail whole-RDRAM, descriptor,
source-span, title, hangar, and type-2 controls plus port phase/source-hook/
ABI/DMA/source/stage controls. Kill both processes with SIGKILL. Do not alter
guest state or add a mitigation.
