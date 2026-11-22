#!/bin/zsh
set -u
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
C=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
R=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
source /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/tools/oracle/rsp_plugin.sh  # s7816: VU-fixed cxd4 by default
D=scratch/agent/s5354_retail_m4_pcs
mkdir -p "$D"
export RS64_RSP_MID_STRIDE=1
# 0x88 = positive-control PC seen in s5335; 0x12C/0x7F0 = mapped port PCs
export RS64_RSP_MID_PCS=0x12C,0x7F0
export RS64_RSP_DUMP="$D/rsp.dump"
export RS64_RSP_MID_DUMP="$D/mid.dump"
tools/oracle/build/rs64_oracle --core "$C" --rom "$R" --secs 75 --vi-trace --rsp "$RSP" \
  --video tools/oracle/rdplog/rdplog.dylib \
  --watch-write 0x0:0x800000 --hit-cap 10000 \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > "$D/oracle.log" 2>&1 &
P=$!
( sleep 200; kill -9 "$P" 2>/dev/null ) &
W=$!
wait "$P"; RC=$?
kill "$W" 2>/dev/null
grep -E -i 'WIDTH|whole|hits|callbacks' "$D/oracle.log" | head -20
echo "rc=$RC mid_bytes=$(wc -c < "$D/mid.dump" 2>/dev/null || echo 0) rsd_bytes=$(wc -c < "$D/rsp.dump" 2>/dev/null || echo 0)"
