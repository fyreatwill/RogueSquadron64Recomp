#!/usr/bin/env python3
"""s7783 fb-shared-slot verdict: port vs retail placement of display-list chunks.
Port: a ROGUESQ_S7779_ARENA=1 ROGUESQ_S7781_PLANT=1 run.log ([s7783] dlep/sum/plant lines, src/main/main.cpp s7783_*).
Retail: an rs64_oracle log run with RS64_EXEC_REG_HIST=3 --watch-pc 0x8000D5A8 --watch-pc 0x8000D5E0 and angrylion video
([s7783-reg] rows: 4 KB pages of $v1 = the DL emitter's store base, keyed by VI width).
Compares the 640x340 intro phase: port epoch 2 (arena 62B800 ext 6A400) vs retail width-640 rows, against the FB pair
[0x62B800, 0x700000). Controls (rc 3 on failure): port plant_in>=1 (fake store at cimg+0x100 counted in-cimg), port epoch 2
present, retail total>0 with a [gpr-ctl] line, and the classifier must put a planted page 0x6F0000 inside the FB pair.
rc 0 = H-design (both place chunks in the FB pair, or neither), rc 4 = H-overlap port-only (port in pair, retail not),
rc 5 = retail-only. usage: s7783_shared_slot_score.py <port run.log> <oracle log> [ep=2]"""
import re, sys
port, orc = sys.argv[1], sys.argv[2]; ep = int(sys.argv[3]) if len(sys.argv) > 3 else 2
LO, HI = 0x62B800, 0x700000
inpair = lambda p: LO <= p < HI
P = open(port, errors="replace").read().splitlines(); O = open(orc, errors="replace").read().splitlines()
ok = True
if not inpair(0x6F0000): print("CONTROL FAIL classifier"); ok = False
sums = [l for l in P if l.startswith("[s7783] sum")]
pin = int(re.search(r"plant_in=(\d+)", sums[-1])[1]) if sums else 0
if pin < 1: print("CONTROL FAIL port plant_in", pin); ok = False
dl = [l for l in P if l.startswith(f"[s7783] dlep ep={ep} ")]
if not dl: print("CONTROL FAIL no port epoch", ep); ok = False
if not any(l.startswith("[gpr-ctl]") for l in O): print("CONTROL FAIL oracle gpr-ctl"); ok = False
rows = [dict(kv.split("=") for kv in l.split()[1:]) for l in O if l.startswith("[s7783-reg] width=")]
rt = sum(int(r["n"]) for r in rows if r["width"] == "640")
if rt < 1: print("CONTROL FAIL oracle 640 total 0"); ok = False
if not ok: sys.exit(3)
d = dl[-1]; pages = {int(a, 16): int(b) for a, b in re.findall(r" ([0-9A-F]{6})=(\d+)", d.split("pages:")[1])}
p_in = sum(n for a, n in pages.items() if inpair(a)); p_n = int(re.search(r" n=(\d+)", d)[1])
r_in = sum(int(r["n"]) for r in rows if r["width"] == "640" and inpair(int(r["page"], 16)))
rp = sorted(int(r["page"], 16) for r in rows if r["width"] == "640")
print(f"port ep{ep}: dl_stores={p_n} in_FB_pair={p_in} lo..hi={re.search(r'lo=(\w+) hi=(\w+)', d).groups()}")
print(f"retail w640: dl_stores={rt} in_FB_pair={r_in} pages {rp[0]:06X}..{rp[-1] + 0xFFF:06X}")
if p_in and not r_in: print("H-overlap (port-only): the port places DL chunks inside the framebuffer pair, retail never does"); sys.exit(4)
if r_in and not p_in: print("retail-only"); sys.exit(5)
print("H-design (same placement class)"); sys.exit(0)
