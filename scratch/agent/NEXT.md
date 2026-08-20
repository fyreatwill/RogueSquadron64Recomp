# NEXT work unit (s2068)

HYPOTHESIS-ID: m5-audio-image-output-contract

## Work unit

Run one exact-span retail writer attribution using the corrected Rice oracle.
Reuse the admissible s2067 port table; do not rebuild, regenerate, rerun the
port, or change task fields, dispatch, guards, guest behavior, or host output
routing. Watch the title CB0 span, hangar CB0 span, and the title E50 span
envelope separately, with the whole-RDRAM watch as the same-run positive
control. The oracle must reach both target VI anchors and produce writer-PC
histograms for the exact watches.

## Competing hypotheses and discriminator

- **H-E50-RetailOutput** — the exact E50 envelope receives writes from the
  named retail MusyX writer cluster. Combined with s2067's zero overlap table,
  this identifies a live task/output ABI mismatch rather than scratch data.
- **H-CB0Only** — the exact CB0 spans receive named retail MusyX writes, but the
  E50 envelope does not. The CB0 path is independently audio-owned; the E50
  canary path remains scratch/unknown and cannot be promoted to final output.
- **H-NoExactOwner** — the exact watches have no named MusyX writer hits (or
  fail to fire despite the whole-RDRAM control). The prior broad-band writer
  result cannot be transferred to the generated spans, so the E50 contract is
  unevaluable.

The discriminator is the four-watch table: positive-control callback count,
title-CB0 callback count and writer PCs, hangar-CB0 callback count and writer
PCs, and title-E50-envelope callback count and writer PCs, joined to the
s2067 effective spans. A positive whole-RDRAM control plus named MusyX PCs on
E50 selects H-E50-RetailOutput; named MusyX PCs only on CB0 selects
H-CB0Only; zero exact callbacks or missing route/PC controls selects
H-NoExactOwner. Do not infer ownership from the broad candidate-band count.

## Exact command

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 60 --vi-trace --pif-trace \
  --watch-write 0x0:0x800000 \
  --watch-write 0x178D80:0x178F18 \
  --watch-write 0x1798B0:0x179A48 \
  --watch-write 0x1931F0:0x194E70 \
  --first-watch 1 --pc-hist-watch 1 \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/s2068_oracle_exact_spans.log 2>&1

rg -n 'positive-control threshold|watch write \[|writer-pc|\[vi\]|done:' \
  scratch/agent/s2068_oracle_exact_spans.log | tail -160
rg -n 'VI.*1024|VI.*512|0x00790400|0x006AB400' \
  scratch/agent/s2068_oracle_exact_spans.log
git diff --check
```

If the whole-RDRAM threshold, both target anchors, or any exact-watch PC
histogram is missing, the result is H-NoExactOwner and the next iteration must
not alter the port to compensate.
