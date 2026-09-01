# Session 3505 — LLE-off, spin-yield-off real-audio route

The single discriminator arm used the existing real-audio controls with
`ROGUESQ_AUDIO_UCODE=1`, `ROGUESQ_LLE_FORCE=0`, `ROGUESQ_SPIN_YIELD=0`,
`ROGUESQ_STUB_MISSING_FUNCS=1`, `ROGUESQ_LOG_ALL=1`, and the validated
autopilot. The self-contained watchdog ran from `build/` for 30 seconds and
SIGKILLed the game.

Results from [the captured run](../scratch/agent/s3505_m5_lle_off_no_spin_real_audio/run.log):

- Startup and phase controls fired; phases 0/320/640 were observed.
- The route reached VI 640 at origin `0x0066A500` at 3.1 seconds and remained
  there through the watchdog interval. Title 1024 (`0x00790400`) and hangar
  512 (`0x006AB400`) were absent.
- Real-audio activity was live: the log contains the audio task path and two
  `m5-route-state` `audio-return` rows. Selector rows at the target title
  phase were absent because title was not reached.
- No crash, access-violation, assertion, or abort marker appeared. The log
  ended in the VI-640 scheduler wait path.

This selects `H-LLEOffAdvanceBlocker` from NEXT.md: disabling spin-yield does
not restore the pre-title advance after LLE is disabled. It rejects
`H-SpinYieldDependency` for this LLE-off arm and makes the selector-table
writer/value hypotheses unevaluable. The positive controls make the null
target-phase result interpretable; this is a route result, not an audio
output-contract result.
