# NEXT work unit (s866)

HYPOTHESIS-ID: m3-coalesce-entry-state

Run one extended retail-oracle writer-PC experiment. Preserve the whole-RDRAM
positive control, VI trace, retail ROM, and repeated-Start schedule from s865;
run for 180 seconds and keep `--detail-watch 1 --detail-watch 2` enabled. Do
not change emulated game behavior or add a mitigation.

Competing hypotheses:

- H-init-writer: target writes remain limited to boot/heap initialization PCs.
- H-runtime-writer: a later gameplay/heap-maintenance PC writes the state.
- H-control-invalid: whole-RDRAM or VI control fails, making target attribution
  unevaluable.

Discriminating measurement: whole-RDRAM and VI controls must fire in the same
run, and every target hit must print its guest PC. A target PC after a
documented phase/VI transition selects H-runtime-writer; target PCs confined to
boot support H-init-writer for the observed run; failed controls select
H-control-invalid. Counts without PCs are unevaluable.

Exact command:

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --secs 180 --watch-write 0x0:0x800000 \
  --watch-write 0x1163E4:0x1163F0 --watch-write 0x10FF18:0x10FF1C \
  --vi-trace \
  --press '6:start,11:start,16:start,21:start,26:start' \
  --detail-watch 1 --detail-watch 2 2>&1 | tee scratch/agent/oracle_s866_writer.log
```
