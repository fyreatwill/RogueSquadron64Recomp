# NEXT: phase-gate the retail writer operand
HYPOTHESIS-ID: m5-audio-destub

Run one Rice-qualified 90-second retail oracle capture. s4612 passed the
whole-RDRAM, VI-512, source-span, target-span, and pointer-target controls;
`0x80007670` fired 1,211 times, while `0x80007640` stayed at zero. The
512-phase target snapshot contains the five copied names, the source base
`0x165D9C` is pointer/control data, and all 17 discovered pointer targets had
zero writes.

Competing hypotheses:

- H-other-shared-table: the phase-gated `rs_strncpy` writer receives a distinct
  RDRAM source containing the five records; it is outside the visible pointer
  targets.
- H-pointer-no-records: the writer receives a stable non-RDRAM or alternate
  source operand; the visible pointer table is metadata/control only.
- H-control-invalid: the writer control is live only outside VI 512, so the
  phase-gated operand remains unevaluable.

Discriminator: phase-gate execution at `0x80007670` with
`--pc-phase-log-width 0x6ab400:512`, while retaining snapshots and writes for
the source span, target span, and all dynamically discovered pointer targets.
A phase-512 writer hit with a distinct RDRAM operand selects
H-other-shared-table; a phase-512 hit with a stable alternate/non-RDRAM
operand selects H-pointer-no-records; zero phase-512 writer hits selects
H-control-invalid. Whole-RDRAM, VI-512, source-span, target-span, and caller
controls must all fire before interpreting nulls. Do not add a mitigation.

Build/run:

    tools/oracle/build.sh
    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 90 --hit-cap 10000 --watch-write 0x0:0x800000 --watch-write 0x1724c0:0x17250c --watch-write 0x165d9c:0x165e9c --watch-pc 0x80007640,0x80007670 --pc-phase-log-width 0x6ab400:512 --phase-pointer-watch 2:0x400 --phase-snapshot-watch 1 --phase-snapshot-watch 2 --phase-origin-watch 1 --phase-origin-watch 2 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150 > scratch/agent/s4613_retail_writer_operand.log 2>&1
