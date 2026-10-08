# Next work unit (s4304): phase-gated post-free value/order join

HYPOTHESIS-ID: m5-audio-destub-sequence

State (s4303): the retail oracle passed the whole-RDRAM positive control,
reached VI-512 hangar, and measured 1,141,187 accesses to physical
0x17D000:0x17E200 (1,072,566 reads and 68,621 writes), with 2,820
`musyxSynthFrame` entries and three `waitForAnyAudioSlot` entries. Retail
therefore continues synth activity after the shared free path. The port trace
also shows the freed block and continued synth entries. The remaining
discriminator is the first post-free writer/read value sequence, not whether
the free or synth entry exists.

Competing hypotheses:

- H-layout-equivalent: retail and port perform the same post-free writes and
  synth reads; the crash is caused by a later port-only timing/order defect.
- H-retail-layout-different: retail writes a different object layout into the
  reused block before synth reads it, so only the port forms invalid stream
  nodes.
- H-port-only-damaging-write: both runtimes reuse the block, but only the port
  emits the damaging ASCII/name or ltex-cache value into the stream-node span.

Discriminator: one retail oracle run with the positive control, VI-512 phase
bucket, `--first-watch 1`, `--pc-hist-watch 1`, and the existing port
post-free/synth breadcrumbs from the matching seeded-save VI-512 run. Compare
the first writer PCs and post-free block word samples, then the first synth
read after the free. Positive-control callbacks and VI-512 are mandatory.

Exact command:

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 48 --hit-cap 20 --watch-write 0x0:0x800000 --watch-rw 0x17D000:0x17E200 --watch-pc 0x8009123C,0x800668B0 --first-watch 1 --pc-hist-watch 1 --pc-hist-phase 0x006ab400:512 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start --vi-trace`

Expected outcomes: matching post-free writer/value/read ordering supports
H-layout-equivalent; retail-only differing values/order supports
H-retail-layout-different; a damaging writer present only in the port supports
H-port-only-damaging-write. A zero target count or no VI-512 phase is invalid.
Do not add a guard or skip from this probe.
