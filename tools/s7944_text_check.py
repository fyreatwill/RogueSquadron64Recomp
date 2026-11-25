#!/usr/bin/env python3
"""s7944: text-mask checks on the F6 panel shots from tools/s7944_pad_text_witness.zsh.
Text mask = pixels with min(R,G,B) > 170 (panel text is white; the 0.92-alpha window bg and the blue cursor band are not).
Crops come from the logged srcA= (A-row source cell) and msg= (message line) rects, window points -> png px as in s7942.
Checks (each needs the logged draw-thread text AND the pixels to agree):
  drawn text: open srcA = r3 srcA != (unbound); clear srcA = (unbound); clear msg 'Row cleared...'; r3 msg 'Defaults restored...'
  pixels: srcA IoU(open,r3) >= 0.85 (defaults redrawn), IoU(open,clear) <= 0.5 (cell changed), every srcA crop has text;
          msg crop has text in clear and r3, IoU(clear,r3) <= 0.5 (message changed)
  negative control: the closed shot cropped at open's srcA rect has IoU(open,closed) <= 0.3 (no panel -> no match)."""
import re, sys, os
from PIL import Image
D = sys.argv[1]
shots = {}
for line in open(os.path.join(D, 'shots.txt')):
    sh = int(re.search(r'shot=(\d+)', line).group(1)); step = re.search(r'step=(\S+)', line).group(1)
    wx, wy, ww, wh = map(int, re.search(r'win=\d+ (-?\d+) (-?\d+) (\d+) (\d+)', line).groups())
    m = re.search(r'disp=(\d+)x(\d+)', line); dh = float(m.group(2)) if m else None
    rect = lambda k: tuple(map(int, re.search(k + r'=(-?\d+),(-?\d+),(-?\d+),(-?\d+)', line).groups())) if re.search(k + r'=-?\d', line) else None
    txt = lambda k: (re.search(r'\|' + k + r'=(.*?)\|', line) or [None, None])[1]
    shots[step] = dict(sh=sh, ww=ww, wh=wh, dh=dh, srcA=rect('srcA'), msg=rect('msg'), srcA_txt=txt('srcA_txt'), msg_txt=txt('msg_txt'),
                       im=Image.open(os.path.join(D, f'shot{sh}.png')).convert('RGB'))
def mask(s, r, ref):
    im = s['im']; W, H = im.size; sc = W / s['ww']; title = s['wh'] - ref['dh']
    x0, y0, x1, y1 = r; px = im.load(); out = set()
    for y in range(int((title + y0) * sc), int((title + y1) * sc)):
        for x in range(int(x0 * sc), int(x1 * sc)):
            if 0 <= x < W and 0 <= y < H and min(px[x, y]) > 170: out.add((x - int(x0 * sc), y - int((title + y0) * sc)))
    return out
iou = lambda a, b: len(a & b) / max(1, len(a | b))
res = []
def chk(name, ok, det): res.append(ok); print(f'{name}={"PASS" if ok else "FAIL"} {det}')
need = ['open_idle', 'close_idle', 'clear_idle', 'r3_hold_idle']
miss = [k for k in need if k not in shots]
if miss: print('missing shots', miss); print('VERDICT FAIL'); sys.exit(1)
o, c, cl, r3 = (shots[k] for k in need)
chk('drawn_srcA', o['srcA_txt'] == r3['srcA_txt'] != '(unbound)' and cl['srcA_txt'] == '(unbound)',
    f"open={o['srcA_txt']!r} clear={cl['srcA_txt']!r} r3={r3['srcA_txt']!r}")
chk('drawn_msg', (cl['msg_txt'] or '').startswith('Row cleared') and (r3['msg_txt'] or '').startswith('Defaults restored'),
    f"open={o['msg_txt']!r} clear={cl['msg_txt']!r} r3={r3['msg_txt']!r}")
mo, mcl, mr3 = mask(o, o['srcA'], o), mask(cl, cl['srcA'], cl), mask(r3, r3['srcA'], r3)
mc = mask(c, o['srcA'], o)  # closed: no rect of its own, crop at open's rect
chk('srcA_text_present', min(len(mo), len(mcl), len(mr3)) >= 15, f'px open={len(mo)} clear={len(mcl)} r3={len(mr3)} closed={len(mc)}')
chk('srcA_reset_redraws_defaults', iou(mo, mr3) >= 0.85, f'IoU(open,r3)={iou(mo, mr3):.3f}')
chk('srcA_clear_changes_cell', iou(mo, mcl) <= 0.5, f'IoU(open,clear)={iou(mo, mcl):.3f}')
chk('neg_closed_no_match', iou(mo, mc) <= 0.3, f'IoU(open,closed)={iou(mo, mc):.3f}')
if cl['msg'] and r3['msg']:
    gcl, gr3 = mask(cl, cl['msg'], cl), mask(r3, r3['msg'], r3)
    chk('msg_text_present', min(len(gcl), len(gr3)) >= 15, f'px clear={len(gcl)} r3={len(gr3)}')
    chk('msg_changes', iou(gcl, gr3) <= 0.5, f'IoU(clear,r3)={iou(gcl, gr3):.3f}')
else: chk('msg_rect_logged', False, f"clear={cl['msg']} r3={r3['msg']}")
print(f'tag=s7944_pad_text checks={len(res)} pass={sum(res)}')
print('VERDICT', 'PASS' if all(res) else 'FAIL'); sys.exit(0 if all(res) else 1)
