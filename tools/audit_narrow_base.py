#!/usr/bin/env python3
"""s5100: shape-4 audit. Reports MEM_x(off, X) where bare identifier X's nearest preceding declaration
(within 400 lines) is a narrow C integer type (int/unsigned/uint32_t/int32_t/...). A 32-bit base is
zero- or sign-extended wrongly vs. the gpr (64-bit sign-extended) convention.
ALLOW = reviewed benign sites.
Usage: audit_narrow_base.py <RecompiledFuncs dir | --selftest>"""
import pathlib, re, sys

NARROW = r'(?:unsigned(?:\s+int)?|int|uint(?:8|16|32)_t|int(?:8|16|32)_t|u32|s32|size_t)'
USE = re.compile(r'\bMEM_[A-Z]+\(\s*[^,()]+,\s*([A-Za-z_]\w*)\s*\)')
# s_vagn_i: non-negative 0..0x1f for-loop index added to a gpr offset (funcs_24 s4204 dump); reviewed s5100.
ALLOW = {"s_vagn_i"}


def scan_text(t):
    L = t.split("\n")
    hits = []
    for i, l in enumerate(L):
        for m in USE.finditer(l):
            v = m.group(1)
            if v == "ctx" or v in ALLOW:
                continue
            dec = re.compile(r'\b(?:const\s+)?(' + NARROW + r'|gpr)\s+(?:[^;()]*,\s*)?\*?' + v + r'\b\s*(=|;|,|\[|\)|:)')
            for j in range(i, max(-1, i - 400), -1):
                d = dec.search(L[j])
                if d:
                    if d.group(1) != "gpr":
                        hits.append((i + 1, v, d.group(1)))
                    break
    return hits


def scan_dir(base):
    out = []
    for f in sorted(pathlib.Path(base).glob("funcs_*.c")):
        out += [(f.name,) + h for h in scan_text(f.read_text(errors="replace"))]
    return out


if __name__ == "__main__":
    if sys.argv[1] == "--selftest":
        ctl = scan_text('void f(){ int zz = a; x=MEM_W(4, zz);}\nvoid g(){ unsigned q; y=MEM_B(0, q);}')
        neg = scan_text('void f(gpr zz){ x=MEM_W(4, zz);}')
        print("positive control hits:", len(ctl), "negative:", len(neg))
        sys.exit(0 if len(ctl) == 2 and not neg else 1)
    hits = scan_dir(sys.argv[1])
    for h in hits:
        print(*h)
    print("hits", len(hits))
    sys.exit(1 if hits else 0)
