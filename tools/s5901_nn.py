"""s5901 offline analysis: nearest-neighbour bolt tracks from [s5901] raw samples.
usage: python3 -I tools/s5901_nn.py run.log
Per cycle c, samples (pp,len,best_ratio,id). Greedy NN match of cycle c samples to cycle c-1 (max 40 u).
Reports: segment length stats, per-step displacement, track age histogram, positive control (#tracks age>=3),
and per-track min over life of best_ratio (sd2/r2; <=1 means segment inside collider sphere)."""
import re, sys, math, collections
R = re.compile(r"\[s5901\] c=(\d+) pp=([^,]+),([^,]+),([^ ]+) len=(\S+) rows=(\d+) best_ratio=(\S+) id=(\S+) ctr=([^,]+),([^,]+),([^ ]+) r2=(\S+)")
cyc = collections.defaultdict(list)
for line in open(sys.argv[1], errors="replace"):
    m = R.search(line)
    if m:
        g = m.groups(); cyc[int(g[0])].append(((float(g[1]), float(g[2]), float(g[3])), float(g[4]), float(g[6]), g[7], int(g[5])))
print("cycles", len(cyc), "samples", sum(map(len, cyc.values())))
lens = sorted(s[1] for v in cyc.values() for s in v)
if lens: print("seg len p10/50/90/max", lens[len(lens)//10], lens[len(lens)//2], lens[9*len(lens)//10], lens[-1])
tracks = []; live = []; steps = []
for c in sorted(cyc):
    new = []; used = set()
    for s in cyc[c]:
        best = None
        for i, t in enumerate(live):
            if i in used: continue
            d = math.dist(s[0], t["p"])
            if d < 40 and (best is None or d < best[0]): best = (d, i)
        if best:
            used.add(best[1]); t = live[best[1]]; steps.append(best[0]); t["age"] += 1; t["disp"] += best[0]; t["p"] = s[0]; t["min"] = min(t["min"], s[2]); new.append(t)
        else:
            new.append({"p": s[0], "age": 1, "disp": 0.0, "min": s[2], "len": s[1]})
    for i, t in enumerate(live):
        if i not in used: tracks.append(t)
    live = new
tracks += live
ages = collections.Counter(min(t["age"], 10) for t in tracks)
print("tracks", len(tracks), "age hist (10=10+)", sorted(ages.items()))
print("POSITIVE CONTROL tracks age>=3:", sum(1 for t in tracks if t["age"] >= 3), "(need >=100)")
if steps: steps.sort(); print("step disp p10/50/90", steps[len(steps)//10], steps[len(steps)//2], steps[9*len(steps)//10])
long_ = [t for t in tracks if t["age"] >= 3]
if long_:
    tot = [t["disp"] for t in long_]; tot.sort(); print("total disp (age>=3) p10/50/90/max", tot[len(tot)//10], tot[len(tot)//2], tot[9*len(tot)//10], tot[-1])
    mr = sorted(t["min"] for t in long_); print("min best_ratio over life (age>=3) p10/50/90", mr[len(mr)//10], mr[len(mr)//2], mr[9*len(mr)//10], " frac<=1:", sum(1 for x in mr if x <= 1) / len(mr))
allmr = sorted(t["min"] for t in tracks); print("ALL tracks frac min ratio<=1:", sum(1 for x in allmr if x <= 1) / max(1, len(allmr)), " <=4:", sum(1 for x in allmr if x <= 4) / max(1, len(allmr)))
