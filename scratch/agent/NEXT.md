# NEXT work unit (s2201) — retail target VI descriptor/source census

HYPOTHESIS-ID: m5-a1-retail-vi-origin-source

## Work unit

Extend `tools/oracle/rs64_oracle.c` with one bounded, route-safe option
`--mode-dump-pc A` for an execution watch at `osViSetMode` (`0x800352D0`).
For each watched call whose mode descriptor width is 640, print the mode
pointer and both field descriptors: `fldRegs[0].origin`, `fldRegs[1].origin`,
and their `yScale` values. Keep the existing phase-gated PC logging and add
`osViSwapBuffer` (`0x80035500`) to the same run so target-origin rows retain
the framebuffer `$a0`. Build the oracle once and run one 45-second retail
session with the whole-RDRAM positive-control watch, VI trace, and the
existing start schedule. Do not build the port or change the diagnostic
alternation knob.

## Competing hypotheses and discriminator

- H-FieldDescriptorSource: one 640 mode descriptor has distinct field
  origins, and the origin-keyed swap rows satisfy `framebuffer + fld.origin`
  for both `0x00696100` and `0x00696600`; the missing host state is the VI
  descriptor/scanout selection, not `osViGetCurrentField`.
- H-SwapBufferSource: the two target origins are explained by different
  `osViSwapBuffer` framebuffer arguments or mode pointers while the field
  descriptor pair does not account for them; the next audit follows that
  producer instead.
- H-RetailDescriptorCoverage: the whole-RDRAM control fires but no repeated
  target 640 mode/swap table is collected; reject the null and redesign the
  oracle arm.

The discriminator is one origin-keyed table containing, for every observed
640 mode descriptor, `(mode_ptr, fld0.origin, fld1.origin)` and, for every
target-origin swap execution, `(VI origin, $a0 framebuffer)`. Accept a source
conclusion only if the whole-RDRAM control is positive, VI trace repeats both
target origins, and the descriptor/swap rows cover the same run.

## Exact commands

```sh
# First implement the bounded --mode-dump-pc option described above.
bash tools/oracle/build.sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom ./rogue_squadron.z64 \
  --video /opt/homebrew/Cellar/mupen64plus/2.6.0/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --rsp /opt/homebrew/Cellar/mupen64plus/2.6.0/lib/mupen64plus/mupen64plus-rsp-hle.dylib \
  --secs 45 --watch-write 0x0:0x800000 \
  --watch-pc 0x800352D0,0x80035500 --hit-cap 10000 \
  --pc-phase-log 0x00696100,0x00696600 --mode-dump-pc 0x800352D0 \
  --vi-trace \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start \
  --hold-ms 200 > scratch/agent/s2201_retail_vi_descriptor_source.log 2>&1
```

Do not add a port guard, mitigation, task rewrite, or audio default change.
