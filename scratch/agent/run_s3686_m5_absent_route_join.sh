#!/bin/zsh
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s3686_m5_absent_route_join"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
mkdir -p "$OUT"
bash "$ROOT/tools/oracle/build.sh" > "$OUT/oracle-build.log" 2>&1
cd "$ROOT/build" || exit 3
"$ORACLE" --core "$CORE" --rom "$ROM" --video "$VIDEO" --secs 55 \
  --watch-write 0x0:0x800000 --watch-write 0x1797B0:0x179930 \
  --watch-write 0x171CE0:0x171EE0 --watch-write 0x173B20:0x173D20 \
  --watch-write 0x171E70:0x171F70 --watch-write 0x173CB0:0x173DB0 \
  --watch-pc 0x80033FCC --pc-task-dump 0x80033FCC --pc-task-type 2 --pc-task-join \
  --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 \
  --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start \
  > "$OUT/oracle.log" 2>&1 & oracle=$!
env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_PHASE=1 \
  ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_LOG_M5_STAGE_CALLS=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 \
  ROGUESQ_LOG_M5_ROUTE_ORDER=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_M5_SOURCE_TRANSITION=1 \
  PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
  ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
  ROGUESQ_AUTOPILOT_STOP_WIDTH=512 ./RogueSquadron64Recomp > "$OUT/port.log" 2>&1 & port=$!
sleep 70
kill -KILL "$oracle" "$port" 2>/dev/null || true
wait "$oracle" 2>/dev/null || true
wait "$port" 2>/dev/null || true
grep -a -E '^\[(oracle|vi|watch|hit|pc-task-dump|gpr-ctl)' "$OUT/oracle.log" | tail -160 > "$OUT/oracle-summary.log" || true
grep -a -E '^\[(phase|m5-rsp-source-hook-control|m5-source-range-reader|audtask-image-stage|audtask-image-stage-row|audtask-abi|audtask-dma-row|audtask-image-dma-join|CRASH|ABORT)' "$OUT/port.log" | tail -320 > "$OUT/port-summary.log" || true
python3 - "$OUT/port.log" "$OUT/classification.txt" <<'PY'
import re, sys, collections
src_re = re.compile(r'\[m5-source-range-reader\].*event=(\d+).*row=(\d+).*phase=(\d+).*width=(\d+).*origin=0x([0-9A-Fa-f]+).*route_ordinal=(\d+).*route_row=(\d+).*dram=0x([0-9A-Fa-f]+).*len=0x([0-9A-Fa-f]+).*source_fnv=([0-9A-Fa-f]+).*source_nz=(\d+).*task_data_ptr=0x([0-9A-Fa-f]+).*task_generation=(\d+)')
stage_re = re.compile(r'\[audtask-image-stage-row\].*ordinal=(\d+).*row=(\d+).*phase=(\d+).*width=(\d+).*origin=0x([0-9A-Fa-f]+).*stage=(\d+).*event=(\d+).*dest=0x([0-9A-Fa-f]+).*task_data_ptr=0x([0-9A-Fa-f]+).*task_generation=(\d+)')
sources, stages = [], []
for line in open(sys.argv[1], errors='replace'):
    m = src_re.search(line)
    if m: sources.append(m.groups()); continue
    m = stage_re.search(line)
    if m: stages.append(m.groups())
def src(x):
    return {'event':int(x[0]), 'row':int(x[1]), 'phase':int(x[2]), 'width':int(x[3]), 'origin':int(x[4],16), 'ord':int(x[5]), 'route_row':int(x[6]), 'dram':int(x[7],16), 'length':int(x[8],16), 'fnv':x[9], 'nz':int(x[10]), 'ptr':int(x[11],16), 'gen':int(x[12])}
def st(x):
    return {'ord':int(x[0]), 'route_row':int(x[1]), 'phase':int(x[2]), 'width':int(x[3]), 'origin':int(x[4],16), 'stage':int(x[5]), 'event':int(x[6]), 'dest':int(x[7],16), 'ptr':int(x[8],16), 'gen':int(x[9])}
sources = [src(x) for x in sources]
stages = [st(x) for x in stages]
hangar = [x for x in sources if x['phase'] == 5 and x['width'] == 512 and x['origin'] == 0x6AB400]
hstages = [x for x in stages if x['phase'] == 5 and x['width'] == 512 and x['origin'] == 0x6AB400]
by_ptr = collections.defaultdict(list)
for x in hstages: by_ptr[x['ptr']].append(x)
absent, same_route, later_route, no_route = [], [], [], []
for s in hangar:
    if any(x['gen'] == s['gen'] and x['ptr'] == s['ptr'] for x in by_ptr[s['ptr']]): continue
    candidates = sorted((x for x in by_ptr[s['ptr']] if x['gen'] > s['gen']), key=lambda x: x['gen'])
    absent.append(s)
    if s['gen'] == 0 or not candidates:
        no_route.append((s, None))
        continue
    x = candidates[0]
    if x['ord'] == s['ord'] and x['route_row'] == s['route_row']: same_route.append((s, x))
    elif x['ord'] > s['ord'] or (x['ord'] == s['ord'] and x['route_row'] > s['route_row']): later_route.append((s, x))
    else: no_route.append((s, x))
with open(sys.argv[2], 'w') as f:
    f.write('hangar_sources=%d stage_rows=%d absent_with_later_stage=%d same_route=%d later_route=%d contradictory_route=%d\n' % (len(hangar), len(hstages), len(absent), len(same_route), len(later_route), len(no_route)))
    f.write('absent_source_events=%s\n' % [s['event'] for s in absent])
    for label, rows in [('same', same_route), ('later', later_route), ('contradictory', no_route)]:
        for s, x in rows[:80]:
            if x is None:
                f.write('%s source_event=%d source_row=%d source_route=%d/%d source_gen=%d dma=0x%X+0x%X source_fnv=%s stage=missing\n' % (label, s['event'], s['row'], s['ord'], s['route_row'], s['gen'], s['dram'], s['length'], s['fnv']))
            else:
                f.write('%s source_event=%d source_row=%d source_route=%d/%d source_gen=%d dma=0x%X+0x%X source_fnv=%s stage_event=%d stage_route=%d/%d stage_gen=%d stage_dest=0x%X\n' % (label, s['event'], s['row'], s['ord'], s['route_row'], s['gen'], s['dram'], s['length'], s['fnv'], x['event'], x['ord'], x['route_row'], x['gen'], x['dest']))
PY
