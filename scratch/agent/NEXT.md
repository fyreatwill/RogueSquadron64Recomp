# NEXT work unit (s2377) — M5 A1 queue/return boundary

HYPOTHESIS-ID: m5-a1-queue-return-boundary

## Work unit

Run one ground-truth-first, same-build capture of the `rs_free` call to
`osRecvMesg` at `0x80001CB8`, recording queue argument, return/result, and the
post-call queue-head value in both port arms; pair it with an independent
retail physical watch of the corresponding queue state. Do not change game
behavior, dispatch, VI selection, task data, or audio behavior.

## Competing hypotheses and discriminating measurement

- H-QueueStateDiffers: retail and port enter the same `osRecvMesg` call, but
  queue contents/return or the post-call bit-0x8 state differ.
- H-CallContractDiffers: the queue argument, blocking mode, or return contract
  differs between retail and port.
- H-JoinOrLabelArtifact: the observed rows do not refer to the same call or
  post-call state.

The discriminator is one joined table keyed by phase and call ordinal:
queue argument, `$a1`, `$a2`, osRecvMesg result, queue-head word, and the
post-call `0x8` decision, with positive controls for whole-RDRAM, target phase,
and the call-site marker. Matching call arguments but different queue/result
state selects `H-QueueStateDiffers`; a call-argument or blocking-mode mismatch
selects `H-CallContractDiffers`; failure to join the same call selects
`H-JoinOrLabelArtifact`.

## Exact commands

    read docs/F5-UCODE-REFERENCE.md before designing the oracle watch
    inspect tools/oracle/README.md and arm a whole-RDRAM positive control
    build one instrumented binary with the complete joined table
    run the oracle and both port arms concurrently; SIGKILL each port arm after the phase marker

The driver must report controls plus every joined field for both arms and the
retail watch, and must not treat a null result as evidence unless all positive
controls fire in that same run.
