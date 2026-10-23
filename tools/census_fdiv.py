#!/usr/bin/env python3
"""M3 FP divide / square-root idiom census (div.s, div.d, sqrt.s, sqrt.d).

Usage: python3 -I tools/census_fdiv.py [RecompiledFuncs dir] [rom.z64] > rows.tsv
Summary counts go to stderr.

For every unique guest PC, walks backward inside the same generated function
to the nearest writer of the divisor (div) or operand (sqrt) and classifies it:
  rodata-const   lwc1/ldc1 off $at after `lui $at` (value read from the ROM
                 main segment when in range: rodata-nonzero / rodata-zero /
                 rodata-unresolved)
  stack-spill    lwc1/ldc1 off $sp
  mem-field      lwc1/ldc1 off another base
  mtc1-gpr       moved from an integer register
  sqrt-result    divisor is a sqrt.s/sqrt.d result (normalize shape)
  int-convert    cvt/trunc result
  arith(op)      produced by add/sub/mul/... in the same region
  no-writer      no writer in the function (argument register)
and whether any float compare (c.*) on that register precedes the site in the
function (the game's own zero/range test; heuristic, not CFG-exact).
"""
import re, glob, sys, struct, collections

D = sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs"
ROM = sys.argv[2] if len(sys.argv) > 2 else "/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64"
rom = open(ROM, "rb").read()

# function -> (rom_addr, ram_addr, size) of its section, from recomp_overlays.inl
sec_of = {}
inl = open(D + "/recomp_overlays.inl", errors="replace").read()
arrays = {}
for m in re.finditer(r"static FuncEntry (\w+)\[\] = \{(.*?)\};", inl, re.S):
    arrays[m.group(1)] = re.findall(r"\.func = (\w+),", m.group(2))
for m in re.finditer(r"\.rom_addr = (0x[0-9A-F]+), \.ram_addr = (0x[0-9A-F]+), \.size = (0x[0-9A-F]+), \.funcs = (\w+)", inl):
    for fn in arrays.get(m.group(4), []):
        sec_of[fn] = (int(m.group(1), 16), int(m.group(2), 16), int(m.group(3), 16))
MAIN = (0x1040, 0x80000440, 0xA4CF0)

def rom_word(vaddr, func):
    # rodata in the main segment is static; rodata in the overlay window
    # (0x800A5130+) belongs to the overlay that holds the reading function.
    sec = MAIN if vaddr < 0x800A5130 else sec_of.get(func)
    if sec is None:
        return None
    rom_addr, ram, size = sec
    if not (ram <= vaddr < ram + size):
        return None
    off = rom_addr + (vaddr - ram)
    return struct.unpack(">I", rom[off:off + 4])[0]

fn_re = re.compile(r"^RECOMP_FUNC void (\w+)\(")
op_re = re.compile(r"^\s*// (0x[0-9A-F]{8}): (\S+)\s*(.*)$")
NONWRITE = ("swc1", "sdc1", "mfc1", "dmfc1", "cfc1", "ctc1")
rows = {}
for f in sorted(glob.glob(D + "/funcs_*.c")):
    ops = []
    func = None; fstart = 0
    for i, l in enumerate(open(f, errors="replace")):
        m = fn_re.match(l)
        if m:
            func = m.group(1); fstart = len(ops)
        m = op_re.match(l)
        if m:
            ops.append((i + 1, m.group(1), m.group(2), m.group(3), func, fstart))
    for k, (ln, pc, mn, opd, func, fstart) in enumerate(ops):
        if mn not in ("div.s", "div.d", "sqrt.s", "sqrt.d") or pc in rows:
            continue
        regs = [r.strip() for r in opd.split(",")]
        src = regs[2] if mn.startswith("div") else regs[1]
        writer = None; wk = None; cmp_before = False
        for j in range(k - 1, fstart - 1, -1):
            _, ppc, pmn, popd, _, _ = ops[j]
            pr = [r.strip() for r in popd.split(",")]
            if pmn.startswith("c.") and src in pr:
                cmp_before = True
                continue
            if pmn == "mtc1" and len(pr) > 1 and pr[1] == src:
                writer = (ppc, pmn, popd); wk = j; break
            if pr and pr[0] == src and pmn not in NONWRITE:
                writer = (ppc, pmn, popd); wk = j; break
        if writer is None:
            cls = "no-writer"
        else:
            wpc, wmn, wopd = writer
            if wmn in ("lwc1", "ldc1") and "($at)" in wopd:
                cls = "rodata-unresolved"
                mo = re.search(r"(-?)(0x[0-9A-Fa-f]+|\d+)\(\$at\)", wopd)
                for j in range(wk - 1, max(fstart, wk - 12) - 1, -1):
                    _, _, lmn, lopd, _, _ = ops[j]
                    if lmn == "lui" and lopd.startswith("$at"):
                        hi = int(lopd.split(",")[1].strip(), 0)
                        off = int(mo.group(2), 0) * (-1 if mo.group(1) else 1)
                        w = rom_word(((hi << 16) + off) & 0xFFFFFFFF, func)
                        if w is not None:
                            cls = "rodata-zero" if (w & 0x7FFFFFFF) == 0 else "rodata-nonzero"
                            if wmn == "lwc1" and (w & 0x7F800000) == 0 and (w & 0x7FFFFF):
                                cls = "rodata-denormal"
                        break
            elif wmn in ("lwc1", "ldc1") and "($sp)" in wopd:
                cls = "stack-spill"
            elif wmn in ("lwc1", "ldc1"):
                cls = "mem-field"
            elif wmn == "mtc1":
                cls = "mtc1-gpr"
            elif wmn.startswith("sqrt"):
                cls = "sqrt-result"
            elif wmn.startswith(("cvt.", "trunc")):
                cls = "int-convert"
            else:
                cls = "arith(" + wmn + ")"
        rows[pc] = (f.split("/")[-1], ln, func, pc, mn, src, cls,
                    "cmp-before" if cmp_before else "no-cmp",
                    writer[0] if writer else "-", writer[1] if writer else "-")

for pc in sorted(rows):
    print("\t".join(map(str, rows[pc])))
c = collections.Counter((r[4], r[6].split("(")[0], r[7]) for r in rows.values())
for k, v in sorted(c.items()):
    print("#", *k, v, file=sys.stderr)
print("# unique sites", len(rows), file=sys.stderr)
