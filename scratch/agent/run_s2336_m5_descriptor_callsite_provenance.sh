#!/bin/zsh
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TAG=${1:-s2336_m5_descriptor_callsite_provenance}
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
    --watch-pc 0x80092128,0x80092230,0x8009231C,0x80090B68,0x80090C28,0x8009C4E8,0x8009C904,0x8009D740,0x8009D7D0,0x8009B5A8 \
    --pc-phase-log-width 0x006AB400:512 \
    --vi-trace --status-poll --press "$PRESS" > "$OUT/oracle-preflight.log" 2>&1
oracle_rc=$?

python3 - "$OUT/oracle-preflight.log" "$OUT/oracle-gate.txt" <<'PY'
import re
import sys

log, result = sys.argv[1:]
text = open(log, errors="replace").read()
watch = {}
for match in re.finditer(r"^\[oracle\] watch write \[(0x[0-9a-f]+),(0x[0-9a-f]+)\): (\d+) hit", text, re.M):
    watch[match.group(1)] = int(match.group(3))
pcs = {}
for match in re.finditer(r"^\[oracle\] exec-prev pc=0x([0-9a-f]+) .* n=(\d+)$", text, re.M):
    pcs[match.group(1)] = pcs.get(match.group(1), 0) + int(match.group(2))
required_pcs = ["80092128", "80092230", "8009231c", "80090b68", "80090c28",
                "8009c904", "8009d740", "8009d7d0", "8009b5a8"]
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
grep -a -E '^\[oracle\] (done:|watch write|exec-prev pc=0x8009|exec-prev pc=0x80092)' "$OUT/oracle-preflight.log" | tail -80 >> "$OUT/driver.log" || true
if [[ "${oracle_gate:-0}" != 1 || "$oracle_rc" != 0 ]]; then
    print "verdict=H-CoverageInvalid oracle_preflight=0" | tee -a "$OUT/driver.log"
    exit 5
fi

zsh "$ROOT/scratch/agent/run_s2335_m5_descriptor_filter_boundary.sh" "$TAG"
port_rc=$?

python3 - "$OUT/oracle-preflight.log" "$OUT/stub.log" "$OUT/image.log" "$OUT/descriptor-callsite-summary.tsv" <<'PY' | tee -a "$OUT/driver.log"
import re
import sys
from collections import Counter

oracle_path, stub_path, image_path, summary_path = sys.argv[1:]
token = re.compile(r"([^=\s]+)=([^\s]+)")

def fields(line):
    return dict(token.findall(line))

def num(value, default=0):
    try:
        return int(value, 0)
    except (TypeError, ValueError):
        return default

retail = Counter()
oracle = open(oracle_path, errors="replace").read()
for match in re.finditer(r"^\[oracle\] exec-prev pc=0x([0-9a-f]+) .* n=(\d+)$", oracle, re.M):
    retail[match.group(1)] += int(match.group(2))
for match in re.finditer(r"^\[oracle\] watch write \[(0x[0-9a-f]+),(0x[0-9a-f]+)\): (\d+) hit", oracle, re.M):
    retail[match.group(1)] = int(match.group(3))

def read_arm(path):
    c = Counter()
    calls = {}
    entries = {}
    stores = []
    rows = []
    with open(path, errors="replace") as stream:
        for line in stream:
            f = fields(line)
            if line.startswith("[init-voice-sample-control]"):
                c["init_control"] += 1
            if line.startswith("[init-voice-callsite]"):
                c["callsite"] += 1
                calls[f.get("event", "")] = f
                rows.append(("callsite", f))
            if line.startswith("[init-voice-sample]"):
                c["entry"] += 1
                entries[f.get("event", "")] = f
                rows.append(("entry", f))
            if line.startswith("[m5-audio-event]"):
                site = f.get("site", "").lower()
                kind = f.get("kind", "")
                if kind == "keyon-w40" and site == "0x80092230":
                    c["store"] += 1
                    stores.append(f)
                if kind == "init-desc" and site == "0x80092230":
                    c["payload"] += 1
            if "site=render-stage" in line:
                c["render"] += 1
            if "site=render-end" in line:
                c["render_end"] += 1
            if "[m5-keyon-" in line:
                c["keyon"] += 1
            if line.startswith("[audtask-abi]"):
                c["task_abi"] += 1
            if line.startswith("[audtask-dma-row]"):
                c["dma_row"] += 1
            if line.startswith("[audtask-dma-range]"):
                c["dma_range"] += 1
            if line.startswith("[audio-sp-route]") and f.get("edge") == "guest-receive":
                c["guest_receive"] += 1
            if line.startswith("[pcm-boundary-source]"):
                c["pcm_source"] += 1
            if line.startswith("[pcm-boundary-consumer]"):
                c["pcm_consumer"] += 1
            if line.startswith("[filter-voice-audit-control]") and f.get("kind") == "host-positive-control":
                c["filter_control"] += 1
            if line.startswith("[filter-voice-audit]"):
                c["filter_real"] += 1
    joined = sorted(set(calls) & set(entries) - {""})
    same = 0
    prior = 0
    for store in stores:
        key = (store.get("ordinal", ""), store.get("row", ""))
        matching = [f for f in entries.values() if (f.get("ordinal", ""), f.get("row", "")) == key]
        if matching:
            same += 1
        elif entries:
            prior += 1
    c["entry_call_join"] = len(joined)
    c["same_ordinal_store_join"] = same
    c["prior_ordinal_store"] = prior
    return c, calls, entries

arm_data = {name: read_arm(path) for name, path in (("stub", stub_path), ("image", image_path))}
with open(summary_path, "w") as out:
    out.write("arm\tcontrol\tcount\n")
    for arm, (counts, calls, entries) in arm_data.items():
        for key in sorted(counts):
            out.write(f"{arm}\t{key}\t{counts[key]}\n")

required = ("init_control", "task_abi", "dma_row", "guest_receive", "pcm_source",
            "pcm_consumer", "filter_control", "render", "keyon")
port_controls = all(all(arm_data[arm][0][key] > 0 for key in required) for arm in arm_data)
port_controls = port_controls and arm_data["image"][0]["dma_range"] > 0
retail_required = ("80092128", "80092230", "8009231c", "80090b68", "80090c28",
                   "8009c904", "8009d740", "8009d7d0", "8009b5a8")
retail_controls = all(retail[key] > 0 for key in retail_required)
retail_controls = retail_controls and retail["8009c4e8"] == 0
target_rows = sum(arm_data[arm][0]["render"] for arm in arm_data)
entry_rows = sum(arm_data[arm][0]["entry"] for arm in arm_data)
store_rows = sum(arm_data[arm][0]["store"] for arm in arm_data)
if not retail_controls or not port_controls:
    verdict = "H-CoverageInvalid"
elif all(arm_data[arm][0]["entry"] == 0 and arm_data[arm][0]["store"] == 0 for arm in arm_data):
    verdict = "H-PortInitNeverCalled"
elif any(arm_data[arm][0]["entry"] > 0 and arm_data[arm][0]["store"] == 0 for arm in arm_data):
    verdict = "H-PortInitEntryEarlyReturn"
elif entry_rows and store_rows and all(arm_data[arm][0]["same_ordinal_store_join"] == 0 for arm in arm_data):
    verdict = "H-PortInitPriorOrdinal"
else:
    verdict = "H-Unresolved"
print("retail_entry=%d retail_store=%d retail_trigger=%d retail_keyon=%d retail_filter=%d requested_zero=%d" %
      (retail["80092128"], retail["80092230"], retail["8009231c"],
       retail["80090b68"] + retail["80090c28"], retail["8009d7d0"], retail["8009c4e8"]))
for arm, (counts, calls, entries) in arm_data.items():
    callers = Counter(f.get("caller_pc", "") for f in entries.values())
    print(f"{arm}_controls={int(all(counts[key] > 0 for key in required))}"
          f" {arm}_render={counts['render']} {arm}_keyon={counts['keyon']}"
          f" {arm}_callsite={counts['callsite']} {arm}_entry={counts['entry']}"
          f" {arm}_store={counts['store']} {arm}_payload={counts['payload']}"
          f" {arm}_entry_call_join={counts['entry_call_join']}"
          f" {arm}_same_ordinal_store_join={counts['same_ordinal_store_join']}"
          f" {arm}_prior_ordinal_store={counts['prior_ordinal_store']}"
          f" {arm}_entry_callers=" + ",".join(f"{k}:{v}" for k, v in sorted(callers.items())))
print(f"target_render_rows={target_rows} target_entry_rows={entry_rows} target_store_rows={store_rows}")
print(f"verdict={verdict}")
PY
exit "$port_rc"
