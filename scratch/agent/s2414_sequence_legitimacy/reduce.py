#!/usr/bin/env python3
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

IDENTITY = re.compile(r"\[m5-identity-table\] (.*)")
FIELD = re.compile(r"(\w+)=([^ ]+)")


def parse(path):
    rows = []
    controls = {"title": False, "hangar": False, "keyon": False}
    with open(path, errors="replace") as stream:
        for line in stream:
            if "width=1024" in line and "origin=0x00790400" in line:
                controls["title"] = True
            if "width=512" in line and "origin=0x006AB400" in line:
                controls["hangar"] = True
            if "[m5-audio-event] kind=keyon-w40" in line:
                controls["keyon"] = True
            match = IDENTITY.search(line)
            if not match:
                continue
            fields = dict(FIELD.findall(match.group(1)))
            rows.append({
                "phase": int(fields["stage_phase"]),
                "stage_width": int(fields["stage_width"]),
                "stage_origin": fields["stage_origin"].lower(),
                "stage": int(fields["stage"]),
                "stage_event": int(fields["stage_event"]),
                "keyon_event": int(fields["keyon_event"]),
                "event_phase": int(fields["event_phase"]),
                "event_width": int(fields["event_width"]),
                "event_origin": fields["event_origin"].lower(),
                "stage_ordinal": int(fields["stage_ordinal"]),
                "stage_row": int(fields["stage_row"]),
                "event_ordinal": int(fields["event_ordinal"]),
                "event_row": int(fields["event_row"]),
                "phase_key": int(fields["phase_key"]),
                "ordinal_key": int(fields["ordinal_key"]),
                "sequence_key": int(fields["sequence_key"]),
                "class": int(fields["class"]),
            })
    return rows, controls


def describe(rows):
    by_capture = Counter()
    by_phase = Counter()
    by_class = Counter()
    by_partition = Counter()
    deltas = defaultdict(list)
    for row in rows:
        cls = row["class"]
        capture = row["capture"]
        phase = row["phase"]
        route_equal = (row["stage_ordinal"] == row["event_ordinal"] and
                       row["stage_row"] == row["event_row"])
        ordering = ("after" if row["keyon_event"] > row["stage_event"] else
                    "same" if row["keyon_event"] == row["stage_event"] else "before")
        partition = (capture, phase, "route-equal" if route_equal else "route-different", ordering)
        by_capture[capture] += 1
        by_phase[(capture, phase)] += 1
        by_class[(capture, cls)] += 1
        by_partition[partition] += 1
        if cls in (5, 7):
            deltas[(capture, phase, cls, "route-equal" if route_equal else "route-different", ordering)].append(
                row["keyon_event"] - row["stage_event"])

    print("identity rows by capture:", dict(sorted(by_capture.items())))
    print("identity rows by capture/phase:", dict(sorted(by_phase.items())))
    print("identity rows by capture/class:", dict(sorted(by_class.items())))
    print("all-row route/order partitions:")
    for key, count in sorted(by_partition.items()):
        print(f"  {key}: count={count}")
    print("selected class 5/7 event-delta table:")
    if not deltas:
        print("  EMPTY")
    for key, values in sorted(deltas.items()):
        print(f"  {key}: count={len(values)} min_delta={min(values)} max_delta={max(values)} deltas={values}")
    print("selected class 5/7 rows:")
    for row in sorted(rows, key=lambda item: (item["capture"], item["stage_event"], item["stage"])):
        if row["class"] not in (5, 7):
            continue
        route_equal = (row["stage_ordinal"] == row["event_ordinal"] and
                       row["stage_row"] == row["event_row"])
        ordering = ("after" if row["keyon_event"] > row["stage_event"] else
                    "same" if row["keyon_event"] == row["stage_event"] else "before")
        print("  capture=%s phase=%d stage=%d stage_event=%d keyon_event=%d "
              "route_stage=%d/%d route_keyon=%d/%d delta=%d class=%d "
              "route=%s ordering=%s" %
              (row["capture"], row["phase"], row["stage"], row["stage_event"],
               row["keyon_event"], row["stage_ordinal"], row["stage_row"],
               row["event_ordinal"], row["event_row"],
               row["keyon_event"] - row["stage_event"], row["class"],
               "equal" if route_equal else "different", ordering))


def main(argv):
    if len(argv) != 3:
        raise SystemExit("usage: reduce.py LOG2412 LOG2413")
    output = Path("scratch/agent/s2414_sequence_legitimacy")
    output.mkdir(parents=True, exist_ok=True)
    all_rows = []
    for path in argv[1:]:
        rows, controls = parse(path)
        missing = [name for name, present in controls.items() if not present]
        if missing:
            raise SystemExit(f"route-invalid {path}: missing controls {','.join(missing)}")
        capture = "s2412" if "s2412" in path else "s2413"
        for row in rows:
            row["capture"] = capture
        all_rows.extend(rows)
        print(f"control {capture}: rows={len(rows)} title=1 hangar=1 keyon=1")
    describe(all_rows)
    with open(output / "summary.txt", "w") as saved:
        old = sys.stdout
        sys.stdout = saved
        for path in argv[1:]:
            rows, _ = parse(path)
            capture = "s2412" if "s2412" in path else "s2413"
            for row in rows:
                row["capture"] = capture
        describe(all_rows)
        sys.stdout = old


if __name__ == "__main__":
    main(sys.argv)
