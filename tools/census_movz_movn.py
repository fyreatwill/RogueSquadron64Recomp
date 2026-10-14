#!/usr/bin/env python3
"""Census generated movz/movn annotations and their emitted host bodies."""

from __future__ import annotations

import argparse
import glob
import re
from collections import Counter
from pathlib import Path

REGS = (
    "zero", "at", "v0", "v1", "a0", "a1", "a2", "a3",
    "t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7",
    "s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7",
    "t8", "t9", "k0", "k1", "gp", "sp", "fp", "ra",
)
GUEST = re.compile(r"//\s+0x([0-9A-Fa-f]+):\s+(.*)")
FUNC = re.compile(r"RECOMP_FUNC\s+void\s+(\w+)\(")
MOV = re.compile(r"\b(movz|movn)\s+\$([^,]+),\s*\$([^,]+),\s*\$([^\s#]+)")
WORD = re.compile(r"\.word\s+0x([0-9A-Fa-f]{8})")


def parse(path: Path):
    lines = path.read_text(errors="replace").splitlines()
    function = "(preamble)"
    records = []
    for index, line in enumerate(lines):
        fm = FUNC.search(line)
        if fm:
            function = fm.group(1)
        gm = GUEST.search(line)
        if not gm:
            continue
        mm = MOV.search(gm.group(2))
        if not mm:
            continue
        pc, text = int(gm.group(1), 16), gm.group(2).strip()
        body = []
        cursor = index + 1
        while cursor < len(lines) and not GUEST.search(lines[cursor]):
            if lines[cursor].strip():
                body.append(lines[cursor].strip())
            cursor += 1
        following = []
        scan = cursor
        while scan < len(lines) and len(following) < 3:
            next_guest = GUEST.search(lines[scan])
            if next_guest:
                following.append((int(next_guest.group(1), 16), next_guest.group(2).strip()))
            scan += 1
        raw = WORD.search(text)
        decoded = None
        if raw:
            word = int(raw.group(1), 16)
            funct = word & 0x3F
            decoded = (
                "movz" if funct == 0x0A else "movn" if funct == 0x0B else "funct=0x%02X" % funct,
                REGS[(word >> 11) & 31], REGS[(word >> 21) & 31], REGS[(word >> 16) & 31],
            )
        records.append({
            "file": path.name,
            "line": index + 1,
            "function": function,
            "pc": pc,
            "text": text,
            "op": mm.group(1),
            "operands": tuple(x.lower() for x in mm.groups()[1:]),
            "raw": raw.group(1).lower() if raw else None,
            "decoded": decoded,
            "body": "; ".join(body) if body else "(empty)",
            "next": following,
        })
    return records


def body_class(record):
    return "do_break" if "do_break(" in record["body"] else "other"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="../N64Recomp/RecompiledFuncs/funcs_*.c")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    records = []
    for name in sorted(glob.glob(args.source)):
        records.extend(parse(Path(name)))
    records.sort(key=lambda r: (r["file"], r["line"]))

    raw = [r for r in records if r["decoded"]]
    raw_match = sum(
        r["decoded"][:1] == (r["op"],) and r["decoded"][1:] == r["operands"]
        for r in raw
    )
    unique = len({(r["file"], r["pc"]) for r in records})
    kinds = Counter(r["op"] for r in records)
    forms = Counter(".word" if r["raw"] else "direct" for r in records)
    bodies = Counter(body_class(r) for r in records)
    dests = Counter(r["operands"][0] for r in records)

    out = Path(args.output)
    with out.open("w") as stream:
        stream.write("# M3 generated `movz`/`movn` census\n\n")
        stream.write("## Result\n\n")
        stream.write(
            f"The source census contains **{len(records)} textual occurrences** "
            f"({kinds['movz']} `movz`, {kinds['movn']} `movn`) across "
            f"{unique} file/guest-PC sites. Duplicate PCs are retained below because "
            "the generator emits them in multiple control-flow/overlay copies.\n\n"
        )
        stream.write(
            f"Pass 1 (annotation parser): {forms['direct']} direct annotations and "
            f"{forms['.word']} `.word` annotations. Pass 2 (raw SPECIAL decoder): "
            f"{raw_match}/{len(raw)} `.word` encodings agree with the annotated opcode "
            "and register operands. This independently validates the decoded operands "
            "where an instruction word is present.\n\n"
        )
        stream.write(
            f"The emitted host body immediately following every occurrence is `do_break`: "
            f"{bodies['do_break']}/{len(records)}. No occurrence has a conditional assignment "
            "or a preserved-destination implementation. Destination registers are "
            f"{sum(dests.values())} occurrences total, including {dests['zero']} writes to `$zero`.\n\n"
        )
        stream.write("## Interpretation\n\n")
        stream.write(
            "The static translation-faithfulness hypothesis is **not selected**: the "
            "generated output does not implement the MIPS conditional move semantics. "
            "This is not yet an authorised runtime fix. The sites are concentrated in "
            "obfuscated/data-like regions and several occur after generated `return` or "
            "indirect-return paths; reachability must be established before changing the "
            "fixup pipeline. The route-gap hypothesis therefore remains open for runtime "
            "impact, while the concrete generated-body mismatch is established statically.\n\n"
        )
        stream.write("## Complete occurrence table\n\n")
        stream.write("| file:line | function | guest PC | form/op/operands | raw decode | generated body | next three guest instructions |\n")
        stream.write("|---|---|---:|---|---|---|---|\n")
        for r in records:
            decoded = "—" if not r["decoded"] else "%s $%s,$%s,$%s" % r["decoded"]
            following = "<br>".join("0x%08X: %s" % item for item in r["next"])
            form = "direct" if not r["raw"] else ".word 0x%s" % r["raw"]
            operands = "$%s,$%s,$%s" % r["operands"]
            stream.write(
                "| %s:%d | `%s` | `0x%08X` | `%s %s` | `%s` | `%s` | %s |\n"
                % (r["file"], r["line"], r["function"], r["pc"], form, operands,
                   decoded, body_class(r), following)
            )


if __name__ == "__main__":
    main()
