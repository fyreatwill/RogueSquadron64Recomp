# NEXT work unit — restore independent oracle for setup contract

HYPOTHESIS-ID: m5-selector-setup-writer-contract

Session 3531 qualified the port-side `0x80091CC8` setup contract: title and
hangar controls were live; `reapplyAudioConfig` preserved `a0=0x80165ED0`,
`a1=0x12`, loaded AI input `0x5622`, and observed AI return `v0=0x5622`.
The retail oracle could not start because `libmupen64plus.dylib` is absent.

Next unit: restore/build the oracle core, then run one retail capture with a
whole-RDRAM positive control, target write watch `0x165ED0:0x165ED4`, and
phase-gated execution watches at `0x80091C88`, `0x80091CAC`, `0x80091CB0`,
`0x80091CB8`, `0x80091CBC`, `0x80091CC4`, and `0x80091CC8`. Use the canonical
Rice/autopilot route and explicit title/hangar width buckets. Do not repeat
the port capture or rewrite audio/selector/task/output state.

Competing hypotheses and discriminator:

- `H-SetupWriterSourceDivergence`: retail source arguments or AI return/value
  differ from the qualified port tuple; the first differing field selects the
  next producer/contract.
- `H-SetupWriterSourceParity`: retail source and return/value match the port;
  the remaining difference is an intervening generated store/ABI edge.
- `H-CaptureInvalid`: whole-RDRAM control, target phase, or target execution
  witness is absent; no parity conclusion is allowed.

Required setup check before the run: locate or build
`libmupen64plus.dylib`; if it cannot be made available, document the exact
missing dependency and the one command that would falsify that blocker.
