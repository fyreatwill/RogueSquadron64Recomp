# M5 s3448 — state-pointer phase qualification

The retail oracle was run first with a whole-RDRAM write watch and execution
watches at `0x80001C98`, `0x80001CB8`, `0x80001CC8`, and `0x80001F84`.
The positive control fired; the oracle completed 2,656 VI in 45.2 seconds and
recorded title-1024 rows at origin `0x00790400` for all three state-related
PCs. This establishes that the title phase and target execution sites are
present in the independent route.

One rebuilt port binary was run in silent and Factor 5 image arms. Both arms
reached title 1024 (`0x00790400`) and hangar 512 (`0x006AB400`). The existing
frequency consumer and output controls were live in both arms (513 consumer
rows and 344 output rows each), and the state-pointer checkpoint positive
control fired.

The original witness was found to hard-code the hangar-512 phase. It was
changed to accept the two established title-1024 origins as well, then rebuilt
and rerun. The repaired witness emitted 512 title entry and 1,024 title
checkpoint rows per arm at `0x790400`, with no crash. Silent and image had the
same first rows and the same consumer callsite mix (358 rows at `0x80001B04`,
154 at `0x80001CB8`). In sampled title rows, `s1` and its pointed word were
unchanged from entry through post-receive and pre-consumer in both arms.

The repaired witness did not emit hangar rows within its 512-row entry budget,
so the prior hangar parity result remains the independent 512 evidence.

This closes the phase-mismatch instrumentation defect and selects
`H-StatePointerParity` for the observed title `rs_free` boundary: no
port-only pointer change occurred between the three checkpoints. It does not
prove the observed pointer values are retail-equivalent or identify the
downstream output-contract cause. The initial wrapper also left its first
process alive and did not launch the image arm; that wrapper failure was
corrected by explicit SIGKILL teardown before collecting the image result.
