# NEXT work unit (s1092)

HYPOTHESIS-ID: oracle-branch-delay-boundary

Run one established eleven-Start retail-oracle capture. Retain whole-RDRAM,
mission-state, VI, PIF, entry/continuation/gate, four existing milestones,
the eight post-loop watches, and the three branch-region watches from s1091.
Add PC watches for the statically identified branch target `0x8006D980` and
the nearby loop instructions through `0x8006D9AC`, as one bounded target set.
Generated control flow shows `0x8006D9B4` branches to `0x8006D980` when
`$s0 < 0x20`, with `0x8006D9B8` as the delay slot.

Competing hypotheses and discriminator:

* H-taken-target: `0x8006D980` or nearby loop PCs fire with `0x8006D9B4`
  positive and `0x8006D9B8`/`0x8006D9BC` silent, selecting the taken target
  and leaving delay-slot callback behavior as an oracle detail.
* H-delay-slot-callback-gap: `0x8006D9B8` remains silent but the target set
  does not fire, selecting a debugger PC-callback limitation or an earlier
  stop boundary.
* H-first-sequential-reached: `0x8006D9BC` fires, reopening a watch-gap or
  later control-flow explanation.
* H-unresolved: whole-RDRAM, PIF, or VI controls fail, invalidating all nulls.

Discriminating measurement: one same-run hit vector for the target/nearby-loop
PC set, the three branch-region PCs, the eight post-loop PCs, all four existing
milestones, and the entry/continuation/gate PCs, with whole-RDRAM, PIF, and VI
controls positive.

Exact command shape:

```sh
tools/oracle/build.sh
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 120 --press '6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' --hold-ms 150 --watch-write 0x0:0x800000 --watch-rw 0x130B10:0x130B58 --watch-pc 0x8006D900,0x8003E018,0x8003E07C,0x8006D9B0,0x8006DA7C,0x8006DAB8,0x8006DAF0,0x8006D9C0,0x8006D9D0,0x8006D9E0,0x8006D9F0,0x8006DA10,0x8006DA30,0x8006DA50,0x8006DA70,0x8006D9B4,0x8006D9B8,0x8006D9BC,0x8006D980,0x8006D984,0x8006D988,0x8006D98C,0x8006D990,0x8006D994,0x8006D998,0x8006D99C,0x8006D9A0,0x8006D9A4,0x8006D9A8,0x8006D9AC --vi-trace --pif-trace
```
