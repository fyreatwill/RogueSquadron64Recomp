# NEXT work unit (s2172) — retail writer of heap object +0 (phys 0x25A580)

HYPOTHESIS-ID: m5-a1-cinematic-split

## Work unit

s2171 selected `H-NullV0At87A8` on a failing `=1` cinematic:
SIGBUS at `cutsceneDispatchSlotsByFlag` `0x800A87A8`
`lwc1 $f2, 0x44($v0)` with `$v0=0` after load879c
`lw $v0, 0x50($a2)` returned heap `0x8025A580`. The next
instruction `0x800A87A0 lw $v0, 0($v0)` loads heap object
word0; that word is the pointer consumed at 87A8.

Ask ground truth before adding a port instrument (iron
rule 12). Name the retail writer of phys `0x25A580`
(`0x8025A580+0`) the same way s2166 named phys `0xC7B0C`.

Do not S32-address, NULL-skip, re-flip default-on,
skip/allow `matchKeywordWithPriority` or the lwc, add a
wait/slot guard, or log `$t0`.

## Competing hypotheses and discriminator

- `H-RetailHeap0NeverZero`: watch 1 never stores 0; writer
  histogram names a constructor; same-run `0x800A87A8` `$v0`
  stays KSEG0 (replicates s2165). Then the port `$v0=0` is
  a port-only clobber of that word.
- `H-RetailStoresZero`: watch 1 stores 0 from a named PC
  during 640/`0x00696100`. Then ask whether retail skips
  the lwc (a branch the port misses) or also dereferences 0.
- `H-RetailDifferentObj`: first-slot `+0x50` is not
  `0x8025A580` on this oracle run (heap aslr). Then retarget
  the watch to the observed heap word.
- `H-CoverageFailure`: missing `[gpr-ctl]`, watch0 10000,
  or VI 640 origin `0x00696100`.

Positive controls (same log): `[gpr-ctl]`; watch 0 write
callbacks=10000; `[vi]` 640 origin=`0x00696100`; exec
`0x800A87A0`/`0x800A87A8` nonzero.

## Exact commands

    tools/oracle/build/rs64_oracle \
      --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
      --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
      --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
      --secs 45 --hit-cap 64 \
      --watch-write 0x0:0x800000 \
      --watch-write 0x25A580:0x25A584 \
      --watch-pc 0x800A87A0,0x800A87A8 \
      --first-watch 0 --pc-hist-watch 1 --post-value-watch 1 --vi-trace \
      > scratch/agent/oracle_s2172_heap0_writer.log 2>&1

Rice 45s, no game rebuild. Table to
`scratch/agent/s2172_heap0_writer.txt`. Classify from
watch-1 writer-pc histogram, post-value/zero stores, and
logged 87A8 `$v0`.
