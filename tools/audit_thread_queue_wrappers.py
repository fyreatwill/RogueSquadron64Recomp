#!/usr/bin/env python3
"""Census guest-pointer handling in thread and message-queue wrappers."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

FILES = (
    "lib/N64ModernRuntime/librecomp/src/ultra_translation.cpp",
    "lib/N64ModernRuntime/ultramodern/src/threads.cpp",
    "lib/N64ModernRuntime/ultramodern/src/mesgqueue.cpp",
)
TARGETS = {
    "osCreateThread", "osStartThread", "osDestroyThread",
    "osCreateMesgQueue", "osRecvMesg", "osSendMesg", "osJamMesg",
    "do_send", "do_recv",
}
FUNCTION = re.compile(
    r"(?m)^\s*(?:extern \"C\" )?(?:__attribute__\(\([^\n]+\)\) )?"
    r"(?:static )?(?:[\w:<>*&]+\s+)+(?P<name>[A-Za-z_][A-Za-z0-9_]*)"
    r"\s*\([^\n]*\)\s*\{"
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
    body = body[body.find("{") + 1:]
    if "assert(false)" in body or "return;" in body and name == "osYieldThread":
        return "intentional assert/no-op"
    if "TO_PTR" in body or "MEM_" in body or "PTR(" in body:
        return "translated/range-checked callee"
    if re.search(r"\b(?:osCreateThread|osStartThread|osDestroyThread|"
                 r"osCreateMesgQueue|osRecvMesg|osSendMesg|osJamMesg)\s*\(", body):
        return "forwarded to runtime callee"
    if re.search(r"\*\s*\w+\s*=|\(\s*\w+\s*\*\s*\)\s*(?:ctx->|rdram)", body):
        return "raw-dereferenced"
    return "no pointer dereference observed"


def scan(root: pathlib.Path):
    rows = []
    for rel in FILES:
        path = root / rel
        if not path.exists():
            continue
        for name, body in blocks(path.read_text(errors="replace")):
            rows.append((rel, name, classify(name, body)))
    return rows


def selftest() -> int:
    sample = """
    void osCreateThread(uint8_t* r, recomp_context* c) { auto p = MEM_W(0x10, c->r29); *p = 1; }
    void osStartThread(uint8_t* r, int t) { osStartThread(r, t); }
    void osRecvMesg(uint8_t* r, recomp_context* c) { int* p = (int*)c->r4; *p = 1; }
    void osSendMesg(uint8_t* r, recomp_context* c) { assert(false); }
    """
    got = [(name, classify(name, body)) for name, body in blocks(sample)]
    expected = [
        ("osCreateThread", "translated/range-checked callee"),
        ("osStartThread", "forwarded to runtime callee"),
        ("osRecvMesg", "raw-dereferenced"),
        ("osSendMesg", "intentional assert/no-op"),
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
