#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2344_m5_c88_writer_treatment}
OUT="$ROOT/scratch/agent/$TAG"
WINCTL="$BUILD/winctl"

[[ "$TAG" != .* ]] || exit 2
mkdir -p "$OUT"
if [[ ! -x "$BUILD/RogueSquadron64Recomp" || ! -f "$BUILD/rogue_squadron.z64" || ! -x "$WINCTL" ]]; then
    print "ERROR: build prerequisites are missing" > "$OUT/driver.log"
    exit 3
fi

cd "$ROOT" || exit 4
PORT_PRESS=(6 11 16 21 26 31 36 41 46 51 56)
COMMON=(
    ROGUESQ_LLE_FORCE=1
    ROGUESQ_SPIN_YIELD=1
    ROGUESQ_LLE_UNGATED=1
    ROGUESQ_LLE_SOLO=1
    ROGUESQ_M5_B40_VALUE=0
    ROGUESQ_STUB_MISSING_FUNCS=1
    ROGUESQ_LOG_PHASE=1
    ROGUESQ_LOG_AUDIO_RETURN=1
    ROGUESQ_LOG_M5_TASK_CONTRACT=1
    ROGUESQ_LOG_PCM_BOUNDARY=1
    ROGUESQ_LOG_M5_HOST_BOUNDARY=1
    ROGUESQ_LOG_M5_B40_ROUTE=1
    ROGUESQ_LOG_M5_B40_WRITER=1
    ROGUESQ_LOG_M5_B40_READ=1
    ROGUESQ_LOG_M5_C88_ROUTE_FINGERPRINT=1
    ROGUESQ_LOG_M5_ROUTE_STATE=1
    ROGUESQ_LOG_M5_GATE_CONTRACT=1
    ROGUESQ_LOG_AUDIOTICK_TRACE=1
    ROGUESQ_LOG_VI_CALLERS=1
    ROGUESQ_LOG_FILTER_VOICE_AUDIT=1
    ROGUESQ_LOG_INIT_VOICE_SAMPLE=1
    ROGUESQ_LOG_M5_KEYON_CENSUS=1
    ROGUESQ_LOG_M5_KEYON_PORT_TUPLES=1
)

PIDS=()
KEYPIDS=()
cleanup_game() {
    local pid="$1"
    local keypid="$2"
    if [[ -n "$keypid" ]] && kill -0 "$keypid" 2>/dev/null; then kill -9 "$keypid" 2>/dev/null || true; fi
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
        /usr/bin/pkill -KILL -P "$pid" 2>/dev/null || true
        kill -9 "$pid" 2>/dev/null || true
    fi
}
cleanup_all() {
    local i
    for (( i = 1; i <= ${#PIDS[@]}; ++i )); do
        cleanup_game "${PIDS[$i]}" "${KEYPIDS[$i]}"
    done
}
trap cleanup_all EXIT INT TERM

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
    local at
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
    local c88="$3"
    local log="$OUT/$name.log"
    (
        cd "$BUILD" || exit 2
        exec env ${=COMMON} ROGUESQ_AUDIO_UCODE="$audio" ROGUESQ_M5_C88_VALUE="$c88" ./RogueSquadron64Recomp
    ) > "$log" 2>&1 &
    local pid=$!
    local keypid=""
    PIDS+=("$pid")
    KEYPIDS+=("")
    print "${name}_pid=$pid audio=$audio c88=$c88" | tee -a "$OUT/driver.log"
    if wait_for_window "$pid"; then
        send_keys "$name" "$pid" &
        keypid=$!
        KEYPIDS[-1]="$keypid"
    else
        print "${name}_window=missing" | tee -a "$OUT/driver.log"
    fi

    local hangar=0
    local deadline=$((SECONDS + 240))
    while (( SECONDS < deadline )); do
        if grep -a -q '^\[phase\] vi_width=1024 .*origin=0x00790400' "$log" && \
           grep -a -q '^\[phase\] vi_width=512 .*origin=0x006AB400' "$log"; then
            hangar=1
            print "${name}_controls=passed title=1 hangar=1; retaining_15s" | tee -a "$OUT/driver.log"
            sleep 15
            break
        fi
        if ! kill -0 "$pid" 2>/dev/null; then break; fi
        sleep 1
    done
    (( hangar )) || print "${name}_controls=failed title_or_hangar_missing" | tee -a "$OUT/driver.log"
    cleanup_game "$pid" "$keypid"
    wait "$keypid" 2>/dev/null || true
    wait "$pid" 2>/dev/null
    local rc=$?
    print "${name}_rc=$rc controls=$hangar" | tee -a "$OUT/driver.log"
}

print "arms=stub_c0,stub_c1,image_c0,image_c1 sequential; eleven-start; B40=0" | tee "$OUT/driver.log"
run_arm stub_c0 0 0
run_arm stub_c1 0 1
run_arm image_c0 1 0
run_arm image_c1 1 1

python3 - "$OUT" "$OUT/c88-table.tsv" "$OUT/c88-summary.tsv" <<'PY' | tee -a "$OUT/driver.log"
import re
import sys
from collections import defaultdict
from pathlib import Path

out_dir, table_path, summary_path = map(Path, sys.argv[1:])
token = re.compile(r"([^=\s]+)=([^\s]+)")
arms = ("stub_c0", "stub_c1", "image_c0", "image_c1")
phases = ((1024, 0x790400), (512, 0x6AB400))

def num(value):
    try:
        return int(value, 0)
    except (TypeError, ValueError):
        return 0

def rows(path, tag):
    result = []
    with path.open(errors="replace") as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.startswith(tag):
                continue
            fields = dict(token.findall(line))
            fields["line"] = str(line_no)
            result.append(fields)
    return result

def count(path, needle):
    with path.open(errors="replace") as stream:
        return sum(needle in line for line in stream)

header = [
    "arm", "audio", "c88", "phase", "width", "origin", "writer_rows",
    "writer_stored_0", "writer_stored_nonzero", "branch_rows", "branch_lhs_0",
    "branch_lhs_nonzero", "branch_taken", "branch_fallthrough", "joined_writer_seq",
    "task_abi", "dma_rows", "dma_ranges", "guest_receive", "render_rows", "keyon_rows",
    "slot_events", "voice_events", "pcm_source", "pcm_consumer", "filter_audit",
    "controls", "crash", "abort",
]
table = [header]
summary = [["arm", "audio", "c88", "controls", "writer_rows", "stored_nonzero", "branch_rows", "branch_lhs_nonzero", "branch_fallthrough", "joined_writer_seq", "task_abi", "dma_rows", "dma_ranges", "guest_receive", "render_rows", "keyon_rows", "slot_events", "voice_events", "pcm_source", "pcm_consumer", "filter_audit", "crash", "abort"]]

for arm in arms:
    log = out_dir / f"{arm}.log"
    audio, c88 = (0, 0) if arm.startswith("stub") else (1, 0)
    if arm.endswith("_c1"):
        c88 = 1
    writer = rows(log, "[m5-b40-writer]")
    branch = [r for r in rows(log, "[m5-synth-pregate]") if r.get("source") == "0x80091468"]
    controls = int(
        count(log, "[vi-callers-control]") > 0 and
        count(log, "[filter-voice-audit-control]") > 0 and
        count(log, "[m5-audio-join-control]") > 0 and
        count(log, "[phase] vi_width=1024") > 0 and
        count(log, "[phase] vi_width=512") > 0
    )
    for width, origin in phases:
        w = [r for r in writer if num(r.get("width")) == width and num(r.get("origin")) == origin]
        b = [r for r in branch if num(r.get("width")) == width and num(r.get("origin")) == origin]
        joined = [r for r in b if num(r.get("writer_seq")) > 0]
        values = [num(r.get("stored")) for r in w]
        lhs = [num(r.get("lhs")) for r in b]
        taken = [num(r.get("taken")) for r in b]
        def c(needle): return count(log, needle)
        row = [
            arm, str(audio), str(c88), "target", str(width), f"0x{origin:06X}", str(len(w)),
            str(sum(v == 0 for v in values)), str(sum(v != 0 for v in values)), str(len(b)),
            str(sum(v == 0 for v in lhs)), str(sum(v != 0 for v in lhs)), str(sum(v != 0 for v in taken)),
            str(sum(v == 0 for v in taken)), str(len(joined)), str(c("[audtask-abi]")),
            str(c("[audtask-dma-row]")), str(c("[audtask-dma-range]")),
            str(c("[audio-sp-route] edge=guest-receive")), str(c("[audtask-image-stage-row]")),
            str(c("[m5-keyon-")), str(c("[m5-audio-event] kind=slot")),
            str(c("[m5-audio-event] kind=voice")), str(c("[pcm-boundary-source]")),
            str(c("[pcm-boundary-consumer]")), str(c("[filter-voice-audit]")), str(controls),
            str(c("[CRASH]")), str(c("[ABORT]")),
        ]
        table.append(row)
    w_all = [r for r in writer if num(r.get("stored")) != 0]
    srow = [
        arm, str(audio), str(c88), str(controls), str(len(writer)), str(len(w_all)), str(len(branch)),
        str(sum(num(r.get("lhs")) != 0 for r in branch)),
        str(sum(num(r.get("taken")) == 0 for r in branch)),
        str(sum(num(r.get("writer_seq")) > 0 for r in branch)),
        str(count(log, "[audtask-abi]")), str(count(log, "[audtask-dma-row]")),
        str(count(log, "[audtask-dma-range]")), str(count(log, "[audio-sp-route] edge=guest-receive")),
        str(count(log, "[audtask-image-stage-row]")), str(count(log, "[m5-keyon-")),
        str(count(log, "[m5-audio-event] kind=slot")), str(count(log, "[m5-audio-event] kind=voice")),
        str(count(log, "[pcm-boundary-source]")), str(count(log, "[pcm-boundary-consumer]")),
        str(count(log, "[filter-voice-audit]")), str(count(log, "[CRASH]")), str(count(log, "[ABORT]")),
    ]
    summary.append(srow)

for path, data in ((table_path, table), (summary_path, summary)):
    path.write_text("\n".join("\t".join(row) for row in data) + "\n")

print("c88_summary")
for row in summary[1:]:
    print(" ".join(f"{key}={value}" for key, value in zip(summary[0], row)))

qualified = all(row[3] == "1" for row in summary[1:])
if not qualified:
    print("verdict=H-CoverageInvalid missing same-run controls")
    raise SystemExit(5)

by_arm = {row[0]: row for row in summary[1:]}
controls = [by_arm["stub_c0"], by_arm["stub_c1"]]
images = [by_arm["image_c0"], by_arm["image_c1"]]
all_pairs = (controls, images)
writer_ok = all(int(c1[5]) > int(c0[5]) for c0, c1 in all_pairs)
branch_ok = all(int(c1[7]) > int(c0[7]) and int(c1[8]) > int(c0[8]) for c0, c1 in all_pairs)
downstream_progress = all(
    int(c1[16]) > int(c0[16]) and
    int(c1[20]) > int(c0[20]) and
    int(c1[14]) >= int(c0[14])
    for c0, c1 in all_pairs
)
complete_pcm_progress = all(
    int(c1[18]) > int(c0[18]) and int(c1[19]) > int(c0[19])
    for c0, c1 in all_pairs
)
if writer_ok and branch_ok:
    if downstream_progress and complete_pcm_progress:
        print("verdict=H-C88WriterRestoresGateAndAudioContractAtCaptureScope")
    elif downstream_progress:
        print("verdict=H-C88GateNotSufficient_PCMVoiceContractStillOpen")
    else:
        print("verdict=H-C88RouteOnly")
elif not any(int(row[5]) > 0 for row in summary[1:]):
    print("verdict=H-C88TreatmentDidNotStoreNonzero")
else:
    print("verdict=H-C88ReadbackOrArmAsymmetryInspectTable")
PY
