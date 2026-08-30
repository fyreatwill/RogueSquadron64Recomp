# Session 3310 — retail 0x000B0934 is written late from in-loop jal 0x800A62B4

HYPOTHESIS-ID: m5-osvimode-postviewer-continuation

## Competing hypotheses

- `H-RetailPtrLive`: physical `0x000B0934` is a KSEG0 pointer
  during first attract, written from `0x800AF4B8` (or another
  named PC) **before the first advancer call**.
- `H-RetailPtrAlsoZero`: retail also holds 0 through the first
  cinematic; the port skip is hardware-like.
- `H-RetailInitThenClear`: retail writes a live pointer then
  `0x800AF640` zeros it before/during the loop.
- `H-CoverageInvalid`: missing whole-RDRAM 10000-write, `[gpr-ctl]`,
  VI `640 @ 0x0066A500`, or cinematic entry `0x800A5D80`.

The written `H-RetailPtrLive` arm (write **before first advancer**)
is refuted. The live result is `H-RetailLateInit`: the word stays 0
for 972 advancer calls, then `cinematicLoopBody` `jal 0x800A62B4`
stores KSEG0 `0x800D9780` at 48.1 s.

## What ran

One independent retail Rice oracle. Watches are physical. No
`--press`. No port instrumentation or build. No M5 Step 3.

`--detail-watch 1` plus rare-exec detail on initializer/store/entry
kept the pointer watch printable after the whole-RDRAM control
filled `--hit-cap`. `--pc-hist-watch 1` and four VI-origin phase
buckets collected writer PCs at shutdown.

Driver: `scratch/agent/s3310_retail_b0934_writer/run.sh`.

```
tools/oracle/build/rs64_oracle
  --core .../libmupen64plus.dylib
  --rom  .../rogue_squadron.z64
  --video .../mupen64plus-video-rice.dylib
  --watch-write 0x0:0x800000
  --watch-write 0x000B0934:0x000B0938
  --watch-pc 0x800AF408,0x800AF430,0x800AF4B8,0x800AF640,
             0x800AF550,0x800AF55C,0x800A5D80
  --detail-watch 1,2,3,4,5,8 --first-watch 1 --pc-hist-watch 1
  --secs 90 --hit-cap 20000 --vi-trace --vi-poll
```

ROM: `sw $v0, 0x934($s2)` at `0x800AF4B8`; `beq $v1,$zero` at
`0x800AF55C` after `lw $v1, 0x934($v0)` at `0x800AF554`;
`sw $zero, 0x934($s0)` is the delay slot of `0x800AF63C` and
always stores when `cinematicDeactivator` does not early-out.
`isCinematicActive` (`0x800AF540`) is `sltu $zero, ptr`.

## Same-run positive controls (90 s)

- Whole-RDRAM write watch: 10002 hits; positive-control threshold
  reached; watch index 1 remained armed.
- `[gpr-ctl]` at 0.5 s.
- VI `320 → 640 @ 0x0066A500` at 2.3 s.
- Cinematic entry `0x800A5D80` at 6.6 s (`prev=0x8003E10C`,
  `$a0=0x13`, 640 @ `0x0066A500`). Second entry at 80.3 s
  (`prev=0x8003E324`).
- Title `1024 @ 0x00790800` at 49.3 s.
- 5356 VI, 90.0 s wall / 89.3 s emulated. `rc=0`.

## Pointer writes (watch index 1: 2 hits, both printed)

| t | pc | value / note | phase |
|---|---|---|---|
| 48.1 | `0x800AF4B8` | exec `$v0=0x800D9780` (KSEG0) | during first cinematic, origin `0x00696100` |
| 49.0 | `0x800AF640` | `sw $zero` | exit-path `jal cinematicDeactivator` at `0x800A64CC` |

No other writer. Lifetime histogram: `AF4B8 n=1`, `AF640 n=1`.
Phase `640 @ 0x00696100` saw only `AF4B8`. Origins `0x0066A500`,
`0x00696600`, and `1024 @ 0x00790400` saw zero pointer writes.

## First-attract timeline

| t | event |
|---|---|
| 6.6 | cinematic entry |
| 10.5 | first `cinematicStageAdvancer` (`jal 0x800A6068`) |
| 10.5–48.0 | **972** advancer calls; **zero** writes to `0x000B0934` |
| 48.1 | `cinematicInitializer` entry `prev=0x800A62B4`; AF430 `$v0=0` (word still 0); AF4B8 `$v0=0x800D9780` |
| 48.1–49.0 | 26 advancer calls with the pointer live |
| 49.0 | deactivator zeros the word (64BC exit path) |
| 49.3 | title 1024 |

Lifetime advancer n=1186 (includes the second cinematic after 80.3 s).
Initializer n=1 (only the 48.1 s call). Deactivator exec n=1.

## Conclusion

`H-CoverageInvalid` is refuted. `H-RetailPtrLive` as written
(KSEG0 **before the first advancer**) is refuted: 972 advancer
calls ran on a null word. `H-RetailPtrAlsoZero` is refuted: retail
does write KSEG0 `0x800D9780` from the named store, then exits.
`H-RetailInitThenClear` as a mid-loop clearer is refuted: the
`AF640` zero is the 64BC exit jal, after the 26 live-pointer
advancer frames.

Selected: `H-RetailLateInit`. Combined with port s3308
(`H-PtrZeroSkip`, n=138 `$v1=0`), the port's null word during
the loop is hardware-like **until 48.1 s**. The port-only stop is
that `cinematicLoopBody` never takes `jal cinematicInitializer`
at `0x800A62B4`. That jal is gated by a time/count sltu at
`0x800A6268`, an `$a0`-byte check at `0x800A6274`, and
`isCinematicActive==0` at `0x800A6288`.

No M5 Step 3. No audio/output change.

Evidence dir: `scratch/agent/s3310_retail_b0934_writer/`.
