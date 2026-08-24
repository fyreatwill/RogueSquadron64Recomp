# NEXT work unit (s2232) — validate the current opt-in image arm

HYPOTHESIS-ID: m5-audio-image-contract

## Work unit

Execute Step 1 of [`docs/M5-AUDIO-PLAN.md`](../../docs/M5-AUDIO-PLAN.md): run
the existing default-stub and `ROGUESQ_AUDIO_UCODE=1` image arms from the same
Debug build, concurrently, with the qualified LLE/C88/spin route. Do not
change code, generated output, guest gates, task fields, waits, guards, or the
audio default. Do not run an image-only soak.

## Competing hypotheses and discriminating measurement

- **H-AudioDegeneracy:** replacing the silent `M_AUDTASK` return with the
  Factor 5 image produces a downstream service, slot, voice, or PCM signal
  beyond route reachability.
- **H-ContractGap:** the image does real DMEM/DMA work and returns `Broke`, but
  the task/output ABI is incomplete; downstream joins remain absent or
  malformed.
- **H-MixedPipelines:** Factor 5 RSP audio and CPU-side MORT speech are
  separate; RSP task rows can change without MORT/voice rows, or the reverse.
- **H-GateArtifact:** a gate suppresses legitimate work. Select this only if
  the independent retail writer/value row and the matching port gate row both
  show the same suppressed transition; a guard or route count is not enough.

The discriminator is one phase-keyed A/B table for each arm and phase:
`M_AUDTASK` dispatch/exit, task fields/source hash, DMEM changes, DMA ranges
and payload, image completion PC, SP completion, service entry/return, slot
`01/02/00` cycle and status-`03` reaping, voice-array/reap rows, MORT
descriptor/decoder rows, PCM source/consumer address/hash/nonzero joins, and
route phase. The positive controls are the whole-RDRAM/route controls already
provided by the driver plus nonzero image-DMEM/DMA and SP-completion rows.
An image `Broke` with no downstream difference selects H-ContractGap rather
than H-AudioDegeneracy; a new downstream signal selects H-AudioDegeneracy;
RSP/MORT divergence selects H-MixedPipelines; no gate change is authorized by
any other outcome.

## Exact commands

Build once, then run both arms concurrently from the same binary. The driver
phase-gates at VI 1024, sends the qualified keys, and kills the game with
SIGKILL after its grace window.

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp

env GAME_EXTRA_ENV="ROGUESQ_AUDIO_UCODE=0 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s2232_stub 30 12 > scratch/agent/s2232_stub_driver.log 2>&1 &
P0=$!
env GAME_EXTRA_ENV="ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1" \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s2232_image 30 12 > scratch/agent/s2232_image_driver.log 2>&1 &
P1=$!
wait "$P0"; R0=$?
wait "$P1"; R1=$?
print "stub_rc=$R0 image_rc=$R1"
```

Read only bounded summaries from the two run logs; do not `cat` them:

```sh
for arm in stub image; do
  log="scratch/s73_post_a_scene/s2232_${arm}/run.log"
  print "== $arm =="
  grep -a -c '^\[audtask-dispatch\]' "$log" || true
  grep -a -c '^\[audtask-abi\]' "$log" || true
  grep -a -c '^\[audtask-dma-row\]' "$log" || true
  grep -a -c '^\[audio-route\] edge=run-task-return' "$log" || true
  grep -a -c '^\[audio-route\] edge=sp-complete-return' "$log" || true
  grep -a -c '^\[audtask-image-stage\]' "$log" || true
  grep -a -c '^\[pcm-boundary-source\]' "$log" || true
  grep -a -c '^\[pcm-boundary-consumer\]' "$log" || true
  grep -a -c '^\[CRASH\]\|^\[ABORT\]\|Unhandled jump target' "$log" || true
  grep -a '^\[phase\] vi_width=' "$log" | tail -12
  grep -a '^\[audio-image-summary\]\|^\[audio-join\]\|^\[m5-gate\]' "$log" | tail -20
done
```

If a process dies before the first target phase, classify that arm as route
failure and do not infer audio ABI from its nulls. Record the same-run control
counts and exact phase rows in the next ledger entry. No mitigation or default
flip follows from this work unit.
