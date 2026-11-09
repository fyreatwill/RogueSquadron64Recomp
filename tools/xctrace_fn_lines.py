#!/usr/bin/env python3
"""s7014: per-source-line self samples of ONE host function from an xctrace time-profile XML export (see
tools/xctrace_ucode_blocks.py). For inlined callees the line table names the inlined file:line, so this says which inlined
helper inside e.g. rs64_dpc_record_submit carries the time. Lines come from the function's object file (the main binary has
no debug map for its TUs).
usage: xctrace_fn_lines.py <tp.xml> <thread-substr> <binary> <obj.o> <demangled-name-prefix> [topN]"""
import re, sys, subprocess, collections, bisect
import xml.etree.ElementTree as ET
xmlp, thr, binary, obj, fname = sys.argv[1:6]
top = int(sys.argv[6]) if len(sys.argv) > 6 else 25
frames, threads, load, mang = {}, {}, None, None
bt0 = {}  # backtrace id -> leaf frame id (xctrace emits each backtrace once, then ref=)
pcs = collections.Counter(); n_thr = 0
for ev, el in ET.iterparse(xmlp, events=("end",)):
    if el.tag == "frame" and "ref" not in el.attrib:
        frames[el.get("id")] = (el.get("name") or "?", int(el.get("addr"), 16))
        b = el.find("binary")
        if b is not None and b.get("name") == "RogueSquadron64Recomp" and load is None: load = int(b.get("load-addr"), 16)
    elif el.tag == "row":
        th = el.find("thread"); tid = th.get("ref") or th.get("id")
        if th.get("fmt"): threads[tid] = th.get("fmt")
        if thr in threads.get(tid, ""):
            n_thr += 1
            fid = None
            tb = el.find("tagged-backtrace")
            if tb is not None and tb.get("ref"): fid = bt0.get(tb.get("ref"))
            for b in ([] if fid else el.iter("backtrace")):
                if b.get("ref"): fid = bt0.get(b.get("ref")); break
                f = next(b.iter("frame"), None)
                if f is not None:
                    fid = f.get("ref") or f.get("id"); bt0[b.get("id")] = fid
                    if tb is not None: bt0[tb.get("id")] = fid
                break
            if fid is not None:
                nm, ad = frames.get(fid, ("?", 0))
                if nm.startswith(fname): pcs[ad] += 1
        el.clear()
def syms(path):
    out = {}
    for l in subprocess.run(["nm", "-C", path], capture_output=True, text=True).stdout.split("\n"):
        p = l.split(None, 2)
        if len(p) == 3 and p[1] in "Tt": out.setdefault(p[2][1:] if p[2].startswith("_") else p[2], int(p[0], 16))  # C symbols carry a leading _ (s7022)
    return out
sb, so = syms(binary), syms(obj)
key = next(k for k in so if k.startswith(fname))
slide = load - 0x100000000; fb, fo = sb[key], so[key]
dl = subprocess.run(["dwarfdump", "--debug-line", obj], capture_output=True, text=True).stdout.split("\n")
files, rows, cu = {}, [], 0
for i, l in enumerate(dl):
    if l.startswith("debug_line["): cu += 1
    m = re.match(r"file_names\[\s*(\d+)\]:", l)
    if m: files[(cu, int(m.group(1)))] = re.sub(r'.*"(.*)".*', r"\1", dl[i + 1]).split("/")[-1]
    m = re.match(r"(0x[0-9a-f]{16})\s+(\d+)\s+\d+\s+(\d+)", l)
    if m and int(m.group(2)): rows.append((int(m.group(1), 16), int(m.group(2)), (cu, int(m.group(3)))))
rows.sort(); ra = [r[0] for r in rows]
lc = collections.Counter()
for ad, c in pcs.items():
    k = bisect.bisect_right(ra, ad - slide - fb + fo) - 1
    lc[f"{files.get(rows[k][2], '?')}:{rows[k][1]}" if k >= 0 else "?"] += c
tot = sum(pcs.values())
print(f"{key}: {tot} self samples of {n_thr} thread samples ({100*tot/max(n_thr,1):.1f}%)")
for b, c in lc.most_common(top): print(f"  {c:6d} {100*c/max(tot,1):5.1f}%  {b}")
