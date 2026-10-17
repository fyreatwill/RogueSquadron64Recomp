#!/usr/bin/env python3
"""Join cxd4 mid-task VACC samples to their per-task completion records."""

import struct
import sys
from collections import defaultdict

RSM_SIZE = 72  # magic, sample seq, task serial, type, PC, step, 24 i16s
RSD_SIZE = 4160  # magic, dump seq, task serial, type, 24 i16s, 4096 DMEM


def records(path, magic, size):
    data = open(path, "rb").read()
    if len(data) % size:
        raise ValueError(f"{path}: {len(data)} bytes is not a multiple of {size}")
    for off in range(0, len(data), size):
        rec = data[off : off + size]
        if rec[:4] != magic:
            raise ValueError(f"{path}: bad magic at offset {off}")
        yield rec


def main():
    if len(sys.argv) != 4:
        raise SystemExit("usage: analyze_m4_task_join.py MID.dump RSP.dump oracle.log")
    mid_path, rsp_path, log_path = sys.argv[1:]

    mids = defaultdict(list)
    for rec in records(mid_path, b"RSM1", RSM_SIZE):
        _, sample_seq, task_serial, task_type, pc, step = struct.unpack_from("<4s5I", rec)
        vacc = struct.unpack_from("<24h", rec, 24)
        if task_type == 1:
            mids[task_serial].append((sample_seq, pc, step, vacc))

    ends = {}
    for rec in records(rsp_path, b"RSD1", RSD_SIZE):
        _, dump_seq, task_serial, task_type = struct.unpack_from("<4s3I", rec)
        vacc = struct.unpack_from("<24h", rec, 16)
        if task_type == 1:
            ends[task_serial] = (dump_seq, vacc)

    joined = sorted(set(mids) & set(ends))
    bad = sorted(set(mids) - set(ends))
    with_8000 = []
    for serial in joined:
        samples = mids[serial]
        lanes = [lane for _, _, _, vacc in samples for lane in vacc if lane == -32768]
        pcs = sorted({pc for _, pc, _, _ in samples})
        if lanes:
            with_8000.append((serial, len(samples), len(lanes), pcs,
                              samples[0][2], samples[-1][2], ends[serial][1]))

    log = open(log_path, "r", errors="replace").read()
    vi_controls = log.count("WIDTH")
    watch_controls = log.count("hit(s)")
    end_with_8000 = sum(any(lane == -32768 for lane in vacc)
                         for _, vacc in ends.values())
    print(f"mid_records={sum(map(len, mids.values()))} graphics_tasks_with_mid={len(mids)}")
    print(f"end_graphics_tasks={len(ends)} joined_tasks={len(joined)} unmatched_mid={len(bad)}")
    print(f"joined_with_8000={len(with_8000)}")
    print(f"vi_width_controls={vi_controls} whole_rdram_controls={watch_controls}")
    print(f"end_tasks_with_8000={end_with_8000} end_tasks_zero_8000={len(ends) - end_with_8000}")
    if not mids or not ends or not joined or not vi_controls or not watch_controls:
        print("H3: controls or task-keyed join failed")
        return 2
    if with_8000:
        pcs = sorted({pc for _, _, _, pcs, _, _, _ in with_8000 for pc in pcs})
        print(f"8000_pcs={','.join(f'0x{x:04X}' for x in pcs)}")
        print("H1/H2 discriminator: task-keyed retail 0x8000 samples are present; compare distribution to port")
    else:
        print("H2: task-keyed retail samples contain no 0x8000 lanes")


if __name__ == "__main__":
    main()
