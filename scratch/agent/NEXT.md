# NEXT work unit (s2203) — join retail VI context to following origin

HYPOTHESIS-ID: m5-a1-vi-context-producer

## Work unit

Before adding the instrument, use the retail ground-truth result from s2202
and the companion libultra context layout: `__osViNext` is the retail symbol
at `0x80039214`; its `framep` is at `+0x04`, `modep` at `+0x08`, and the mode
field origins are at `+0x28`/`+0x3C`. Extend `tools/oracle/rs64_oracle.c`
with one bounded option `--vi-context-table-pc A` for an already-watched
execution PC. At each 640-wide execution at `A=0x80035550`
(`__osViSwapContext`), read the physical `__osViNext` pointer, its state,
physical frame pointer, mode pointer, both mode field origins/yScales, and
`VI_CURRENT_REG & 1`. Latch that complete context row and join it to the
following `dbg_vi` callback. Print a joined row only when the next width is
640 and the next origin is `0x00696100` or `0x00696600`; include both candidate
origins `framep_phys + fld0.origin` and `framep_phys + fld1.origin`. Cap rows
at 256 and report latched, joined, pending, dropped, and overflow counts.

Keep the existing whole-RDRAM positive control, phase-gated execution logs,
mode dump, and s2202 swap-to-VI table in the same run. Do not build the port,
change the VI alternation knob, or add a runtime guard.

## Competing hypotheses and discriminator

- H-ContextFramep: joined rows cover both target origins and one of the two
  context candidates equals the following VI origin. The matching field
  identifies the context-selected base/field path that must be compared with
  the port.
- H-ContextOther: joined rows cover both target origins with bounded capacity,
  but neither `framep_phys + fld0.origin` nor `framep_phys + fld1.origin`
  matches. The target is produced by a repeatline/fade override, a later state
  mutation, or another VI-context producer; follow that branch.
- H-ContextCoverage: the whole-RDRAM control and both target VI phases are
  positive, but context joins do not cover both origins or overflow. Treat the
  null as an instrument/timing coverage failure and redesign the join.

The discriminator is one table with positive-control status, both target
origins, zero row overflow, and the complete tuple
`(context_ptr, state, framep_phys, mode_ptr, current_field, fld0.origin,
fld1.origin, candidate0, candidate1, next_origin)`. A source conclusion is
allowed only if both target origins have joined rows and the cap has not
overflowed.

## Exact commands

```sh
# First implement the bounded --vi-context-table-pc option described above.
bash tools/oracle/build.sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom ./rogue_squadron.z64 \
  --video /opt/homebrew/Cellar/mupen64plus/2.6.0/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --rsp /opt/homebrew/Cellar/mupen64plus/2.6.0/lib/mupen64plus/mupen64plus-rsp-hle.dylib \
  --secs 45 --watch-write 0x0:0x800000 \
  --watch-pc 0x800352D0,0x80035500,0x80035550 --hit-cap 10000 \
  --pc-phase-log 0x00696100,0x00696600 \
  --mode-dump-pc 0x800352D0 --post-swap-table-pc 0x80035500 \
  --vi-context-table-pc 0x80035550 --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start \
  --hold-ms 200 > scratch/agent/s2203_retail_vi_context.log 2>&1
```

Do not add a port guard, mitigation, task rewrite, or audio default change.
