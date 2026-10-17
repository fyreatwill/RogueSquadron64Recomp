#!/usr/bin/env python3
"""s5345: offline delay-slot operand-hazard census.

Disassembles the game ELF with mips-linux-gnu-objdump and finds every
branch/jump whose delay-slot instruction writes a GPR that the branch reads
(condition operands, jr/jalr target) or that jal/jalr link ($ra / rd).
Prints counts and writes sites to the given output file.
"""
import re, subprocess, sys, collections

ELF = sys.argv[1]
OUT = sys.argv[2]
dis = subprocess.run(["mips-linux-gnu-objdump", "-d", "-M", "no-aliases", ELF],
                     capture_output=True, text=True).stdout.splitlines()

ins = []  # (addr, mnemonic, operands)
for l in dis:
    m = re.match(r"\s*([0-9a-f]+):\s+[0-9a-f]{8}\s+(\S+)\s*(.*)", l)
    if m:
        ops = m.group(3).split("#")[0].strip()
        ins.append((int(m.group(1), 16), m.group(2), ops))

GPR = set("zero at v0 v1 a0 a1 a2 a3 t0 t1 t2 t3 t4 t5 t6 t7 s0 s1 s2 s3 s4 s5 s6 s7 t8 t9 k0 k1 gp sp s8 fp ra".split())
def regs(s):
    return [t for t in re.split(r"[,()\s]+", s) if t in GPR]

BR2 = {"beq", "bne", "beql", "bnel"}
BR1 = {"beqz", "bnez", "blez", "bgtz", "bltz", "bgez", "blezl", "bgtzl", "bltzl", "bgezl",
       "bltzal", "bgezal", "bltzall", "bgezall"}
LOADSTORE_NOWRITE = {"sw", "sh", "sb", "sd", "swl", "swr", "sdl", "sdr", "swc1", "sdc1", "sc",
                     "nop", "ssnop", "sync", "cache", "mtc1", "mtc0", "mthi", "mtlo",
                     "mult", "multu", "div", "divu", "dmult", "dmultu", "ddiv", "ddivu",
                     "mtc2", "ctc1", "swc2", "lwc1", "ldc1", "lwc2", "ldc2", "sdc2", "tlbwi", "eret"}

def dest(mn, ops):
    r = regs(ops)
    if mn in LOADSTORE_NOWRITE or not r:
        return None
    if mn in ("mfc1", "mfc0", "cfc1", "dmfc1", "mfc2", "cfc2"):
        return r[0]
    if mn in ("mfhi", "mflo"):
        return r[0]
    if mn.startswith(("c.", "b", "j")) and mn not in ("jal", "jalr"):
        return None
    if mn == "jal":
        return "ra"
    if mn == "jalr":
        return r[0] if len(r) > 1 else "ra"
    return r[0]

def norm(x):
    return {"zero": "zero"}.get(x, x)

# aliases numeric -> names are not applied with no-aliases; normalise numerics
sites = []
nb = 0
kinds = collections.Counter()
for i, (a, mn, ops) in enumerate(ins[:-1]):
    src = None
    link = None
    if mn in BR2:
        src = regs(ops)[:2]
    elif mn in BR1:
        src = regs(ops)[:1]
    elif mn == "jr":
        src = regs(ops)[:1]
    elif mn == "jalr":
        r = regs(ops)
        src = [r[-1]]
        link = r[0] if len(r) > 1 else "ra"
    elif mn in ("jal",):
        link = "ra"
        src = []
    elif mn in ("j", "b", "bal"):
        src = []
        if mn == "bal":
            link = "ra"
    else:
        continue
    nb += 1
    sa, smn, sops = ins[i + 1]
    d = dest(smn, sops)
    if d is None:
        continue
    d = norm(d)
    if d == "zero":
        continue
    hit = None
    if d in [norm(x) for x in src]:
        hit = "src-clobber"
    elif link is not None and d == norm(link):
        hit = "link-clobber"
    if hit:
        kinds[(hit, mn)] += 1
        sites.append((a, hit, f"{mn} {ops}", f"{smn} {sops}"))

with open(OUT, "w") as f:
    for s in sites:
        f.write("%08x %s | %s | %s\n" % s)
print("instructions", len(ins), "branch/jump with slot", nb, "hazard sites", len(sites))
for k, v in sorted(kinds.items()):
    print(k, v)
