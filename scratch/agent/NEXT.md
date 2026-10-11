# NEXT: locate the five-name copy across boot and intro phases
HYPOTHESIS-ID: m5-audio-destub

The s4615 fixed capture passed whole-RDRAM, title VI 1024, hangar VI 512,
target/source, and all 17 pointer-target controls. The title target snapshot
already contained the five names (same FNV as hangar), but `0x80007670` had
zero title-bucket target writer rows despite 1,211 lifetime executions; the
`0x80007640` control fired.

Competing hypotheses:

- H-intro-or-boot-copy: a writer row appears in the 320 boot or 640 intro
  bucket, before title/hangar.
- H-other-512-copy: a writer row appears only in one of the 512 buckets not
  previously covered, such as attract/demo.
- H-no-live-copy: all covered buckets are zero; the names predate this route
  or arrive through a path not represented by the target writer watch.

Discriminator: one run with `--pc-hist-watch 1` and phase buckets for every
known route phase. A target writer row in 320/640 selects H-intro-or-boot-copy;
a row only in 512 selects H-other-512-copy; zero rows in all buckets, with
whole-RDRAM, target/source, and `0x80007640` controls firing, selects
H-no-live-copy provisionally. Do not add a mitigation.

Build/run:

    tools/oracle/build.sh
    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 90 --hit-cap 10000 --watch-write 0x0:0x800000 --watch-write 0x1724c0:0x17250c --watch-write 0x165d9c:0x165e9c --watch-pc 0x80007640,0x80007670 --pc-hist-watch 1 --pc-hist-phase 0x00000280:320 --pc-hist-phase 0x0066A500:640 --pc-hist-phase 0x00790400:1024 --pc-hist-phase 0x00690000:512 --pc-hist-phase 0x00690800:512 --pc-hist-phase 0x006AB400:512 --pc-hist-phase 0x006AB800:512 --pc-phase-log-width 0x6ab400:512 --phase-pointer-watch 2:0x400 --phase-snapshot-watch 1 --phase-snapshot-watch 2 --phase-origin-watch 1 --phase-origin-watch 2 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150 > scratch/agent/s4616_retail_writer_all_phases.log 2>&1
