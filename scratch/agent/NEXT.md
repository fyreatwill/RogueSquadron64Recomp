# NEXT work unit — retail 0x000B0934 writer during first attract

HYPOTHESIS-ID: m5-osvimode-postviewer-continuation

## Resume context

Port Session 3308 selected `H-PtrZeroSkip`: every
`cinematicStageAdvancer` ptr-check at `0x800AF55C` sees `$v1=0`
after `lw` of `0x800B0934` (n=138/138), takes `L_800AF604`, and
returns `$v0=0`. Silent: fp-compare, stage-lt7, ret-one. dt `$a2`
is live (1/60 then 1/30). Same-run `[phase] cineState` is 0 after
boot. Named guest writer is `cinematicInitializer` `sw` at
`0x800AF4B8`; named clearer is `cinematicDeactivator` `sw $zero`
at `0x800AF640`. Ask retail before another port instrument.

## Competing hypotheses

- `H-RetailPtrLive`: physical `0x000B0934` is a KSEG0 pointer
  during first-attract cinematic, written from `0x800AF4B8`
  (or another named PC) before the first advancer call.
- `H-RetailPtrAlsoZero`: retail also holds 0 through the first
  cinematic; the port skip is hardware-like and the 6074 `$v0=1`
  has a different producer.
- `H-RetailInitThenClear`: retail writes a live pointer then
  `0x800AF640` (or another store) zeros it before/during the
  loop — so a port clearer would be the mismatch.
- `H-CoverageInvalid`: missing whole-RDRAM 10000-write, `[gpr-ctl]`,
  VI `640 @ 0x0066A500`, or cinematic entry `0x800A5D80`.

## Discriminator

One Rice oracle: whole-RDRAM write control plus write-watch
`0x000B0934:0x000B0938` and exec-watch of `0x800AF408`,
`0x800AF4B8`, `0x800AF640`, `0x800AF550`, `0x800AF55C`,
`0x800A5D80`. 90 s, `--hit-cap 20000`, `--vi-trace --vi-poll`.
No `--press`.

KSEG0 write from `0x800AF4B8` (or another PC) before cinematic
entry selects `H-RetailPtrLive`. Zero write hits and `$v0`/`exec`
of initializer still live with a 0 snapshot selects
`H-RetailPtrAlsoZero`. Nonzero write then a later zero store
before/during the loop selects `H-RetailInitThenClear`. Missing
controls select `H-CoverageInvalid`.

## Exact commands

```
tools/oracle/build/rs64_oracle \
  --core .../libmupen64plus.dylib \
  --rom  .../rogue_squadron.z64 \
  --video .../mupen64plus-video-rice.dylib \
  --watch-write 0x0:0x800000 \
  --watch-write 0x000B0934:0x000B0938 \
  --watch-pc 0x800AF408,0x800AF4B8,0x800AF640,0x800AF550,0x800AF55C,0x800A5D80 \
  --secs 90 --hit-cap 20000 --vi-trace --vi-poll
```

Use the same CORE/ROM/VIDEO paths as
`scratch/agent/s3306_retail_cinematic_exit/run.sh`. Require
10000-write, `[gpr-ctl]`, VI `640 @ 0x0066A500`, and cinematic
entry. If `--hit-cap` truncates before entry, raise it in the
same iteration.

No M5 Step 3. No audio/output change. No port build.
