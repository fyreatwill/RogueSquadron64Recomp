#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TAG=${1:-s2337_m5_descriptor_source_reachability}
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
    --hit-cap 64 \
    --watch-pc 0x8008A38C,0x8008A564,0x80097FE8,0x800980EC,0x80092128,0x80092230,0x8009231C,0x80090B68,0x80090C28,0x8009C4E8,0x8009C904,0x8009D740,0x8009D7D0,0x8009B5A8 \
    --pc-phase-log-width 0x006AB400:512 \
    --vi-trace --status-poll --press "$PRESS" > "$OUT/oracle-preflight.log" 2>&1
oracle_rc=$?

python3 - "$OUT/oracle-preflight.log" "$OUT/oracle-gate.txt" <<'PY'
import re
import sys

log, result = sys.argv[1:]
text = open(log, errors="replace").read()
watch = {}
pcs = {}
for match in re.finditer(r"^\[oracle\] watch write \[(0x[0-9a-f]+),(0x[0-9a-f]+)\): (\d+) hit", text, re.M):
    watch[match.group(1)] = int(match.group(3))
for match in re.finditer(r"^\[oracle\] exec-prev pc=0x([0-9a-f]+) .* n=(\d+)$", text, re.M):
    pcs[match.group(1)] = pcs.get(match.group(1), 0) + int(match.group(2))
required_pcs = ["8008a38c", "8008a564", "80097fe8", "800980ec", "80092128",
                "80092230", "8009231c", "80090b68", "80090c28", "8009c904",
                "8009d740", "8009d7d0", "8009b5a8"]
required_watches = ["0x00000000", "0x00165000", "0x00141ad0", "0x000a0f50",
                    "0x00154620"]
ok = all(watch.get(w, 0) > 0 for w in required_watches)
ok = ok and watch.get("0x0001498a", 0) == 0
ok = ok and all(pcs.get(pc, 0) > 0 for pc in required_pcs)
ok = ok and pcs.get("8009c4e8", 0) == 0
ok = ok and "origin=0x00790400" in text and "origin=0x006ab400" in text
with open(result, "w") as out:
    out.write(f"controls={int(ok)}\n")
    out.write("watches=" + ",".join(f"{k}:{watch.get(k, 0)}" for k in required_watches) + "\n")
    out.write("pcs=" + ",".join(f"{k}:{pcs.get(k, 0)}" for k in required_pcs) + "\n")
    out.write(f"requested_zero_pc_0x8009c4e8={pcs.get('8009c4e8', 0)}\n")
    out.write(f"status_zero_watch_0x0001498a={watch.get('0x0001498a', 0)}\n")
    out.write(f"target_origins={int('origin=0x00790400' in text and 'origin=0x006ab400' in text)}\n")
PY
oracle_gate=$(grep -a -E '^controls=' "$OUT/oracle-gate.txt" | tail -1 | cut -d= -f2)
print "oracle_rc=$oracle_rc oracle_controls=${oracle_gate:-0}" | tee -a "$OUT/driver.log"
grep -a -E '^\[oracle\] (done:|watch write|exec-prev pc=0x8008|exec-prev pc=0x8009)' "$OUT/oracle-preflight.log" | tail -100 >> "$OUT/driver.log" || true
if [[ "${oracle_gate:-0}" != 1 || "$oracle_rc" != 0 ]]; then
    print "verdict=H-CoverageInvalid oracle_preflight=0" | tee -a "$OUT/driver.log"
    exit 5
fi

port_rc=0
zsh "$ROOT/scratch/agent/run_s2335_m5_descriptor_filter_boundary.sh" "$TAG" || port_rc=$?

python3 - "$OUT/oracle-preflight.log" "$OUT/stub.log" "$OUT/image.log" "$OUT/caller-reachability-table.tsv" "$OUT/caller-reachability-summary.tsv" <<'PY' | tee -a "$OUT/driver.log"
import re
import sys
from collections import Counter

oracle_path, stub_path, image_path, table_path, summary_path = sys.argv[1:]
token = re.compile(r"([^=\s]+)=([^\s]+)")
callers = {
    "0x8008a38c": {"callsite": "0x8008a564"},
    "0x80097fe8": {"callsite": "0x800980ec"},
}

def fields(line):
    return dict(token.findall(line))

def num(value, default=0):
    try:
        return int(value, 0)
    except (TypeError, ValueError):
        return default

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
        f = fields(line)
        if line.startswith("[phase]"):
            current = {"phase": f.get("phase", ""), "width": f.get("vi_width", ""),
                       "origin": f.get("origin", "")}
        if line.startswith("[init-voice-caller]"):
            caller = f.get("caller", "").lower()
            edge = f.get("edge", "")
            if caller in callers and edge in ("entry", "pre-call"):
                counts[(caller, edge)] += 1
                rows.append({"arm": arm, "class": edge, "caller": caller,
                             "phase": f.get("phase", current["phase"]),
                             "width": f.get("width", current["width"]),
                             "origin": f.get("origin", current["origin"]),
                             "ordinal": f.get("ordinal", ""), "row": f.get("row", ""),
                             "event": f.get("event", "")})
        if line.startswith("[init-voice-callsite]"):
            caller = f.get("caller_pc", "").lower()
            if caller in ("0x8008a564", "0x800980ec"):
                counts[(caller, "direct-callsite")] += 1
                rows.append({"arm": arm, "class": "direct-callsite", "caller": caller,
                             "phase": f.get("phase", current["phase"]),
                             "width": f.get("width", current["width"]),
                             "origin": f.get("origin", current["origin"]),
                             "ordinal": f.get("ordinal", ""), "row": f.get("row", ""),
                             "event": f.get("event", "")})
        if line.startswith("[init-voice-sample]"):
            caller = f.get("caller_pc", "").lower()
            if caller in ("0x8008a564", "0x800980ec"):
                counts[(caller, "callee-entry") ] += 1
        if "site=render-stage" in line: counts[("control", "render")] += 1
        if "site=render-stage" in line or "[m5-keyon-" in line: counts[("control", "target")] += 1
        for marker, key in (("[init-voice-sample-control]", "host-control"),
                            ("[audtask-abi]", "task"),
                            ("[audtask-dma-row]", "dma"),
                            ("edge=guest-receive", "guest-receive"),
                            ("[pcm-boundary-source]", "pcm-source"),
                            ("[pcm-boundary-consumer]", "pcm-consumer"),
                            ("[filter-voice-audit-control]", "filter-control")):
            if line.startswith(marker) or (marker == "edge=guest-receive" and line.startswith("[audio-sp-route]")):
                counts[("control", key)] += 1
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
retail_controls = all(retail[pc] > 0 for pc in
                      ("8008a38c", "8008a564", "80097fe8", "800980ec", "80092128",
                       "80092230", "8009231c", "80090b68", "80090c28", "8009c904",
                       "8009d740", "8009d7d0", "8009b5a8")) and retail["8009c4e8"] == 0

def count(arm, caller, edge):
    return arm_data[arm][0][(caller, edge)]

if not (retail_controls and port_controls):
    verdict = "H-CoverageInvalid"
elif all(count(arm, caller, "entry") == 0 and count(arm, caller, "pre-call") == 0
         for arm in arm_data for caller in callers):
    verdict = "H-PortCallerInactive"
else:
    bypassed = any(count(arm, caller, "entry") > 0 and count(arm, caller, "pre-call") == 0
                   for arm in arm_data for caller in callers)
    instrument_fault = any(
        count(arm, caller, "pre-call") > 0 and
        (count(arm, callers[caller]["callsite"], "direct-callsite") == 0 or
         count(arm, callers[caller]["callsite"], "callee-entry") == 0)
        for arm in arm_data for caller in callers)
    if bypassed:
        verdict = "H-PortBranchBypassed"
    elif instrument_fault:
        verdict = "H-PortCallsiteInstrumentationFault"
    else:
        verdict = "H-Unresolved"

with open(summary_path, "w") as out:
    out.write("metric\tvalue\n")
    out.write(f"retail_controls\t{int(retail_controls)}\n")
    out.write(f"port_controls\t{int(port_controls)}\n")
    out.write(f"verdict\t{verdict}\n")
    for pc, values in callers.items():
        for arm in arm_data:
            out.write(f"{arm}\t{pc}\tentry\t{count(arm, pc, 'entry')}\n")
            out.write(f"{arm}\t{pc}\tpre-call\t{count(arm, pc, 'pre-call')}\n")
            callsite = values["callsite"]
            out.write(f"{arm}\t{callsite}\tdirect-callsite\t{count(arm, callsite, 'direct-callsite')}\n")
            out.write(f"{arm}\t{callsite}\tcallee-entry\t{count(arm, callsite, 'callee-entry')}\n")
    for arm in arm_data:
        for key in required_controls:
            out.write(f"{arm}\tcontrol\t{key}\t{arm_data[arm][0][('control', key)]}\n")
print(f"caller_reachability retail_controls={int(retail_controls)} port_controls={int(port_controls)} verdict={verdict}")
PY

sed -n '1,80p' "$OUT/oracle-gate.txt" >> "$OUT/driver.log"
sed -n '1,120p' "$OUT/caller-reachability-summary.tsv" >> "$OUT/driver.log"
stub_hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/stub.log" 2>/dev/null || true)
image_hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/image.log" 2>/dev/null || true)
print "controls oracle=$oracle_gate stub_hangar=$stub_hangar image_hangar=$image_hangar port_rc=$port_rc" | tee -a "$OUT/driver.log"
if (( port_rc != 0 || stub_hangar == 0 || image_hangar == 0 )); then
    print "verdict=H-CoverageInvalid" | tee -a "$OUT/driver.log"
    exit 6
fi
exit 0
