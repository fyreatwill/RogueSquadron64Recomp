#!/usr/bin/env python3
"""Audit the retained image-stage nonzero and range-join evidence."""

import csv
import sys
from collections import defaultdict
from pathlib import Path


def rows(path):
    with path.open(newline="", errors="replace") as stream:
        yield from csv.DictReader(stream, delimiter="\t")


def main(root):
    root = Path(root)
    summary = list(rows(root / "ordinal-summary.tsv"))
    comparison = list(rows(root / "range-matcher-comparison.tsv"))
    stages = {}
    for row in comparison:
        key = (row["arm"], row["phase"], row["width"], row["origin"],
               row["stage_event"])
        stages[key] = row

    print("controls")
    for row in summary:
        print(f"{row['arm']} controls={row['controls']} crash={row['crash']} "
              f"abort={row['abort']} task_dma_rows={row['task_dma_rows']} "
              f"render_rows={row['render_rows']}")

    by_scope = defaultdict(lambda: defaultdict(int))
    for row in stages.values():
        scope = (row["arm"], row["phase"], row["width"], row["origin"])
        by_scope[scope]["stages"] += 1
        by_scope[scope]["stage_nz_zero"] += row["stage_nz"] == "0"
        by_scope[scope]["stage_nz_positive"] += row["stage_nz"] != "0"
        by_scope[scope]["stage_matchable"] += row["stage_matchable"] == "1"
        by_scope[scope]["same_range"] += row["same_range"] == "1"
        by_scope[scope]["conflict"] += row["same_range"] == "-1"
        if row["stage_nz"] != row["dma_nz"]:
            by_scope[scope]["stage_dma_nz_disagree"] += 1

    print("stage-table")
    for scope in sorted(by_scope):
        counts = by_scope[scope]
        print(" ".join(map(str, scope)),
              " ".join(f"{k}={counts[k]}" for k in sorted(counts)))

    # The retained comparison has no payload bytes, so a byte-level
    # recomputation is intentionally reported as unavailable rather than
    # inferred from a hash or from the nonzero field itself.
    print("payload-recompute unavailable=1 reason=retained_rows_have_hash_and_nz_only")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: s2390_audit_stage_nonzero.py ARTIFACT_DIR")
    main(sys.argv[1])
