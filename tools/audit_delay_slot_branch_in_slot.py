#!/usr/bin/env python3
"""s5346: census of branches/jumps whose delay slot is itself a branch/jump,
and of branch-likely slots that load/store (side effects when untaken).

Usage: audit_delay_slot_branch_in_slot.py <elf> <out> | --selftest
"""
import re, subprocess, sys

CTRL = {"beq", "bne", "beql", "bnel", "beqz", "bnez", "blez", "bgtz", "bltz", "bgez", "blezl",
        "bgtzl", "bltzl", "bgezl", "bltzal", "bgezal", "bltzall", "bgezall", "bc1t", "bc1f",
        "bc1tl", "bc1fl", "jr", "jalr", "j", "jal", "b", "bal"}
LIKELY = {"beql", "bnel", "blezl", "bgtzl", "bltzl", "bgezl", "bltzall", "bgezall", "bc1tl",
          "bc1fl", "beqzl", "bnezl"}
MEM = re.compile(r"^(l[bhwd]u?|lw[lr]|ld[lr]|ll|lld|s[bhwd]|sw[lr]|sd[lr]|sc|scd|[ls]wc[12]|[ls]dc[12])$")


def parse(lines):
    ins = []
    for l in lines:
        m = re.match(r"\s*([0-9a-f]+):\s+[0-9a-f]{8}\s+(\S+)\s*(.*)", l)
        if m:
            ins.append((int(m.group(1), 16), m.group(2), m.group(3).split("#")[0].strip()))
    return ins


def audit(ins):
    bis, likely_mem, nb = [], [], 0
    for i, (a, mn, ops) in enumerate(ins[:-1]):
        if mn not in CTRL:
            continue
        nb += 1
        _, smn, sops = ins[i + 1]
        if smn in CTRL:
            bis.append((a, f"{mn} {ops}", f"{smn} {sops}"))
        elif mn in LIKELY and MEM.match(smn):
            likely_mem.append((a, f"{mn} {ops}", f"{smn} {sops}"))
    return nb, bis, likely_mem


SYN = """  100: 10000002 beq a0,a1,0x10c
  104: 10000001 b 0x10c
  108: 00000000 nop
  10c: 5480fffe bnel a0,zero,0x108
  110: 8c820000 lw v0,0(a0)
  114: 03e00008 jr ra
  118: 00000000 nop"""

if sys.argv[1] == "--selftest":
    nb, bis, lm = audit(parse(SYN.splitlines()))
    assert nb == 4 and len(bis) == 1 and bis[0][0] == 0x100 and len(lm) == 1 and lm[0][0] == 0x10c, (nb, bis, lm)
    print("selftest ok: flagged branch-in-slot @100 and likely+lw @10c")
    sys.exit(0)

dis = subprocess.run(["mips-linux-gnu-objdump", "-d", "-M", "no-aliases", sys.argv[1]],
                     capture_output=True, text=True).stdout.splitlines()
ins = parse(dis)
nb, bis, lm = audit(ins)
with open(sys.argv[2], "w") as f:
    for s in bis:
        f.write("BRANCH-IN-SLOT %08x | %s | %s\n" % s)
    for s in lm:
        f.write("LIKELY-MEM-SLOT %08x | %s | %s\n" % s)
print("instructions", len(ins), "branch/jump with slot", nb, "branch-in-slot", len(bis), "likely+mem slot", len(lm))
