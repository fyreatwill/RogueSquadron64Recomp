# Session 3338 — M5 callback entry capture

The first run of the new entry probe was invalid: it crashed at 169 ms before
title/hangar controls. The fixed reachability recipe completed without crash
or abort and passed the required controls: host-boundary rows, task-handoff
rows, title VI 1024, and hangar VI 512.

The entry hook at `0x80007910` fired 11 times. It captured
`a0=0x80003250` once, `a0=0x8009123C` six times, and
`a0=0x8009B5A8` four times. Every captured `$ra` was `0x00000000`, including
the phase-2 `0x8009123C` entry and later target-phase entries. The callback
census simultaneously showed `[80003250,8009123C,...]`.

This refutes `H-PortStoreEntryMismatch`: the store value is visible at callee
entry. It does not select either caller hypothesis because the generated entry
context supplies no caller marker. `$ra=0` is single-source port evidence and
is not evidence that the caller is address zero. No behavior change is
authorized.
