#!/bin/zsh
set -u
set -o pipefail

ROOT="${0:A:h:h:h}"
OUT="$ROOT/scratch/agent/s5183_retail_entry_function_gate"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
PRESS='6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start,66:a,73:a,80:start,90:a,100:start,110:a,120:start,130:a,140:start,150:a,160:start,170:a,180:start,190:a,200:start,210:a,220:start,230:a,240:start,250:a'

mkdir -p "$OUT"
if [[ ! -x "$ORACLE" || ! -f "$CORE" || ! -f "$ROM" || ! -f "$VIDEO" ]]; then
    print -r -- 'result=unevaluable prerequisite-failure' | tee "$OUT/summary.txt"
    exit 2
fi

cd "$ROOT"
env "$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 270 \
    --watch-write 0x0:0x800000 \
    --watch-pc 0x8008FAAC,0x800903F0,0x80090C80,0x800921E8 \
    --watch-pc-range 0x8008FFAC:0x80090640 \
    --pc-phase-log-width 0x00690400:512 \
    --pc-phase-log-width 0x00620400:512 \
    --vi-trace --first-watch 1 --hit-cap 30000 \
    --press "$PRESS" --hold-ms 150 > "$OUT/retail.log" 2>&1

LC_ALL=C awk '
BEGIN { c=ma=mb=e=s=w=0 }
/positive-control threshold reached/ { c++ }
/origin=0x00690400 width=512/ { ma++ }
/origin=0x00620400 width=512/ { mb++ }
/pc=0x8008faac/ { e++ }
/pc=0x800903f0/ { s++ }
/pc=0x80090c80|pc=0x800921e8/ { w++ }
END {
    if (c == 0 || ma == 0 || mb == 0) result="unevaluable"
    else if (e == 0) result="function-absent"
    else if (s == 0) result="branch-diff"
    else result="site-live"
    printf "result=%s control=%d mission_690400=%d mission_620400=%d entry_8008FAAC=%d site_800903F0=%d adjacent_writers=%d\n", result,c,ma,mb,e,s,w
}' "$OUT/retail.log" | tee "$OUT/summary.txt"
