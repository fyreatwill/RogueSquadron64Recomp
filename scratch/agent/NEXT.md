# NEXT work unit (s2038)

HYPOTHESIS-ID: m5-c88-value-phase-valid-ab

## Work unit

Run the unset-C88 versus `ROGUESQ_M5_C88_VALUE=1` A/B from one freshly built
binary, concurrently, with a two-stage phase-relative schedule: five
width-640 Starts to drive boot/menu, then three width-1024 Starts after title
entry to drive title-to-hangar. The last key in each width group must precede
the expected next VI transition, avoiding s2037's scorer false negative. Keep
forced LLE, opt-in audio, spin yield, and every existing M5 witness. Do not
change the game writer or treat the C88=1 arm as a shipped behavior.

## Competing hypotheses and discriminator

- **H1 — value-dependent route split is real:** exactly one arm reaches the
  phase-valid hangar anchor, and the route difference reproduces with the
  writer/value and raw-gate state: unset has `0 -> 0`, gate zero/skip; C88=1
  has `0 -> 1`, gate one/gate-1. This confirms a value-dependent route effect,
  but still does not authorize changing the default.
- **H2 — value changes the downstream gate but not reachability:** both arms
  reach title VI 1024 and hangar VI 512 with live controls, while unset keeps
  the phase-valid gate-zero skip and C88=1 reaches gate one/gate-1 rows. The
  earlier inverse route split was a focus/schedule artifact; the next M5
  boundary is downstream task/PCM behavior.
- **H3 — the C88 arm is not the discriminator:** both arms reach both anchors
  and their phase-valid raw-gate/gate-1 census is indistinguishable, or the
  named writer rows do not show `0 -> 0` versus `0 -> 1`. This reopens the
  writer/control mapping rather than the audio consumer.
- **H4 — harness failure:** either arm lacks `input=ok visual=ok`, lacks a
  post-640 host Start edge, or lacks the title anchor needed to fire the
  width-1024 group. Reject the A/B and repair the route; do not interpret a
  scorer FAIL when those controls and the requested transitions are present.

The discriminator is one same-build table per arm: preflight; width-relative
host Start edges; title/hangar VI transitions and origins; `s2006-svc`
entry/exit; phase-valid `reapplyDisplayMode` writer rows; phase-8 and
phase-10 raw-gate/gate-1 rows; audio-task dispatch; and PCM rows. H1 is a
reproduced route split, H2 is matching anchors with value-correlated gate
rows, H3 is no value-correlated writer/gate result, and H4 is a missing
positive control.

## Commands

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp

set +e
env REGRESS_SECS=90 REGRESS_INTERVAL=0.6 \
REGRESS_KEYS='640@1:start 640@3:start 640@5:start 640@7:start 640@9:start 1024@1:start 1024@3:start 1024@5:start' \
REGRESS_LABEL=s2038_c88_unset \
ROGUESQ_LLE_FORCE=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 \
ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 \
ROGUESQ_LOG_PCM_SANITY=1 \
  zsh tools/regress.sh scratch/agent/s2038_c88_unset 90 > scratch/agent/s2038_c88_unset_driver.log 2>&1 &
pid_unset=$!
env REGRESS_SECS=90 REGRESS_INTERVAL=0.6 \
REGRESS_KEYS='640@1:start 640@3:start 640@5:start 640@7:start 640@9:start 1024@1:start 1024@3:start 1024@5:start' \
REGRESS_LABEL=s2038_c88_one \
ROGUESQ_M5_C88_VALUE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 \
ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 \
ROGUESQ_LOG_PCM_SANITY=1 \
  zsh tools/regress.sh scratch/agent/s2038_c88_one 90 > scratch/agent/s2038_c88_one_driver.log 2>&1 &
pid_one=$!
wait "$pid_unset"; rc_unset=$?
wait "$pid_one"; rc_one=$?
print "unset_rc=$rc_unset c88_one_rc=$rc_one"
```

After both runs, use only bounded `grep -c`, `grep -n ... | head/tail`,
`tail`, and `verdict.json` reads. If H4 is selected, do not interpret the
value A/B; repair the GUI route in a new work unit.
