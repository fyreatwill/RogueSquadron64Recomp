# NEXT work unit (after s708: qualified retail recovery-cell zero)

HYPOTHESIS-ID: m3-oracle-recovery-cell-origin

Run one Rice-qualified retail arm through the hangar with three simultaneous
watches: whole RDRAM, the exact recovery cell `0x76B768:0x76B76C`, and its
surrounding physical page `0x76B000:0x76C000`. Keep debugger=1/emulator=0,
`--vi-poll`, `--vi-trace`, `--pif-trace`, a fresh config, and the established
6..56-second eleven-Start schedule. Do not alter the recomp E9 tracer.

## Competing hypotheses

- **H-retail-writes-recovery-cell:** Rice reaches `0x006ABxxx` and the narrow
  physical watch records one or more game writes with a guest PC.
- **H-cell-is-runtime-only:** Rice reaches `0x006ABxxx`, the page and
  whole-RDRAM controls write, but the narrow watch remains zero.
- **H-region-quiescent:** Rice reaches `0x006ABxxx`, but both the target and
  surrounding-page watches remain zero; the s708 target null cannot classify
  ownership.
- **H-rice-phase-control-fails:** Rice fails to reach 640/1024/`0x006ABxxx`;
  every narrow/page zero is unqualified and no origin claim follows.

## Discriminating measurement

The positive controls are Rice's visible 320→640→1024→512/`0x006ABxxx` phase
trace, eleven PIF-observed Starts, a high whole-RDRAM count, and at least one
surrounding-page hit in the same run. A narrow hit supports
H-retail-writes-recovery-cell; narrow zero plus page hits supports
H-cell-is-runtime-only; page zero yields H-region-quiescent; missing phase
control proves only H-rice-phase-control-fails.

## Commands

    tools/oracle/build.sh
    mkdir -p scratch/agent/s709_oracle_recovery_page_watch/rice
    tools/oracle/build/rs64_oracle \
      --core "$HOME/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib" \
      --rom "$HOME/Documents/Tools/rogue_squadron64/rogue_squadron.z64" \
      --secs 70 --configdir scratch/agent/s709_oracle_recovery_page_watch/rice \
      --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
      --oracle-debugger 1 --oracle-emulator 0 --vi-poll --vi-trace --pif-trace \
      --watch-write 0:0x800000 --watch-write 0x76B000:0x76C000 \
      --watch-write 0x76B768:0x76B76C \
      --press '6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' \
      > scratch/agent/s709_oracle_recovery_page_watch/rice/run.log 2>&1
