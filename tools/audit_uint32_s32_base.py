#!/usr/bin/env python3
"""s5099: shape-3 unsigned-base audit. Reports `uint32_t X = S32(...)` locals later used
as the base argument of MEM_x(off, X) within the next 3000 chars (a uint32_t base >= 2^31
lands at rdram+2^32). Usage: audit_uint32_s32_base.py <RecompiledFuncs dir | --selftest>"""
import pathlib, re, sys

DECL = re.compile(r'\buint32_t\s+(\w+)\s*=\s*S32\(')


def scan_text(t):
    hits = []
    for m in DECL.finditer(t):
        v = m.group(1)
        u = re.search(r'MEM_[A-Z]+\([^,()]*,\s*' + v + r'\s*\)', t[m.end():m.end() + 3000])
        if u:
            hits.append((v, u.group(0)))
    return hits


def scan_dir(base):
    out = []
    for f in sorted(pathlib.Path(base).glob("funcs_*.c")):
        out += [(f.name,) + h for h in scan_text(f.read_text(errors="replace"))]
    return out


if __name__ == "__main__":
    if sys.argv[1] == "--selftest":
        ctl = scan_text('void f(){ uint32_t zz = S32(a<<16); x=MEM_W(4, zz);}')
        neg = scan_text('void f(){ int zz = S32(a<<16); x=MEM_W(4, zz);}')
        print("positive control hits:", len(ctl), "negative:", len(neg))
        sys.exit(0 if len(ctl) == 1 and not neg else 1)
    hits = scan_dir(sys.argv[1])
    for h in hits:
        print(*h)
    print("hits", len(hits))
    sys.exit(1 if hits else 0)
