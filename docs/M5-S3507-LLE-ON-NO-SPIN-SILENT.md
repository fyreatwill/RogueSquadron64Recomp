# M5 Session 3507 — silent LLE-on/no-spin discriminator

Ran one bounded port arm from `build/` using
`ROGUESQ_AUDIO_UCODE=0`, `ROGUESQ_LLE_FORCE=1`, and
`ROGUESQ_SPIN_YIELD=0`, with the Session 3506 autopilot and existing
`ROGUESQ_LOG_ALL=1` controls unchanged. The capture was terminated with
SIGKILL after 30 seconds.

The startup and phase controls were live: VI widths 0 and 320 appeared at
`0x00000000` and `0x00000280`, followed by VI 640 at `0x0066A500`. The route
then remained in the VI-640 scheduler path. The silent dispatch arm produced
no real-audio dispatch or audio-return rows, and the target-phase selector
controls produced zero rows. There were no crash or abort markers. The
existing `[audio-wait-pump-stall]` marker fired after 64 `musyxSynthFrame`
pumps.

This selects `H-AudioIndependentNoSpinBlocker`: disabling the audio ucode did
not advance the forced-LLE/no-spin route past VI 640. It rejects
`H-RealAudioDependency` for this route. Selector-table hypotheses remain
unevaluable because title was not reached. This is a route result, not a
claim that the silent path is generally equivalent to retail audio.

ORIGIN: diagnostic-only route, phase, audio, and selector observations; no
audio state, selector value, task field, or output was rewritten, skipped, or
validated.
