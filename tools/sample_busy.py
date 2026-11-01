"""s6704: per-thread busy samples from a macOS sample(1) report. A leaf is a call-tree line with no deeper child; leaves whose
symbol is a kernel wait (cvwait/semaphore/workq/mach_msg/...) count as idle, the rest as busy. Prints the busiest threads and
their top busy leaf symbols. Usage: sample_busy.py <sample.txt> [nthreads]"""
import sys, re, collections
WAIT = re.compile(r"cvwait|semaphore_|workq_kernreturn|semwait|mach_msg|kevent|__select|__ulock_wait|nanosleep|start_wqthread")
L = re.compile(r"^(\s+[+!:| ]*)(\d+) (.*)$")
lines = open(sys.argv[1], errors="replace").read().split("\n")
nt = int(sys.argv[2]) if len(sys.argv) > 2 else 6
threads = []; cur = None; tree = []
for ln in lines:
    if ln.startswith("Total number in stack") or ln.startswith("Sort by top"): break
    m = L.match(ln)
    if not m: continue
    depth, n, sym = len(m[1]), int(m[2]), m[3]
    if "Thread_" in sym and depth <= 5:
        cur = [sym.split("  ")[0][:60], n, []]; threads.append(cur); continue
    if cur is not None: cur[2].append((depth, n, sym))
for t in threads:
    busy = 0; leaf = collections.Counter(); fr = t[2]
    for i, (d, n, s) in enumerate(fr):
        child = 0
        j = i + 1
        while j < len(fr) and fr[j][0] > d:
            if fr[j][0] == min(x[0] for x in fr[i + 1:j + 1]): child += fr[j][1]
            j += 1
        self_n = n - child
        if self_n > 0 and not WAIT.search(s):
            busy += self_n; leaf[re.sub(r"\s+\(in .*", "", s)[:70]] += self_n
    t.append(busy); t.append(leaf)
for t in sorted(threads, key=lambda t: -t[3])[:nt]:
    print(f"{t[0]:60s} busy={t[3]:6d}/{t[1]}")
    for s, n in t[4].most_common(6): print(f"      {n:6d} {s}")
