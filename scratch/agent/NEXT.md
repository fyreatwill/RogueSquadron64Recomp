# NEXT work unit (s2037)

HYPOTHESIS-ID: m5-c88-value-phase-valid-ab

## Work unit

Run the C88 unset versus `ROGUESQ_M5_C88_VALUE=1` A/B from one freshly built
binary, concurrently, using the preflighted `tools/regress.sh` route. Keep
forced LLE, opt-in audio, spin yield, and all existing M5 witnesses. Use ten
width-640-relative Starts at offsets 1, 3, ..., 19 seconds so the last key is
before the expected hangar transition; do not change the game writer or the
default value.

## Competing hypotheses and discriminator

- **H1 — C88 value is the route cause:** unset reaches phase-valid VI 1024 and
  VI 512, while C88=1 remains at VI 640 despite `input=ok`, `visual=ok`, live
  post-640 host Start edges, and live `s2006-svc`/reapply controls.
- **H2 — C88 is not the route cause:** both arms reach VI 1024 and VI 512
  with the same controls and no phase-valid difference in raw-gate,
  audio-task, or PCM rows. The earlier C88=1 stall was a route artifact.
- **H3 — C88 changes the downstream audio contract but not the route:** both
  arms reach the anchors, but their phase-valid raw-gate/task/PCM census
  differs. This reopens the guest gate/task boundary without changing the
  writer.
- **H4 — harness failure:** either arm lacks preflight or the width-relative
  schedule has no post-640 host Start positive control. Reject the A/B rather
  than interpret a phase null.

The discriminator is one same-build table with, for each arm: preflight input
and visual status; VI 1024/512 transitions and origins; width-relative key
rows and post-640 host Start edges; `s2006-svc` entry/exit; reapply writer
rows; raw-gate branch counts; real audio-task dispatch; and phase-valid PCM
rows. H1 is selected by the phase-valid unset-versus-C88=1 route split; H2 by
matching anchors and downstream rows; H3 by matching anchors with a
downstream census split; H4 by a missing preflight/input control.

## Commands

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp

set +e
env REGRESS_SECS=90 REGRESS_INTERVAL=0.6 \
REGRESS_KEYS='640@1:start 640@3:start 640@5:start 640@7:start 640@9:start 640@11:start 640@13:start 640@15:start 640@17:start 640@19:start' \
REGRESS_LABEL=s2037_c88_unset \
ROGUESQ_LLE_FORCE=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 \
ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 \
ROGUESQ_LOG_PCM_SANITY=1 \
  zsh tools/regress.sh scratch/agent/s2037_c88_unset 90 > scratch/agent/s2037_c88_unset_driver.log 2>&1 &
pid_unset=$!
env REGRESS_SECS=90 REGRESS_INTERVAL=0.6 \
REGRESS_KEYS='640@1:start 640@3:start 640@5:start 640@7:start 640@9:start 640@11:start 640@13:start 640@15:start 640@17:start 640@19:start' \
REGRESS_LABEL=s2037_c88_one \
ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 \
ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 \
ROGUESQ_LOG_PCM_SANITY=1 \
  zsh tools/regress.sh scratch/agent/s2037_c88_one 90 > scratch/agent/s2037_c88_one_driver.log 2>&1 &
pid_one=$!
wait "$pid_unset"; rc_unset=$?
wait "$pid_one"; rc_one=$?
print "unset_rc=$rc_unset c88_one_rc=$rc_one"
```

After both runs, use only bounded `grep -c`, `grep -n ... | head/tail`,
`tail`, and `verdict.json` reads. If either arm selects H4, do not interpret
the A/B; repair the GUI route in a new work unit.
