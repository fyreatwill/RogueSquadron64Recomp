# M5 Session 3494 — real-audio route qualification

The prescribed capture used the existing `run_s3493_m5_real_selector.sh`
recipe with `ROGUESQ_LOG_AUDIO_RETURN=1`. It ran from `build/`, used the
real-audio/LLE/spin-yield route, and was stopped by the script's SIGKILL
watchdog after 60 seconds.

The same run provided positive controls and reached the title phase:

- `selector_load_rows=1024`, `selector_writer_rows=1024`
- `load_controls=1`, `writer_controls=1`
- `title_origins=1` at `0x00790400`
- `audio_dispatch=62`, `audio_return=260`
- no crash, abort, access-violation, or last-guest-PC marker

The first title selector row loaded `0x8018DD30`; subsequent rows included
the known `0x80171CE0` and `0x80173B20` families. Audio returns reported
`exit=1` on the captured real-audio task rows. The prior
`fillSampleStreamRange` failure therefore did not reproduce in this bounded
retry.

This selects `H-RealAudioRouteTransient` for the measured retry and refutes
`H-RealAudioRouteStableCrash`. It does not yet compare the selector rows with
the independent retail route; that is the next work unit. The capture is
diagnostic-only and does not rewrite audio, selector, or task state.
