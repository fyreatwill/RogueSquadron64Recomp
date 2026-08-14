# NEXT work unit (s1091)

HYPOTHESIS-ID: oracle-save-tail-boundary

Run one established eleven-Start retail-oracle capture. Retain whole-RDRAM,
mission-state, VI, PIF, entry/continuation/gate, four existing milestones,
and the eight post-loop watches from s1090. Add the three exact branch-region
PC watches `0x8006D9B4`, `0x8006D9B8`, and `0x8006D9BC`. These are respectively
the loop-boundary `bne`, its delay-slot `lui`, and the first sequential
instruction `addiu`, as verified in generated funcs_17.c.

Competing hypotheses and discriminator:

* H-branch-delay-boundary: 0x8006D9B4 or 0x8006D9B8 fires while 0x8006D9BC
  stays silent, locating the boundary in the branch/delay-slot sequence.
* H-first-sequential-reached: 0x8006D9BC fires, selecting a control-flow or
  watch-gap explanation for the prior all-zero post-loop bracket.
* H-loop-exit-repeat: all three new PCs stay silent while 0x8006D9B0 remains
  positive, repeating the exit-path boundary and requiring a later ROM/PC
  execution-bracket design.
* H-unresolved: whole-RDRAM, PIF, or VI controls fail, invalidating all nulls.

Discriminating measurement: one same-run hit vector for the three new PCs,
the eight s1090 post-loop PCs, all four existing milestones, and the
entry/continuation/gate PCs, with whole-RDRAM, PIF, and VI controls positive.
Do not arm a freelist watch without an independently observed 0x6abxxx
hangar-origin 512 transition.

Exact commands:

```sh
tools/oracle/build.sh
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 120 --press '6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' --hold-ms 150 --watch-write 0x0:0x800000 --watch-rw 0x130B10:0x130B58 --watch-pc 0x8006D900,0x8003E018,0x8003E07C,0x8006D9B0,0x8006DA7C,0x8006DAB8,0x8006DAF0,0x8006D9C0,0x8006D9D0,0x8006D9E0,0x8006D9F0,0x8006DA10,0x8006DA30,0x8006DA50,0x8006DA70,0x8006D9B4,0x8006D9B8,0x8006D9BC --vi-trace --pif-trace
```
