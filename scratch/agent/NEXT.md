# NEXT work unit — trace the selected M5 stage-3 destination mismatch

HYPOTHESIS-ID: m5-image-stage3-destination

Do one bounded phase-qualified port census using the repaired
`run_s2285_m5_step1_contract_pair.sh`. Join the retail-backed stage-3
destination `0x1935E0` to the port image arm's source DMEM, DMA completion,
guest service, and PCM rows; retain all four destination rows and the silent
control. Build once and run both port arms concurrently. Do not use the old
normal-exit summary path.

Competing hypotheses:

- `H-PortStage3Alias`: the port's `0x178D80` stage-3 destination is the same
  logical publication under a shifted/aliased address contract.
- `H-PortStage3Missing`: the port lacks the retail-backed `0x1935E0` publication
  edge or its required ordering/completion.
- `H-PortStage3LegitimateZero`: the port's zero output is legitimate and the
  remaining PCM gap is downstream.

Discriminator: the same run must show positive-control callbacks, the retail
nonzero `0x1935E0` payload/writer row, and paired port rows tying stage-3 DMEM
source, destination, DMA/exit, guest service, and PCM. Matching source bytes
and completion with only a destination shift selects `H-PortStage3Alias`; a
missing `0x1935E0` publication/order selects `H-PortStage3Missing`; a matching
legitimate zero path with completion selects `H-PortStage3LegitimateZero`.

The oracle checkpoint and positive control are qualified in s3397. Before
adding a new port field, use that ground-truth result; then batch the port
census, build with `cmake --build build --target RogueSquadron64Recomp`, and
run the repaired paired recipe from `build/`. Use SIGKILL for every timeout and
retain both arms in that one run.
