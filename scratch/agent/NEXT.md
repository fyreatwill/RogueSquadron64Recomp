# Next work unit (s4303): compare post-free reuse of the stream-node block in retail and port

HYPOTHESIS-ID: m5-audio-destub-sequence

State (s4302): retail reaches hangar, enters `waitForAnyAudioSlot` 3-4 times,
reads the B39 flag at aligned physical word 0x00130B38, then reads all three
asset pointers and takes the same free path as the port. The B39-difference
hypothesis is closed. The port still sees the freed 0x8017D910 block reused by
level-texture-cache records while `musyxSynthFrame` continues to walk it.

Competing hypotheses:

- H-retail-different-reuse: retail's allocator gives the post-free block to a
  different legitimate consumer, so the synth's stale walk does not encounter
  text records.
- H-retail-synth-stop: retail stops or retargets `musyxSynthFrame` before the
  first post-free walk; the port's audio scheduling/de-stubbing leaves it live.
- H-port-only-writer: the same retail reuse occurs, but only the port writes
  the damaging ltex-cache/name bytes into the stream-node range.

Discriminator: first run the retail oracle with whole-RDRAM positive control,
read/write watches on physical 0x17D000:0x17E200, and `--watch-pc` for the
known synth entry plus `waitForAnyAudioSlot`; phase-gate attribution to the
hangar origin. In the same iteration, use the existing port guest write/synth
breadcrumbs (no new field-by-field counter) on the matching VI-512 phase.

Interpretation: retail writes in the block after the wait and synth reads it
after those writes => H-retail-different-reuse is false and the allocator
consumer/value layout is the discriminator. Retail has no post-free synth reads
=> H-retail-synth-stop is supported. Retail and port have the same post-free
writer/synth sequence but only port produces ASCII pairs => H-port-only-writer
is supported. A zero result without the positive control or without VI 512 is
invalid. Do not add a free guard or skip; this is an origin/lifetime probe.

Exact first command shape:

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 65 --hit-cap 20 --watch-write 0x0:0x800000 --watch-rw 0x17D000:0x17E200 --watch-pc <synth-entry>,0x800668B0 --pc-hist-watch 1 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --vi-trace`
