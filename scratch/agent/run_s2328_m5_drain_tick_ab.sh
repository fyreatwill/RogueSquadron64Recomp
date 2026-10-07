#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2328_m5_drain_tick_ab}
OUT="$ROOT/scratch/agent/$TAG"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
ORACLE_CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ORACLE_ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
ORACLE_VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
WINCTL="$BUILD/winctl"
mkdir -p "$OUT"

if [[ ! -x "$ORACLE" || ! -f "$ORACLE_CORE" || ! -f "$ORACLE_ROM" || ! -f "$ORACLE_VIDEO" ]]; then
    print "ERROR: retail oracle prerequisites are missing" > "$OUT/driver.log"
    exit 2
fi
if [[ ! -x "$BUILD/RogueSquadron64Recomp" || ! -f "$BUILD/rogue_squadron.z64" || ! -x "$WINCTL" ]]; then
    print "ERROR: build/ control prerequisites are missing" > "$OUT/driver.log"
    exit 3
fi

cd "$ROOT" || exit 4
PRESS=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
PORT_PRESS=(6 11 16 21 26 31 36 41 46 51 56)
COMMON=(
    ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1
    ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
    ROGUESQ_M5_C88_VALUE=0 ROGUESQ_STUB_MISSING_FUNCS=1
    ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1
    ROGUESQ_LOG_AUDIO_DRAIN=1
    ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_PCM_BOUNDARY=1
    ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_M5_B40_ROUTE=1
    ROGUESQ_LOG_M5_ROUTE_STATE=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1
    ROGUESQ_LOG_VI_CALLERS=1 ROGUESQ_LOG_FILTER_VOICE_AUDIT=1
    ROGUESQ_LOG_M5_KEYON_CENSUS=1 ROGUESQ_LOG_M5_KEYON_PORT_TUPLES=1
)

print "oracle_start" > "$OUT/driver.log"
env "$ORACLE" \
    --core "$ORACLE_CORE" --rom "$ORACLE_ROM" --video "$ORACLE_VIDEO" \
    --secs 75 \
    --watch-write 0x0:0x800000 \
    --watch-write 0x166000:0x16A000 \
    --watch-write 0x141AD0:0x141AF0 \
    --watch-write 0xA0F50:0xA0F54 \
    --watch-write 0x1498A:0x1498C \
    --watch-write 0x154620:0x154624 \
    --hit-cap 40 \
    --watch-pc 0x8008EB8C,0x8008EBBC,0x80094648 \
    --pc-phase-log-width 0x006AB400:512 \
    --pc-hist-phase 0x006AB400:512 --pc-hist-watch 2 \
    --post-value-watch 2 \
    --post-value-pc 0x8008EB8C,0x8008EBBC,0x80094648 \
    --vi-trace --press "$PRESS" > "$OUT/oracle.log" 2>&1
oracle_rc=$?

oracle_gate=1
(( oracle_rc == 0 )) || oracle_gate=0
for marker in \
    '[oracle] watch write [0x00000000,0x00800000):' \
    '[oracle] watch write [0x00166000,0x0016a000):' \
    '[oracle] watch write [0x00141ad0,0x00141af0):' \
    '[oracle] watch write [0x000a0f50,0x000a0f54):' \
    '[oracle] watch write [0x00154620,0x00154624):'; do
    grep -a -F "$marker" "$OUT/oracle.log" | grep -Eq '[1-9][0-9]* hit' || oracle_gate=0
done
grep -a -F '[oracle] watch write [0x0001498a,0x0001498c): 0 hit' "$OUT/oracle.log" >/dev/null || oracle_gate=0
grep -a -F 'origin=0x00790400' "$OUT/oracle.log" >/dev/null || oracle_gate=0
grep -a -F 'origin=0x006ab400' "$OUT/oracle.log" >/dev/null || oracle_gate=0
grep -a -F '[oracle] writer-pc-phase origin=0x006ab400 width=512 watch=2 range=' "$OUT/oracle.log" >/dev/null || oracle_gate=0
for pc in 8008eb8c 8008ebbc 80094648; do
    grep -a -F "[oracle] writer-pc pc=0x$pc n=" "$OUT/oracle.log" >/dev/null || oracle_gate=0
done
print "oracle_rc=$oracle_rc oracle_controls=$oracle_gate" | tee -a "$OUT/driver.log"
grep -a -E '^\[oracle\] (done:|watch write \[0x00000000|watch write \[0x00166000|watch write \[0x00141ad0|watch write \[0x000a0f50|watch write \[0x0001498a|watch write \[0x00154620|writer-pc-phase|writer-pc pc=)' "$OUT/oracle.log" | tail -40 >> "$OUT/driver.log" || true
if (( oracle_gate == 0 )); then
    print "verdict=H-CoverageInvalid oracle_controls=0" | tee -a "$OUT/driver.log"
    exit 5
fi

GAME_PID=""
KEY_PID=""
cleanup_game() {
    local pid="$1"
    local keypid="$2"
    if [[ -n "$keypid" ]] && kill -0 "$keypid" 2>/dev/null; then kill -9 "$keypid" 2>/dev/null || true; fi
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
        /usr/bin/pkill -KILL -P "$pid" 2>/dev/null || true
        kill -9 "$pid" 2>/dev/null || true
    fi
}
trap 'cleanup_game "$GAME_PID" "$KEY_PID"' EXIT INT TERM

raise_game() {
    local pid="$1"
    "$WINCTL" activate "$pid" >/dev/null 2>&1 || true
    /usr/bin/osascript -e "tell application \"System Events\" to set frontmost of first application process whose unix id is $pid to true" >/dev/null 2>&1 || true
}

wait_for_window() {
    local pid="$1"
    local deadline=$((SECONDS + 30))
    local wid=""
    while (( SECONDS < deadline )); do
        if ! kill -0 "$pid" 2>/dev/null; then return 1; fi
        wid="$($WINCTL find "$pid" 2>/dev/null || true)"
        if [[ -n "$wid" ]]; then
            print "window pid=$pid id=${wid%% *}" >> "$OUT/driver.log"
            return 0
        fi
        sleep 1
    done
    return 1
}

send_keys() {
    local name="$1"
    local pid="$2"
    local previous=0
    print "port_input=$name schedule=eleven-start keycode=36" >> "$OUT/driver.log"
    for at in $PORT_PRESS; do
        sleep "$((at - previous))"
        previous=$at
        if ! kill -0 "$pid" 2>/dev/null; then return 0; fi
        raise_game "$pid"
        "$WINCTL" key "$pid" 36 >/dev/null 2>&1 || true
        print "port_input=$name start_at_process_s=$at keycode=36" >> "$OUT/driver.log"
    done
}

run_arm() {
    local name="$1"
    local audio="$2"
    local tick="$3"
    local log="$OUT/$name.log"
    ( cd "$BUILD" && exec env ${=COMMON} ROGUESQ_AUDIO_UCODE="$audio" ROGUESQ_DRAIN_INLOOP_TICK="$tick" ./RogueSquadron64Recomp ) > "$log" 2>&1 &
    GAME_PID=$!
    print "${name}_pid=$GAME_PID audio=$audio drain_tick=$tick" | tee -a "$OUT/driver.log"
    local window_ok=0
    wait_for_window "$GAME_PID" && window_ok=1
    if (( window_ok )); then
        send_keys "$name" "$GAME_PID" &
        KEY_PID=$!
    else
        print "${name}_window=missing" | tee -a "$OUT/driver.log"
    fi
    local hangar=0
    local deadline=$((SECONDS + 240))
    while (( SECONDS < deadline )); do
        if grep -a -q '^\[phase\] vi_width=512 .*origin=0x006AB400' "$log"; then
            hangar=1
            print "${name}_hangar=observed; retaining_15s" | tee -a "$OUT/driver.log"
            sleep 15
            break
        fi
        if ! kill -0 "$GAME_PID" 2>/dev/null; then break; fi
        sleep 1
    done
    (( hangar )) || print "${name}_hangar=missing" | tee -a "$OUT/driver.log"
    cleanup_game "$GAME_PID" "$KEY_PID"
    wait "$KEY_PID" 2>/dev/null || true
    wait "$GAME_PID" 2>/dev/null
    local rc=$?
    print "${name}_rc=$rc ${name}_hangar=$hangar" | tee -a "$OUT/driver.log"
    GAME_PID=""
    KEY_PID=""
}

print "arms=stub,image_tick_on,image_tick_off; each uses eleven-start schedule" | tee -a "$OUT/driver.log"
if [[ "${DRAIN_TICK_ORDER:-legacy}" == "image-off-first" ]]; then
    run_arm image_tick_off 1 0
    run_arm image_tick_on 1 1
else
    run_arm stub 0 1
    run_arm image_tick_on 1 1
    run_arm image_tick_off 1 0
fi

for name in stub image_tick_on image_tick_off; do
    log="$OUT/$name.log"
    print -- "--- $name controls ---" >> "$OUT/driver.log"
    for marker in \
        '[vi-callers-control]' '[filter-voice-audit-control]' '[audtask-dispatch]' \
        '[audtask-abi]' '[audtask-dma-row]' '[audtask-dma-range]' \
        '[audtask-image-stage-row]' '[audtask-image-join]' '[audtask-join]' \
        '[audio-return]' '[audio-sp-route] edge=guest-receive' '[m5-audio-join-control]' \
        '[m5-audio-event]' '[drain-inloop-gate]' '[drain-tick]' '[slot-alloc]' '[slot-byte]' '[slot-sb]' '[init-desc]' \
        '[keyon-w40]' '[pcm-boundary-source]' '[pcm-boundary-consumer]' '[CRASH]' '[ABORT]'; do
        print "$marker=$(grep -a -F -c "$marker" "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
    done
    print "title=$(grep -a -c '^\[phase\] vi_width=1024 .*origin=0x00790400' "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
    print "hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$log" 2>/dev/null || true)" >> "$OUT/driver.log"
done

python3 - "$OUT" "$OUT/drain-tick-table.tsv" "$OUT/drain-tick-summary.tsv" <<'PY' | tee -a "$OUT/driver.log"
import re
import sys
from collections import Counter

out_dir, table_path, summary_path = sys.argv[1:]
kv = re.compile(r'([^=\s]+)=([^\s]+)')
arms = [("image_tick_on", "1"), ("image_tick_off", "0")]

def integer(value, default=0):
    try:
        return int(value, 0)
    except (TypeError, ValueError):
        return default

def scope(row):
    return (integer(row.get("phase")), integer(row.get("width")), integer(row.get("origin")))

def parse_log(name, tick):
    stages, joins, tasks, events, drain_ticks = [], [], [], [], []
    phase = {"phase": "", "width": "", "origin": ""}
    path = f"{out_dir}/{name}.log"
    with open(path, errors="replace") as stream:
        for seq, line in enumerate(stream, 1):
            parts = line.split()
            tag = parts[0] if parts else ""
            fields = dict(kv.findall(line))
            if tag == "[phase]" and "vi_width" in fields and "origin" in fields:
                phase = {"phase": fields.get("phase", ""), "width": fields.get("vi_width", ""), "origin": fields.get("origin", "")}
            if tag in ("[audtask-image-stage-row]", "[audtask-image-join]", "[audtask-join]", "[m5-audio-event]"):
                for key in ("phase", "width", "origin"):
                    if key not in fields and phase.get(key) != "":
                        fields[key] = phase[key]
            row = {"seq": seq, "tick": tick, "arm_name": name, **fields}
            if tag == "[audtask-image-stage-row]":
                stages.append(row)
            elif tag == "[audtask-image-join]":
                joins.append(row)
            elif tag == "[audtask-join]":
                tasks.append(row)
            elif tag == "[m5-audio-event]":
                events.append(row)
            elif tag == "[drain-tick]":
                drain_ticks.append(row)
    stages = [s for s in stages if integer(s.get("width")) == 512 and integer(s.get("origin")) == 0x6AB400 and integer(s.get("stage")) in (2, 3) and integer(s.get("nz")) > 0]
    stages.sort(key=lambda row: row["seq"])
    return stages, joins, tasks, events, drain_ticks

def same_scope(a, b):
    return scope(a) == scope(b)

def stage_join(stage, joins):
    rows = [j for j in joins if j.get("ordinal") == stage.get("ordinal") and j.get("row") == stage.get("row") and integer(j.get("stage_event")) == integer(stage.get("event"))]
    return rows[-1] if rows else {}

def task_for(stage, tasks):
    candidates = [t for t in tasks if same_scope(t, stage)]
    exact = [t for t in candidates if t.get("n") == stage.get("ordinal")]
    if exact:
        return min(exact, key=lambda t: abs(integer(t.get("begin")) - integer(stage.get("event"))))
    return min(candidates, key=lambda t: abs(integer(t.get("begin")) - integer(stage.get("event"))), default={})

def event_detail(stage, task, events):
    same = [e for e in events if e.get("ordinal") == stage.get("ordinal") and e.get("row") == stage.get("row") and same_scope(e, stage)]
    begin = integer(task.get("begin"))
    end = integer(task.get("end"))
    lo, hi = begin - 256, end + 256
    wrong = [e for e in events if lo <= integer(e.get("event")) <= hi and not (e.get("ordinal") == stage.get("ordinal") and e.get("row") == stage.get("row") and same_scope(e, stage))]
    return same, wrong

header = ["arm", "tick", "phase", "width", "origin", "ordinal", "row", "stage", "dest", "stage_event", "complete_event", "source_event", "consumer_event", "same_ordinal_pre", "same_ordinal_post", "earlier_tick_signature", "lifecycle_signature"]
rows = []
metrics = {}
for name, tick in arms:
    stages, joins, tasks, events, drain_ticks = parse_log(name, tick)
    arm_rows = []
    for stage in stages:
        join = stage_join(stage, joins)
        task = task_for(stage, tasks)
        same, wrong = event_detail(stage, task, events)
        pre = [e for e in same if integer(e.get("event")) < integer(stage.get("event"))]
        post = [e for e in same if integer(e.get("event")) > integer(stage.get("event"))]
        signature = ",".join(sorted(f"{e.get('kind','')}@{integer(e.get('event'))-integer(stage.get('event'))}" for e in same))
        prior_signature = ",".join(e.get("kind", "") for e in sorted(wrong, key=lambda e: integer(e.get("event"))))
        row = [name, tick, stage.get("phase", ""), stage.get("width", ""), stage.get("origin", ""), stage.get("ordinal", ""), stage.get("row", ""), stage.get("stage", ""), stage.get("dest", ""), stage.get("event", ""), join.get("complete_event", ""), join.get("source_event", ""), join.get("consumer_event", ""), len(pre), len(post), prior_signature, signature]
        rows.append(row)
        arm_rows.append((len(pre), len(post), prior_signature, signature, join.get("classification", "")))
    tick_gate_values = Counter(integer(row.get("gate"), -1) for row in drain_ticks)
    metrics[name] = {"stages": len(stages), "abi": sum(1 for _ in open(f"{out_dir}/{name}.log", errors="replace") if "[audtask-abi]" in _), "vi": sum(1 for _ in open(f"{out_dir}/{name}.log", errors="replace") if "[vi-callers-control]" in _), "join_control": sum(1 for _ in open(f"{out_dir}/{name}.log", errors="replace") if "[m5-audio-join-control]" in _), "sp_receive": sum(1 for _ in open(f"{out_dir}/{name}.log", errors="replace") if "[audio-sp-route] edge=guest-receive" in _), "pcm_source": sum(1 for _ in open(f"{out_dir}/{name}.log", errors="replace") if "[pcm-boundary-source]" in _), "pcm_consumer": sum(1 for _ in open(f"{out_dir}/{name}.log", errors="replace") if "[pcm-boundary-consumer]" in _), "lifecycle": sum(1 for _ in open(f"{out_dir}/{name}.log", errors="replace") if "[m5-audio-event]" in _), "gate": len(drain_ticks), "tick_rows": len(drain_ticks), "tick_gate_values": tick_gate_values, "hangar": sum(1 for _ in open(f"{out_dir}/{name}.log", errors="replace") if "[phase] vi_width=512" in _), "rows": arm_rows}

with open(table_path, "w") as out:
    out.write("\t".join(header) + "\n")
    for row in rows:
        out.write("\t".join(map(str, row)) + "\n")

def qualified(m):
    return all(m[key] > 0 for key in ("hangar", "abi", "vi", "stages", "join_control", "sp_receive", "pcm_source", "pcm_consumer", "tick_rows"))

on, off = metrics["image_tick_on"], metrics["image_tick_off"]
same_table = sorted(on["rows"]) == sorted(off["rows"]) and on["stages"] == off["stages"]
if not qualified(on):
    verdict = "H-CoverageInvalid"
elif not qualified(off):
    verdict = "H-DrainRequired"
elif not same_table:
    verdict = "H-DrainChangesOrdering"
else:
    verdict = "H-DrainRedundant"

with open(summary_path, "w") as out:
    out.write("arm\ttick\tqualified\thangar\tvi\tabi\tstages\tjoin_control\tsp_receive\tpcm_source\tpcm_consumer\tlifecycle\ttick_rows\ttick_gate_values\n")
    for name, tick in arms:
        m = metrics[name]
        out.write(f"{name}\t{tick}\t{int(qualified(m))}\t{m['hangar']}\t{m['vi']}\t{m['abi']}\t{m['stages']}\t{m['join_control']}\t{m['sp_receive']}\t{m['pcm_source']}\t{m['pcm_consumer']}\t{m['lifecycle']}\t{m['tick_rows']}\t{dict(m['tick_gate_values'])}\n")
print(f"verdict={verdict} on_qualified={int(qualified(on))} off_qualified={int(qualified(off))} on_stages={on['stages']} off_stages={off['stages']} same_table={int(same_table)}")
PY

sed -n '1,120p' "$OUT/drain-tick-summary.tsv" >> "$OUT/driver.log"
sed -n '1,100p' "$OUT/drain-tick-table.tsv" >> "$OUT/driver.log"
exit 0
