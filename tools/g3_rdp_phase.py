#!/usr/bin/env python3
"""s6785 G3: phase-free RDP-stream compare for ANIMATED screens, where g3_rdp_frame_match.py best pairs never go exact.

g3_rdp_frame_match keys tris by PRIM and texrects by exact geometry, so a scene-wide PRIM flicker (hangar: ~1100 tris
under one PRIM that changes every frame) or a wobbling image grid reads as hundreds of differing items. This compares
distributions instead, over a long tail (--k, default 1500 frames):
  - texrect count per frame and tri count quantiles (steady frames = trailing run of the modal texrect count)
  - rects present in EVERY steady frame (static HUD/prompt text): must be the same set in both arms
  - animated rects (not in every frame): number of distinct positions per arm and how many are shared
  - tri-count autocorrelation peak (period hint)
H-match = equal texrect count, same static set, overlapping animated families, tri quantiles within a few %.
usage: g3_rdp_phase.py RETAIL.bin PORT.bin [--k 1500]
"""
import sys, collections
sys.path.insert(0, __import__('os').path.dirname(__file__)); import g3_rdp_frame_match as m
def summary(F):
    nt = [sum(v for k, v in c.items() if k[0] != 'tri') for c in F]
    mode = collections.Counter(nt).most_common(1)[0][0]
    # steady = the trailing run of modal frames (gaps of <=3 off-mode frames allowed), so an earlier screen with the
    # same texrect count (hangar fly-in before SELECT LEVEL) does not leak in
    i, gap = len(F) - 1, 0
    while i >= 0 and gap <= 3: gap = 0 if nt[i] == mode else gap + 1; i -= 1
    S = [c for c, n in zip(F[i + 1:], nt[i + 1:]) if n == mode]
    tris = sorted(sum(v for k, v in c.items() if k[0] == 'tri') for c in S)
    pres = collections.Counter(); [pres.update({k[:4] for k in c if k[0] != 'tri'}) for c in S]
    static = {k for k, v in pres.items() if v == len(S)}
    t = [sum(v for k, v in c.items() if k[0] == 'tri') for c in S]; mu = sum(t) / len(t); d = [x - mu for x in t]
    den = sum(x * x for x in d) or 1
    ac = max(((sum(d[i] * d[i + l] for i in range(len(d) - l)) / den, l) for l in range(2, max(3, len(d) // 2))), default=(0, 0))
    return dict(n=len(F), steady=len(S), mode=mode, q=[tris[int(len(tris) * x)] for x in (.05, .25, .5, .75, .95)],
                mean=mu, static=static, anim=set(pres) - static, ac=ac)
if __name__ == '__main__':
    a = sys.argv; k = int(a[a.index('--k') + 1]) if '--k' in a else 1500
    R = summary(m.frames(a[1], True, k)); P = summary(m.frames(a[2], False, k))
    for tag, s in (('retail', R), ('port', P)):
        print('%-6s frames %d steady %d texrects/frame %d | tris q05..q95 %s mean %.1f | static %d animated %d | ac %.2f@%d'
              % (tag, s['n'], s['steady'], s['mode'], s['q'], s['mean'], len(s['static']), len(s['anim']), s['ac'][0], s['ac'][1]))
    print('static set equal: %s (retail-only %s, port-only %s)' % (R['static'] == P['static'],
          sorted(R['static'] - P['static'])[:6], sorted(P['static'] - R['static'])[:6]))
    print('animated positions shared %d (retail-only %d, port-only %d)' % (len(R['anim'] & P['anim']),
          len(R['anim'] - P['anim']), len(P['anim'] - R['anim'])))
    print('tri mean ratio port/retail %.3f' % (P['mean'] / R['mean'] if R['mean'] else 0))
