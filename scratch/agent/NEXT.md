# NEXT work unit — retail observed zero-fill predecessor join

HYPOTHESIS-ID: m5-image-task-zero-fill-contract

Session 3575 established that the retail entry watch is live in the target
bucket, but presumed caller `0x8008F2CC` itself has zero hits. The observed
entry predecessors are `0x800C825C` and `0x800052C4`.
The port target entry remains `dst=0x801797B0`, `fill=0`, `len=0x298`.

Competing hypotheses and discriminator:

- H-ObservedEdgeParity: an observed retail predecessor reaches `0x800078E0`
  with the port tuple before the first target source DMA.
- H-ObservedEdgeInput: an observed predecessor reaches the entry, but its
  argument tuple differs from the port tuple.
- H-ObservedEdgeOrdering: tuple matches, but predecessor/entry versus first
  source DMA ordering differs.

The single table must watch retail predecessors `0x800C825C,0x800052C4` and
entry `0x800078E0` in the same run, phase-gated with
`--pc-phase-log-width 0x006AB400:512`, while retaining whole-RDRAM and
source-span watches. Use `--detail-watch 2`. Match each predecessor's
arguments to the port tuple and order it against the first source DMA.
Matching tuple/order selects H-ObservedEdgeParity; a tuple difference selects
H-ObservedEdgeInput; a matching tuple with ordering difference selects
H-ObservedEdgeOrdering. Missing any control is unevaluable.

Run from the repo root:

    env tools/oracle/build/rs64_oracle --core "$HOME/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib" --rom ./rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 60 --press 3:start,7:start,11:start,15:a,30:start,45:start --hold-ms 150 --watch-write 0x0:0x800000 --watch-write 0x1797B0:0x179930 --watch-pc 0x800078E0,0x800C825C,0x800052C4 --pc-phase-log-width 0x006AB400:512 --vi-trace --detail-watch 2 --hit-cap 16

Retain the already-built target-valid port arm only as the paired reference;
do not add another port instrument or change runtime behavior unless the
oracle caller-to-entry table requires a new field.
