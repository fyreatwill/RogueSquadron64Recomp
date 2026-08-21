# NEXT work unit (s2089)

HYPOTHESIS-ID: m5-voice-output-base-provenance

## Work unit

Extend the corrected oracle post-store-PC facility to retain one bounded,
phase-keyed table of the first 16 `(writer PC, VI, width, origin, physical
destination, post-store value)` rows for each requested PC. Add the known
pointer publisher `0x8008F0EC` to the same table, then run one qualified
retail recipe with the two candidate `+0x34` writers. Do not arm the old
pointer-address stepping watch, change the port, or add a guest witness.

The table must include `0x8008F0EC`, `0x80090C80`, and `0x800921E8` in one
run. The whole-RDRAM watch remains the positive control and is removed at
10,000 callbacks; the second whole-RDRAM watch remains the post-store watch.
Only rows after the title/hangar phase gate are admissible.

## Competing hypotheses and discriminator

- **H-ReallocatedVoiceBase** — the pointer publisher writes a new dynamic base
  between candidate-writer rows, and each destination satisfies
  `base + voiceIdx*0x88 + 0x34` under the contemporaneous base.
- **H-ValidVoiceBase** — the pointer base remains stable and repeated candidate
  destinations form one `0x88` lattice with descriptor-compatible values.
- **H-WrongField** — the pointer base remains stable, but one or both exact
  writer destinations stay off that lattice despite the generated source's
  `+0x34` labels.
- **H-ScalarField** — the pointer/destination table has no voice-base relation
  and the sampled values do not match the generated descriptor/zero roles.

The discriminator is the single same-run table, gated by the whole-RDRAM
positive control plus title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`. A pointer update between non-lattice samples that makes
both samples land on the `0x88` lattice selects H-ReallocatedVoiceBase; a
stable pointer with a common lattice selects H-ValidVoiceBase; a stable
pointer with a persistent non-lattice destination selects H-WrongField; and
absence of both pointer relation and role-compatible values selects
H-ScalarField. A missing row is unevaluable, not a null result.

## Exact commands

First update `tools/oracle/rs64_oracle.c` so requested post-store PCs retain
the bounded table above, including VI width/origin at the post-store sample;
`g_post_value_armed` must gate every requested PC. Then build and run:

```sh
tools/oracle/build.sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 65 \
  --watch-write 0x0:0x800000 \
  --watch-write 0x0:0x800000 \
  --post-value-watch 1 \
  --post-value-pc 0x8008F0EC,0x80090C80,0x800921E8 \
  --watch-pc 0x8009024C:0x80090250 \
  --watch-pc 0x800902CC:0x800902D0 \
  --watch-pc 0x800903F0:0x800903F4 \
  --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/s2089_oracle/run.log 2>&1
```

Before interpreting the table, require the positive-control threshold, both
target VI transitions, and at least one post-store row for every requested
PC. Do not infer a base from a row without its contemporaneous pointer value.
