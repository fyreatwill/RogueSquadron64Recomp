# NEXT work unit — trace the field348 zero-fill input

HYPOTHESIS-ID: m5-image-stage3-destination

Add one guest-side probe at the `0x8008F2C8` store immediately before the
`0x8008F2CC` `rs_memset` call, recording the value written to the owning
pointer slot, the active audio route, and the resulting memset arguments. Keep
the existing field348 writer/candidate/memset and image-stage probes. Build
once, then run the repaired paired recipe with silent and image arms
concurrently; retain the retail checkpoint and all positive controls.

Competing hypotheses:

- `H-PortStage3Field348ProducerGap`: the port caller stores a different/null
  source pointer or otherwise supplies a different input before the zero-fill.
- `H-PortStage3LegitimateZero`: the zero-fill is the intended contract and the
  missing nonzero publication is downstream of this caller.
- `H-PortStage3Alias`: the port pointer slot and destination are an alias of
  retail's `0x1935E0` publication despite the current address difference.

Discriminator: whole-RDRAM, title/hangar, and retail `0x1935E0` nonzero
controls must fire in the same run. A port-side pointer/input row that matches
retail's logical publication and is followed by a zero-only stage selects the
downstream branch; a null/different input or absent producer row selects the
field348 producer gap; a retail-equivalent destination/payload selects alias.
If the new probe does not fire while the existing writer control does, treat
the caller edge as unevaluable and do not infer from the null.

Commands:

    cmake --build build --target RogueSquadron64Recomp
    zsh scratch/agent/run_s2285_m5_step1_contract_pair.sh s3401_m5_field348_input

Use SIGKILL-only cleanup and do not change audio behavior, waits, slots, status
handling, consumer dispatch, or PCM writeback.
