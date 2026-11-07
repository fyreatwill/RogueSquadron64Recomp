#!/usr/bin/env python3
"""s6925 G5h: per 30 VIs of a port RDP dump (RS64_RDP_BIN_PORT): colour images (width, address), scissors, texrect x span and fill rects.
Shows what width a screen really draws, to set against the VI mode in the [osViSetMode] log lines.  g5h_rdp_extents.py BIN [last=14]"""
import collections, importlib.util, os, sys
sp = importlib.util.spec_from_file_location('g', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'g5h_rdp_groups.py'))
src = open(sp.origin).read(); ns = {}; exec(src[:src.find('\ndef ', src.find('def cmds') + 10)], ns); cmds = ns['cmds']
fr = collections.OrderedDict()
for c in cmds(sys.argv[1]):
    vi, op, w0, w1 = c[:4]
    d = fr.setdefault(vi // 30 * 30, dict(ci=collections.Counter(), sc=collections.Counter(), tx=[9999, -1], n=0, fill=collections.Counter()))
    if op == 0x3F: d['ci'][(w0 & 0xFFF) + 1, hex(w1 & 0xFFFFFF)] += 1
    elif op == 0x2D: d['sc'][((w0 >> 12 & 0xFFF) >> 2, (w0 & 0xFFF) >> 2, (w1 >> 12 & 0xFFF) >> 2, (w1 & 0xFFF) >> 2)] += 1
    elif op in (0x24, 0x25):
        d['tx'][0] = min(d['tx'][0], (w1 >> 12 & 0xFFF) >> 2); d['tx'][1] = max(d['tx'][1], (w0 >> 12 & 0xFFF) >> 2); d['n'] += 1
    elif op == 0x36: d['fill'][((w1 >> 12 & 0xFFF) >> 2, (w1 & 0xFFF) >> 2, (w0 >> 12 & 0xFFF) >> 2, (w0 & 0xFFF) >> 2)] += 1
for k, d in list(fr.items())[-(int(sys.argv[2]) if len(sys.argv) > 2 else 14):]:
    print(k, 'ci', d['ci'].most_common(2), 'sc', d['sc'].most_common(2), 'tex', d['tx'], d['n'], 'fill', d['fill'].most_common(2))
