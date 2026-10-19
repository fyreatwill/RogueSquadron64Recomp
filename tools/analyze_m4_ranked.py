#!/usr/bin/env python3
"""Compare M4 lane masks without requiring portable progress values.

The two captures are independent runs, so the task-local progress counter is
not a join key.  Rows are retained under the existing phase/image/PC key, then
each key's rows are divided into fixed rank bins.  A bin is represented by the
most common lane mask in each arm; this avoids treating a different sampling
density as a value divergence.
"""

import argparse
import sys
from collections import Counter, defaultdict

import analyze_m4_normalized as normalized

MAPPED_PCS = normalized.MAPPED_PCS
BIN_COUNT = 16
MIN_BINS_PER_PC = 4
MIN_MATCH_RATE = 0.80


def rank_bins(rows):
    groups = defaultdict(list)
    for row in rows:
        if row["image"] is None:
            continue
        key = (row["phase"], row["image"], row["pc"])
        groups[key].append(row["lanes"])
    binned = {}
    for key, lanes in groups.items():
        bins = defaultdict(list)
        last = max(len(lanes) - 1, 1)
        for rank, lane_mask in enumerate(lanes):
            bucket = min(BIN_COUNT - 1, (rank * BIN_COUNT) // last)
            bins[bucket].append(lane_mask)
        binned[key] = {
            bucket: Counter(masks).most_common(1)[0][0]
            for bucket, masks in bins.items()
        }
    return binned


def compare(retail_rows, port_rows):
    retail = rank_bins(retail_rows)
    port = rank_bins(port_rows)
    table = []
    by_pc = defaultdict(lambda: {"bins": 0, "same": 0, "groups": 0})
    retail_by_pc = defaultdict(list)
    port_by_pc = defaultdict(list)
    for key in sorted(retail, key=str):
        retail_by_pc[key[2]].append(key)
    for key in sorted(port, key=str):
        port_by_pc[key[2]].append(key)
    for pc in MAPPED_PCS:
        paired = zip(retail_by_pc[pc], port_by_pc[pc])
        for ordinal, (retail_key, port_key) in enumerate(paired):
            common = sorted(set(retail[retail_key]) & set(port[port_key]))
            if common:
                by_pc[pc]["groups"] += 1
            for bucket in common:
                same = retail[retail_key][bucket] == port[port_key][bucket]
                stats = by_pc[pc]
                stats["bins"] += 1
                stats["same"] += int(same)
                table.append((ordinal, retail_key[1], port_key[1], pc, bucket, same,
                              retail[retail_key][bucket], port[port_key][bucket]))
    return table, by_pc


def print_table(table, by_pc):
    print("rank_bins=%d" % BIN_COUNT)
    print("ordinal retail_image port_image pc bin same retail_lanes port_lanes")
    for ordinal, retail_image, port_image, pc, bucket, same, retail_lanes, port_lanes in table:
        print("%d %s %s 0x%04X %d %d %s %s" %
              (ordinal, retail_image, port_image, pc, bucket, int(same),
               ",".join(map(str, retail_lanes)) or "-",
               ",".join(map(str, port_lanes)) or "-"))
    for pc in MAPPED_PCS:
        stats = by_pc[pc]
        rate = stats["same"] / stats["bins"] if stats["bins"] else 0.0
        print("summary pc=0x%04X groups=%d bins=%d same=%d rate=%.3f" %
              (pc, stats["groups"], stats["bins"], stats["same"], rate))


def verdict(retail, port):
    reasons = []
    for arm, rows, controls in (("retail", *retail), ("port", *port)):
        if not controls["whole_rdram"]:
            reasons.append("%s: whole-RDRAM positive control absent" % arm)
        if not controls["vi"]:
            reasons.append("%s: VI positive control absent" % arm)
        if not controls["mapped_pc"]:
            reasons.append("%s: mapped-PC positive control absent" % arm)
        if not controls["image"] or any(row["image"] is None for row in rows):
            reasons.append("%s: ucode image identity absent" % arm)
        if not rows:
            reasons.append("%s: no normalized rows" % arm)
    retail_rows = [row for row in retail[0]
                   if row["viw"] == 512 and 0x6AB000 <= row["origin"] < 0x6AC000]
    port_rows = [row for row in port[0]
                 if row["viw"] == 512 and 0x6AB000 <= row["origin"] < 0x6AC000]
    print("rank_scope retail_rows=%d port_rows=%d" % (len(retail_rows), len(port_rows)))
    table, by_pc = compare(retail_rows, port_rows)
    print_table(table, by_pc)
    for pc in MAPPED_PCS:
        if by_pc[pc]["bins"] < MIN_BINS_PER_PC:
            reasons.append("pc=0x%04X: fewer than %d shared rank bins" %
                           (pc, MIN_BINS_PER_PC))
        if not any(pc == row[3] and (row[6] or row[7]) for row in table):
            reasons.append("pc=0x%04X: lane discriminator had no active masks" % pc)
    if reasons:
        print("verdict=H3")
        for reason in reasons:
            print("reason=" + reason)
        return 2
    rates = [by_pc[pc]["same"] / by_pc[pc]["bins"] for pc in MAPPED_PCS]
    if all(rate >= MIN_MATCH_RATE for rate in rates):
        print("verdict=H1")
    else:
        print("verdict=H2")
    return 0


def self_test():
    controls = {name: True for name in ("whole_rdram", "vi", "mapped_pc", "image")}
    rows = []
    for pc in MAPPED_PCS:
        for rank in range(32):
            rows.append({"phase": 1, "image": "f5", "pc": pc,
                         "lanes": (rank % 3,), "progress": rank,
                         "viw": 512, "origin": 0x6AB000})
    assert rank_bins(rows)[(1, "f5", MAPPED_PCS[0])][0] == (0,)
    assert verdict((rows, controls), (rows, controls)) == 0
    mismatch = [dict(row, lanes=(99,)) if row["pc"] == MAPPED_PCS[1]
                else row for row in rows]
    assert verdict((rows, controls), (mismatch, controls)) == 0
    print("self-test=pass")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--retail", nargs=3, metavar=("RSM", "RSD", "ORACLE"))
    parser.add_argument("--port")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if not args.retail or not args.port:
        parser.error("--retail RSM RSD ORACLE and --port LOG are required")
    retail = normalized.retail_rows(*args.retail)
    port = normalized.port_rows(args.port)
    print("retail_rows=%d port_rows=%d" % (len(retail[0]), len(port[0])))
    print("retail_controls=%s port_controls=%s" % (retail[1], port[1]))
    return verdict(retail, port)


if __name__ == "__main__":
    sys.exit(main())
