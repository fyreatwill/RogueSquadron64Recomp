#!/usr/bin/env python3
"""s7705: join s7702 census hits against RT64 SKIP_WILD_W write-back extents (addr, w, rowEnd exclusive, from run.log).
A hit is IN when its row range overlaps [0,rowEnd) of a skipped buffer at the same address and width; PAST when every row >= rowEnd
(memory after the buffer: the census matches a conservative 480 rows). Prints per-hit class and a summary; boot-cinematic timg hits
on 0x9B6000 (s7702/s7704) are the positive control and must come out IN.
s7706: in_after_boot counts EVERY post-boot IN hit whatever its age (a stale read of a skipped buffer still gets RDRAM that was
never written back); fresh_in_after_boot is the old non-stale subset. Optional argv[2] = boot cutoff seconds (default 23).
Test: tools/test_s7705_join.sh."""
import re, sys
d = sys.argv[1]
boot = float(sys.argv[2]) if len(sys.argv) > 2 else 23.0
skip = {}
for l in open(f"{d}/run.log", errors="replace"):
    m = re.search(r"SKIP_WILD_W #\d+ tag=color addr=0x([0-9A-F]+) w=(\d+) siz=\d+ rows=(\d+)\.\.(\d+)", l)
    if m:
        k = (int(m[1], 16), int(m[2])); skip[k] = max(skip.get(k, 0), int(m[4]))
nin = npast = 0; ctl = 0; post_in = []; post_any = 0
for l in open(f"{d}/s7702.log"):
    m = re.match(r"hit src=(\S+) img=(\w+)@0x([0-9A-F]+) cur=\d+ w=(\d+) age=(\S+) n=(\d+) loaded=\d+ rows=(\d+)\.\.(\d+) t=([\d.]+)\.\.([\d.]+)", l)
    if not m: continue
    k = (int(m[3], 16), int(m[4]))
    if k not in skip: continue
    re_ = skip[k]; r0 = int(m[7]); t0 = float(m[9]); age = m[5]
    cls = "IN" if r0 < re_ else "PAST"
    print(f"{cls:4} {m[1]:7} {m[2]:6} 0x{k[0]:06X} w={k[1]} rowEnd={re_} rows={m[7]}..{m[8]} age={age} n={m[6]} t={m[9]}..{m[10]}")
    if cls == "IN":
        nin += 1
        if m[1] == "timg" and k[0] == 0x9B6000 and t0 < boot: ctl += 1
        if t0 >= boot:
            post_any += 1
            if age != "stale": post_in.append(l.strip())
    else: npast += 1
print(f"summary skipped_bufs={len(skip)} in={nin} past={npast} ctl_boot_in={ctl} fresh_in_after_boot={len(post_in)} in_after_boot={post_any}")
sys.exit(0 if ctl > 0 else 1)
