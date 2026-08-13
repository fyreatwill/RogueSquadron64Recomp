# NEXT work unit (s867)

HYPOTHESIS-ID: m3-coalesce-entry-state

Run one 70-second retail-oracle phase-transition experiment. Preserve the
whole-RDRAM positive control, VI trace, retail ROM, and target watches; use the
documented eleven-Start schedule through the hangar boundary:
`6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start`.
Keep `--detail-watch 1 --detail-watch 2` enabled. Do not change emulated game
behavior or add a mitigation.

Competing hypotheses:

- H-init-writer: target writes remain limited to boot/heap initialization PCs
  because the run stays in width 320.
- H-runtime-writer: a later phase is reached and a later gameplay/heap-
  maintenance PC writes the state.
- H-control-invalid: whole-RDRAM or VI control fails, making attribution
  unevaluable.

Discriminating measurement: whole-RDRAM and VI controls must fire and the VI
trace must show a post-320 transition (ideally width 1024 or 512). A target PC
after that transition selects H-runtime-writer; target PCs confined to boot
with no transition select H-init-writer only for the observed phase; failed
controls or no transition leave the writer question unevaluable. Counts without
PCs are unevaluable.

Exact command:

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --secs 70 --watch-write 0x0:0x800000 \
  --watch-write 0x1163E4:0x1163F0 --watch-write 0x10FF18:0x10FF1C \
  --vi-trace \
  --press '6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' \
  --detail-watch 1 --detail-watch 2 2>&1 | tee scratch/agent/oracle_s867_phase.log
```
