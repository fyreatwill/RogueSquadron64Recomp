#!/bin/zsh
set -u
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
C=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
R=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
RSP=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/projects/unix/mupen64plus-rsp-cxd4.dylib
D=scratch/agent/s5129_m4_mid_acc
mkdir -p "$D"
export RS64_RSP_DUMP="$D/rsp.dump"
export RS64_RSP_MID_DUMP="$D/mid.dump"
export RS64_RDP_BIN="$D/rdp.bin"
export RS64_RDP_LOG="$D/rdp.log"
export RS64_RDP_BIN_WIDTH=512
tools/oracle/build/rs64_oracle --core "$C" --rom "$R" --secs 75 --vi-trace --rsp "$RSP" \
  --video tools/oracle/rdplog/rdplog.dylib \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start \
  > "$D/oracle.log" 2>&1 &
P=$!
( sleep 165; kill -9 "$P" 2>/dev/null ) &
W=$!
wait "$P"
RC=$?
kill "$W" 2>/dev/null
grep -E 'WIDTH' "$D/oracle.log" || true
echo "rc=$RC"
echo "rdp_rows=$(grep -c '^\\[rdp\\]' "$D/rdp.log" 2>/dev/null || true)"
echo "task_dump_bytes=$(wc -c < "$D/rsp.dump" 2>/dev/null || echo 0)"
echo "mid_dump_bytes=$(wc -c < "$D/mid.dump" 2>/dev/null || echo 0)"
exit "$RC"
