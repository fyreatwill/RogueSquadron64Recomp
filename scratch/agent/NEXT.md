# NEXT work unit — qualify a pre-title M5 audio route for the mixer boundary

HYPOTHESIS-ID: m5-mixer-entry-route-qualification

Session 3514 qualified retail `musyxMixActiveVoices` entry `0x80090E04`, but
both port arms were pre-title: real audio crashed in `fillSampleStreamRange`
and silent audio stopped at VI 640. Do not repeat either launch unchanged.

Before building, identify one concrete pre-title audio/route change or arm that
can make the already-built mixer witness reach title. If changing code or
instrumentation, ask the independent retail oracle first with whole-RDRAM and
selector-store controls.

Competing hypotheses:

- `H-RealAudioTransient`: the real-audio crash is a transient route failure;
  a materially changed launch reaches title and emits the mixer control.
- `H-SilentRouteBlocked`: silent `Broke` audio cannot advance the state machine;
  a de-stub or alternate completion path is required.
- `H-PreTitleNonAudio`: both outcomes are caused upstream of audio; a route
  change will leave the target phase absent.
- `H-CaptureInvalid`: phase or witness controls fail, making the arm
  unevaluable.

Discriminating measurement: title/hangar plus mixer control and rows enables
the tuple join; a pre-title crash/stop with controls alive selects route
blocking; missing controls makes the arm unevaluable. Use SIGKILL, a non-dot
final capture path, run from `build/`, and retain
`ROGUESQ_LOG_M5_MIX_ENTRY=1`.
