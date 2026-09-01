# NEXT work unit — qualify internal setup return boundary

HYPOTHESIS-ID: m5-selector-setup-return-contract

Session 3532 qualified the missing retail half. Whole-RDRAM control fired and
the retail run reached hangar 512. Retail had the same AI input `a0=0x5622`
as the port but returned/stored `v0=0x561F`; the port returned/stored
`v0=0x5622`.

Next unit: add one regeneration-safe, phase-keyed port witness around the
internal AI-frequency call/return that feeds `0x80091CC4`, then run the port
and restored retail oracle arms in the same iteration. Use the canonical
Rice/autopilot route, explicit title/hangar width buckets, and a whole-RDRAM
positive control in the oracle arm. Do not repeat the valid port setup capture
alone or rewrite audio/selector/task/output state.

Competing hypotheses and discriminator:

- `H-SetupWriterReturnDivergence`: internal input matches but retail return is
  `0x561F` versus port `0x5622`; the callee/host return contract is next.
- `H-SetupWriterReturnParity`: internal input and return match in the new
  witness; the divergence is later in the store/ABI edge.
- `H-SetupWriterInputDivergence`: the new internal input differs; its producer
  is next.
- `H-CaptureInvalid`: a positive control, target phase, or execution witness
  is absent; no parity conclusion is allowed.

Required setup check before building: verify the existing DEBUGGER-enabled
core exports `DebugBreakpointCommand` and `DebugGetCPUDataPtr`; if absent,
`tools/oracle/build_core.sh` is the falsifying rebuild command.
