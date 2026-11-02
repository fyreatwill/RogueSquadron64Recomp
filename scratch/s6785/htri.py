# s6785: hangar tri-count distribution over a long window (steady hangar frames only: 153 texrects), plus autocorrelation period.
import sys, collections
sys.path.insert(0, 'tools'); import g3_rdp_frame_match as m
K = int(sys.argv[3])
for tag, F in (('retail', m.frames(sys.argv[1], True, K)), ('port', m.frames(sys.argv[2], False, K))):
    t = [sum(v for k, v in c.items() if k[0] == 'tri') for c in F if sum(v for k, v in c.items() if k[0] != 'tri') == 153]
    s = sorted(t); q = [s[int(len(s) * x)] for x in (0.05, 0.25, 0.5, 0.75, 0.95)]
    n = len(t); mu = sum(t) / n; v = [x - mu for x in t]
    ac = [(sum(v[i] * v[i + l] for i in range(n - l)) / sum(x * x for x in v), l) for l in range(20, min(600, n // 2))]
    print(tag, 'steady frames', n, 'of', len(F), 'tri q05..q95', q, 'mean %.1f' % mu, 'best period (ac,lag)', max(ac))
