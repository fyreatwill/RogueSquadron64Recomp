#!/usr/bin/env python3
"""s5347: census of unaligned load/store halves (lwl/lwr, ldl/ldr, swl/swr, sdl/sdr)
whose partner half is missing, far, or separated by a branch/branch-target.

Usage: audit_lwl_lwr_split.py <elf> <out> | --selftest
"""
import re, subprocess, sys

CTRL = {"beq", "bne", "beql", "bnel", "beqz", "bnez", "blez", "bgtz", "bltz", "bgez", "blezl",
        "bgtzl", "bltzl", "bgezl", "bltzal", "bgezal", "bltzall", "bgezall", "bc1t", "bc1f",
        "bc1tl", "bc1fl", "jr", "jalr", "j", "jal", "b", "bal"}
# half -> (family, other half)
HALF = {"lwl": ("lw", "lwr"), "lwr": ("lw", "lwl"), "ldl": ("ld", "ldr"), "ldr": ("ld", "ldl"),
        "swl": ("sw", "swr"), "swr": ("sw", "swl"), "sdl": ("sd", "sdr"), "sdr": ("sd", "sdl")}
WINDOW = 8


def parse(lines):
    ins = []
    for l in lines:
        m = re.match(r"\s*([0-9a-f]+):\s+[0-9a-f]{8}\s+(\S+)\s*(.*)", l)
        if m:
            ins.append((int(m.group(1), 16), m.group(2), m.group(3).split("#")[0].strip()))
    return ins


def memops(ops):
    m = re.match(r"(\$?\w+),(-?\w+)\((\$?\w+)\)", ops)
    return (m.group(1), int(m.group(2), 0), m.group(3)) if m else None


def runs(ins):
    """Run id per instruction; overlays alias the same VMAs, so a new run starts at any address discontinuity."""
    r, out = 0, []
    for i, (a, _, _) in enumerate(ins):
        if i and a != ins[i - 1][0] + 4:
            r += 1
        out.append(r)
    return out


def targets(ins, rid):
    t = set()
    for i, (a, mn, ops) in enumerate(ins):
        if mn in CTRL and mn not in ("jr", "jalr", "jal"):
            m = re.search(r"\b(?:0x)?([0-9a-f]+)\s*(?:<[^>]*>)?\s*$", ops)
            if m:
                t.add((rid[i], int(m.group(1), 16)))
    return t


def audit(ins):
    rid = runs(ins)
    tg = targets(ins, rid)
    idx = {a: i for i, (a, _, _) in enumerate(ins)}
    stats = dict(halves=0, adjacent=0, straight=0)
    flagged = []
    paired = set()
    for i, (a, mn, ops) in enumerate(ins):
        if mn not in HALF or mn[-1] != "l":      # visit each pair from its 'l' half
            continue
        mo = memops(ops)
        if not mo:
            continue
        stats["halves"] += 1
        other = HALF[mn][1]
        rt, off, base = mo
        span = 3 if mn[1] == "w" else 7
        partner = None
        lo, hi = max(0, i - WINDOW), min(len(ins), i + WINDOW + 1)
        for j in sorted(range(lo, hi), key=lambda j: abs(j - i)):
            if j == i or j in paired:
                continue
            _, m2, o2 = ins[j]
            if m2 != other:
                continue
            mo2 = memops(o2)
            if mo2 and mo2[2] == base and abs(mo2[1] - off) == span and (mo2[0] == rt or mn[0] == "s"):
                partner = j
                break
        if partner is None:
            flagged.append((a, "NO-PARTNER", f"{mn} {ops}"))
            continue
        paired.add(partner)
        s, e = sorted((i, partner))
        if rid[s] != rid[e]:
            flagged.append((a, "RUN-BREAK", f"{mn} {ops}"))
            continue
        # separated if any control insn lies in [s, e) except one whose slot is e (adjacent branch+slot)
        sep = []
        for k in range(s, e):
            if ins[k][1] in CTRL and not (k + 1 == e):
                sep.append(("CTRL", ins[k][0]))
        for k in range(s + 1, e + 1):
            if (rid[k], ins[k][0]) in tg:
                sep.append(("TARGET", ins[k][0]))
        if sep:
            flagged.append((a, "SPLIT", f"{mn} {ops} <-> {ins[partner][1]} {ins[partner][2]} via {sep}"))
        elif e - s == 1:
            stats["adjacent"] += 1
        else:
            stats["straight"] += 1
    for i, (a, mn, ops) in enumerate(ins):
        if mn in HALF and mn[-1] == "r":
            stats["halves"] += 1
            if i not in paired:
                flagged.append((a, "NO-PARTNER", f"{mn} {ops}"))
    return stats, flagged


SYN = """  100: 88820003 lwl v0,3(a0)
  104: 98820000 lwr v0,0(a0)
  108: 88830003 lwl v1,3(a0)
  10c: 10600002 beqz v1,0x118
  110: 00000000 nop
  114: 98830000 lwr v1,0(a0)
  118: 88840003 lwl a0,3(a1)
  11c: 03e00008 jr ra
  120: 00000000 nop"""

if sys.argv[1] == "--selftest":
    st, fl = audit(parse(SYN.splitlines()))
    kinds = [(f[0], f[1]) for f in fl]
    assert st["adjacent"] == 1, st
    assert (0x108, "SPLIT") in kinds and (0x118, "NO-PARTNER") in kinds, kinds
    print("selftest ok: adjacent=1, flagged split @108 and no-partner @118")
    sys.exit(0)

dis = subprocess.run(["mips-linux-gnu-objdump", "-d", "-M", "no-aliases", sys.argv[1]],
                     capture_output=True, text=True).stdout.splitlines()
ins = parse(dis)
st, fl = audit(ins)
with open(sys.argv[2], "w") as f:
    for s in fl:
        f.write("%s %08x | %s\n" % (s[1], s[0], s[2]))
print("instructions", len(ins), st, "flagged", len(fl))
