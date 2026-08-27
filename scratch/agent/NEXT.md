# NEXT work unit (s2833) — qualify current M5 image against silent control

HYPOTHESIS-ID: m5-audio-destub-step1-qualification

## Work unit

Run the Step 1 same-build qualification described in
`docs/M5-AUDIO-PLAN.md`: build once, then compare the image arm and
`ROGUESQ_AUDIO_UCODE=0` silent arm with phase-gated controls. Do not change
runtime behavior in this unit.

## Competing hypotheses and discriminator

- H-audio-degenerate-paths: the current silent/stubbed paths plausibly cause
  recurring audio-related crashes or state corruption, so at least one planned
  de-stub has a concrete validation discriminator.
- H-audio-boundary-independent: the active stubs are not on the named crash or
  publication paths, so the plan must preserve them as controls and identify
  the evidence needed before de-stubbing.
- H-contract-unknown: a stub lacks enough contract evidence for safe execution,
  so it must remain parked behind a ground-truth or microcode prerequisite.

The discriminator is the complete inventory-to-step matrix in the new plan:
every active stub maps to either a bounded de-stub step with a measurable
outcome, an explicit control, or a named prerequisite. Missing mappings mean
the survey is incomplete.

## Exact commands

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
zsh scratch/agent/run_s2774_m5_step1_pair.sh
rg -n -E 'oracle_gate=|--- (image|silent) ---|\[(audtask-dispatch|audtask-abi|audtask-dma-row|audtask-image-stage|audio-return|audio-route|audio-sp-route|pcm-boundary-source|pcm-boundary-consumer|CRASH|ABORT)\]=' scratch/agent/s2774_m5_step1_pair/driver.log
git diff --check
```

The existing pair recipe launches the retail oracle first, then launches image
and silent arms concurrently from the same executable. Expected discriminators:
stub has dispatch/return but no image DMEM or DMA rows; image has nonzero
image-stage/DMA and `Broke` plus SP completion. A downstream service/slot/PCM
join selects a contract edge; route-only or pre-target output is unevaluable.
