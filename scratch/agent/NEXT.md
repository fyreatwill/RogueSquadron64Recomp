# NEXT work unit — audit silent-route audio dispatch before selector capture

HYPOTHESIS-ID: m5-silent-audio-dispatch-gate

Session 3491 reproduced the pre-title failure in both a 30-second prescribed
arm and a 60-second corrective retry. Both used `ROGUESQ_AUDIO_UCODE=0`; the
first stopped at guest PC `0x8000834C` in `spTaskSchedulerThread`, and the
second crashed at `fillSampleStreamRange+932` below `musyxSynthFrame`. No title
controls or selector rows fired.

Competing hypotheses and discriminating outcomes:

- `H-SilentGateHonored`: `ROGUESQ_AUDIO_UCODE=0` dispatches the failing task to
  `musyx_stub`; the audio-dispatch marker appears and no
  `fillSampleStreamRange` crash occurs.
- `H-SilentGateBypassed`: the failing task still enters real MusyX processing;
  the marker is absent and `fillSampleStreamRange` remains the crash site.
- `H-NonAudioSchedulerFault`: the crash is independent of audio dispatch;
  the same task reaches a non-MusyX scheduler/guest fault when the dispatch
  marker is positively shown.

Discriminating measurement: in one instrumented build/run, enable the
existing audio-dispatch log alongside the route and phase logs, and capture
the first pre-title audio task through termination. A `musyx_stub` marker
paired with a later non-MusyX crash selects `H-NonAudioSchedulerFault`; no
marker plus `fillSampleStreamRange` selects `H-SilentGateBypassed`; a stub
marker with no crash and title controls selects `H-SilentGateHonored`.

Exact command: create one batched route capture from the existing
`run_s3490_m5_upstream_selector.sh` environment, adding only the documented
audio-dispatch env var; run from `build/` with a SIGKILL watchdog. Ask the
retail oracle for the same-task dispatch ground truth before adding any new
port hook. Do not build another selector instrument until title controls fire.
