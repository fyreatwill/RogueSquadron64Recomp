# NEXT work unit (s2033)

HYPOTHESIS-ID: m5-c88-value-ab

## Work unit

Build one env-gated C88 value arm and compare it with the unset control. The
arm restores the original guest value at `reapplyDisplayMode`'s
`0x8008EC88` store only; all other `0x800A0F50` writers remain unchanged.
Keep `ROGUESQ_AUDIO_UCODE=1` opt-in and use the existing eleven-Start,
phase-gated probe recipe. Both arms must be built from the same instrumented
tree and run in the same iteration; no value conclusion is allowed from a
single arm or from a run without the existing positive controls.

## Competing hypotheses and discriminator

- **A — value enables the intended path:** the C88=1 arm records a phase-valid
  `gate=1` transition and downstream gate-1/task/slot/PCM activity that the
  unset arm lacks, while both arms pass the s2006/task positive controls.
- **B — value is insufficient or destabilizing:** C88=1 is phase-valid but
  remains consumer/task/PCM-silent, or it stalls/crashes before the required
  phase rows while the unset control stays valid. This selects a later audio
  boundary, not permission to add another gate change.
- **C — arm/control failure:** the new env arm does not appear in the binary or
  both arms lack the same-run positive controls. Treat the comparison as
  unevaluable and repair the fixup/build recipe before interpreting audio.

The discriminator is one phase-keyed A/B table containing C88 writer value,
raw gate, gate-1, wait, task exit/DMEM, slot/status, and PCM rows, with the
existing s2006 control in both arms. A/B split on downstream gate/task
activity; C is accepted only when its positive-control failure is visible.
Use VI width/origin gates, never wall-clock scene matching.

## Build and A/B commands

~~~sh
# Regeneration order when the external generated tree is changed:
# make_elf.py -> N64Recomp -> fixup_game_funcs.py -> cmake.
cmake --build build --config Debug --target RogueSquadron64Recomp

env PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 \
PROBE_LEAVE_OK=1 PROBE_KEYS='6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' \
ROGUESQ_LLE_FORCE=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 \
  zsh tools/probe.sh scratch/agent/s2033_c88_unset 70 0.5 > scratch/agent/s2033_c88_unset_driver.log 2>&1 &

env PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 \
PROBE_LEAVE_OK=1 PROBE_KEYS='6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' \
ROGUESQ_LLE_FORCE=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_M5_C88_VALUE=1 \
  zsh tools/probe.sh scratch/agent/s2033_c88_value 70 0.5 > scratch/agent/s2033_c88_value_driver.log 2>&1 &
wait
~~~

Accept an arm only if the same-run s2006/task controls fire, the arm reaches
the 1024-width title and 512-width hangar phases, and its phase rows are
present for the full table. The C88=1 arm is the only treatment; the unset arm
is the control. Do not change any other gate writer or promote the value from
task exit alone. If C88=1 produces no downstream gate/task/PCM distinction,
park the value arm and move to the next M5 boundary.
