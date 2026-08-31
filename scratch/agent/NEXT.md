# NEXT work unit — qualify M5 image payloads with the live oracle checkpoint

HYPOTHESIS-ID: m5-image-output-edge

Do one bounded phase-qualified measurement using the repaired
`run_s2285_m5_step1_contract_pair.sh`. Add post-store payload sampling for the
four candidate retail destinations (`0x166D50`, `0x167050`, `0x167350`,
`0x1935E0`) while retaining the whole-RDRAM positive control and SIGUSR1 live
checkpoint. Then build once and run both port arms concurrently. Do not use
the old normal-exit summary path.

Competing hypotheses:

- `H-ImagePayloadZero`: retail candidate stores are zero or absent in the
  target phase, so they cannot explain the port's zero PCM.
- `H-ImageEdgeMissing`: retail has a nonzero target-phase payload row, while
  the port lacks the corresponding DMEM-to-RDRAM edge or ordering.
- `H-ImageEdgePresent`: retail and port have matching nonzero image publication,
  exit, and SP-completion ordering; the remaining zero PCM gap is downstream.

Discriminator: the same run must show positive-control callbacks, retail
nonzero/zero payload values and writer PCs in the target phase, and paired port
dispatch → image DMA/exit → SP completion → PCM rows. A zero/absent retail
payload selects `H-ImagePayloadZero`; a retail-backed payload with a port-side
ordering/publication gap selects `H-ImageEdgeMissing`; matching publication
and completion with zero PCM selects `H-ImageEdgePresent`.

Candidate edge remains Factor 5 `SP_WR_LEN` DMEM-to-RDRAM publication: writer
is `factor5_ucode_b`, observed destinations are stage-2 `0x166D50`,
`0x167050`, `0x167350` and stage-3 `0x1935E0`, with OSTask `output_buff=0`.
Legitimacy is unresolved. Required ordering is image entry -> DMA rows ->
`Broke`/SP completion -> guest service/slot/PCM.

Before any new port instrument, run the oracle with its whole-RDRAM positive
control and SIGUSR1 checkpoint plus post-store sampling. Then build with
`cmake --build build --target RogueSquadron64Recomp` and run the repaired paired
recipe from `build/`; use SIGKILL for every timeout and retain both arms in that
one run.
