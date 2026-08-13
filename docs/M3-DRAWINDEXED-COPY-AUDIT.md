# `drawIndexedTri` / `G_CYC_COPY` source audit

Reviewed in s842 (2026-08-13). This is a source-only audit; no behavior was
changed and no build or run was performed.

## Findings

All regular triangle entry points reach `RSP::drawIndexedTri` through standard
TRI1/TRI2/quad handlers (plus the extended vertex-test helpers). The RSP method
asserts immediately for `G_CYC_COPY`; copy mode has rectangle handling, but no
source path makes a regular triangle legitimate in copy mode.

`RSP::setOtherMode`, `setOtherModeH`, and `setOtherModeL` update the active RSP
other-mode stack and immediately call `RDP::setOtherMode`. Extended push/pop
copies and restores that stack. RSP reset initializes `H=0x080CFF` and RDP
reset initializes `H=0`; both decode as 1-cycle. No static stale-copy
transition was found in reset, push/pop, or normal setter paths.

`GBI_F3DFACTOR5::setup` starts with `GBI_F3DEX::setup`, then overrides 0xB4 and
0xBF with `op_consume16`. The Factor 5 reference identifies those opcodes as
the real TRI2 and TRI1 commands, with conditional inline advances. The current
overrides are therefore wrong handlers for legitimate Factor 5 geometry,
though they do not themselves call `drawIndexedTri`.

The inherited setup leaves 0xB1 mapped to standard F3DEX TRI2, while the Factor
5 reference does not identify 0xB1 as a Factor 5 triangle opcode. A
desynchronized or reused 0xB1 can therefore reach `drawIndexedTri` through the
wrong standard handler while copy mode is active. This is the only concrete
source path connecting Factor 5 dispatch to the assertion; runtime attribution
is still required.

## Classification

- `H-copy-cycle-legitimate`: not supported by the RT64 source contract.
- `H-cycle-state-stale`: not selected by the setter/reset audit.
- `H-wrong-handler`: leading hypothesis, based on inherited 0xB1 TRI2 and the
  documented 0xB4/0xBF Factor 5 geometry mapping.

This is not a mitigation justification. The next probe must record active GBI,
dispatch opcode, caller family, and cycle values at each triangle call, with a
positive triangle control in the same run.
