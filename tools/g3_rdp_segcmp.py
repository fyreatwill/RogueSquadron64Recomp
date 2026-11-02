#!/usr/bin/env python3
"""s6801 G3: score one retail segment against one port segment from the g3_rdp_segments.py frame caches.
Runs both the frame-pair matcher (g3_rdp_frame_match.score) and the phase-free summary (g3_rdp_phase.summary), so a
positive control (same screen, other segment pair) and a cross-screen control come from the SAME run.
usage: g3_rdp_segcmp.py RETAIL.bin A:B PORT.bin C:D [label]
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import g3_rdp_frame_match as m, g3_rdp_phase as ph, g3_rdp_segments as sg
def sl(F, s): a, b = map(int, s.split(':')); return F[a:b]
if __name__ == '__main__':
    a = sys.argv; R = sl(sg.all_frames(a[1], True), a[2]); P = sl(sg.all_frames(a[3], False), a[4]); lab = a[5] if len(a) > 5 else ''
    ex, n, med, mx = m.score(R[-240:], P[-240:])
    r, p = ph.summary(R), ph.summary(P)
    print('%s pair exact %d/%d median %d max %d | rects %d/%d static %d/%d eq=%s shared-anim %d (r-only %d p-only %d) '
          'tris q %s / %s ratio %.3f' % (lab, ex, n, med, mx, r['mode'], p['mode'], len(r['static']), len(p['static']),
          r['static'] == p['static'], len(r['anim'] & p['anim']), len(r['anim'] - p['anim']), len(p['anim'] - r['anim']),
          r['q'], p['q'], p['mean'] / r['mean'] if r['mean'] else 0))
    if r['static'] != p['static']:
        print('  retail-only static', sorted(r['static'] - p['static'])[:8]); print('  port-only static', sorted(p['static'] - r['static'])[:8])
