# NEXT work unit — qualify selector capture on the real-audio arm

HYPOTHESIS-ID: m5-real-audio-selector-capture

Session 3492 positively showed that `ROGUESQ_AUDIO_UCODE=0` selects
`musyx_stub` (47 samples through `n=896`), but that arm stalls in the existing
audio wait-pump before title. The independent retail control observed 666
type-2 tasks at `0x80033FCC`, so the next unit must use the qualified
real-audio route to exercise the selector boundary.

Competing hypotheses and discriminating outcomes:

- `H-RealSelectorReachable`: real audio reaches title and both selector
  controls plus selector rows fire.
- `H-RealSelectorSuppressed`: real audio reaches title, but one or both
  selector controls/rows remain absent.
- `H-RealAudioRouteFails`: real audio fails before title again; the failure
  site and positive dispatch marker identify route qualification as unresolved.

Discriminating measurement: one real-audio run using the existing
`run_s3490_m5_upstream_selector.sh` environment, with its route arm changed
from `ROGUESQ_AUDIO_UCODE=0` to `1`; retain the selector controls, phase log,
and `ROGUESQ_LOG_AUDIO_RETURN=1`. Require the existing four-PC positive
control, title origin, selector-load/writer controls, and the independent
retail handoff control before interpreting any zero.

Exact command: create a session-specific copy of the existing script, change
only its `ROGUESQ_AUDIO_UCODE=0` assignment to `1`, and run it from the repo
root with `env ROGUESQ_LOG_AUDIO_RETURN=1 zsh
scratch/agent/run_s3493_m5_real_selector.sh`. Before that run, repeat the
oracle command from `s3492_audio_dispatch_ground_truth` with its whole-RDRAM
and `0x80033FCC` controls; do not add another port hook. Use SIGKILL for the
watchdog and capture all results under `scratch/agent/`.
