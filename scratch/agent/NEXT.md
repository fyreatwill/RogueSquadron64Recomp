# Next work unit: record the input-DMA ownership boundary

HYPOTHESIS-ID: m5-audio-source-ownership

Maintenance session 3689 compacted CURRENT-TRUTH; no experiment was run.
S3688 selected `H-DmaKeyStillUnavailable` at the output-DMA boundary: the
fields fire, but 257/258 absent-generation hangar source rows have no matching
source event there and one has a contradictory key.

Competing hypotheses:

- `H-LaterRouteOwnsInput`: the input-DMA key joins absent source rows to the
  later route/task.
- `H-StaleInputAcrossReuse`: the input-DMA key joins the earlier source
  generation/route while the later stage consumes the reused pointer.
- `H-InputDmaKeyStillUnavailable`: the input-DMA boundary still produces
  missing or contradictory identity.

Discriminating measurement: add one monotonic input-DMA event and the current
task generation plus route publication snapshot at `dma_rdram_to_dmem`, carry
it through the source witness, and classify every absent-generation hangar
source row in one table as later-route/task, earlier-route/task, or
missing/contradictory. A dominant later join selects the first hypothesis; a
dominant earlier join selects the second; missing or contradictory identity
selects the third. Require whole-RDRAM, descriptor, source-span, title, hangar,
and type-2 retail controls plus port phase/source-hook/ABI/DMA/source/stage
controls. Keep all arms in one build/run. Do not alter guest state or add a
mitigation.

Exact commands:

    ./submodule-patches/export.sh
    cmake --build build -j8
    env zsh scratch/agent/run_s3688_m5_input_dma_owner_join.sh

Kill both processes with SIGKILL. Run the game from `build/` with the ROM
present. If `lib/` changes, commit the refreshed submodule patch export.
