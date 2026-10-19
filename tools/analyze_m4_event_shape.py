#!/usr/bin/env python3
"""Compare M4 event shape without reusing exact or rank-bin joins."""

import argparse
import re
import struct
from collections import defaultdict

MAPPED_PCS = (0x012C, 0x07F0)
RSD2_SIZE = 4168
RSM2_SIZE = 80


def bucket(total):
    return total.bit_length() if total else 0


def phase_table(path):
    rows = []
    for line in open(path, encoding="utf-8", errors="replace"):
        match = re.search(r"\[rdp\] sync=(\d+) vi_origin=0x([0-9a-fA-F]+) vi_width=(\d+)", line)
        if match:
            rows.append((int(match.group(2), 16), int(match.group(3))))
    return rows


def retail(path_mid, path_end, path_oracle):
    phases = phase_table(path_oracle)
    tasks = []
    with open(path_end, "rb") as stream:
        while raw := stream.read(RSD2_SIZE):
            if len(raw) != RSD2_SIZE or raw[:4] != b"RSD2":
                continue
            fields = struct.unpack_from("<4s5I", raw)
            if fields[3] == 1:
                tasks.append(fields[2])
    if len(tasks) != len(phases):
        raise ValueError(f"retail VI/task control failed: {len(phases)} != {len(tasks)}")
    phase_by_task = {task: (n, *phases[n]) for n, task in enumerate(tasks)}
    groups = defaultdict(lambda: {"rows": 0, "progress": set(), "lanes": 0, "totals": set()})
    with open(path_mid, "rb") as stream:
        while raw := stream.read(RSM2_SIZE):
            if len(raw) != RSM2_SIZE or raw[:4] != b"RSM2":
                continue
            _, _, task, task_type, pc, step, image, total = struct.unpack_from("<4s7I", raw)
            if task_type != 1 or task not in phase_by_task or pc not in MAPPED_PCS:
                continue
            phase, origin, width = phase_by_task[task]
            if width != 512 or not (0x6AB000 <= origin < 0x6AC000):
                continue
            key = (phase, image, pc, bucket(total))
            stat = groups[key]
            stat["rows"] += 1
            stat["progress"].add(min(20, (step * 20) // total) if total else 0)
            stat["totals"].add(total)
            vacc = struct.unpack_from("<24h", raw, 32)
            stat["lanes"] += any((value & 0xFFFF) == 0x8000 for value in vacc)
    return groups, {"whole_rdram": "[hit]" in open(path_oracle, encoding="utf-8", errors="replace").read(),
                    "vi": bool(phases), "mapped_pc": bool(groups), "image": bool(groups)}


def port(path):
    groups = defaultdict(lambda: {"rows": 0, "progress": set(), "lanes": 0, "totals": set()})
    controls = {"whole_rdram": False, "vi": False, "mapped_pc": False, "image": False}
    for line in open(path, encoding="utf-8", errors="replace"):
        if "[m4-port-rdram-control]" in line and "bytes=0x800000" in line and "unavailable=1" not in line:
            controls["whole_rdram"] = True
        if not line.startswith("[m4-norm]"):
            continue
        fields = dict(re.findall(r"(\w+)=([^ ]+)", line))
        if not all(name in fields for name in ("phase", "viw", "origin", "image", "pc", "total", "progress", "lanes")):
            continue
        pc = int(fields["pc"], 0) & 0x0FFF
        origin = int(fields["origin"], 0)
        width = int(fields["viw"], 0)
        total = int(fields["total"], 0)
        controls["vi"] |= width == 512 and 0x6AB000 <= origin < 0x6AC000
        controls["mapped_pc"] |= pc in MAPPED_PCS
        controls["image"] |= fields["image"] not in ("none", "0", "missing")
        if width != 512 or not (0x6AB000 <= origin < 0x6AC000) or pc not in MAPPED_PCS:
            continue
        key = (int(fields["phase"], 0), fields["image"], pc, bucket(total))
        stat = groups[key]
        stat["rows"] += 1
        stat["progress"].add(min(20, int(fields["progress"], 0) // 50))
        stat["totals"].add(total)
        stat["lanes"] += fields["lanes"] != "-"
    return groups, controls


def show(name, groups, controls):
    print(f"{name}_groups={len(groups)} {name}_rows={sum(s['rows'] for s in groups.values())} {name}_controls={controls}")
    for pc in MAPPED_PCS:
        selected = [(key, stat) for key, stat in groups.items() if key[2] == pc]
        print(f"{name}_pc=0x{pc:04X} classes={len(selected)} rows={sum(s['rows'] for _, s in selected)} active_lane_rows={sum(s['lanes'] for _, s in selected)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--retail", nargs=3, metavar=("MID", "END", "ORACLE"))
    parser.add_argument("--port")
    args = parser.parse_args()
    retail_groups, retail_controls = retail(*args.retail)
    port_groups, port_controls = port(args.port)
    show("retail", retail_groups, retail_controls)
    show("port", port_groups, port_controls)
    reasons = []
    for name, controls, groups in (("retail", retail_controls, retail_groups), ("port", port_controls, port_groups)):
        for control, passed in controls.items():
            if not passed:
                reasons.append(f"{name}: {control} control absent")
        if not groups:
            reasons.append(f"{name}: no hangar rows")
    shared = set(retail_groups) & set(port_groups)
    print(f"shared_classes={len(shared)}")
    for pc in MAPPED_PCS:
        pc_shared = [key for key in shared if key[2] == pc]
        print(f"shared_pc=0x{pc:04X} classes={len(pc_shared)}")
        for key in sorted(pc_shared)[:20]:
            left, right = retail_groups[key], port_groups[key]
            print(f"class={key} retail_rows={left['rows']} port_rows={right['rows']} retail_progress={len(left['progress'])} port_progress={len(right['progress'])} retail_totals={sorted(left['totals'])[:4]} port_totals={sorted(right['totals'])[:4]} retail_lanes={left['lanes']} port_lanes={right['lanes']}")
    if reasons or any(not any(key[2] == pc for key in shared) for pc in MAPPED_PCS):
        print("verdict=H3")
        for reason in reasons:
            print(f"reason={reason}")
        return 2
    if any(retail_groups[key]["lanes"] or port_groups[key]["lanes"] for key in shared):
        print("verdict=H2")
    else:
        print("verdict=H1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
