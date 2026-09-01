# M5 s3532 selector setup return boundary

The independent retail oracle was rerun after the DEBUGGER-enabled core was
verified present. Its whole-RDRAM positive control fired 48,922 times, and the
run reached the target `0x006AB400` 512-wide hangar phase. The setup execution
watches fired twice in that phase.

Retail preserved the same setup inputs measured on the qualified real-audio
port: at `0x80091CB8`, `a0=0x5622`; at `0x80091CC4`/`0x80091CC8`, the value
consumed by both stores was `v0=0x561F`. The same-build port witness observed
the corresponding input `0x5622` and AI return/store value `v0=0x5622` in
title and hangar. The retail and port rows are phase-qualified, independent
execution evidence, not a stopwatch comparison.

This selects `H-SetupWriterReturnDivergence`: the source argument agrees, but
the return value differs before the setup stores. It rules out a source-value
divergence at `MEM_W(0x80165ED0)`, a load-only explanation, and an allocator
explanation at this boundary. The writer of the differing return remains open;
the next discriminator must qualify the internal AI-frequency call/return
contract and its producer on both sides. No audio, selector, task, or output
state was rewritten.

ORIGIN: diagnostic-only retail and port execution/return observations. The
retail setup stores are legitimate game audio state writes.
