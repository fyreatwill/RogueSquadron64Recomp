# M5 Session 3534 — AI-frequency return contract

The bounded unit was a static contract audit of `osAiSetFrequency` at
`0x80029D20`. The companion retail ELF contains the complete function body,
so no new runtime instrument or build was needed.

Retail computes `dacRate = round(osViClock / frequency)`, rejects rates below
`0x84`, clamps `dacRate / 66` to `16`, writes the AI DAC/bitrate/control
registers, and returns `osViClock / dacRate`. Its `osViClock` is the NTSC
clock at `0x80039108`. This is the standard libultra actual-frequency return
contract, not an identity function.

For the qualified hangar input `0x5622` (22,050 Hz), the NTSC calculation is:

```
dacRate = round(48,681,812 / 22,050) = 2,208
return  = 48,681,812 / 2,208 = 22,047 = 0x561F
```

That exactly explains the independent retail observation at
`0x80091CC4`/`0x80091CC8`. The current host implementation in
`lib/N64ModernRuntime/librecomp/src/ai.cpp` assigns `ctx->r2 = freq`, while
its console-equivalent calculation is commented out. This selects
`H-InternalReturnSemantics` and refutes `H-LaterStoreABI` for the qualified
boundary. Session 3533's target-phase port setup witness and independent
retail execution watch are the two evidence lines; the static ELF audit is
the semantic explanation.

No behavior change was applied in this unit. The next unit may implement the
contract in the host AI primitive and validate the result on the real-audio
route.

ORIGIN: retail ELF disassembly plus the independent retail/port return split;
the legitimate writer is `osAiSetFrequency`, which returns the actual
hardware-programmed frequency rather than the requested input.
