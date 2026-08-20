# NEXT work unit (s2035)

HYPOTHESIS-ID: m5-c88-writer-reachability

## Work unit

Qualify the unset C88 control in one fresh single-window run before repeating
the value A/B. Explicitly remove `ROGUESQ_M5_C88_VALUE` from the child
environment, keep the corrected whitespace-separated eleven-Start schedule,
forced LLE, opt-in audio, spin yield, and all existing passive witnesses. Do
not change a game writer or add an instrument. This is a control-recovery
experiment, not a C88 value conclusion.

## Competing hypotheses and discriminator

- **H1 — inherited behavior arm:** omitting the variable in the prior recipe
  inherited or otherwise preserved the C88 value arm; `env -u` restores the
  force-zero control and reaches VI 1024.
- **H2 — common route failure:** the explicitly cleared control still passes
  the 24/24 service control and reapply entry/exit but remains at VI 640, so
  the current failure is upstream/common and the s2033 value comparison must
  wait for a route fix.
- **H3 — input/focus recipe failure:** the cleared control remains at VI 640
  without the expected post-title input-route witness; the phase result is
  invalid until the wrapper/focus path is repaired.

The discriminator is the one control table: `env -u` arm's final VI width,
VI-1024 reach, `s2006-svc` entry/exit count, reapply entry/exit count, and
input-route rows. H1 is selected by a phase-valid VI-1024 control with the
force-zero route; H2 by a live control that still stalls at VI 640; H3 by a
missing input positive control. Do not use phase-6 PCM or a reapply row alone
as evidence. Retail oracle writer/phase evidence remains the independent
ground truth.

## Commands

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp

env -u ROGUESQ_M5_C88_VALUE \
PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=120 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
ROGUESQ_LLE_FORCE=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 \
ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 \
ROGUESQ_LOG_PCM_SANITY=1 \
  zsh tools/probe.sh scratch/agent/s2035_c88_control 70 0.5 > scratch/agent/s2035_c88_control_driver.log 2>&1
```

The control must provide the 24/24 `s2006-svc` entry/exit positive control;
otherwise repair the wrapper before interpreting the VI result. If it reaches
VI 1024, the next iteration can batch the unset and C88=1 arms again from this
same build. If it remains at VI 640, leave the C88 value unchanged and move to
the input/focus route boundary rather than repeating the same A/B.
