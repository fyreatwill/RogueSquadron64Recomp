#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TAG=${1:-s2342_m5_synth_pre_gate_census}
OUT="$ROOT/scratch/agent/$TAG"
ORACLE_LOG="$OUT/oracle-ground-truth.log"
PORT_TAG="${TAG}_port"
PORT_OUT="$ROOT/scratch/agent/$PORT_TAG"

[[ "$TAG" != .* ]] || exit 2
mkdir -p "$OUT"
if [[ ! -s "$ORACLE_LOG" ]]; then
    print "ERROR: ground-truth preflight is missing: $ORACLE_LOG" > "$OUT/driver.log"
    exit 3
fi

python3 - "$ORACLE_LOG" "$OUT/oracle-gate.txt" <<'PY'
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
required_pcs = """
8009123c 8009142c 80091454 80091468 80091484 80091544 800915f8
800914a4 80091564 80091618 8008c9ac 8008ca14 80019b74 8009b5a8
8008bc10 8008c454 8009b784 8008a38c 8008a564 80097fe8 800980ec
80092128 80092230 8009231c 80090b68 80090c28 8009c904 8009d740
8009d7d0
""".split()
required_watches = "0x00000000 0x00165000 0x00141ad0 0x000a0f50 0x00154620 0x0011a8a4".split()
controls = all(watches.get(address, 0) > 0 for address in required_watches)
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
print "oracle_controls=${oracle_controls:-0}" | tee "$OUT/driver.log"
if [[ "${oracle_controls:-0}" != 1 ]]; then
    print "verdict=H-CoverageInvalid oracle_preflight=0" | tee -a "$OUT/driver.log"
    exit 5
fi

env ROGUESQ_LOG_AUDIOTICK_TRACE=1 zsh "$ROOT/scratch/agent/run_s2335_m5_descriptor_filter_boundary.sh" "$PORT_TAG" > "$OUT/port-driver.log" 2>&1
port_rc=$?

python3 - "$ORACLE_LOG" "$PORT_OUT/stub.log" "$PORT_OUT/image.log" "$OUT/synth-pre-gate-table.tsv" "$OUT/synth-pre-gate-summary.tsv" "$port_rc" <<'PY' | tee -a "$OUT/driver.log"
import re
import sys
from collections import Counter, defaultdict

oracle_path, stub_path, image_path, table_path, summary_path, port_rc = sys.argv[1:]
port_rc = int(port_rc)
token = re.compile(r"([^=\s]+)=([^\s]+)")
sources = ("0x8009142c", "0x80091454", "0x80091468")
gates = ("0x80091484", "0x80091544", "0x800915f8")
callsites = ("0x800914a4", "0x80091564", "0x80091618")
required_controls = ("host-control", "task", "dma", "guest-receive", "pcm-source",
                     "pcm-consumer", "filter-control", "render", "keyon", "seq-helper")

def fields(line):
    return dict(token.findall(line))

def number(value, default=0):
    try:
        return int(value, 0)
    except (TypeError, ValueError):
        return default

retail_pcs = set((
    "8009123c", *[source[2:] for source in sources],
    *[source[2:] for source in gates], *[source[2:] for source in callsites],
    "8008c9ac", "8008ca14", "80019b74", "8009b5a8", "8008bc10", "8008c454",
    "8009b784", "8008a38c", "8008a564", "80097fe8", "800980ec", "80092128",
    "80092230", "8009231c", "80090b68", "80090c28", "8009c904", "8009d740",
    "8009d7d0"))
retail = Counter()
watches = {}
with open(oracle_path, errors="replace") as stream:
    for line in stream:
        match = re.search(r"^\[oracle\] exec-prev pc=0x([0-9a-f]+) .* n=(\d+)$", line)
        if match and match.group(1) in retail_pcs:
            retail[match.group(1)] += int(match.group(2))
        match = re.search(r"^\[oracle\] watch write \[(0x[0-9a-f]+),[^]]+\): (\d+) hit", line)
        if match:
            watches[match.group(1)] = int(match.group(2))

def read_arm(path, arm):
    counts = Counter()
    pregate = []
    parent = Counter()
    sequence = Counter()
    try:
        stream = open(path, errors="replace")
    except OSError:
        return counts, pregate, parent, sequence
    with stream:
        for line in stream:
            row = fields(line)
            if line.startswith("[m5-synth-pregate]"):
                source = row.get("source", "").lower()
                if source in sources:
                    pregate.append({"arm": arm, **row})
            if line.startswith("[m5-synth-parent]"):
                source = row.get("source", "").lower()
                if source == "0x8009123c" and row.get("edge") == "entry":
                    parent["entry"] += 1
                elif source in gates:
                    parent[source] += 1
            if line.startswith("[m5-audio-seq]"):
                source = row.get("source", "").lower()
                if source == "0x80019b74" and row.get("edge") == "control":
                    sequence["seq-helper"] += 1
                elif source in callsites:
                    sequence[source] += 1
            if line.startswith("[init-voice-sample-control]"):
                counts["host-control"] += 1
            if line.startswith("[audtask-abi]"):
                counts["task"] += 1
            if line.startswith("[audtask-dma-row]") or line.startswith("[audtask-dma-range]"):
                counts["dma"] += 1
            if line.startswith("[audio-sp-route]") and row.get("edge") == "guest-receive":
                counts["guest-receive"] += 1
            if line.startswith("[pcm-boundary-source]"):
                counts["pcm-source"] += 1
            if line.startswith("[pcm-boundary-consumer]"):
                counts["pcm-consumer"] += 1
            if line.startswith("[filter-voice-audit-control]"):
                counts["filter-control"] += 1
            if "site=render-stage" in line:
                counts["render"] += 1
            if "[m5-keyon-" in line:
                counts["keyon"] += 1
    return counts, pregate, parent, sequence

arms = {name: read_arm(path, name) for name, path in (("stub", stub_path), ("image", image_path))}
all_rows = arms["stub"][1] + arms["image"][1]
columns = ("arm", "source", "event", "taken", "lhs", "rhs", "target", "phase", "width",
           "origin", "active", "ordinal", "row", "ra")
with open(table_path, "w") as out:
    out.write("\t".join(columns) + "\n")
    for row in all_rows:
        out.write("\t".join(row.get(column, "") for column in columns) + "\n")

def rows(arm, source):
    return [row for row in arms[arm][1] if row.get("source", "").lower() == source]

def all_taken(arm, source, value):
    selected = rows(arm, source)
    return bool(selected) and all(number(row.get("taken")) == value for row in selected)

def has_taken(arm, source, value):
    return any(number(row.get("taken")) == value for row in rows(arm, source))

def control_count(arm, key):
    if key == "seq-helper":
        return arms[arm][3][key]
    return arms[arm][0][key]

port_controls = all(all(control_count(arm, key) > 0 for key in required_controls) for arm in arms)
hangar = all("origin=0x006AB400" in open(path, errors="replace").read()
             for path in (stub_path, image_path))
parent_entry = {arm: arms[arm][2]["entry"] for arm in arms}
gate1 = {arm: arms[arm][2][gates[0]] for arm in arms}
outer = all(all_taken(arm, sources[0], 1) and not rows(arm, sources[1]) and not rows(arm, sources[2])
            for arm in arms)
inner = all(all_taken(arm, sources[0], 0) and all_taken(arm, sources[1], 1) and not rows(arm, sources[2])
            for arm in arms)
b40 = all(has_taken(arm, sources[0], 0) and has_taken(arm, sources[1], 0)
         and all_taken(arm, sources[2], 1) and gate1[arm] == 0 for arm in arms)
probe_mismatch = all(all_taken(arm, sources[0], 0) and all_taken(arm, sources[1], 0) and all_taken(arm, sources[2], 0)
                     and gate1[arm] == 0 for arm in arms)
if not (port_controls and hangar):
    verdict = "H-CoverageInvalid"
elif outer:
    verdict = "H-PortPreGateOuterReject"
elif inner:
    verdict = "H-PortPreGateInnerReject"
elif b40:
    verdict = "H-PortPreGateB40Reject"
elif probe_mismatch:
    verdict = "H-PortPreGateProbeMismatch"
else:
    verdict = "H-Unresolved"

with open(summary_path, "w") as out:
    out.write("metric\tvalue\n")
    out.write(f"oracle_controls\t1\n")
    out.write(f"port_rc\t{port_rc}\n")
    out.write(f"port_controls\t{int(port_controls)}\n")
    out.write(f"hangar_control\t{int(hangar)}\n")
    out.write(f"verdict\t{verdict}\n")
    for arm in ("stub", "image"):
        out.write(f"{arm}\tparent_entry\t{parent_entry[arm]}\n")
        for source in sources:
            selected = rows(arm, source)
            out.write(f"{arm}\t{source}\trows={len(selected)}\t"
                      f"taken0={sum(number(row.get('taken')) == 0 for row in selected)}\t"
                      f"taken1={sum(number(row.get('taken')) == 1 for row in selected)}\n")
        for source in gates:
            out.write(f"{arm}\tgate={source}\t{arms[arm][2][source]}\n")
        for source in callsites:
            out.write(f"{arm}\tcallsite={source}\t{arms[arm][3][source]}\n")
        for key in required_controls:
            out.write(f"{arm}\tcontrol={key}\t{control_count(arm, key)}\n")
    for pc in sorted(retail_pcs):
        out.write(f"retail_pc_{pc}\t{retail[pc]}\n")
print(f"synth_pre_gate oracle_controls=1 port_controls={int(port_controls)} hangar={int(hangar)} parent_entry={parent_entry} gate1={gate1} rows={Counter(row.get('source') for row in all_rows)} verdict={verdict}")
PY

sed -n '1,120p' "$OUT/synth-pre-gate-summary.tsv" >> "$OUT/driver.log"
summary_verdict=$(awk -F '\t' '$1 == "verdict" {print $2}' "$OUT/synth-pre-gate-summary.tsv")
print "verdict=$summary_verdict oracle_controls=1 port_rc=$port_rc" | tee -a "$OUT/driver.log"
exit 0
