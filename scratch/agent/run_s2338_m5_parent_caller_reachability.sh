#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TAG=${1:-s2338_m5_parent_caller_reachability}
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

print "oracle_preflight_start" > "$OUT/oracle-driver.log"
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
    --hit-cap 64 \
    --watch-pc 0x8008BC10,0x8008C454,0x8009B5A8,0x8009B784,0x8008A38C,0x8008A564,0x80097FE8,0x800980EC,0x80092128,0x80092230,0x8009231C,0x80090B68,0x80090C28,0x8009C4E8,0x8009C904,0x8009D740,0x8009D7D0 \
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
for match in re.finditer(r"^\[oracle\] watch write \[(0x[0-9a-f]+),(0x[0-9a-f]+)\): (\d+) hit", text, re.M):
    watches[match.group(1)] = int(match.group(3))
for match in re.finditer(r"^\[oracle\] exec-prev pc=0x([0-9a-f]+) .* n=(\d+)$", text, re.M):
    pcs[match.group(1)] = pcs.get(match.group(1), 0) + int(match.group(2))
required_pcs = [
    "8008bc10", "8008c454", "8009b5a8", "8009b784",
    "8008a38c", "8008a564", "80097fe8", "800980ec",
    "80092128", "80092230", "8009231c", "80090b68", "80090c28",
    "8009c904", "8009d740", "8009d7d0", "80090b68",
]
required_watches = ["0x00000000", "0x00165000", "0x00141ad0", "0x000a0f50", "0x00154620"]
ok = oracle_rc = 0
ok = all(watches.get(w, 0) > 0 for w in required_watches)
ok = ok and watches.get("0x0001498a", 0) == 0
ok = ok and all(pcs.get(pc, 0) > 0 for pc in required_pcs)
ok = ok and pcs.get("8009c4e8", 0) == 0
ok = ok and "origin=0x00790400" in text and "origin=0x006ab400" in text
with open(result, "w") as out:
    out.write(f"controls={int(ok)}\n")
    out.write("watches=" + ",".join(f"{k}:{watches.get(k, 0)}" for k in required_watches) + "\n")
    out.write("pcs=" + ",".join(f"{k}:{pcs.get(k, 0)}" for k in required_pcs) + "\n")
    out.write(f"requested_zero_pc_0x8009c4e8={pcs.get('8009c4e8', 0)}\n")
    out.write(f"target_origins={int('origin=0x00790400' in text and 'origin=0x006ab400' in text)}\n")
PY
oracle_gate=$(grep -a -E '^controls=' "$OUT/oracle-gate.txt" | tail -1 | cut -d= -f2)
print "oracle_rc=$oracle_rc oracle_controls=${oracle_gate:-0}" | tee -a "$OUT/oracle-driver.log"
grep -a -E '^\[oracle\] (done:|watch write|exec-prev pc=0x8008|exec-prev pc=0x8009)' "$OUT/oracle-ground-truth.log" | tail -120 >> "$OUT/oracle-driver.log" || true
if [[ "${oracle_gate:-0}" != 1 || "$oracle_rc" != 0 ]]; then
    print "verdict=H-CoverageInvalid oracle_preflight=0" | tee -a "$OUT/oracle-driver.log"
    exit 5
fi

port_rc=0
zsh "$ROOT/scratch/agent/run_s2335_m5_descriptor_filter_boundary.sh" "$TAG" || port_rc=$?

python3 - "$OUT/oracle-ground-truth.log" "$OUT/stub.log" "$OUT/image.log" "$OUT/parent-reachability-table.tsv" "$OUT/parent-reachability-summary.tsv" <<'PY' | tee -a "$OUT/driver.log"
import re
import sys
from collections import Counter

oracle_path, stub_path, image_path, table_path, summary_path = sys.argv[1:]
token = re.compile(r"([^=\s]+)=([^\s]+)")
parents = {
    "0x8008bc10": {"edge": "0x8008c454", "child": "0x8008a38c", "callsite": "0x8008a564"},
    "0x8009b5a8": {"edge": "0x8009b784", "child": "0x80097fe8", "callsite": "0x800980ec"},
}

def fields(line):
    return dict(token.findall(line))

def target(width, origin):
    try:
        return (int(width, 0) == 1024 and int(origin, 0) == 0x790400) or (int(width, 0) == 512 and int(origin, 0) == 0x6AB400)
    except (TypeError, ValueError):
        return False

retail = Counter()
for line in open(oracle_path, errors="replace"):
    match = re.search(r"^\[oracle\] exec-prev pc=0x([0-9a-f]+) .* n=(\d+)$", line)
    if match:
        retail[match.group(1)] += int(match.group(2))

def read_arm(path, arm):
    counts = Counter()
    rows = []
    current = {"phase": "", "width": "", "origin": ""}
    for line in open(path, errors="replace"):
        row = fields(line)
        if line.startswith("[phase]"):
            current["phase"] = row.get("phase", row.get("n", current["phase"]))
            if "vi_width" in row or "width" in row:
                current["width"] = row.get("vi_width", row.get("width", current["width"]))
            if "origin" in row:
                current["origin"] = row["origin"]
        if line.startswith("[filter-voice-audit-control]"):
            counts[("control", "filter-control")] += 1
        if not target(current["width"], current["origin"]):
            continue
        if line.startswith("[init-voice-caller]"):
            caller = row.get("caller", "").lower()
            edge = row.get("edge", "")
            if caller in parents and edge in ("entry", "pre-call"):
                counts[(caller, edge)] += 1
                rows.append({"arm": arm, "class": edge, "caller": caller,
                             "phase": row.get("phase", current["phase"]),
                             "width": row.get("width", current["width"]),
                             "origin": row.get("origin", current["origin"]),
                             "ordinal": row.get("ordinal", ""), "row": row.get("row", ""),
                             "event": row.get("event", "")})
        if line.startswith("[init-voice-callsite]"):
            caller = row.get("caller_pc", "").lower()
            for parent in parents.values():
                if caller == parent["callsite"]:
                    counts[(caller, "direct-callsite")] += 1
        if line.startswith("[init-voice-sample]"):
            caller = row.get("caller_pc", "").lower()
            for parent in parents.values():
                if caller == parent["callsite"]:
                    counts[(caller, "callee-entry")] += 1
        if "site=render-stage" in line:
            counts[("control", "render")] += 1
        if "site=render-stage" in line or "[m5-keyon-" in line:
            counts[("control", "target")] += 1
        for marker, key in (("[init-voice-sample-control]", "host-control"),
                            ("[audtask-abi]", "task"),
                            ("[audtask-dma-row]", "dma"),
                            ("[pcm-boundary-source]", "pcm-source"),
                            ("[pcm-boundary-consumer]", "pcm-consumer")):
            if line.startswith(marker):
                counts[("control", key)] += 1
        if line.startswith("[audio-sp-route]") and row.get("edge") == "guest-receive":
            counts[("control", "guest-receive")] += 1
    return counts, rows

arm_data = {name: read_arm(path, name) for name, path in (("stub", stub_path), ("image", image_path))}
columns = ["arm", "class", "caller", "phase", "width", "origin", "ordinal", "row", "event"]
with open(table_path, "w") as out:
    out.write("\t".join(columns) + "\n")
    for arm in ("stub", "image"):
        for row in arm_data[arm][1]:
            out.write("\t".join(row.get(c, "") for c in columns) + "\n")

required_controls = ("host-control", "task", "dma", "guest-receive", "pcm-source",
                     "pcm-consumer", "filter-control", "render", "target")
port_controls = all(all(arm_data[arm][0][("control", key)] > 0 for key in required_controls)
                    for arm in arm_data)
retail_required = tuple(pc[2:] for pc in parents) + tuple(
    pc for pc in ("8008a38c", "8008a564", "80097fe8", "800980ec", "80092128",
                  "80092230", "8009231c", "80090b68", "80090c28", "8009c904",
                  "8009d740", "8009d7d0")
)
retail_controls = all(retail[pc] > 0 for pc in retail_required) and retail["8009c4e8"] == 0

def count(arm, key, edge):
    return arm_data[arm][0][(key, edge)]

all_parent_edges_zero = all(
    count(arm, parent, "entry") == 0 and count(arm, parent, "pre-call") == 0
    for arm in arm_data for parent in parents
)
bypassed = any(
    count(arm, parent, "entry") > 0 and count(arm, parent, "pre-call") == 0
    for arm in arm_data for parent in parents
)
dispatch_fault = any(
    count(arm, parent, "pre-call") > 0 and (
        count(arm, info["child"], "entry") == 0 or
        count(arm, info["callsite"], "direct-callsite") == 0 or
        count(arm, info["callsite"], "callee-entry") == 0)
    for arm in arm_data for parent, info in parents.items()
)
if not (retail_controls and port_controls):
    verdict = "H-CoverageInvalid"
elif all_parent_edges_zero:
    verdict = "H-PortParentInactive"
elif bypassed:
    verdict = "H-PortParentBranchBypassed"
elif dispatch_fault:
    verdict = "H-PortParentDispatchFault"
else:
    verdict = "H-Unresolved"

with open(summary_path, "w") as out:
    out.write("metric\tvalue\n")
    out.write(f"retail_controls\t{int(retail_controls)}\n")
    out.write(f"port_controls\t{int(port_controls)}\n")
    out.write(f"verdict\t{verdict}\n")
    for parent, info in parents.items():
        for arm in arm_data:
            out.write(f"{arm}\t{parent}\tentry\t{count(arm, parent, 'entry')}\n")
            out.write(f"{arm}\t{parent}\tpre-call\t{count(arm, parent, 'pre-call')}\n")
            out.write(f"{arm}\t{info['child']}\tentry\t{count(arm, info['child'], 'entry')}\n")
            out.write(f"{arm}\t{info['callsite']}\tdirect-callsite\t{count(arm, info['callsite'], 'direct-callsite')}\n")
            out.write(f"{arm}\t{info['callsite']}\tcallee-entry\t{count(arm, info['callsite'], 'callee-entry')}\n")
    for arm in arm_data:
        for key in required_controls:
            out.write(f"{arm}\tcontrol\t{key}\t{arm_data[arm][0][('control', key)]}\n")
print(f"parent_reachability retail_controls={int(retail_controls)} port_controls={int(port_controls)} verdict={verdict}")
PY

sed -n '1,120p' "$OUT/oracle-gate.txt" >> "$OUT/driver.log"
sed -n '1,120p' "$OUT/parent-reachability-summary.tsv" >> "$OUT/driver.log"
print "controls oracle=$oracle_gate port_rc=$port_rc" | tee -a "$OUT/driver.log"
if (( port_rc != 0 )); then
    print "verdict=H-CoverageInvalid" | tee -a "$OUT/driver.log"
    exit 6
fi
exit 0
