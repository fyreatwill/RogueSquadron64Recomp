#!/usr/bin/env python3
"""Census guest-pointer handling in time and interrupt wrappers."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

FILES = (
    "lib/N64ModernRuntime/librecomp/src/ultra_translation.cpp",
    "lib/N64ModernRuntime/ultramodern/src/timer.cpp",
)
TARGETS = {"osGetCount", "osGetTime", "osSetTime", "osSetCount", "osSetIntMask"}
FUNCTION = re.compile(
    r'(?m)^\s*(?:extern "C" )?(?:static )?(?:[\w:<>*&]+\s+)+'
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\([^\n]*\)\s*\{"
)


def blocks(text: str):
    for match in FUNCTION.finditer(text):
        name = match.group("name")
        if name.removesuffix("_recomp") not in TARGETS:
            continue
        depth = 0
        end = match.end() - 1
        for pos in range(end, len(text)):
            if text[pos] == "{":
                depth += 1
            elif text[pos] == "}":
                depth -= 1
                if depth == 0:
                    yield name, text[match.start():pos + 1]
                    break


def classify(name: str, body: str) -> str:
    base = name.removesuffix("_recomp")
    if base == "osSetIntMask":
        return "intentional no-op"
    if base in {"osGetCount", "osGetTime", "osSetCount", "osSetTime"}:
        if "MEM_" in body or "TO_PTR" in body:
            return "translated/range-checked callee"
        if re.search(r"\*\s*\w+\s*=|\(\s*\w+\s*\*\s*\)", body):
            return "raw-dereferenced"
        return "host scalar/time handling, no guest dereference"
    if "MEM_" in body or "TO_PTR" in body or "PTR(" in body:
        return "translated/range-checked callee"
    if re.search(r"\*\s*\w+\s*=|\(\s*\w+\s*\*\s*\)\s*(?:ctx->|rdram)", body):
        return "raw-dereferenced"
    return "no pointer dereference observed"


def scan(root: pathlib.Path):
    rows = []
    found = set()
    for rel in FILES:
        path = root / rel
        if not path.exists():
            continue
        for name, body in blocks(path.read_text(errors="replace")):
            found.add(name.removesuffix("_recomp"))
            rows.append((rel, name, classify(name, body)))
    for target in sorted(TARGETS - found):
        rows.append(("<searched sources>", target, "not found"))
    return rows


def selftest() -> int:
    sample = """
    void osGetTime_recomp(uint8_t* r, recomp_context* c) { return time_now(); }
    void osSetIntMask_recomp(uint8_t* r, recomp_context* c) { ; }
    void osSetCount_recomp(uint8_t* r, recomp_context* c) { int* p = (int*)c->r4; *p = 1; }
    void osSetTime_recomp(uint8_t* r, recomp_context* c) { auto p = TO_PTR(int, c->r4); *p = 1; }
    """
    got = [(name, classify(name, body)) for name, body in blocks(sample)]
    expected = [
        ("osGetTime_recomp", "host scalar/time handling, no guest dereference"),
        ("osSetIntMask_recomp", "intentional no-op"),
        ("osSetCount_recomp", "raw-dereferenced"),
        ("osSetTime_recomp", "translated/range-checked callee"),
    ]
    print("positive-control rows:", len(got), "expected:", len(expected))
    print("synthetic classifications:", got)
    return 0 if got == expected else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    rows = scan(pathlib.Path(args.root))
    for rel, name, result in rows:
        print(f"{rel}:{name}: {result}")
    counts = {}
    for _, _, result in rows:
        counts[result] = counts.get(result, 0) + 1
    print("summary:", ", ".join(f"{key}={counts[key]}" for key in sorted(counts)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
