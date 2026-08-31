# NEXT work unit — trace the M5 stage-3 field348 producer

HYPOTHESIS-ID: m5-image-stage3-destination

Grep-enumerate the guest producer/caller chain that supplies
`field348=0x801797B0` to the image-stage hook, then do one bounded
phase-qualified same-build port census using the repaired
`run_s2285_m5_step1_contract_pair.sh`, retaining the retail-backed
`0x1935E0` watch, both port arms, source DMEM, DMA completion, guest service,
and PCM rows. Do not change audio behavior or use the old normal-exit path.

Competing hypotheses:

- `H-PortStage3Alias`: the port's `0x1798B0` stage-3 destination is the same
  logical publication under a shifted/aliased address contract.
- `H-PortStage3Missing`: the port lacks the retail-backed `0x1935E0` publication
  edge or its required ordering/completion.
- `H-PortStage3LegitimateZero`: the port's zero output and differing
  destination are legitimate, with the remaining PCM gap downstream.
- `H-PortStage3Field348ProducerGap`: the stage hook is faithful, but the
  guest-side producer/caller that should establish the publication buffer is
  missing or receives a different contract in the port.

Discriminator: the same run must show positive-control callbacks, the retail
nonzero `0x1935E0` payload/writer row, and paired port rows tying stage-3 DMEM
source, destination, DMA/exit, guest service, and PCM. Matching source bytes
and completion with only a destination shift selects `H-PortStage3Alias`; a
missing `0x1935E0` publication/order selects `H-PortStage3Missing`; a matching
legitimate zero path with completion selects `H-PortStage3LegitimateZero`.

The oracle checkpoint and positive control are qualified in s3399. Before
adding a new port field, use that ground-truth result; then batch the port
census, build with `cmake --build build --target RogueSquadron64Recomp`, and
run the repaired paired recipe from `build/`. Use SIGKILL for every timeout and
retain both arms in that one run. A matching `field348` producer and
stage-only result selects the downstream-legitimacy branch; absent or
different producer inputs select `H-PortStage3Field348ProducerGap`; a
nonzero/retail-equivalent publication selects the missing image-edge branch.
