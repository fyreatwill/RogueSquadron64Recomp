#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BUILD="$ROOT/build"
TAG=${1:-s2341_m5_synth_parent_gate_census}
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
if [[ ! -x "$BUILD/RogueSquadron64Recomp" || ! -f "$BUILD/rogue_squadron.z64" || ! -x "$BUILD/winctl" ]]; then
    print "ERROR: build prerequisites are missing" > "$OUT/driver.log"
    exit 3
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
    --watch-pc 0x8009123C,0x80091484,0x80091544,0x800915F8,0x800914A4,0x80091564,0x80091618,0x8008C9AC,0x8008CA14,0x80019B74,0x8009B5A8,0x8008BC10,0x8008C454,0x8009B784,0x8008A38C,0x8008A564,0x80097FE8,0x800980EC,0x80092128,0x80092230,0x8009231C,0x80090B68,0x80090C28,0x8009C4E8,0x8009C904,0x8009D740,0x8009D7D0 \
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
for m in re.finditer(r"^\[oracle\] watch write \[(0x[0-9a-f]+),[^]]+\): (\d+) hit", text, re.M):
    watches[m.group(1)] = int(m.group(2))
for m in re.finditer(r"^\[oracle\] exec-prev pc=0x([0-9a-f]+) .* n=(\d+)$", text, re.M):
    pcs[m.group(1)] = pcs.get(m.group(1), 0) + int(m.group(2))
required_pcs = "8009123c 80091484 80091544 800915f8 800914a4 80091564 80091618 8008c9ac 8008ca14 80019b74 8009b5a8 8008bc10 8008c454 8009b784 8008a38c 8008a564 80097fe8 800980ec 80092128 80092230 8009231c 80090b68 80090c28 8009c904 8009d740 8009d7d0".split()
required_watches = "0x00000000 0x00165000 0x00141ad0 0x000a0f50 0x00154620 0x0011a8a4".split()
controls = all(watches.get(w, 0) > 0 for w in required_watches)
controls = controls and watches.get("0x0001498a", 0) == 0
controls = controls and all(pcs.get(pc, 0) > 0 for pc in required_pcs)
controls = controls and pcs.get("8009c4e8", 0) == 0
controls = controls and "origin=0x00790400" in text and "origin=0x006ab400" in text
with open(result, "w") as out:
    out.write(f"controls={int(controls)}\n")
    for address in required_watches:
        out.write(f"watch_{address}={watches.get(address, 0)}\n")
    for pc in required_pcs:
        out.write(f"pc_{pc}={pcs.get(pc, 0)}\n")
    out.write(f"requested_zero_pc_0x8009c4e8={pcs.get('8009c4e8', 0)}\n")
    out.write(f"title_origin={int('origin=0x00790400' in text)}\n")
    out.write(f"hangar_origin={int('origin=0x006ab400' in text)}\n")
PY
oracle_controls=$(awk -F= '/^controls=/{print $2}' "$OUT/oracle-gate.txt" | tail -1)
print "oracle_rc=$oracle_rc oracle_controls=${oracle_controls:-0}" | tee -a "$OUT/driver.log"
grep -a -E '^\[oracle\] (done:|watch write|exec-prev pc=0x8009|exec-prev pc=0x80091|vi )' "$OUT/oracle-ground-truth.log" | tail -140 >> "$OUT/driver.log" || true
if [[ "${oracle_controls:-0}" != 1 || "$oracle_rc" != 0 ]]; then
    print "verdict=H-CoverageInvalid oracle_preflight=0" | tee -a "$OUT/driver.log"
    exit 5
fi

env ROGUESQ_LOG_AUDIOTICK_TRACE=1 zsh "$ROOT/scratch/agent/run_s2335_m5_descriptor_filter_boundary.sh" "$TAG"
port_rc=$?

python3 - "$OUT/stub.log" "$OUT/image.log" "$OUT/synth-parent-gate-table.tsv" "$OUT/synth-parent-gate-summary.tsv" <<'PY' | tee -a "$OUT/driver.log"
import re
import sys
from collections import Counter

stub_path, image_path, table_path, summary_path = sys.argv[1:]
token = re.compile(r"([^=\s]+)=([^\s]+)")
sources = ("0x8009123c", "0x80091484", "0x80091544", "0x800915f8")
callsites = ("0x800914a4", "0x80091564", "0x80091618")
required_controls = ("host-control", "task", "dma", "guest-receive", "pcm-source",
                     "pcm-consumer", "filter-control", "render", "keyon", "seq-helper")

def fields(line):
    return dict(token.findall(line))

def read_arm(path, arm):
    counts = Counter()
    rows = []
    for line in open(path, errors="replace"):
        row = fields(line)
        if line.startswith("[m5-synth-parent]"):
            source = row.get("source", "").lower()
            if source in sources:
                counts[("synth", source)] += 1
                rows.append({"arm": arm, **row})
        if line.startswith("[m5-audio-seq]"):
            source = row.get("source", "").lower()
            if source in ("0x8008d960", *callsites):
                counts[("sequencer", source)] += 1
            if source == "0x80019b74" and row.get("edge") == "control":
                counts[("control", "seq-helper")] += 1
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
columns = ("arm", "event", "source", "edge", "gate", "callsite", "taken", "countdown",
           "period", "phase", "width", "origin", "active", "arm", "ordinal", "row", "ra")
with open(table_path, "w") as out:
    out.write("\t".join(columns) + "\n")
    for name in ("stub", "image"):
        for row in arms[name][1]:
            out.write("\t".join(row.get(c, "") for c in columns) + "\n")

port_controls = all(all(arms[name][0][("control", key)] > 0 for key in required_controls)
                    for name in arms)
oracle_controls = 0
try:
    import os
    oracle_controls = int(open(os.path.join(os.path.dirname(stub_path), "oracle-gate.txt"), errors="replace").read().split("controls=", 1)[1].splitlines()[0])
except (IndexError, OSError, ValueError):
    pass
entry = {arm: arms[arm][0][("synth", "0x8009123c")] for arm in arms}
gate = {arm: [arms[arm][0][("synth", source)] for source in sources[1:]] for arm in arms}
call = {arm: [arms[arm][0][("sequencer", source)] for source in callsites] for arm in arms}
pair_fired = {arm: [gate[arm][i] > 0 or call[arm][i] > 0 for i in range(3)] for arm in arms}
all_zero_entry = all(entry[arm] == 0 for arm in arms)
any_edge = any(any(pair_fired[arm]) for arm in arms)
all_zero_pairs = all(not any(pair_fired[arm]) for arm in arms)
all_pairs = all(all(pair_fired[arm]) for arm in arms)
some_pairs = any(any(pair_fired[arm]) and not all(pair_fired[arm]) for arm in arms)
if not (oracle_controls and port_controls):
    verdict = "H-CoverageInvalid"
elif all_zero_entry and any_edge:
    verdict = "H-PortSynthDispatchMismatch"
elif all_zero_entry:
    verdict = "H-PortSynthInactive"
elif all_zero_pairs:
    verdict = "H-PortSynthGateBypassed"
elif some_pairs or not all_pairs:
    verdict = "H-PortSynthPartialGate"
else:
    verdict = "H-Unresolved"

with open(summary_path, "w") as out:
    out.write("metric\tvalue\n")
    out.write(f"oracle_controls\t{oracle_controls}\n")
    out.write(f"port_controls\t{int(port_controls)}\n")
    out.write(f"verdict\t{verdict}\n")
    for arm in ("stub", "image"):
        out.write(f"{arm}\tentry\t{entry[arm]}\n")
        for index in range(3):
            out.write(f"{arm}\tgate{index + 1}\t{gate[arm][index]}\n")
            out.write(f"{arm}\tcallsite{index + 1}\t{call[arm][index]}\n")
            out.write(f"{arm}\tpair{index + 1}\t{int(pair_fired[arm][index])}\n")
        for key in required_controls:
            out.write(f"{arm}\tcontrol:{key}\t{arms[arm][0][('control', key)]}\n")
print(f"synth_parent_gate oracle_controls={oracle_controls} port_controls={int(port_controls)} entry={dict(entry)} gate={dict(gate)} call={dict(call)} verdict={verdict}")
PY

sed -n '1,100p' "$OUT/synth-parent-gate-summary.tsv" >> "$OUT/driver.log"
stub_hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/stub.log" 2>/dev/null || true)
image_hangar=$(grep -a -c '^\[phase\] vi_width=512 .*origin=0x006AB400' "$OUT/image.log" 2>/dev/null || true)
summary_verdict=$(awk -F '\t' '$1 == "verdict" {print $2}' "$OUT/synth-parent-gate-summary.tsv" 2>/dev/null || true)
print "controls oracle=$oracle_controls port_rc=$port_rc stub_hangar=$stub_hangar image_hangar=$image_hangar verdict=$summary_verdict" | tee -a "$OUT/driver.log"
if (( stub_hangar == 0 || image_hangar == 0 )); then
    print "verdict=H-CoverageInvalid port_hangar=0" | tee -a "$OUT/driver.log"
    exit 6
fi
exit 0
