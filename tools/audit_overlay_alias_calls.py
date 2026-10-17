#!/usr/bin/env python3
"""s5348: census of direct j/jal whose target address is instruction-covered by >=2 address runs
(overlays alias the same VMAs in the main ELF). Classifies caller run vs target run(s).

Usage: audit_overlay_alias_calls.py <elf> <out> | --selftest
"""
import re, subprocess, sys
from collections import defaultdict


def parse(lines):
    ins = []
    for l in lines:
        m = re.match(r"\s*([0-9a-f]+):\s+[0-9a-f]{8}\s+(\S+)\s*(.*)", l)
        if m:
            ins.append((int(m.group(1), 16), m.group(2), m.group(3).split("#")[0].strip()))
    return ins


def audit(ins):
    rid, r = [], 0
    for i, (a, _, _) in enumerate(ins):
        if i and a != ins[i - 1][0] + 4:
            r += 1
        rid.append(r)
    cover = defaultdict(set)            # address -> set of runs containing an instruction there
    for (a, _, _), r in zip(ins, rid):
        cover[a].add(r)
    stats = defaultdict(int)
    flagged = []
    for (a, mn, ops), r in zip(ins, rid):
        if mn not in ("j", "jal"):
            continue
        m = re.match(r"(?:0x)?([0-9a-f]+)", ops)
        if not m:
            continue
        t = int(m.group(1), 16)
        runs_t = cover.get(t, set())
        stats[mn] += 1
        if not runs_t:
            stats["target-uncovered"] += 1
            flagged.append((a, "UNCOVERED", f"{mn} {t:#x} run{r}"))
        elif len(runs_t) == 1:
            stats["unambiguous-same" if r in runs_t else "unambiguous-cross"] += 1
        elif r in runs_t:
            stats["aliased-intra"] += 1
            flagged.append((a, "ALIASED-INTRA", f"{mn} {t:#x} run{r} targets runs {sorted(runs_t)}"))
        else:
            stats["aliased-cross"] += 1
            flagged.append((a, "ALIASED-CROSS", f"{mn} {t:#x} run{r} targets runs {sorted(runs_t)}"))
    stats["runs"] = rid[-1] + 1 if rid else 0
    stats["aliased_addrs"] = sum(1 for s in cover.values() if len(s) > 1)
    return dict(stats), flagged


SYN = """  100: 0c000040 jal 0x100
  104: 00000000 nop
  200: 0c000040 jal 0x100
  204: 00000000 nop
  300: 0c000080 jal 0x200
  304: 00000000 nop
  100: 03e00008 jr ra
  104: 00000000 nop
  400: 0c000041 jal 0x104
  404: 00000000 nop"""

if sys.argv[1] == "--selftest":
    st, fl = audit(parse(SYN.splitlines()))
    kinds = {(f[0], f[1]) for f in fl}
    assert (0x100, "ALIASED-INTRA") in kinds, (st, kinds)   # run0 jal 0x100; 0x100 is in run0 and run3
    assert (0x200, "ALIASED-CROSS") in kinds, (st, kinds)
    assert (0x400, "ALIASED-CROSS") in kinds, (st, kinds)
    assert (0x300, "ALIASED-CROSS") not in kinds
    print("selftest ok:", st)
    sys.exit(0)

def audit_sections(dis, relocatable_pred=lambda name: False):
    """Predict N64Recomp's resolve_jal (src/recompilation.cpp:resolve_jal) per section.
    Same-section function at target -> static. Else candidates = functions at the exact target vram
    in OTHER non-relocatable sections: 1 -> static Match, >=2 -> runtime lookup, 0 -> lookup.
    HAZARD = static Match to one section while another section also has code covering that vram."""
    sec = None
    secs, labels, cover, calls = [], defaultdict(set), defaultdict(set), []
    for l in dis:
        m = re.match(r"Disassembly of section (\S+):", l)
        if m:
            sec = m.group(1)
            secs.append(sec)
            continue
        m = re.match(r"([0-9a-f]{8}) <[^>]+>:", l)
        if m:
            labels[int(m.group(1), 16)].add(sec)
            continue
        m = re.match(r"\s*([0-9a-f]+):\s+[0-9a-f]{8}\s+(\S+)\s*(.*)", l)
        if m:
            a = int(m.group(1), 16)
            cover[a].add(sec)
            if m.group(2) in ("j", "jal"):
                t = re.match(r"(?:0x)?([0-9a-f]+)", m.group(3))
                if t:
                    calls.append((a, m.group(2), int(t.group(1), 16), sec))
    stats = defaultdict(int)
    out = []
    for a, mn, t, cs in calls:
        stats["calls"] += 1
        if cs in labels.get(t, ()):
            stats["same-section-func"] += 1
            continue
        if cs in cover.get(t, ()):      # target lies in the caller's own section: in_current_section path, never cross-binds
            stats["same-section-static"] += 1
            continue
        cand = [s for s in labels.get(t, ()) if s != cs and not relocatable_pred(s)]
        others = sorted(s for s in cover.get(t, ()) if s != cs)
        if len(cand) >= 2 or not cand:
            stats["lookup(ambiguous/none)"] += 1
        elif len(others) > 1:
            stats["HAZARD"] += 1
            out.append((a, "HAZARD", f"{mn} {t:#x} from {cs} static->{cand[0]}, also covered by {others}"))
        else:
            stats["static-unique"] += 1
    stats["sections"] = len(secs)
    return dict(stats), out


SYN_SEC = """Disassembly of section .a:

00000100 <fa>:
  100: 0c000040 jal 0x100
Disassembly of section .b:

00000100 <fb>:
  100: 03e00008 jr ra
Disassembly of section .c:

00000200 <fc>:
  200: 0c000040 jal 0x100
Disassembly of section .d:

00000300 <fd>:
  300: 0c000080 jal 0x200
Disassembly of section .e:

  100: 03e00008 jr ra
00000400 <fe>:
  400: 0c0000c0 jal 0x300
Disassembly of section .f:

  300: 00000000 nop
  304: 0c000040 jal 0x100"""

if sys.argv[1] == "--selftest2":
    st, out = audit_sections(SYN_SEC.splitlines())
    # .c->0x100 has 2 labelled candidates (.a,.b) => lookup; .d->0x200 unique label in .c and covered only there => static-unique;
    # .e->0x300 labelled in .d only but covered by .f too => HAZARD.
    assert st.get("lookup(ambiguous/none)") == 2, st      # .c->0x100 (ambig) and .f->0x100 (ambig)
    assert st.get("static-unique") == 1 and st.get("HAZARD") == 1, st
    print("selftest2 ok:", st)
    sys.exit(0)

if sys.argv[1] == "--generated":
    # --generated <elf> <RecompiledFuncs dir> <out>: ground-truth how N64Recomp emitted every j/jal whose
    # target is not covered by the caller's own section. lookup = LOOKUP_FUNC(...) (runtime, overlay-aware);
    # direct = named C call (statically bound). Cross-tab by how many sections cover the target vram.
    import glob
    dis = subprocess.run(["mips-linux-gnu-objdump", "-d", "-M", "no-aliases", sys.argv[2]],
                         capture_output=True, text=True).stdout.splitlines()
    sec, cover, calls = None, defaultdict(set), []
    for l in dis:
        m = re.match(r"Disassembly of section (\S+):", l)
        if m:
            sec = m.group(1)
            continue
        m = re.match(r"\s*([0-9a-f]+):\s+[0-9a-f]{8}\s+(\S+)\s*(.*)", l)
        if m:
            a = int(m.group(1), 16)
            cover[(a, sec)] = 1
            cover[a] = cover.get(a, set()) if isinstance(cover.get(a), set) else set()
            cover[a].add(sec)
            if m.group(2) in ("j", "jal"):
                t = re.match(r"(?:0x)?([0-9a-f]+)", m.group(3))
                if t:
                    calls.append((a, m.group(2), int(t.group(1), 16), sec))
    emitted = {}
    for fn in glob.glob(sys.argv[3] + "/funcs_*.c"):
        pend = None
        for l in open(fn, errors="replace"):
            m = re.match(r"\s*// 0x([0-9A-F]{8}): (jal|j)\s+0x([0-9A-F]+)", l)
            if m:
                pend = (int(m.group(1), 16), int(m.group(3), 16))
                continue
            if pend:
                m = re.match(r"\s*(LOOKUP_FUNC\(0x[0-9A-F]+\)|[A-Za-z_]\w*)\(rdram, ctx\);", l)
                if m:
                    emitted[pend[0]] = "lookup" if m.group(1).startswith("LOOKUP_FUNC") else "direct:" + m.group(1)
                    pend = None
    tab = defaultdict(int)
    bad = []
    for a, mn, t, cs in calls:
        if (a, cs) not in cover or cs in cover.get(t, ()):
            continue                     # target inside caller's own section: not a cross-section bind
        n = len(cover.get(t, ()))
        kind = emitted.get(a, "no-call-line(branch/j-internal)")
        k = "lookup" if kind == "lookup" else ("direct" if kind.startswith("direct") else kind)
        tab[(n, k)] += 1
        if n >= 2 and k == "direct":
            bad.append((a, "ALIAS-DIRECT", f"{mn} {t:#x} from {cs} -> {kind}, covered by {sorted(cover[t])}"))
    with open(sys.argv[4], "w") as f:
        for s_ in bad:
            f.write("%s %08x | %s\n" % (s_[1], s_[0], s_[2]))
    for k in sorted(tab):
        print("sections-covering-target=%d emitted=%s : %d" % (k[0], k[1], tab[k]))
    print("ALIAS-DIRECT flagged", len(bad))
    sys.exit(0)

if sys.argv[1] == "--sections":
    dis = subprocess.run(["mips-linux-gnu-objdump", "-d", "-M", "no-aliases", sys.argv[2]],
                         capture_output=True, text=True).stdout.splitlines()
    st, out = audit_sections(dis)
    with open(sys.argv[3], "w") as f:
        for s in out:
            f.write("%s %08x | %s\n" % (s[1], s[0], s[2]))
    print(st, "flagged", len(out))
    sys.exit(0)

dis = subprocess.run(["mips-linux-gnu-objdump", "-d", "-M", "no-aliases", sys.argv[1]],
                     capture_output=True, text=True).stdout.splitlines()
ins = parse(dis)
st, fl = audit(ins)
with open(sys.argv[2], "w") as f:
    for s in fl:
        f.write("%s %08x | %s\n" % (s[1], s[0], s[2]))
print("instructions", len(ins), st, "flagged", len(fl))
