#!/usr/bin/env python3
"""s4916: tid-marked slot-byte stores. Inserts rs64_s4916_sb(rdram, pc, addr, val) before every `sb`
(MEM_B(off, base) = val;) inside viRetraceHandlerThread and bufferArbiterProducerMark. The host
interns a tag and calls rs64_s4913_mark only when addr is in the arbiter table 0x80128EA8..B7.
Idempotent. Usage: apply_s4916_marks.py <RecompiledFuncs dir>."""
import re, sys, pathlib

DECL = 'extern void rs64_s4916_sb(uint8_t* rdram, uint32_t pc, uint32_t addr, uint32_t val);\n'
STORE = re.compile(r'^(\s*)MEM_B\((-?0[xX][0-9A-Fa-f]+|0), (ctx->r\d+)\) = ([^;]+);\n', re.M)
PC = re.compile(r'// (0x[0-9A-Fa-f]{8}): sb ')


def func_span(t, name):
    i = t.index("RECOMP_FUNC void " + name + "(")
    j = t.index("{\n", i) + 2
    k = t.find("RECOMP_FUNC void ", j)
    return i, j, (len(t) if k < 0 else k)


def patch_func(t, name):
    if "RECOMP_FUNC void " + name + "(" not in t:
        return t
    i, j, e = func_span(t, name)
    body = t[j:e]
    if "s4916 sb mark" in body:
        return t
    out, last = [], 0
    for m in STORE.finditer(body):
        pcs = PC.findall(body[:m.start()])
        pc = pcs[-1] if pcs else "0"
        off, base, val = m.group(2), m.group(3), m.group(4)
        out.append(body[last:m.start()])
        out.append(f"{m.group(1)}rs64_s4916_sb(rdram, {pc}u, U32(ADD32({base}, {off})), U32({val})); // PATCH: s4916 sb mark\n")
        out.append(m.group(0))
        last = m.end()
    out.append(body[last:])
    return t[:j] + "".join(out) + t[e:]


def patch_text(t):
    n = t
    for nm in ("viRetraceHandlerThread", "bufferArbiterProducerMark"):
        n = patch_func(n, nm)
    if "s4916 sb mark" in n and DECL not in n:
        n = n.replace('#include "recomp.h"\n', '#include "recomp.h"\n' + DECL, 1)
    return n


if __name__ == "__main__":
    for p in sorted(pathlib.Path(sys.argv[1]).glob("funcs_*.c")):
        t = p.read_text()
        n = patch_text(t)
        if n != t:
            p.write_text(n)
            print("patched", p.name)
