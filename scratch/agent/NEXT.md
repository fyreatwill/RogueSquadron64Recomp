# NEXT: locate the five-name copy before the 512 phase
HYPOTHESIS-ID: m5-audio-destub

Run one Rice-qualified 90-second retail oracle capture. The s4614 capture
passed whole-RDRAM, VI-512, source-span, target-span, and all 17
pointer-target controls. `0x80007670` fired 1,211 times over the run, but
emitted no phase-detail rows at either 512 origin; the same-run `0x80007640`
phase control did emit rows. The 512 target snapshot contains the five names,
while `0x165D9C` is pointer/control data and all discovered pointer targets
had zero writes.

Competing hypotheses:

- H-title-copy: the writer executes in the title 1024 phase and supplies the
  five names before the 512 snapshot.
- H-other-phase: the writer executes in another VI bucket not yet selected.
- H-no-live-copy: the names arrive through a non-writer or earlier boot path;
  the lifetime writer count is unrelated.

Discriminator: retain `--watch-pc 0x80007640,0x80007670` and add
`--pc-hist-phase 0x00790400:1024`, while retaining source/target snapshots,
dynamic pointer-target watches, and the whole-RDRAM positive control. A
phase-title writer row selects H-title-copy; zero title rows with the positive
lifetime writer count leaves H-other-phase/H-no-live-copy open and requires a
wider VI-origin census. Do not add a mitigation.

Build/run:

    tools/oracle/build.sh
    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 90 --hit-cap 10000 --watch-write 0x0:0x800000 --watch-write 0x1724c0:0x17250c --watch-write 0x165d9c:0x165e9c --watch-pc 0x80007640,0x80007670 --pc-phase-log-width 0x6ab400:512 --pc-hist-phase 0x00790400:1024 --phase-pointer-watch 2:0x400 --phase-snapshot-watch 1 --phase-snapshot-watch 2 --phase-origin-watch 1 --phase-origin-watch 2 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150 > scratch/agent/s4615_retail_writer_title_phase.log 2>&1
