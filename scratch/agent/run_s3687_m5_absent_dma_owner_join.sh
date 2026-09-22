#!/bin/zsh
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/scratch/agent/s3687_m5_absent_dma_owner_join"
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
stage_re = re.compile(r'\[audtask-image-stage-row\].*ordinal=(\d+).*row=(\d+).*phase=(\d+).*width=(\d+).*origin=0x([0-9A-Fa-f]+).*stage=(\d+).*event=(\d+).*dest=0x([0-9A-Fa-f]+).*len=0x([0-9A-Fa-f]+).*fnv=([0-9A-Fa-f]+).*nz=(\d+).*task_data_ptr=0x([0-9A-Fa-f]+).*task_generation=(\d+)')
dma_re = re.compile(r'\[audtask-dma-row\].*phase=(\d+).*width=(\d+).*origin=0x([0-9A-Fa-f]+).*data_ptr=0x([0-9A-Fa-f]+).*data_size=0x([0-9A-Fa-f]+).*source_fnv=([0-9A-Fa-f]+).*source_nz=(\d+)')
sources, stages, dmas = [], [], []
for lineno, line in enumerate(open(sys.argv[1], errors='replace')):
    m = src_re.search(line)
    if m: sources.append((lineno, m.groups())); continue
    m = stage_re.search(line)
    if m: stages.append((lineno, m.groups())); continue
    m = dma_re.search(line)
    if m: dmas.append((lineno, m.groups()))
def source(x):
    g=x[1]; return {'line':x[0], 'event':int(g[0]), 'phase':int(g[2]), 'width':int(g[3]), 'origin':int(g[4],16), 'ord':int(g[5]), 'route_row':int(g[6]), 'length':int(g[8],16), 'fnv':g[9].upper(), 'ptr':int(g[11],16), 'gen':int(g[12])}
def stage(x):
    g=x[1]; return {'line':x[0], 'ord':int(g[0]), 'route_row':int(g[1]), 'phase':int(g[2]), 'width':int(g[3]), 'origin':int(g[4],16), 'event':int(g[6]), 'ptr':int(g[11],16), 'gen':int(g[12])}
def dma(x):
    g=x[1]; return {'line':x[0], 'phase':int(g[0]), 'width':int(g[1]), 'origin':int(g[2],16), 'ptr':int(g[3],16), 'length':int(g[4],16), 'fnv':g[5].upper(), 'nz':int(g[6])}
sources=[source(x) for x in sources]; stages=[stage(x) for x in stages]; dmas=[dma(x) for x in dmas]
hs=[x for x in sources if x['phase']==5 and x['width']==512 and x['origin']==0x6AB400]
hst=[x for x in stages if x['phase']==5 and x['width']==512 and x['origin']==0x6AB400]
hd=[x for x in dmas if x['phase']==5 and x['width']==512 and x['origin']==0x6AB400]
by_ptr=collections.defaultdict(list)
for x in hst: by_ptr[x['ptr']].append(x)
classes=collections.Counter(); reports=[]
for s in hs:
    if any(x['gen']==s['gen'] for x in by_ptr[s['ptr']]): continue
    later=sorted((x for x in by_ptr[s['ptr']] if x['gen']>s['gen'] and (x['ord']>s['ord'] or (x['ord']==s['ord'] and x['route_row']>s['route_row']))), key=lambda x:(x['ord'],x['route_row'],x['line']))
    earlier=sorted((x for x in by_ptr[s['ptr']] if x['gen']<=s['gen'] and x['line']<s['line']), key=lambda x:x['line'], reverse=True)
    target=later[0] if later else None
    candidates=[d for d in hd if d['ptr']==s['ptr']]
    target_dma=[d for d in candidates if target and s['line']<=d['line']<=target['line']]
    earlier_dma=[d for d in candidates if d['line']<s['line']]
    if target and target_dma and earlier_dma: label='pointer-only-ambiguous'
    elif target and target_dma: label='later-route-pointer-only'
    elif earlier and earlier_dma: label='earlier-route-pointer-only'
    else: label='dma-identity-unavailable'
    classes[label]+=1
    if len(reports)<100: reports.append((label,s,target,target_dma[-1] if target_dma else (earlier_dma[-1] if earlier_dma else None)))
with open(sys.argv[2],'w') as f:
    f.write('hangar_sources=%d stage_rows=%d dma_rows=%d absent_classified=%d %s\n' % (len(hs),len(hst),len(hd),sum(classes.values()),dict(classes)))
    for label,s,t,d in reports:
        f.write('%s source_event=%d route=%d/%d gen=%d ptr=0x%X fnv=%s' % (label,s['event'],s['ord'],s['route_row'],s['gen'],s['ptr'],s['fnv']))
        if t: f.write(' stage_event=%d stage_route=%d/%d stage_gen=%d' % (t['event'],t['ord'],t['route_row'],t['gen']))
        if d: f.write(' dma_line=%d dma_len=0x%X dma_nz=%d' % (d['line'],d['length'],d['nz']))
        f.write('\n')
PY
