#!/bin/zsh
# s7494 class ES: retail ground truth for a heap block vs the boot 640x480 image region.
# Runs the retail ROM under the oracle (Rice video, undriven boot), watching CPU writes to a physical
# block plus rs_free / freeManifestSegmentAssets / runIdleFramesAndLoadSaveData / buildAndRegisterDefaultMaterial
# executions, and prints who frees the block, when, and when the 640 phase starts.
# Usage: tools/s7494_es_oracle.zsh [BLOCK_LO BLOCK_HI SECS]   (default 0x787810 0x78E440 12)
set -u
LO=${1:-0x787810}; HI=${2:-0x78E440}; SECS=${3:-12}
O=tools/oracle/build/rs64_oracle
C=$HOME/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
R=$HOME/Documents/Tools/rogue_squadron64/rogue_squadron.z64
V=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
OUT=scratch/s7494/es_oracle_$$.log; mkdir -p scratch/s7494
$O --core $C --rom $R --video $V --secs $SECS --hit-cap 3000 --vi-trace --watch-write $LO:$HI \
  --watch-pc 0x80004994 --watch-pc 0x8006D900 --watch-pc 0x80017b88 --watch-pc 0x80001c98 > $OUT 2>&1 || exit 3
VLO=$(printf '0x%x' $(( LO | 0x80000000 )))
grep -E 'watch (write|pc)' $OUT
grep '^\[vi\].*WIDTH' $OUT | head -4
echo "-- exec rows (not rs_free):"
grep '^\[hit\] x' $OUT | grep -v 'pc=0x80001c98' | awk '{for(i=1;i<=NF;i++) if($i~/^(pc=|t=|prev_pc|a0=|a1=|width|origin)/) printf "%s ",$i; print ""}' | head -20
echo "-- rs_free of the block (a0=$VLO):"
grep '^\[hit\] x.*pc=0x80001c98' $OUT | grep -i "a0=$VLO" | awk '{for(i=1;i<=NF;i++) if($i~/^(t=|prev_pc|a0=)/) printf "%s ",$i; print ""}'
echo "-- CPU writers of the block:"
grep '^\[hit\] w' $OUT | awk '{print $4,$6}' | sort | uniq -c
nw=$(grep -c '^\[hit\] w' $OUT); [[ $nw -gt 0 ]] || { echo "CONTROL FAIL: no block writes"; exit 3; }
echo "log=$OUT"
