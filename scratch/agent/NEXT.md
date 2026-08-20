# NEXT work unit (s2034)

HYPOTHESIS-ID: m5-c88-writer-reachability

## Work unit

Use the existing `ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH` entry/exit witness to
locate the C88=1 VI-640 stall relative to `reapplyDisplayMode`. Keep the
current one-site env arm and default-zero control unchanged; do not alter
another gate writer. Use the corrected whitespace-separated eleven-Start list
from boot. Run both arms from the same build; the value arm is expected to
stall before VI 1024, while the unset control must provide the phase-valid
title census and its 24/24 `s2006-svc` control.

## Competing hypotheses and discriminator

- **H1 — post-writer gate transition:** C88=1 reaches
  `reapplyDisplayMode` entry/exit before the VI-640 stall. The entry/exit
  witness appears in the value arm, while the control reaches its title
  writer/raw-gate rows.
- **H2 — pre-writer route boundary:** C88=1 has the same pre-phase service and
  real-audio-task controls but never reaches `reapplyDisplayMode`; the stall is
  upstream of the C88 store or in the route that invokes it.
- **H3 — recipe/arm failure:** the value arm lacks its 24/24 pre-phase service
  control, or the binary does not contain `ROGUESQ_M5_C88_VALUE`; do not
  interpret the phase result until the recipe/build is repaired.

The discriminator is one A/B table of reapply entry/exit counts and last VI
width, joined to the existing s2006, `audtask-dispatch`, phase-gated C88/raw-
gate, and PCM rows. H1 versus H2 is selected by whether the value arm reaches
the named function; H3 is accepted only with a missing positive control or a
missing binary string. The retail oracle ground truth remains the independent
writer/phase control, not a port null.

## Commands

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp

env PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=120 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
ROGUESQ_LLE_FORCE=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 \
ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 \
ROGUESQ_LOG_PCM_SANITY=1 \
  zsh tools/probe.sh scratch/agent/s2034_c88_unset 70 0.5 > scratch/agent/s2034_c88_unset_driver.log 2>&1 &

env PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=120 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
ROGUESQ_LLE_FORCE=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 \
ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 \
ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_M5_C88_VALUE=1 \
  zsh tools/probe.sh scratch/agent/s2034_c88_value 70 0.5 > scratch/agent/s2034_c88_value_driver.log 2>&1 &
wait
```

If the two macOS windows race and the unset control misses hangar, retain its
title-phase rows as the control for this reachability question and do not
infer a hangar/PCM result. If either arm lacks the s2006 positive control,
repair the wrapper before interpreting the reachability table.
