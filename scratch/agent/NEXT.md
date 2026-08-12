# NEXT work unit (after s707: phase-qualified retail recovery-cell watch under Rice)

HYPOTHESIS-ID: m3-oracle-recovery-cell-origin

Use the phase-qualified Rice video arm to run the retail ROM through the
hangar and watch physical `0x0076B768:0x0076B76C`, with a simultaneous
whole-RDRAM `0:0x800000` positive control. Keep debugger=1/emulator=0,
`--vi-poll`, `--vi-trace`, `--pif-trace`, separate config, and the established
6..56-second eleven-Start schedule. Do not alter the recomp E9 tracer.

## Competing hypotheses

- **H-retail-writes-recovery-cell:** Rice reaches `0x006ABxxx` and the narrow
  physical watch records one or more game writes with a guest PC.
- **H-cell-is-runtime-only:** Rice reaches `0x006ABxxx`, the whole-RDRAM and
  PIF/VI controls are live, but the narrow watch remains zero.
- **H-rice-phase-control-fails:** Rice fails to reach 640/1024/`0x006ABxxx`;
  the narrow zero is unqualified and no origin claim follows.

## Discriminating measurement

The positive controls are Rice's visible 320→640→1024→512/`0x006ABxxx` phase
trace, eleven PIF-observed Starts, and a high whole-RDRAM watch count in the
same run. A narrow hit supports H-retail-writes-recovery-cell; a narrow zero
with every control live supports H-cell-is-runtime-only (single source until
corroborated); missing phase control proves only H-rice-phase-control-fails.

## Commands

    tools/oracle/build.sh
    mkdir -p scratch/agent/s708_oracle_recovery_watch/rice
    tools/oracle/build/rs64_oracle \
      --core "$HOME/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib" \
      --rom "$HOME/Documents/Tools/rogue_squadron64/rogue_squadron.z64" \
      --secs 70 --configdir scratch/agent/s708_oracle_recovery_watch/rice \
      --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
      --oracle-debugger 1 --oracle-emulator 0 --vi-poll --vi-trace --pif-trace \
      --watch-write 0:0x800000 --watch-write 0x76B768:0x76B76C \
      --press '6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' \
      > scratch/agent/s708_oracle_recovery_watch/rice/run.log 2>&1
