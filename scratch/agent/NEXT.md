# NEXT work unit — re-qualify the selector route caller boundary

HYPOTHESIS-ID: m5-selector-route-gate

Session 3522's static census is complete, but its port runtime arm was
capture-invalid: the corrected canonical route crashed pre-title at guest
`0x8000B650` in `fillSampleStreamRange`. The next single work unit is one
fresh real-audio route qualification using the already-built caller witness;
do not interpret absent port rows from the failed run.

Run from `build/` with `ROGUESQ_AUDIO_UCODE=1`,
`ROGUESQ_LLE_FORCE=1`, `ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`,
`ROGUESQ_SPIN_YIELD=1`, `ROGUESQ_STUB_MISSING_FUNCS=1`, and
`ROGUESQ_AUTOPILOT='3:start,7:start,11:start,15:a,30:start,45:start,60:a,75:start,90:a'`.
Enable `ROGUESQ_LOG_M5_SELECTOR_ROUTE=1` plus the existing selector
callsite/AI/store/producer controls. Require title 1024 and hangar 512
phase rows before using the caller comparison. The static result is fixed:
there are no additional direct generated callers beyond the two known calls.

Outcomes: phase-matched caller entry with suppressed known calls selects a
route gate; a phase-matched alternate host-equivalent call selects an
alternate caller; live caller rows with no target call and no alternate call
select retail-equivalence mismatch; missing title/hangar or startup controls
means capture invalid and no M5 conclusion.
