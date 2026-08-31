# NEXT work unit — repair the M5 ground-truth completion path

HYPOTHESIS-ID: m5-ground-truth-completion-safe

Do one bounded measurement-design/implementation unit for the M5 image-output
edge. Do not repeat `run_s2285_m5_step1_contract_pair.sh` unchanged: s3395's
oracle positive control passed, but both port arms crashed before dispatch at
guest PC `0x8000834c`, leaving every M5 field absent.

Competing hypotheses:

- `H-PreDispatchSchedulerCrash`: the paired route dies before M_AUDTASK, so a
  completion-safe control must distinguish route failure from an audio gap.
- `H-ImageEdgeMissing`: once the route survives, Factor 5 image output lacks a
  named DMEM-to-RDRAM contract edge.
- `H-ImageEdgePresent`: once the route survives, existing image DMA and SP
  completion already close the output contract.

Discriminator: first obtain an independent retail control that reaches the
target phase and produces a completion-safe summary, then run both port arms in
one build/run with phase-scoped dispatch, ABI, DMA, image exit, SP completion,
service/slot, and PCM controls. A pre-dispatch port crash with a live retail
control selects `H-PreDispatchSchedulerCrash`; matching image DMA/exit and
completion with no downstream gap selects `H-ImageEdgePresent`; a named
retail-backed output edge with matching port ordering selects
`H-ImageEdgeMissing`.

Candidate edge remains Factor 5 `SP_WR_LEN` DMEM-to-RDRAM publication: writer
is `factor5_ucode_b`, observed destinations are stage-2 `0x166D50`,
`0x167050`, `0x167350` and stage-3 `0x1935E0`, with OSTask `output_buff=0`.
Legitimacy is unresolved. Required ordering is image entry -> DMA rows ->
`Broke`/SP completion -> guest service/slot/PCM.

Before any new port instrument, use the oracle's existing whole-RDRAM positive
control and replace the incomplete final-summary path with a completion-safe
measurement. Then build with `cmake --build build --target
RogueSquadron64Recomp` and run the repaired paired recipe from `build/`; use
SIGKILL for every timeout and retain both arms in that one run.
