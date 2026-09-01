# NEXT work unit — retail caller-to-entry zero-fill join

HYPOTHESIS-ID: m5-image-task-zero-fill-contract

Session 3574 established that the retail entry watch is live in the target
bucket, but the bounded oracle output did not retain the specific caller row.
The port target entry remains `dst=0x801797B0`, `fill=0`, `len=0x298`.

Competing hypotheses and discriminator:

- H-ZeroFillParity: retail caller `0x8008F2CC` reaches `0x800078E0` with the
  same tuple and before the first target source DMA.
- H-ZeroFillPortInput: the caller-to-entry tuple differs across systems.
- H-ZeroFillPortOrdering: tuple matches, but caller/entry versus first source
  DMA ordering differs.

The single table must watch retail caller `0x8008F2CC` and entry `0x800078E0`
in the same run, phase-gated with `--pc-phase-log-width 0x006AB400:512`, while
retaining whole-RDRAM and source-span watches. Use `--detail-watch 2` so the
entry rows are not lost to the general hit cap. Matching tuple and ordering
select H-ZeroFillParity; a tuple difference selects H-ZeroFillPortInput; a
matching tuple with an ordering difference selects H-ZeroFillPortOrdering. A
missing whole-RDRAM, source-span, or phase control makes the result
unevaluable.

Run from the repo root:

    env tools/oracle/build/rs64_oracle --core "$HOME/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib" --rom ./rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 60 --press 3:start,7:start,11:start,15:a,30:start,45:start --hold-ms 150 --watch-write 0x0:0x800000 --watch-write 0x1797B0:0x179930 --watch-pc 0x800078E0,0x8008F2CC --pc-phase-log-width 0x006AB400:512 --vi-trace --detail-watch 2 --hit-cap 16

Retain the already-built target-valid port arm only as the paired reference;
do not add another port instrument or change runtime behavior unless the
oracle caller-to-entry table requires a new field.
