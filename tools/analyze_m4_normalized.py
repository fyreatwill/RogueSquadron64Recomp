#!/usr/bin/env python3
"""Apply the M4 normalized-boundary gate without inventing missing keys."""

import argparse
import re
import struct
import sys
from collections import Counter, defaultdict

RSM_SIZE = 72
RSD_SIZE = 4160
MAPPED_PCS = (0x012C, 0x07F0)


def read_fixed(path, magic, size):
    rows = []
    with open(path, "rb") as stream:
        while True:
            raw = stream.read(size)
            if not raw:
                break
            if len(raw) != size or raw[:4] != magic:
                raise ValueError(f"invalid {magic.decode()} record in {path}")
            rows.append(raw)
    return rows


def retail_rows(mid_path, end_path, oracle_path):
    mids = read_fixed(mid_path, b"RSM1", RSM_SIZE)
    ends = read_fixed(end_path, b"RSD1", RSD_SIZE)
    phase_rows = []
    for line in open(oracle_path, encoding="utf-8", errors="replace"):
        m = re.search(r"\[rdp\] sync=(\d+) vi_origin=0x([0-9a-fA-F]+) vi_width=(\d+)", line)
        if m:
            phase_rows.append((int(m.group(1)), int(m.group(2), 16), int(m.group(3))))
    gfx_tasks = [struct.unpack_from("<4s3I", raw) for raw in ends if struct.unpack_from("<4s3I", raw)[3] == 1]
    if len(gfx_tasks) != len(phase_rows):
        raise ValueError(f"retail VI/task control failed: {len(phase_rows)} != {len(gfx_tasks)}")
    phase_by_task = {row[2]: (n, phase_rows[n][1], phase_rows[n][2]) for n, row in enumerate(gfx_tasks)}
    result = []
    for raw in mids:
        _, _, task, task_type, pc, step = struct.unpack_from("<4s5I", raw)
        if task_type != 1 or task not in phase_by_task or pc not in MAPPED_PCS:
            continue
        phase, origin, width = phase_by_task[task]
        if width != 512 or not (0x6AB000 <= origin < 0x6AC000):
            continue
        vacc = struct.unpack_from("<24h", raw, 24)
        result.append({
            "phase": phase, "image": None, "pc": pc,
            "progress": step, "lanes": tuple(i for i, v in enumerate(vacc) if (v & 0xFFFF) == 0x8000),
            "writer": None, "task": task, "end": False,
        })
    end_masks = {}
    for raw in ends:
        _, _, task, task_type = struct.unpack_from("<4s3I", raw)
        if task_type == 1 and task in phase_by_task and phase_by_task[task][2] == 512 and 0x6AB000 <= phase_by_task[task][1] < 0x6AC000:
            vacc = struct.unpack_from("<24h", raw, 16)
            end_masks[task] = tuple(i for i, v in enumerate(vacc) if (v & 0xFFFF) == 0x8000)
    for row in result:
        row["end"] = bool(end_masks.get(row["task"], ()))
    oracle_text = open(oracle_path, encoding="utf-8", errors="replace").read()
    return result, {"whole_rdram": "[hit]" in oracle_text,
                    "vi": bool(phase_rows), "mapped_pc": bool(result), "image": False}


def port_rows(path):
    rows = []
    controls = {"whole_rdram": False, "vi": False, "mapped_pc": False, "image": False}
    for line in open(path, encoding="utf-8", errors="replace"):
        if line.startswith("[m4-norm]"):
            fields = dict(re.findall(r"(\w+)=([^ ]+)", line))
            required = ("phase", "image", "pc", "progress", "end", "lanes")
            if not all(k in fields for k in required):
                continue
            pc = int(fields["pc"], 0)
            controls["mapped_pc"] |= pc in MAPPED_PCS
            controls["image"] |= fields["image"] not in ("none", "0", "missing")
            rows.append({"phase": int(fields["phase"], 0), "image": fields["image"],
                         "pc": pc, "progress": int(fields["progress"], 0),
                         "lanes": tuple(int(x, 0) for x in fields["lanes"].split(",") if x != "-"),
                         "writer": fields.get("writer"), "task": fields.get("task"),
                         "end": fields["end"] not in ("0", "false")})
        if "[m4-key]" in line:
            controls["vi"] |= "viw=512" in line and "origin=0x006AB" in line
            controls["mapped_pc"] |= any(f"pc=0x{x:04X}" in line for x in MAPPED_PCS)
    return rows, controls


def verdict(retail, port, rc_controls):
    reasons = []
    for arm, rows, controls in (("retail", retail[0], retail[1]), ("port", port[0], port[1])):
        if not controls["whole_rdram"]: reasons.append(f"{arm}: whole-RDRAM positive control absent")
        if not controls["vi"]: reasons.append(f"{arm}: VI positive control absent")
        if not controls["mapped_pc"]: reasons.append(f"{arm}: mapped-PC positive control absent")
        if not controls["image"] or any(row["image"] is None for row in rows): reasons.append(f"{arm}: ucode image identity absent")
        if not rows: reasons.append(f"{arm}: no normalized rows")
    joined = Counter((r["phase"], r["image"], r["pc"], r["progress"]) for r in retail[0])
    joined &= Counter((r["phase"], r["image"], r["pc"], r["progress"]) for r in port[0])
    for pc in MAPPED_PCS:
        if sum(n for key, n in joined.items() if key[2] == pc) < 20:
            reasons.append(f"pc=0x{pc:04X}: fewer than 20 shared normalized rows")
    if reasons:
        print("verdict=H3")
        for reason in reasons: print(f"reason={reason}")
        return 2
    print("verdict=H2" if any(r["writer"] for r in retail[0] + port[0]) else "verdict=H1")
    return 0


def self_test():
    controls = {k: True for k in ("whole_rdram", "vi", "mapped_pc", "image")}
    rows = [{"phase": n, "image": "f5", "pc": pc, "progress": n,
             "lanes": (), "writer": None, "task": n, "end": False}
            for pc in MAPPED_PCS for n in range(20)]
    assert verdict((rows, controls), (rows, controls), controls) == 0
    missing = dict(controls); missing["image"] = False
    assert verdict((rows, missing), (rows, controls), controls) == 2
    print("self-test=pass")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--retail", nargs=3, metavar=("RSM1", "RSD1", "ORACLE"))
    parser.add_argument("--port")
    args = parser.parse_args()
    if args.self_test:
        self_test(); return 0
    if not args.retail or not args.port:
        parser.error("--retail RSM1 RSD1 ORACLE and --port LOG are required")
    retail = retail_rows(*args.retail)
    port = port_rows(args.port)
    print(f"retail_rows={len(retail[0])} port_rows={len(port[0])}")
    print(f"retail_controls={retail[1]} port_controls={port[1]}")
    return verdict(retail, port, {})


if __name__ == "__main__":
    sys.exit(main())
