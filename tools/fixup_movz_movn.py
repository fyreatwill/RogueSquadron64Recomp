#!/usr/bin/env python3
"""Replace the do_break trap emitted for MIPS movz/movn with the real semantics.

N64Recomp (patched in ../N64Recomp/src/recompilation.cpp, s4970) now emits
movz/movn natively, but the live RecompiledFuncs tree carries layers of
apply_s*.py instrumentation, so a wholesale regen swap is not possible.  This
script applies only the movz/movn delta to the live tree and is idempotent
(replaced do_break lines no longer match).  movz rd,rs,rt: if (rt==0) rd=rs;
movn: if (rt!=0) rd=rs.  A write to $zero is a no-op.
"""
import glob, re, sys

BASE = "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs"
REGS = ("zero at v0 v1 a0 a1 a2 a3 t0 t1 t2 t3 t4 t5 t6 t7 s0 s1 s2 s3 s4 s5 s6 s7 "
        "t8 t9 k0 k1 gp sp fp ra").split()
HDR = re.compile(r"^(\s*)//\s+0x([0-9A-Fa-f]+):.*\b(movz|movn)\s+\$(\w+),\s*\$(\w+),\s*\$(\w+)")
BRK = re.compile(r"^(\s*)do_break\((\d+)\);\s*$")


def reg(name):
    return "0" if name == "zero" else f"ctx->r{REGS.index(name)}"


def main(base=BASE):
    total = 0
    for path in sorted(glob.glob(base + "/funcs_*.c")):
        lines = open(path, errors="surrogateescape").read().split("\n")
        out, i, n = [], 0, 0
        while i < len(lines):
            out.append(lines[i])
            m = HDR.match(lines[i])
            if m and i + 1 < len(lines):
                b = BRK.match(lines[i + 1])
                if b and int(b.group(2)) == int(m.group(2), 16):
                    ind, op, rd, rs, rt = m.group(1), m.group(3), m.group(4), m.group(5), m.group(6)
                    if rd == "zero":
                        out.append(f"{ind};")
                    else:
                        cond = f"!{reg(rt)}" if op == "movz" else f"{reg(rt)}"
                        out += [f"{ind}if ({cond}) {{", f"{ind}    {reg(rd)} = {reg(rs)};", f"{ind}}}"]
                    n += 1
                    i += 1
            i += 1
        if n:
            open(path, "w", errors="surrogateescape").write("\n".join(out))
            total += n
    print(f"fixup_movz_movn: replaced {total} do_break traps")


if __name__ == "__main__":
    main(*sys.argv[1:2])
