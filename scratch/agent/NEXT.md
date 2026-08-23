# NEXT work unit (s2202) — join retail swaps to the following VI commit

HYPOTHESIS-ID: m5-a1-post-swap-origin-correlation

## Work unit

Before adding the instrument, re-check the retail-oracle contract in
`tools/oracle/README.md` and use the already-established whole-RDRAM watch as
the positive control. Then extend `tools/oracle/rs64_oracle.c` with one bounded
option `--post-swap-table-pc A` for an already-watched execution PC. At each
640-wide `osViSwapBuffer` execution at `A`, latch the current VI origin, the
swap caller, physical `$a0` framebuffer, and the most recently dumped 640-wide
mode descriptor. At the following `dbg_vi` callback, print a joined row only
when the newly observed VI origin is `0x00696100` or `0x00696600`, including
the pre-call origin, swap `$a0`, next origin, mode pointer, both field origins,
and both yScales. Cap joined rows at 256 and report pending/dropped/overflow
counts. Keep the existing phase-gated PC logging and mode dump in the same
run; do not build the port or change the VI alternation knob.

The purpose is to correct the s2201 scope boundary: `VI_ORIGIN` sampled at the
swap breakpoint is the current state before the swap commits the next state,
so the prior same-row arithmetic cannot establish or refute the causal source.

## Competing hypotheses and discriminator

- H-PostSwapFieldDescriptor: for both target origins, the following VI origin
  equals the latched swap framebuffer plus one of the active mode descriptor's
  field origins. With retail field-0 ground truth, the selected row should
  identify which field descriptor is committed.
- H-PostSwapStateBase: joined rows cover both target origins, but neither
  `a0 + fld0.origin` nor `a0 + fld1.origin` matches. The target source is a
  different framebuffer base or a later VI-state producer, so follow that
  producer rather than changing the port.
- H-PostSwapCoverage: the whole-RDRAM control and VI trace are positive, but
  no bounded joined rows cover both target origins. Reject the null as a
  callback/latch coverage failure and redesign the join before interpreting
  descriptor arithmetic.

The discriminator is one same-run table with positive-control status, repeated
VI rows at both target origins, and the complete joined tuple
`(pre_origin, swap_prev_pc, a0_phys, next_origin, mode_ptr, fld0.origin,
fld1.origin, fld0.yScale, fld1.yScale)`. A source conclusion is allowed only
when both target origins have joined rows and the row cap has not overflowed.

## Exact commands

```sh
# First implement the bounded --post-swap-table-pc option described above.
bash tools/oracle/build.sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom ./rogue_squadron.z64 \
  --video /opt/homebrew/Cellar/mupen64plus/2.6.0/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --rsp /opt/homebrew/Cellar/mupen64plus/2.6.0/lib/mupen64plus/mupen64plus-rsp-hle.dylib \
  --secs 45 --watch-write 0x0:0x800000 \
  --watch-pc 0x800352D0,0x80035500 --hit-cap 10000 \
  --pc-phase-log 0x00696100,0x00696600 \
  --mode-dump-pc 0x800352D0 --post-swap-table-pc 0x80035500 \
  --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start \
  --hold-ms 200 > scratch/agent/s2202_retail_post_swap_origin.log 2>&1
```

Do not add a port guard, mitigation, task rewrite, or audio default change.
