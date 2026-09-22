# Next work unit: M5 Step 1 same-build audio qualification

HYPOTHESIS-ID: m5-step1-audio-contract-qualification

The retail shared guest tuple is now qualified. The next M5 unit is the
existing Step 1 checkpoint from `docs/M5-AUDIO-PLAN.md`: re-baseline the
current real Factor 5 image against the silent `M_AUDTASK` control using one
fresh build and concurrent, phase-gated runs.

Competing hypotheses:

- `H-ImageContractProgress`: the real image completes the task contract and
  produces downstream service/slot/PCM progress that the silent arm cannot.
- `H-ImageRouteOnly`: the real image differs only in route reachability; it
  has no additional valid task, service, slot, or nonzero PCM contract edge.
- `H-AudioControlInvalid`: one or both arms fail the qualification route or
  positive controls, so no audio conclusion is valid.

Discriminator: same-build paired rows after VI 1024 and VI 512. The real arm
must show dispatch, task fields, nonzero DMEM/DMA, image completion at
`0x1328`, `Broke`, SP completion, and downstream service/slot/PCM rows; the
silent arm must show its intentional `Broke` stub with no DMEM/DMA. If both
arms fail to reach a target phase, select `H-AudioControlInvalid` and do not
interpret downstream nulls. A real-arm task/control chain without downstream
rows selects `H-ImageContractProgress` only up to the missing edge; identical
chains apart from route reachability select `H-ImageRouteOnly`.

Exact commands:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
mkdir -p /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s3724_audio_real /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s3724_audio_silent
(env ROGUESQ_LOG_ALL=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' zsh tools/probe.sh /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s3724_audio_real 180 2) &
(env ROGUESQ_AUDIO_UCODE=0 ROGUESQ_LOG_ALL=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' zsh tools/probe.sh /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s3724_audio_silent 180 2) &
wait
```

Require positive controls in both logs before classifying any null: phase
transitions, RSP-source/task dispatch, and SP completion. Do not change task,
selector, clear, payload, or audio gate behavior in this checkpoint.
