# Next work unit (s4306): port-side post-free value/order join

HYPOTHESIS-ID: m5-audio-destub-sequence

State (s4305): the retail oracle passed the whole-RDRAM positive control,
reached VI-512 hangar, and captured an ordered post-store table for the target
block. The first 256 rows repeatedly show structured stream-node links and
sample metadata, with scalar-store mismatch=0. The port still has only
writer/synth breadcrumbs, so the cross-runtime discriminator remains open.

Competing hypotheses:

- H-layout-equivalent: retail and port perform the same post-free writes and
  synth reads; the crash is caused by a later port-only timing/order defect.
- H-retail-layout-different: retail writes a different object layout into the
  reused block before synth reads it, so only the port forms invalid stream
  nodes.
- H-port-only-damaging-write: both runtimes reuse the block, but only the port
  emits the damaging ASCII/name or ltex-cache value into the stream-node span.

Discriminator: one port run with the positive control equivalent (a phase-gated
whole-RDRAM/known-framebuffer control), target range 0x17D000:0x17E200,
phase VI 0x006ab400/512, and one bounded table containing writer PC, aligned
address, post-store word, scalar mismatch, and ordinal. Compare the first
post-free table rows and first synth read against the retail rows in
`scratch/agent/oracle_s4305_fixed.log`. A matching table supports
H-layout-equivalent; a different legitimate link/layout sequence supports
H-retail-layout-different; a damaging value written only by the port supports
H-port-only-damaging-write. A missing control or VI-512 phase is invalid.

Exact command:

Before changing code, inspect the existing `ROGUESQ_LOG_AUDIOTICK_TRACE`,
`ROGUESQ_LOG_AUDIO_OBJECTS`, and phase-key plumbing; add the entire table in
one build, then run the existing seeded-save VI-512 driver from `build/` with
all passive breadcrumbs enabled. Do not add a guard or skip.

Expected outcomes: matching rows select H-layout-equivalent; a different
legitimate layout selects H-retail-layout-different; a damaging port-only
value selects H-port-only-damaging-write. No control or no VI-512 phase is
invalid. Do not add a guard or skip from this probe.
