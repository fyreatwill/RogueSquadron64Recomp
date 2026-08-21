# NEXT work unit (s2091)

HYPOTHESIS-ID: m5-command-list-root-provenance

## Work unit

Run one phase-gated retail-oracle table to qualify the command-list root used
by `0x80090C80`. Keep the whole-RDRAM positive control, watch the physical
command-list head and count entries, and retain post-store rows for the root
publisher `0x80091074`, the off-lattice writer `0x80090C80`, and the voice-array
writer `0x800921E8`. This is ground-truth attribution only: do not change the
port, task ABI, output routing, waits, guards, or gates.

## Competing hypotheses and discriminator

- **H-RetailCommandListMatch** — retail `0x80090C80` uses the same command-list
  contract as generated source: `head + count*0xA10 + inner*0x50 + 0x44`, with
  head from `0x80149750` and count from `0x80149760`.
- **H-RetailVoiceArrayDivergence** — retail `0x80090C80` follows the voice
  array or another root, so its destination does not fit the generated
  command-list formula even though the exact PC is active.
- **H-ReallocatedCommandRoot** — the command-list head is republished or
  relocates contemporaneously with the writer rows; a single stable root is
  not the right join key.
- **H-OracleWriterMismatch** — the requested PCs or physical watched stores do
  not correspond to the source instructions under test.

The discriminator is one table joining each phase-gated `0x80091074` root
store, the contemporaneous `0x80149750`/`0x80149760` values, and each
`0x80090C80` destination/value. A stable root plus destinations matching
`head + count*0xA10 + inner*0x50 + 0x44` selects H-RetailCommandListMatch. A
voice-lattice destination or another stable root selects
H-RetailVoiceArrayDivergence. Root changes bracketed by writer rows select
H-ReallocatedCommandRoot. Missing exact-PC rows while the positive control,
both target VI phases, and the other requested PCs fire is H-OracleWriterMismatch
or an unevaluable join; do not call it a semantic null.

## Exact command

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 65 --hit-cap 64 \
  --watch-write 0x0:0x800000 \
  --watch-write 0x149750:0x149754 \
  --watch-write 0x149760:0x149762 \
  --watch-pc 0x80091074,0x80090C80,0x800921E8 \
  --post-value-pc 0x80091074,0x80090C80,0x800921E8 \
  --first-watch 0 --pc-hist-watch 0 --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
```

Require the positive-control hit, title `1024 @ 0x00790400`, hangar `512 @
0x006AB400`, and rows for the requested PCs before interpreting any null.
