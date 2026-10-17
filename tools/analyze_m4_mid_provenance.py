#!/usr/bin/env python3
import re
import struct
import sys
from collections import Counter, defaultdict


def read_mid(path):
    record_size = 68
    records = []
    bad = 0
    with open(path, "rb") as stream:
        offset = 0
        while True:
            record = stream.read(record_size)
            if not record:
                break
            if len(record) != record_size:
                bad += 1
                break
            magic, seq, task_type, pc, step = struct.unpack_from("<4sIIII", record)
            if magic != b"RSM1":
                bad += 1
                offset += record_size
                continue
            vacc = struct.unpack_from("<24h", record, 20)
            lanes = [i for i, value in enumerate(vacc) if (value & 0xFFFF) == 0x8000]
            records.append((seq, task_type, pc, step, lanes))
            offset += record_size
    return records, bad


def read_end(path):
    record_size = 4156
    records = []
    bad = 0
    with open(path, "rb") as stream:
        while True:
            record = stream.read(record_size)
            if not record:
                break
            if len(record) != record_size:
                bad += 1
                break
            magic, seq, task_type = struct.unpack_from("<4sII", record)
            if magic != b"RSD1":
                bad += 1
                continue
            vacc = struct.unpack_from("<24h", record, 12)
            records.append((seq, task_type, sum((value & 0xFFFF) == 0x8000 for value in vacc)))
    return records, bad


def monotonic(sequences):
    return all(b == a + 1 for a, b in zip(sequences, sequences[1:]))


def oracle_512_tasks(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    matches = re.findall(r"(?:width|viw)[ =:]+512", text, re.IGNORECASE)
    return len(matches)


def main(mid_path, end_path, oracle_path):
    mid, mid_bad = read_mid(mid_path)
    end, end_bad = read_end(end_path)
    sequences = [row[0] for row in mid]
    task_types = Counter(row[1] for row in mid)
    pc_hits = Counter()
    step_hits = Counter()
    sample_hits = Counter()
    for seq, task_type, pc, step, lanes in mid:
        if lanes:
            pc_hits[pc] += len(lanes)
            step_hits[step] += len(lanes)
            sample_hits[seq] += len(lanes)
    end_gfx = [row for row in end if row[1] == 1]
    end_hit_tasks = sum(row[2] > 0 for row in end_gfx)
    print(f"mid_records={len(mid)} mid_sample_ordinals={len({row[0] for row in mid})} mid_bad={mid_bad}")
    print(f"mid_type_counts={dict(sorted(task_types.items()))}")
    print(f"mid_seq_monotonic={monotonic(sequences)} seq_first={sequences[0] if sequences else 'NA'} seq_last={sequences[-1] if sequences else 'NA'}")
    print(f"mid_8000_records={sum(bool(row[4]) for row in mid)} mid_8000_lanes={sum(len(row[4]) for row in mid)}")
    print("pc_hits=" + ",".join(f"0x{pc:04X}:{count}" for pc, count in pc_hits.most_common(20)))
    print("step_hits=" + ",".join(f"{step}:{count}" for step, count in step_hits.most_common(20)))
    print("sample_hit_hist=" + ",".join(f"{count}:{n}" for count, n in sorted(Counter(sample_hits.values()).items())))
    print(f"end_records={len(end)} end_gfx={len(end_gfx)} end_bad={end_bad} end_gfx_8000_tasks={end_hit_tasks}")
    print(f"oracle_width512_mentions={oracle_512_tasks(oracle_path)}")
    if not mid or not end or mid_bad or end_bad or not monotonic(sequences):
        raise SystemExit("positive control failed")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("usage: analyze_m4_mid_provenance.py MID.dump END.dump ORACLE.log")
    main(*sys.argv[1:])
