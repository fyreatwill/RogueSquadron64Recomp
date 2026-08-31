# M5 Session 3425 — allocateSongChannelArray caller boundary

The independent retail oracle ran first with a whole-RDRAM positive control,
the target source-span watch, and execution watches at `0x8008F0A0` and
`0x8008F2A0`. The control reached 10,000 callbacks; retail reached title and
hangar. Retail entry had `a0=0x12`, `a1=0x561F`, `prev_pc=0x80091934`; its
`0x8008F2A0` row had `a0=0x3C9`, `s1=0x561F`, and `v0=0x80175AF0`.

The fresh-build port pair used silent and Factor 5 image arms. Both reached
title 1024 and hangar 512, with phase, setup, target, audio ABI/DMA, and PCM
controls live and no crash/abort markers. The regeneration-safe allocate
witness ran in both arms before title. At `0x8008F0A0`, port `a1=0x5622`;
at `0x8008F2A0`, port `s1=0x5622`, with allocator returns
`0x8016FD20`/`0x80177730`/`0x801772F0` across the 320/640/1024 route.

The entry argument `a1` is already divergent before the observed malloc-return
boundary. This selects `H-UpstreamCallerContract` and refutes
`H-InternalMallocReturn` at the observed boundary. The differing caller/entry
contract is not itself proven illegitimate; the next boundary is the sole
caller `initN64RspMixer` at `0x80091934`.

Evidence: `scratch/agent/s3425_groundtruth/oracle.log` and the paired logs in
`scratch/agent/s3423_m5_writer_setup/`.
