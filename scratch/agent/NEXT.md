# Next work unit: independent retail source-writer/value parity

HYPOTHESIS-ID: m5-audio-retail-source-writer-parity

s3818 qualified the port-side writer join. The active generated scalar-store
census recorded final writer sequence 664 at PC `0x800078EC`, physical
`0x179A44`, zero byte; repeated hangar input DMAs read
`0x1798B0..0x179A48` as `FNV=0x762B22A5`, `nz=0`. Do not repeat that port
writer or DMEM ordering probe.

Competing hypotheses and discriminator:

- H1: retail also clears/fills this source span with a zero-valued
  `0x800078EC` byte store, so the port zero payload is writer-parity-compatible
  and the divergence is downstream or in a later retail writer.
- H2: retail reaches the same target phase with a distinct writer PC or a
  nonzero value, so the port clear/fill is the source of the parity break.
- H3: the retail oracle cannot join a source-span byte writer to the hangar
  phase/input boundary, so writer parity remains unevaluable.

The discriminator is one independent retail-oracle run with the mandatory
whole-RDRAM positive control, Rice video, hangar-driving Start schedule,
phase-gated byte watches for physical `0x1798B0..0x179A48`, and writer-PC
histograms/post-store scalar samples. A same-phase retail writer/value match
selects H1; a distinct PC or nonzero byte selects H2; absent phase/control or
zero target attribution selects H3. Keep the port result fixed as the first
comparison row and do not change runtime code before the oracle result.

Read `tools/oracle/README.md` for the exact oracle binary/config paths. Use a
whole-RDRAM watch as the first watch and the source span as the target watch;
arm the hangar VI phase before interpreting target rows. Capture under
`scratch/agent/s3819_m5_retail_source_writer/`, kill only with SIGKILL, and
inspect bounded watch/histogram/phase summaries.
