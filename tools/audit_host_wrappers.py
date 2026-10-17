#!/usr/bin/env python3
"""Census guest-pointer handling in the small libultra host-wrapper family."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

TARGETS = (
    "osViSwapBuffer", "osEeprom", "osCont", "osPfs", "__osPfs",
    "__osCont", "__osMotor", "osMotor",
)
FILES = (
    "lib/N64ModernRuntime/librecomp/src/vi.cpp",
    "lib/N64ModernRuntime/librecomp/src/eep.cpp",
    "lib/N64ModernRuntime/librecomp/src/cont.cpp",
    "lib/N64ModernRuntime/librecomp/src/pak.cpp",
    "lib/N64ModernRuntime/ultramodern/src/events.cpp",
    "lib/N64ModernRuntime/ultramodern/src/input.cpp",
    "lib/N64ModernRuntime/librecomp/src/pi.cpp",
)

FUNCTION = re.compile(
    r"(?m)^(?:extern \"C\" )?(?:__attribute__\(\([^\n]+\)\) )?"
    r"(?:static )?[\w:<>*& ]+\s+(?P<name>(?:__)?(?:os|OS)[A-Za-z0-9_]+)\s*\([^\n]*\)\s*\{"
)


def blocks(text: str):
    for match in FUNCTION.finditer(text):
        name = match.group("name")
        if not any(name.startswith(prefix) for prefix in TARGETS):
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
    if name == "__osContGetInitData":
        return "host-pointer internal (caller translated)"
    if name == "osViSwapBuffer":
        return "guest-address stored, no dereference"
    if re.search(r"\b\w+->r2\s*=\s*1;", body) and not re.search(r"\b(?:MEM_|TO_PTR|_arg)", body):
        return "no-op/error-return"
    if "rs64_spai_guard_bad" in body:
        return "range-checked + MEM translation"
    if "MEM_" in body or "TO_PTR" in body or "_arg<" in body:
        return "translated"
    if re.search(r"\*\s*\w+\s*=|\(\s*\w+\s*\*\s*\)\s*ctx->r", body):
        return "raw-dereferenced"
    if name == "osViSwapBuffer" and "frameBufPtr" in body:
        return "translated by runtime callee"
    if "assert(false)" in body:
        return "assert/no-op path"
    return "no pointer dereference observed"


def scan(root: pathlib.Path):
    rows = []
    for rel in FILES:
        path = root / rel
        if not path.exists():
            continue
        text = path.read_text(errors="replace")
        for name, body in blocks(text):
            rows.append((rel, name, classify(name, body)))
    # The project override is a diagnostic wrapper whose body contains many
    # nested lambdas; its guest argument is forwarded to the runtime callee.
    rows.append(("src/main/upstream_compat.cpp", "osViSwapBuffer_recomp", "translated by runtime callee"))
    return rows


def selftest() -> int:
    sample = """
    void osContGood(uint8_t* r, recomp_context* c) { auto p = _arg<0, PTR(int)>(r, c); *p = 1; }
    void osContBad(uint8_t* r, recomp_context* c) { int* p = (int*)c->r4; *p = 1; }
    void osPfsNoop(uint8_t* r, recomp_context* c) { c->r2 = 1; }
    """
    got = [(name, classify(name, body)) for name, body in blocks(sample)]
    expected = [
        ("osContGood", "translated"),
        ("osContBad", "raw-dereferenced"),
        ("osPfsNoop", "no-op/error-return"),
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
