# Session 2973 M5 route-preparation census

The Debug build completed before the capture. The corrected wrapper passed the
retail oracle gate in the same artifact: its whole-RDRAM positive control
reached 10,000 callbacks, then retail VI title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`.

Both port arms were launched from that build with phase-gated input and the
same route diagnostics. Silent (`ROGUESQ_AUDIO_UCODE=0`) reached 11 phase rows,
55 audio dispatches, and VI 640 (`0x0066A500`); image (`=1`) reached 10 phase
rows, 57 audio dispatches, and the same VI 640 boundary. Neither arm crashed
or aborted.

The route-preparation table was positive in both arms, but all rows were
non-target: silent 1,027 rows and image 839 rows, every row `target=0`
`accepted=0`. The target predicate is the requested title/hangar pair, so no
row requested width 1024/origin `0x00790400` or width 512/origin
`0x006AB400`. VI-commit/route-transition rows did run for the pre-title path;
target-candidate and identity-edge rows were zero in both arms.

This selects `H-route-prep-absent`: the port never prepares the target route
after reaching VI 640. The identical absence across silent and image arms
rules out `H-audio-arm-route` for this capture. The oracle control and the two
independent port arms are the two evidence lines; downstream audio/service/
PCM nulls remain unevaluable because no target phase occurred.

The first two wrapper attempts failed before the game measurement due to zsh
`set -u`/`print` formatting bugs. They were fixed and the capture was rerun;
only the third run is evidence above.
