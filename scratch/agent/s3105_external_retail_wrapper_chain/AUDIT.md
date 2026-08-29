# Session 3105 — surviving retail swap callers

Date: 2026-08-28

## Discriminator

The competing hypotheses were H-DirectModeWrapper (one predecessor owns the
mode decision), H-SharedSwapPath (both are generic swaps and the mode writer is
upstream), and H-OverlayAlias (generated registration disagrees with the
companion identity). The measurement was each generated body, direct callsite,
callee identity, companion identity, and static reachability of
`osViSetMode`/VI descriptor fields.

## Results

| retail predecessor | generated identity | direct operations/callees | mode path |
|---|---|---|---|
| `0x8001BE24` | `bufferArbiterProducerMark` (`0x8001BCE4`, funcs_5.c) | `osRecvMesg` at `0x8001BD00`; scans slot-state bytes at `0x80128EAA..AE`; loads selected framebuffer pointer from the `0x8013-0x7168` table; `osViSwapBuffer` at `0x8001BE24`; updates slot state and returns | none; no `osViSetMode`, mode descriptor load, or mode-field store |
| `0x80019B14` | `viRetraceHandlerThread` (`0x80019868`, funcs_4.c) | waits on retrace queue; scans the same slot-state table; loads selected framebuffer pointer; `osViSwapBuffer` at `0x80019B14`; `postSwapRdpReset`; `osSendMesg`; `osYieldThread` | none; no `osViSetMode`, mode descriptor load, or mode-field store |

The generated header and project symbol table identify the two enclosing
functions consistently. The companion map names them
`bufferArbiterProducerMark` and `viRetraceHandlerThread`, and generated
registration uses the same identities. No overlay-alias disagreement was
found.

The mode-setting path is elsewhere. `advanceVideoFrame` at `0x8001818C`
calls `swapBufferWithViMode` at `0x800182C8`; that wrapper copies the selected
VI descriptor to its staging structure and calls `osViSetMode` at
`0x8001BB28`, then `waitOnVideoQueue`. `applyPendingViChanges` and
`initVideoSubsystem` also contain direct `osViSetMode` callsites. Thus the two
surviving retail predecessors are downstream framebuffer consumers, not
owners of the mode/descriptor decision.

## Selection

`H-SharedSwapPath` selected. `H-DirectModeWrapper` is refuted for both
predecessors by the absence of mode-setting operations in their complete
bodies. `H-OverlayAlias` is refuted by agreement across generated names,
registration, project TOML, and companion symbols.

This is a static result; no runtime instrument or build was needed.
