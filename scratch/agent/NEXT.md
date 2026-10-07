# Next work unit: validate declared-size versus legacy-size audio staging

Run one same-build A/B of the M5 Step 3 staging behavior on the canonical
qualified route. The declared arm uses the current `ucode_data_size` (`0x800`);
the legacy arm sets `ROGUESQ_AUDIO_LEGACY_UCODE_DMA=1` (`0xF80`). Keep both
arms real-audio and collect the complete phase-keyed contract row. This is a
validation/de-stubbing unit, not permission to change the image or infer a
cause from the already-known zero payload.

HYPOTHESIS-ID: m5-step3-declared-audio-ucode-dma

Competing hypotheses and discriminator:

- H-step3-contract: the declared `0x800` staging span is the required task
  contract; declared and legacy arms will differ in DMEM/DMA or downstream
  service/slot/PCM joins while retaining route controls.
- H-step3-equivalent: the reserved `0xF80` legacy span is behaviorally
  irrelevant on the qualified route; both arms have matching task, DMA,
  service, slot, and PCM signatures.
- H-step3-route-invalid: either arm misses a positive control or title/hangar
  phase, so its nulls are unevaluable.

The single discriminating measurement is the same-build, phase-gated two-arm
table joined by task ordinal/generation: dispatch and exit, declared task
fields, DMEM/DMA ranges and hashes, SP completion, service return, slot/status,
PCM source/consumer, and title/hangar phase. Missing whole-RDRAM retail
control, port controls, or either target phase selects H-step3-route-invalid.
Matching qualified rows select H-step3-equivalent; a qualified downstream
split tied to the staging arm selects H-step3-contract.

Before building, verify the existing staging switch and driver with bounded
searches:

`rg -n 'ROGUESQ_AUDIO_LEGACY_UCODE_DMA|audtask-image-stage|audtask-dma|pcm-boundary|AUTOPILOT' src tools scratch/agent --glob '!*.log'`

Build once:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Run the retail oracle first with a whole-RDRAM positive control and title/hangar
phase gates. Then run both port arms concurrently from `build/` with:

`ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a'`
`ROGUESQ_AUTOPILOT_STOP_WIDTH=512 PROBE_PHASE_WIDTH=1024`
`PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1`
`ROGUESQ_LOG_PHASE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1`
`ROGUESQ_LLE_SOLO=1 ROGUESQ_DRAIN_INLOOP_TICK=1 ROGUESQ_SPIN_YIELD=1`
`ROGUESQ_M5_C88_VALUE=0 ROGUESQ_AUDIO_UCODE=1`

Arm `ROGUESQ_LOG_M5_TASK_CONTRACT=1`, `ROGUESQ_LOG_M5_WAIT_CONTRACT=1`,
`ROGUESQ_LOG_M5_KEYON_CENSUS=1`, `ROGUESQ_LOG_AUDIO_RETURN=1`,
`ROGUESQ_LOG_PCM_BOUNDARY=1`, and the existing image-stage/DMA route logs.
SIGKILL both games after both arms reach hangar or after the phase timeout.
