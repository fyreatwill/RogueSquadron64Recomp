# M5 Session 3533 — selector AI return boundary

The planned boundary was the internal AI-frequency call feeding the setup
writer at `0x80091CC4`/`0x80091CC8`. The DEBUGGER-enabled oracle exports were
verified before the build. One build added a regeneration-safe host return
probe in `librecomp/src/ai.cpp`; its startup control fired, but it produced no
target-phase row and is excluded as evidence.

The corrected real-audio port run reached title 1024 and hangar 512. Its
phase-keyed generated setup row after the AI call reported input `0x5622` and
return/store `v0=0x5622`.

The independent Rice/oracle run used the canonical Start schedule, a
whole-RDRAM positive control, and phase-gated execution watches. The control
fired 10,000 times and hangar armed. Retail reported `a0=0x5622` at both
`0x80091CB8` and `0x80029D20`, followed by `v0=0x561F` at `0x80091CC4`.

The two lines select `H-SetupWriterReturnDivergence`: the first qualified
difference is the return contract of `0x80029D20`, not its input, source
writer, load, or allocator. No audio, selector, task, or output state was
rewritten.

ORIGIN: independent retail execution/GPR evidence plus same-build port setup
return evidence.
