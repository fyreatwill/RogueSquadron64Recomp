# M5 s3452 — image-arm schema control repair

The fresh Debug build succeeded and the prescribed two-arm run completed with
SIGKILL teardown. Both the silent and Factor 5 image arms reached title VI
1024 at origin `0x00790400`, emitted the four-PC schema positive-control
marker, and produced 2,048 schema rows. Per-arm target counts were
`0x80001C98=514`, `0x80001CB8=510`, `0x80001CC8=510`, and
`0x80001F84=514`; the existing consumer/output hooks produced 512 and
343 rows respectively. Neither arm logged a crash or abort marker.

This resolves the s3451 image-control failure: it was a stale interpretation
of the retained log, not an absent image hook. The retained s3449 logs and
this fresh run independently show the image positive control and all target
PC buckets live.

The normalized silent/image rows diverge from ordinal 4, including `s1` and
source fields. Because the script runs the arms sequentially through an
animating title scene, that cross-run difference cannot select a contract
edge. The result is control qualification only; output/state parity remains
unevaluable until the port rows are joined to the independent retail rows
with phase/PC/ordinal controls.

Build: `cmake --build build --config Debug --target RogueSquadron64Recomp`.
Run: `zsh scratch/agent/run_s3449_m5_state_tuple_context.sh`.
Evidence: `scratch/agent/s3449_m5_state_tuple_context/`.
