#!/usr/bin/env python3
"""Census generated $at/r1 values at control-flow joins.

The generated comments retain the MIPS instruction stream while the C below
them contains the recompiler's delay-slot normalization.  This audit finds
labels with multiple incoming branch/jump edges, then checks whether the
first r1 use after the join is preceded by an r1 write in the joined block.
It is deliberately a census, not a proof of runtime reachability.
"""

import argparse
import re
from collections import Counter, defaultdict
from pathlib import Path

FUNC_RE = re.compile(r"^RECOMP_FUNC\s+.*?\b([A-Za-z0-9_]+)\s*\([^\n]*\)\s*\{", re.M)
INS_RE = re.compile(r"^\s*//\s+(0x[0-9A-Fa-f]+):\s+([A-Za-z0-9_.]+)\s*(.*)$")
LABEL_RE = re.compile(r"^\s*(L_[0-9A-Fa-f]+):")
TARGET_RE = re.compile(r"\b(L_[0-9A-Fa-f]+)\b")
R1_RE = re.compile(r"ctx->r1\b")
R1_WRITE_RE = re.compile(r"\bctx->r1\s*=")
AT_RE = re.compile(r"\$at\b")
AT_DEST_RE = re.compile(r"^\s*(?:[A-Za-z0-9_.]+)\s+\$at(?:,|\s|$)")
BRANCHES = {
    "beq", "bne", "beql", "bnel", "beqz", "bnez", "beqzl", "bnezl",
    "blez", "bgtz", "bltz", "bgez", "blezl", "bgtzl", "bltzl", "bgezl",
    "bltzal", "bgezal", "bltzall", "bgezall", "j", "jal", "jr", "jalr",
    "b", "bal",
}


def line_no(text, pos):
    return text.count("\n", 0, pos) + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=None, help="directory containing funcs_*.c")
    args = ap.parse_args()
    if args.root:
        root = Path(args.root)
    else:
        root = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs"
    paths = sorted(root.glob("funcs_*.c"))
    if not paths:
        raise SystemExit(f"no generated files under {root}")

    counts = Counter()
    joins = []
    controls = {}

    for path in paths:
        text = path.read_text()
        functions = list(FUNC_RE.finditer(text))
        counts["functions"] += len(functions)
        for idx, fn in enumerate(functions):
            end = functions[idx + 1].start() if idx + 1 < len(functions) else len(text)
            body = text[fn.start():end]
            name = fn.group(1)
            ins = []
            labels = {}
            for m in re.finditer(r"(?m)^.*$", body):
                line = m.group(0)
                lm = LABEL_RE.match(line)
                if lm:
                    labels[lm.group(1)] = len(ins)
                im = INS_RE.match(line)
                if im:
                    ins.append({"addr": im.group(1), "mn": im.group(2),
                                "ops": im.group(3), "line": line_no(text, fn.start() + m.start())})
            counts["r1_writes"] += len(R1_WRITE_RE.findall(body))
            counts["r1_uses"] += len(R1_RE.findall(body))
            counts["at_comment_uses"] += sum(1 for item in ins if AT_RE.search(item["ops"]))
            counts["at_comment_writes"] += sum(1 for item in ins if AT_DEST_RE.search(item["mn"] + " " + item["ops"]))

            incoming = defaultdict(list)
            for pos, item in enumerate(ins):
                if item["mn"] not in BRANCHES:
                    continue
                target = TARGET_RE.search(item["ops"])
                if target and target.group(1) in labels:
                    incoming[target.group(1)].append((pos, item))
            for label, preds in incoming.items():
                if len(preds) < 2:
                    continue
                counts["joins"] += 1
                start = labels[label]
                window = ins[start:start + 12]
                first_use = next((n for n, item in enumerate(window) if AT_RE.search(item["ops"])), None)
                first_write = next((n for n, item in enumerate(window)
                                    if AT_DEST_RE.search(item["mn"] + " " + item["ops"])), None)
                if first_use is not None and (first_write is None or first_use < first_write):
                    counts["r1_use_before_join_write"] += 1
                    reason = "invalid-or-data-gap" if (name.startswith(("data_gap_", "fake_func_")) or
                                                         ".word" in window[first_use]["mn"] or
                                                         ".word" in window[first_use]["ops"] or
                                                         "InstrIdType" in window[first_use]["ops"]) else "fragment-needs-review"
                    joins.append((path.name, name, label, len(preds), window[first_use]["line"],
                                  window[first_use]["addr"], window[first_use]["mn"], window[first_use]["ops"], reason))
                if any(AT_RE.search(item["ops"]) for item in window):
                    counts["joins_touching_r1"] += 1

            if name in {"loadOverlay", "audioMixStereoBlock8", "fake_func_800B75C4"}:
                controls[name] = {
                    "r1_writes": len(R1_WRITE_RE.findall(body)),
                    "labels": len(labels),
                    "joins": sum(1 for p in incoming.values() if len(p) >= 2),
                }

    print(f"root={root}")
    print(f"files={len(paths)} functions={counts['functions']} r1_writes={counts['r1_writes']} r1_uses={counts['r1_uses']} at_comment_uses={counts['at_comment_uses']} at_comment_writes={counts['at_comment_writes']}")
    print(f"joins={counts['joins']} joins_touching_r1={counts['joins_touching_r1']} r1_use_before_join_write={counts['r1_use_before_join_write']}")
    print("suspect_reason_counts=" + ", ".join(f"{k}:{v}" for k, v in sorted(Counter(row[-1] for row in joins).items())))
    for name in ("loadOverlay", "audioMixStereoBlock8", "fake_func_800B75C4"):
        print(f"control_{name}={controls.get(name, 'MISSING')}")
    for row in joins[:80]:
        print("SUSPECT", *row)
    if joins:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
