# NEXT work unit (s2076)

HYPOTHESIS-ID: m5-port-treatment-wait-path

## Work unit

Build one Debug binary containing a single regeneration-stable,
phase-keyed `wait-contract` census for the existing port treatment path, then
run the qualified `ROGUESQ_M5_C88_VALUE=1` arm. Do not change the gate store,
audio task fields, output routing, canary reservation, wait cap, or any guard.
Join in one table: treatment gate value and phase, entry/exit/guard state of
`waitForAnyAudioSlot`, the dominant slot readers (`0x8009B62C`,
`0x8009B654`, `0x8009B3EC`, `0x8009B44C`), slot-0 status, named status-writer
stores, and the first failure/last guest PC. Existing `[pad-host]`, VI 640,
`[audtask-dispatch]`, and process-alive rows are the same-run positive
controls; a wait counter alone is not a control.

The s2075 retail witness established that the real table at `0x154620`
cycles `00 -> 01 -> 02 -> 03 -> 00` and that retail never executes
`0x80095D54`. This unit tests whether the port's treatment-only crash enters
an unrelated wait path, consumes the real slot contract, or fails earlier.

## Competing hypotheses and discriminator

- **H-PortTreatmentMisdirectsGate** — C88 treatment enters the port wait while
  the gate is active or before the legitimate gate/slot transition; the joined
  row shows gate/phase, wait entry, and a zero or non-retail slot state before
  the first failure. This selects a gate-to-wait misrouting boundary.
- **H-PortWaitConsumesRetailSlot** — treatment wait reads the same slot-0
  status contract and observes a valid transition or named writer before
  returning/guarding; this selects a port scheduling/completion boundary,
  not a wrong table or gate value.
- **H-PortTreatmentFailsBeforeWait** — the treatment has live preflight and
  audio-task controls but no `wait-contract` entry before its first failure;
  this selects an earlier render/voice path and rules out the wait as the
  first treatment boundary.
- **H-PortWaitStarvesWorker** — treatment enters the wait, slot readers remain
  active, but no status-zero writer/exit occurs while the worker/VI controls
  stop; this selects a scheduler/worker handoff boundary after the retail
  table identity is established.

The discriminator is one phase-keyed table containing all of those fields and
the first-failure edge. Positive controls must fire in the same run. A missing
wait row without live preflight/audio-task controls is UNEVALUABLE; a guard
fire is a failure outcome, not completion.

## Exact commands

Patch the existing fixup instrumentation in one batch, regenerate in the
required order, and build once:

```sh
(cd ../rogue_squadron64 && python3 tools/make_elf.py)
(cd ../N64Recomp && build/N64Recomp rogue_squadron.toml)
python3 ../N64Recomp/fixup_game_funcs.py
cmake --build build --target RogueSquadron64Recomp
```

Then run the treatment from the repository root; the driver launches from
`build/`, captures to an absolute path, and kills the game with SIGKILL:

```sh
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_SPIN_YIELD=1 \
  ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 \
  ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 \
  ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_AUDIO_DRAIN=1 \
  ROGUESQ_LOG_AUDIOTICK_TRACE=1 \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh s2076_c88_wait 30 12
```

Require `[pad-host]`/preflight and `[audtask-dispatch]` controls before
interpreting any wait or slot null. Expected outcomes are: misdirected gate
if a treatment wait row precedes a non-retail slot state; retail-like slot
consumption if the table transition and named writer join; pre-wait failure if
the first failure precedes every wait row; or worker starvation if wait and
readers stay live while the status-zero/exit edge is absent. No mitigation is
authorized from any outcome.
