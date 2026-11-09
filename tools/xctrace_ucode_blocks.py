#!/usr/bin/env python3
"""s7014: block-level profile of the recompiled F5 gfx ucode. The ucode is ONE huge C function and macOS `sample` merges
all offsets of a function into one line, so neither sample nor tools/sample_self.py can say which RSP block is hot.
Input: `xctrace export --xpath '.../table[@schema="time-profile"]'` XML of a Time Profiler recording (1 ms samples with
full backtraces, one PC per sample). For every sample of the chosen thread, the innermost frame inside factor5_ucode*
is symbolised with atos (file:line in the generated .c), mapped to the enclosing RSP label L_xxxx (IMEM PC of the block),
and counted: 'self' when that frame is the leaf, 'incl' when the leaf is a callee (DMA, RDP submit, helper).
The main binary carries no debug map for these TUs (atos gives function+offset only), so lines come from the arm's own
object file: binary addr -> offset in the function (nm of the binary + slide) -> .o address -> the nearest preceding
`dwarfdump --debug-line` row of the generated .c with line != 0 (inlined vector-op rows are skipped, so a sample in an
inlined helper is charged to the .c statement that called it).
usage: xctrace_ucode_blocks.py <tp.xml> <thread-substr> <binary> <ucode.c> <arm.o> [topN]"""
import re, sys, subprocess, collections, bisect
import xml.etree.ElementTree as ET
xmlp, thr, binary, csrc, obj = sys.argv[1:6]
top = int(sys.argv[6]) if len(sys.argv) > 6 else 30
frames, bts, threads, states = {}, {}, {}, {}
load = None; n_thr = 0; n_run = 0
blk_self = collections.Counter(); blk_incl = collections.Counter(); leafc = collections.Counter(); fnc = collections.Counter()
pend = []  # (addr, self?, callee)
under = collections.Counter(); under2 = collections.Counter(); n_under = 0
for ev, el in ET.iterparse(xmlp, events=("end",)):
    if el.tag == "frame":
        if "ref" in el.attrib: continue
        frames[el.get("id")] = (el.get("name") or "?", int(el.get("addr"), 16))
        b = el.find("binary")
        if b is not None and b.get("name") == "RogueSquadron64Recomp" and load is None: load = b.get("load-addr")
    elif el.tag == "row":
        th = el.find("thread"); tid = th.get("ref") or th.get("id")
        if th.get("fmt"): threads[tid] = th.get("fmt")
        if thr not in threads.get(tid, ""): el.clear(); continue
        n_thr += 1
        bt = el.find("tagged-backtrace")
        if bt is None: bt = el.find("backtrace")
        if bt is None: el.clear(); continue
        if bt.get("ref"): fl = bts.get(bt.get("ref"), [])
        else:
            inner = bt.find("backtrace") if bt.tag == "tagged-backtrace" else bt
            if inner is not None and inner.get("ref"): fl = bts.get(inner.get("ref"), [])
            else:
                fl = [f.get("ref") or f.get("id") for f in (inner if inner is not None else bt).iter("frame")]
                if inner is not None: bts[inner.get("id")] = fl
            bts[bt.get("id")] = fl
        if not fl: el.clear(); continue
        leaf = frames.get(fl[0], ("?", 0))[0]
        leafc[re.sub(r"\(.*", "", leaf)[:60]] += 1
        nms = [frames.get(f, ("?", 0))[0] for f in fl]
        ku = next((i for i, n in enumerate(nms) if n.startswith("rsp_dpc_submit_impl")), None)
        if ku is not None:
            n_under += 1; under[re.sub(r"\(.*", "", nms[0])[:60]] += 1
            under2[re.sub(r"\(.*", "", nms[ku - 1])[:60] if ku else "(self)"] += 1
        for k, fid in enumerate(fl):
            nm, ad = frames.get(fid, ("?", 0))
            if nm.startswith("factor5_ucode"):
                fnc[nm.split("(")[0]] += 1
                pend.append((ad - (0 if k == 0 else 1), k == 0, re.sub(r'\(.*', '', frames.get(fl[k-1], ('?',0))[0])[:50] if k else '')); break
        el.clear()
def nmsym(path, rx):
    for l in subprocess.run(["nm", path], capture_output=True, text=True).stdout.split("\n"):
        p = l.split()
        if len(p) == 3 and p[1] in "Tt" and re.fullmatch(rx, p[2]): return int(p[0], 16)
mangled = {"factor5_ucode_nmac": "__Z18factor5_ucode_nmacPhj", "factor5_ucode_lean": "__Z18factor5_ucode_leanPhj",
           "factor5_ucode": "__Z13factor5_ucodePhj"}[max(fnc, key=fnc.get)]
slide = int(load, 16) - 0x100000000
fbin = nmsym(binary, re.escape(mangled)); fobj = nmsym(obj, re.escape(mangled))
dl = subprocess.run(["dwarfdump", "--debug-line", obj], capture_output=True, text=True).stdout.split("\n")
cfile = None; rows = []
for i, l in enumerate(dl):
    m = re.match(r"file_names\[\s*(\d+)\]:", l)
    if m and i + 1 < len(dl) and "factor5_ucode_recompiled.c" in dl[i + 1]: cfile = int(m.group(1))
    m = re.match(r"(0x[0-9a-f]{16})\s+(\d+)\s+\d+\s+(\d+)", l)
    if m and int(m.group(3)) == cfile and int(m.group(2)) != 0: rows.append((int(m.group(1), 16), int(m.group(2))))
rows.sort(); raddr = [r[0] for r in rows]
def line_of(a):
    k = bisect.bisect_right(raddr, a - slide - fbin + fobj) - 1
    return rows[k][1] if k >= 0 else None
src = open(csrc, errors="replace").read().split("\n")
labs = [(i + 1, m.group(1)) for i, l in enumerate(src) for m in [re.match(r"\s*L_([0-9A-F]+):", l)] if m]
labln = [x[0] for x in labs]
unres = 0
callee = collections.defaultdict(collections.Counter)
for a, s, cn in pend:
    ln = line_of(a)
    if ln:
        k = bisect.bisect_right(labln, ln) - 1; b = "L_" + labs[k][1] if k >= 0 else "pre"
    else:
        unres += 1; b = "?"
    blk_incl[b] += 1
    if s: blk_self[b] += 1
    else: callee[b][cn] += 1
nu = len(pend)
print(f"thread~'{thr}' samples={n_thr} in-ucode={nu} ({100*nu/max(n_thr,1):.1f}%) unresolved={unres} load={load}")
print("ucode arm:", dict(fnc))
print("RSP block   incl  self (% of thread samples)")
for b, c in blk_incl.most_common(top): print(f"  {b:12s} {c:6d} {100*c/max(n_thr,1):5.1f}%  self {blk_self[b]:6d}")
for b, c in blk_incl.most_common(4):
    if callee[b]: print(f"  callees of {b}:", ", ".join(f"{n} {v}" for n, v in callee[b].most_common(6)))
print("leaf symbols:")
for b, c in leafc.most_common(top): print(f"  {c:6d} {100*c/max(n_thr,1):5.1f}%  {b}")
print(f"under rsp_dpc_submit_impl: {n_under} samples; direct callees:")
for b, c in under2.most_common(12): print(f"  {c:6d} {100*c/max(n_thr,1):5.1f}%  {b}")
print("  leaves:")
for b, c in under.most_common(15): print(f"  {c:6d} {100*c/max(n_thr,1):5.1f}%  {b}")
