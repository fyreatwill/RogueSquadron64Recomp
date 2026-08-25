#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TAG=${1:-s2340_m5_scheduler_caller_reachability}
OUT="$ROOT/scratch/agent/$TAG"
ORACLE="$ROOT/tools/oracle/build/rs64_oracle"
ORACLE_CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ORACLE_ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
ORACLE_VIDEO=/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib

[[ "$TAG" != .* ]] || exit 2
mkdir -p "$OUT"
if [[ ! -x "$ORACLE" || ! -f "$ORACLE_CORE" || ! -f "$ORACLE_ROM" || ! -f "$ORACLE_VIDEO" ]]; then
    print "ERROR: retail oracle prerequisites are missing" > "$OUT/driver.log"
    exit 2
fi

cd "$ROOT" || exit 4
PRESS=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start

print "oracle_preflight_start" > "$OUT/driver.log"
env "$ORACLE" \
    --core "$ORACLE_CORE" --rom "$ORACLE_ROM" --video "$ORACLE_VIDEO" \
    --secs 75 \
    --watch-write 0x0:0x800000 \
    --watch-write 0x165000:0x16B000 \
    --watch-write 0x141AD0:0x141AF0 \
    --watch-write 0xA0F50:0xA0F54 \
    --watch-write 0x1498A:0x1498C \
    --watch-write 0x154620:0x154624 \
    --watch-write 0x155848:0x155849 \
    --watch-write 0x156A70:0x156A71 \
    --watch-write 0x157C98:0x157C99 \
    --watch-write 0x158EC0:0x158EC1 \
    --watch-write 0x11A8A4:0x11A8B4 \
    --hit-cap 64 \
    --watch-pc 0x8008D960,0x800914A4,0x80091564,0x80091618,0x8008C9AC,0x8008CA14,0x80019B74,0x8009B5A8,0x8009123C,0x80003250,0x8008BC10,0x8008C454,0x8009B784,0x8008A38C,0x8008A564,0x80097FE8,0x800980EC,0x80092128,0x80092230,0x8009231C,0x80090B68,0x80090C28,0x8009C4E8,0x8009C904,0x8009D740,0x8009D7D0 \
    --pc-phase-log-width 0x006AB400:512 \
    --vi-trace --status-poll --press "$PRESS" > "$OUT/oracle-ground-truth.log" 2>&1
oracle_rc=$?

python3 - "$OUT/oracle-ground-truth.log" "$OUT/oracle-gate.txt" <<'PY'
import re
import sys

log, result = sys.argv[1:]
text = open(log, errors="replace").read()
watches = {}
pcs = {}
for match in re.finditer(r"^\[oracle\] watch write \[(0x[0-9a-f]+),[^]]+\): (\d+) hit", text, re.M):
    watches[match.group(1)] = int(match.group(2))
for match in re.finditer(r"^\[oracle\] exec-prev pc=0x([0-9a-f]+) .* n=(\d+)$", text, re.M):
    pcs[match.group(1)] = pcs.get(match.group(1), 0) + int(match.group(2))
required_pcs = "8008d960 800914a4 80091564 80091618 8008c9ac 8008ca14 80019b74 8009b5a8 8009123c 80003250 8008bc10 8008c454 8009b784 8008a38c 8008a564 80097fe8 800980ec 80092128 80092230 8009231c 80090b68 80090c28 8009c904 8009d740 8009d7d0".split()
required_watches = "0x00000000 0x00165000 0x00141ad0 0x000a0f50 0x00154620 0x0011a8a4".split()
controls = all(watches.get(w, 0) > 0 for w in required_watches)
controls = controls and watches.get("0x0001498a", 0) == 0
controls = controls and all(pcs.get(pc, 0) > 0 for pc in required_pcs)
controls = controls and pcs.get("8009c4e8", 0) == 0
controls = controls and "origin=0x00790400" in text and "origin=0x006ab400" in text
with open(result, "w") as out:
    out.write(f"controls={int(controls)}\n")
    out.write(f"oracle_watch_whole={watches.get('0x00000000', 0)}\n")
    out.write(f"oracle_watch_target={watches.get('0x00165000', 0)}\n")
    out.write(f"oracle_watch_callback_registration={watches.get('0x0011a8a4', 0)}\n")
    for pc in required_pcs:
        out.write(f"pc_{pc}={pcs.get(pc, 0)}\n")
    out.write(f"requested_zero_pc_0x8009c4e8={pcs.get('8009c4e8', 0)}\n")
PY
oracle_controls=$(awk -F= '/^controls=/{print $2}' "$OUT/oracle-gate.txt" | tail -1)
print "oracle_rc=$oracle_rc oracle_controls=${oracle_controls:-0}" | tee -a "$OUT/driver.log"
grep -a -E '^\[oracle\] (done:|watch write|exec-prev pc=0x8008|exec-prev pc=0x8009|vi )' "$OUT/oracle-ground-truth.log" | tail -140 >> "$OUT/driver.log" || true
if [[ "${oracle_controls:-0}" != 1 || "$oracle_rc" != 0 ]]; then
    print "verdict=H-CoverageInvalid oracle_preflight=0" | tee -a "$OUT/driver.log"
    exit 5
fi

env ROGUESQ_LOG_AUDIOTICK_TRACE=1 zsh "$ROOT/scratch/agent/run_s2335_m5_descriptor_filter_boundary.sh" "$TAG"
port_rc=$?

python3 - "$OUT/stub.log" "$OUT/image.log" "$OUT/seq-table.tsv" "$OUT/seq-summary.tsv" <<'PY' | tee -a "$OUT/driver.log"
import re
import sys
from collections import Counter

stub_path, image_path, table_path, summary_path = sys.argv[1:]
token = re.compile(r"([^=\s]+)=([^\s]+)")
sources = ("0x8008d960", "0x800914a4", "0x80091564", "0x80091618")
required_controls = ("host-control", "task", "dma", "guest-receive", "pcm-source",
                     "pcm-consumer", "filter-control", "render", "keyon", "seq-helper")

def fields(line):
    return dict(token.findall(line))

def read_arm(path, arm):
    counts = Counter()
    rows = []
    for line in open(path, errors="replace"):
        row = fields(line)
        if line.startswith("[m5-audio-seq]"):
            source = row.get("source", "").lower()
            if source in sources:
                counts[("seq", source)] += 1
                rows.append({"arm": arm, **row})
            elif source == "0x80019b74" and row.get("edge") == "control":
                counts[("control", "seq-helper")] += 1
        if line.startswith("[m5-scheduler-callback]"):
            source = row.get("source", "").lower()
            if source in ("0x8008c9ac", "0x8008ca14"):
                counts[("retained", source, row.get("edge", ""))] += 1
            if source == "0x80019b74":
                counts[("retained", source, row.get("edge", ""))] += 1
        if line.startswith("[init-voice-caller]"):
            caller = row.get("caller", "").lower()
            if caller in ("0x8008bc10", "0x8008c454", "0x8009b5a8", "0x8009b784",
                          "0x8008a38c", "0x8008a564", "0x80097fe8", "0x800980ec"):
                counts[("parent-child", caller, row.get("edge", ""))] += 1
        if line.startswith("[init-voice-sample-control]"):
            counts[("control", "host-control")] += 1
        if line.startswith("[audtask-abi]"):
            counts[("control", "task")] += 1
        if line.startswith("[audtask-dma-row]") or line.startswith("[audtask-dma-range]"):
            counts[("control", "dma")] += 1
        if line.startswith("[audio-sp-route]") and row.get("edge") == "guest-receive":
            counts[("control", "guest-receive")] += 1
        if line.startswith("[pcm-boundary-source]"):
            counts[("control", "pcm-source")] += 1
        if line.startswith("[pcm-boundary-consumer]"):
            counts[("control", "pcm-consumer")] += 1
        if line.startswith("[filter-voice-audit-control]"):
            counts[("control", "filter-control")] += 1
        if "site=render-stage" in line:
            counts[("control", "render")] += 1
        if "[m5-keyon-" in line:
            counts[("control", "keyon")] += 1
    return counts, rows

arms = {name: read_arm(path, name) for name, path in (("stub", stub_path), ("image", image_path))}
columns = ("arm", "event", "source", "edge", "callsite", "target", "phase", "width",
           "origin", "active", "arm", "ordinal", "row", "ra")
with open(table_path, "w") as out:
    out.write("\t".join(columns) + "\n")
    for name in ("stub", "image"):
        for row in arms[name][1]:
            out.write("\t".join(row.get(c, "") for c in columns) + "\n")

port_controls = all(all(arms[name][0][("control", key)] > 0 for key in required_controls)
                    for name in arms)
entry = lambda arm: arms[arm][0][("seq", "0x8008d960")]
calls = lambda arm: [arms[arm][0][("seq", source)] for source in sources[1:]]
all_calls_zero = all(all(value == 0 for value in calls(arm)) for arm in arms)
all_entry_zero = all(entry(arm) == 0 for arm in arms)
any_call = any(any(value > 0 for value in calls(arm)) for arm in arms)
any_entry = any(entry(arm) > 0 for arm in arms)
callsite_complete = all(all(value > 0 for value in calls(arm)) for arm in arms)
retained_zero = all(arms[arm][0][("retained", "0x8008c9ac", "entry")] == 0 for arm in arms)

oracle_controls = 0
try:
    import os
    oracle_controls = int(open(os.path.join(os.path.dirname(sys.argv[1]), "oracle-gate.txt"), errors="replace").read().split("controls=", 1)[1].splitlines()[0])
except (IndexError, OSError, ValueError):
    pass
if not (oracle_controls and port_controls):
    verdict = "H-CoverageInvalid"
elif all_calls_zero and all_entry_zero:
    verdict = "H-PortSeqCallerInactive"
elif any_call and all_entry_zero:
    verdict = "H-PortSeqDispatchMismatch"
elif any_entry and retained_zero:
    verdict = "H-PortSeqEntryActive"
elif not callsite_complete:
    verdict = "H-PortSeqPartialCallsite"
else:
    verdict = "H-Unresolved"

with open(summary_path, "w") as out:
    out.write("metric\tvalue\n")
    out.write(f"port_controls\t{int(port_controls)}\n")
    out.write(f"oracle_controls\t{oracle_controls}\n")
    out.write(f"verdict\t{verdict}\n")
    for arm in ("stub", "image"):
        out.write(f"{arm}\tentry\t{entry(arm)}\n")
        for source, value in zip(sources[1:], calls(arm)):
            out.write(f"{arm}\t{source}\t{value}\n")
        for key in required_controls:
            out.write(f"{arm}\tcontrol:{key}\t{arms[arm][0][('control', key)]}\n")
        out.write(f"{arm}\tretained_scheduler_entry\t{arms[arm][0][('retained', '0x8008c9ac', 'entry')]}\n")
        out.write(f"{arm}\tretained_scheduler_pre_call\t{arms[arm][0][('retained', '0x8008ca14', 'pre-call')]}\n")
print(f"seq_reachability oracle_controls={oracle_controls} port_controls={int(port_controls)} verdict={verdict}")
PY

sed -n '1,120p' "$OUT/seq-summary.tsv" >> "$OUT/driver.log"
print "controls oracle=${oracle_controls:-0} port_rc=$port_rc" | tee -a "$OUT/driver.log"
exit 0
