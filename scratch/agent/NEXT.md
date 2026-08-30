# NEXT work unit — watch the actual retail target framebuffer writer

HYPOTHESIS-ID: m5-route-boundary-target-span-writer

M5 Step 1 is currently route-invalid: retail reaches title/hangar, while the
port image and silent arms stop at pre-title VI 640. Session 3273 reached the
retail target phase but watched only metadata housekeeping: `0x80094648` wrote
sentinel `0x7F7F7F7F` to `0x00141AD8..0x00141AEC`, and the named candidate PCs
produced no non-sentinel target rows. Run one independent retail capture of
the actual target framebuffer span and adjacent generated-PC range. Do not
change audio behavior or add another port counter.

## Competing hypotheses

- `H-TargetSpanWriter`: a target-phase write lands in physical
  `0x00790000..0x00790C00` and the adjacent PC-range histogram attributes its
  writer.
- `H-TargetSpanSilent`: title/hangar and the target-phase bucket are valid but
  no write lands in the target span, leaving the upstream/output boundary
  unresolved.
- `H-TargetSpanCoverageInvalid`: the whole-RDRAM, title, hangar, or target
  phase control is missing, so no writer conclusion is allowed.

## Discriminator

The same oracle run must pass the whole-RDRAM positive control and reach title
`1024 @ 0x00790400` plus hangar `512 @ 0x006AB400`. Watch target physical
framebuffer span `0x00790000:0x00790C00`, retain the existing metadata span
`0x00141AD0:0x00141AF0` as a positive comparison, and use
`--watch-pc-range 0x8008EB00:0x8008ED00` with
`--pc-hist-phase 0x006AB400:512 --pc-hist-watch 1`. A target-phase writer
entry for watch 1 selects `H-TargetSpanWriter`; a valid target phase with no
watch-1 writes selects `H-TargetSpanSilent`; missing controls select
`H-TargetSpanCoverageInvalid`.

## Exact command

From the repository root, run this bounded oracle capture (the target-span
watch is index 1):

```sh
zsh -c 'set -u; ROOT="$PWD"; OUT="$ROOT/scratch/agent/s3274_m5_target_span_writer"; mkdir -p "$OUT"; ORACLE="$ROOT/tools/oracle/build/rs64_oracle"; CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib; ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64; VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib; env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 120 --watch-write 0x0:0x800000 --watch-write 0x790000:0x790c00 --watch-write 0x141ad0:0x141af0 --hit-cap 200 --watch-pc-range 0x8008eb00:0x8008ed00 --pc-hist-phase 0x006ab400:512 --pc-hist-watch 1 --post-value-watch 1 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start >"$OUT/oracle.log" 2>&1 & p=$!; trap "kill -9 $p 2>/dev/null || true" EXIT INT TERM; (sleep 150; kill -9 $p 2>/dev/null || true) & w=$!; wait $p; rc=$?; kill -9 $w 2>/dev/null || true; exit $rc'
```

It arms the whole-RDRAM control, target/pre-target physical spans, phase-gated
PC histograms, and post-value rows in one retail run, then SIGKILLs the oracle
watchdog. Record the positive controls and target-only writer table. Do not
interpret a missing target row unless the controls are present.

## Follow-up selection

If `H-TargetSpanWriter` is selected, compare that writer/order against the
port's `640 @ 0x0066A500` route before authorizing any M5 Step 3 edge. If
`H-TargetSpanSilent` or `H-TargetSpanCoverageInvalid` is selected, keep Step 1
unevaluable and choose the next route-boundary discriminator; do not infer an
audio, gate, slot, or PCM cause.
