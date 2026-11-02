# s6793: per 0.5-px x bin, maximal runs of frames (gap <= 3) with a tall (>=150 px) near-vertical edge in that bin.
# A stationary on-screen seam = one bin holding for >= MIN frames. Args: MIN tsv...
import sys, collections
MIN = int(sys.argv[1])
for path in sys.argv[2:]:
    last = {}; start = {}; runs = []
    for l in open(path):
        i, st, e = l.rstrip('\n').split('\t'); i = int(i)
        for x in set(round(float(t.split(':')[0]) * 2) / 2 for t in e.split(',') if int(t.split(':')[2]) >= 150):
            if x in last and i - last[x] <= 3: last[x] = i
            else:
                if x in last and last[x] - start[x] >= MIN: runs.append((start[x], last[x], x))
                start[x] = last[x] = i
    runs += [(start[x], last[x], x) for x in last if last[x] - start[x] >= MIN]
    runs.sort(); print(path, len(runs), 'stationary runs >=', MIN)
    for r in runs: print('  frames %d-%d (%d) x=%.1f' % (r[0], r[1], r[1] - r[0], r[2]))
