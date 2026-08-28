# NEXT work unit — M5 Step-1 image/silent qualification

HYPOTHESIS-ID: m5-audio-step1-contract-qualification

Run one same-build, phase-gated qualification of the Factor 5 image arm and
the silent `musyx_stub` control. Preserve the independent retail-oracle
positive control. Do not change a gate, wait, voice guard, or output
destination from this qualification.

Competing hypotheses and the discriminator:

- H-AudioDegeneracy: the silent path causes a downstream wait, slot, voice, or
  PCM failure. The image arm must add the predicted downstream edge.
- H-ContractGap: the image executes but its task/DMEM/DMA/output contract is
  incomplete. Image-only activity must fail to close a later join.
- H-MixedPipelines: Factor 5 RSP audio and CPU MORT speech are independent;
  one can progress while the other remains absent.
- H-RouteFailure: a run without title/hangar makes every downstream audio
  null unevaluable.

The single discriminator is a phase-keyed table in one build/run covering
whole-RDRAM/oracle control, route phase, M_AUDTASK dispatch and task fields,
DMEM/DMA, image break/`Broke`, SP completion, guest service, slot/voice
transitions, MORT class, and PCM source/consumer joins. No target phase selects
RouteFailure. DMEM/DMA plus completion without a later join selects
ContractGap. Independent RSP and MORT progress selects MixedPipelines.
AudioDegeneracy requires the predicted downstream edge, not merely a return
counter.

Exact command:

    cmake --build build --config Debug --target RogueSquadron64Recomp -- -j2
    env ROGUESQ_AUTOPILOT=1 ROGUESQ_AUDIO_UCODE=0 ROGUESQ_LOG_ALL=1 \
      PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 PROBE_PHASE_TIMEOUT=180 \
      PROBE_LEAVE_OK=1 zsh scratch/agent/run_s2285_m5_step1_contract_pair.sh

Write the phase-keyed result under
`scratch/agent/s3040_m5_step1_contract_pair/`. If the qualification cannot
reach target phases, record route failure and leave downstream nulls
unevaluable.
