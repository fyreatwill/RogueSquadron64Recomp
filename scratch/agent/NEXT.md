# NEXT work unit (s2237) — ground-truth audit of field348 source writers

HYPOTHESIS-ID: m5-audio-image-contract

## Work unit

Run one retail-oracle capture, with no port build or runtime change, watching
the two exact physical RDRAM spans observed in s2236:

- `field348=0x80178C80` → physical `0x178C80:0x178E00`
- `field348=0x801797B0` → physical `0x1797B0:0x179930`

Use the oracle's whole-RDRAM watch as the first positive control, drive the
title and hangar route, and collect a writer-PC histogram plus post-store
values for both source spans. This asks ground truth whether retail populates
the source that the port image arm currently sees as zero.

## Competing hypotheses and discriminating measurement

- **H-RetailField348Writer:** whole-RDRAM control and both target route phases
  fire, and one or both exact source watches have writes with nonzero
  post-store values and writer PCs. The port's zero source is then a missing
  or misordered upstream population edge; a port writer audit is justified.
- **H-RetailField348OriginSplit:** controls and route fire, but only one exact
  source span has writes/nonzero post-values. The two port addresses do not
  share one retail population contract; the next probe must stay origin-keyed.
- **H-RetailNoField348Writer:** whole-RDRAM control and both target phases fire,
  but neither exact source watch has a write or nonzero post-value. The port
  zero is not evidence of a missing retail writer; re-evaluate the field348
  identity/offset before adding a port watch.
- **H-RetailNoTargetRoute:** the whole-RDRAM control fires but the driven run
  does not reach title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`.
  Exact-watch nulls are then unevaluable and do not select a source hypothesis.

The discriminating table is `(watch span, route phase, hit count, writer-PC
histogram, post-value FNV/nonzero summary)`, with whole-RDRAM hit count and
the two VI target transitions as controls. Any exact-span result is valid only
if the controls are present in the same oracle run.

## Exact command

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --secs 180 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --vi-trace \
  --watch-write 0x0:0x800000 \
  --watch-write 0x178C80:0x178E00 \
  --watch-write 0x1797B0:0x179930 \
  --first-watch 0 \
  --pc-hist-watch 1 --pc-hist-watch 2 \
  --post-value-watch 1 --post-value-watch 2 \
  > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2237_retail_field348_oracle.log 2>&1
```

Do not add a port writer instrument, change the image default, rewrite task
fields, or add a writeback/consumer guard until the oracle result selects a
source-writer hypothesis.
