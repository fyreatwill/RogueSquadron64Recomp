# Next work unit: capture the pending A11 audio-slot terminal transition

Run one retail-gated, same-build canonical real-audio/LLE/ungated/solo/spin-yield capture. Do not change the wait, cap, predicate, or slot state. The target is the previously observed `waitForAnyAudioSlot` call with `chCount=16`; if it does not recur on a qualified route, classify the table as unevaluable and do not infer safety.

HYPOTHESIS-ID: m5-a11-pending-terminal-transition

Competing hypotheses and discriminator:

- H-A11-legitimate-pending: the pending call is a legitimate guest wait whose slot/status writer reaches a terminal transition; the complete writer/terminal table will show a valid `01/02/00` progression and a return.
- H-A11-degenerate-pending: the call remains pending because the audio-disabled or incomplete path fails to publish the required slot transition; the qualified table will show entry plus a missing writer/terminal edge while other audio controls continue.
- H-A11-not-reproduced: the canonical route reaches both target phases but does not produce the pending `chCount=16` call; the table is unevaluable, not a safety result.
- H-A11-route-invalid: retail control, port controls, or title/hangar phase is absent; all nulls are invalid.

The single discriminating measurement is a phase-keyed join for each A11 call: entry `chCount`, slot/status reads, every matching slot/status writer, wait iterations/cap, terminal return, audio task/PCM controls, and task generation. A qualified pending call with a complete writer-to-terminal return selects H-A11-legitimate; a qualified pending call with no terminal edge and continuing downstream controls selects H-A11-degenerate-pending. Missing pending call selects H-A11-not-reproduced. Missing controls selects H-A11-route-invalid.

Before any build, verify the existing A11 switches and driver:

`rg -n 'waitForAnyAudioSlot|A11|active-slot|ROGUESQ_LOG_M5_WAIT|ROGUESQ_LOG_M5_KEYON|AUTOPILOT' src tools scratch/agent --glob '!*.log'`

Build once:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Run the retail oracle first from the oracle recipe with whole-RDRAM positive control, `--vi-trace`, and title/hangar phase watches. Then run the canonical port from `build/` with `ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a'`, `ROGUESQ_AUTOPILOT_STOP_WIDTH=512`, `PROBE_PHASE_WIDTH=1024`, `PROBE_KEYS_FROM_PHASE=1`, `PROBE_LEAVE_OK=1`, `ROGUESQ_LOG_PHASE=1`, `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`, `ROGUESQ_SPIN_YIELD=1`, and `ROGUESQ_AUDIO_UCODE=1`.

Arm `ROGUESQ_LOG_M5_WAIT_CONTRACT=1`, `ROGUESQ_LOG_M5_KEYON_CENSUS=1`, `ROGUESQ_LOG_AUDIO_RETURN=1`, `ROGUESQ_LOG_M5_TASK_CONTRACT=1`, and `ROGUESQ_LOG_PCM_BOUNDARY=1`. SIGKILL the game after hangar or the phase timeout. Report the positive controls and the full A11 join; do not treat a non-reproduction as proof that the wait is safe.
