#!/usr/bin/env python3
"""s7310 G5f: from s7309_tri_texcoef.py 'all' output, list textured tris that touch the left fb edge (any vertex x <= XMAX, default 1)
plus a census of start-W over all textured tris. usage: s7310_left_w.py texcoef.txt [XMAX]"""
import sys, re, ast
xmax = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
rows = []; cur = None
for ln in open(sys.argv[1]):
    m = re.match(r'i=(\d+) op=(\w+) y\(h,m,l\)=(\(.*?\)) x\(h,dh,m,dm,l,dl\)=(\(.*?\))', ln)
    if m: cur = dict(i=int(m[1]), op=m[2], y=ast.literal_eval(m[3]), x=ast.literal_eval(m[4])); rows.append(cur); continue
    m = re.match(r'\s+S=(\S+) T=(\S+) W=(\S+) \| dx (\S+) (\S+) (\S+) \| de (\S+) (\S+) (\S+)', ln)
    if m and cur: cur.update(W=float(m[3]), dWdx=float(m[6]), dWde=float(m[9]))
tex = [r for r in rows if 'W' in r]
def vx(r):
    yh, ym, yl = r['y']; xh, dh, xm, dm, xl, dl = r['x']
    return [xh, xh + dh * (yl - yh), xm, xm + dm * (ym - yh), xl, xl + dl * (yl - ym)]
lo = [r for r in tex if min(vx(r)) <= xmax]
print('textured', len(tex), 'W<=0.01:', sum(r['W'] <= 0.01 for r in tex), 'min W', min(r['W'] for r in tex))
print('left-edge tris (x<=%g): %d' % (xmax, len(lo)))
for r in lo:
    # W at the far end of the tri's major edge: W + dWde * (yl - yh) (along edge H)
    yh, ym, yl = r['y']; we = r['W'] + r['dWde'] * (yl - yh)
    print('  i=%d op=%s y=%s W=%.4f dWdx=%.3f dWde=%.4f W_end=%.3f minx=%.1f' % (r['i'], r['op'], r['y'], r['W'], r['dWdx'], r['dWde'], we, min(vx(r))))
