# s6785: bottom prompt line (y>=300) texrects with PRIM, per arm: union with frame-presence counts.
import sys, collections
sys.path.insert(0, 'tools'); import g3_rdp_frame_match as m
for tag, F in (('retail', m.frames(sys.argv[1], True, 240)), ('port', m.frames(sys.argv[2], False, 240))):
    u = collections.Counter()
    for c in F: u.update({k[:4] for k in c if k[0] != 'tri' and k[1] >= 300})
    print(tag, len(F), 'frames;', len(u), 'distinct bottom rects')
    for k, v in sorted(u.items()): print('   ', k, v)
