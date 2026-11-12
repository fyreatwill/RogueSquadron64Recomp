#!/usr/bin/env python3
"""s7224: score LIVE window changes (fullscreen toggle / SDL_SetWindowSize mid-flight) per RETINA arm.
Inputs per arm: DIR/log_ARM.txt (game stderr), DIR/ring_ARM.txt (ROGUESQ_PRESENT_RING), DIR/shot_ARM_T.png (screencapture -x).
Per arm prints:
  events  = [g1f] fullscreen on/off, test resize, resized rows, [metal-resize-entry], [retina] swapchain create rows (log order)
  Z rows  = swap chain resize() witnesses from the ring (time, w, h) and how many distinct sizes they took
  per-change present rate: on-screen P/s for the 3 s before and seconds +1..+6 after each Z size change, recovery time to >=25/s
  gaps    = present gaps >250 ms after 10 s
  shots   = hf (s7203 half-res residual, central crop) of each screenshot; on 2x panels a backing-pixel chain scores higher.
  match   = whether each distinct Z size equals 2 x (RETINA=1) or 1 x (RETINA=0) the window point size logged just before it.
Positive control: hf of the first shot after a 2x down/up resample must fall (prints hf_ctl).
NOTE: the whole-screen central crop above FAILED its control in s7224 (ctl rose); trust the phase table instead:
  --phase NAME:X,Y,W,H:T,T,...  (px rect on the 2x desktop shot, or NAME:fs:T,.. for the whole screen), scored with the
  s7223 central-80% crop per arm, with the down/up2 control per phase. Phases are printed side by side for all arms."""
import sys, re, glob, collections
from PIL import Image, ImageChops, ImageStat
d = sys.argv[1]
def m(i): return ImageStat.Stat(i).mean[0]
def hf(a):
    w, h = a.size; a = a.crop((w * 3 // 10, h * 4 // 10, w * 7 // 10, h * 6 // 10)); w, h = a.size
    if ImageStat.Stat(a).stddev[0] < 2: return None
    rt = a.resize((w // 2, h // 2), Image.BOX).resize((w, h), Image.BILINEAR)
    return m(ImageChops.difference(a, rt)) / max(m(ImageChops.difference(a, ImageChops.offset(a, 1, 0))), 1e-6)
PH = [a[8:] for a in sys.argv[2:] if a.startswith('--phase=')]
ARMS = [a for a in sys.argv[2:] if not a.startswith('--')]
for arm in ARMS:
    print(f'===== {arm}')
    log = open(f'{d}/log_{arm}.txt', errors='replace').read().splitlines()
    pat = re.compile(r'\[g1f\] (fullscreen (on|off)|test resize|test F11|resized|window \d+x\d+ fullscreen)|\[metal-resize-entry\]|\[retina\] swapchain')
    ev = [l for l in log if pat.search(l)]
    c = collections.Counter(re.sub(r'\d+', '#', l)[:60] for l in ev)
    for l in ev[:60]: print('  ', l[:150])
    if len(ev) > 60: print('   ... total', len(ev))
    print('  event kinds:', dict(c))
    z = []; ts = []; p = collections.Counter(); t0 = None
    for l in open(f'{d}/ring_{arm}.txt', errors='replace'):
        f = l.split()
        if len(f) < 2: continue
        try: t = float(f[1])
        except Exception: continue
        if t0 is None: t0 = t
        if f[0] == 'P':
            ts.append(t - t0)
            try:
                if float(f[3].split('=')[1]) > 0: p[int(t - t0)] += 1
            except Exception: pass
        elif f[0] == 'Z': z.append((round(t - t0, 2), f[2], f[3]))
    sizes = []
    for t, w, h in z:
        if not sizes or sizes[-1][1:] != (w, h): sizes.append((t, w, h))
    print(f'  Z rows {len(z)}, size changes {len(sizes)}:', sizes)
    for t, w, h in sizes[1:]:
        s = int(t); pre = [p[k] for k in range(s - 3, s)]; post = [p[k] for k in range(s + 1, s + 7)]
        rec = next((k - s for k in range(s, s + 15) if p[k] >= 25), None)
        print(f'   change @{t} -> {w} {h}: pre {pre} post {post} recover>=25/s in {rec} s')
    print('  gaps>250ms after 10s:', [(round(b - a, 3), round(a, 1)) for a, b in zip(ts, ts[1:]) if b - a > 0.25 and a > 10])
    if ts: print('  on-screen P/s min 12..end-2:', min(p[s] for s in range(12, int(ts[-1]) - 1)), ' last t', round(ts[-1], 1))
    shots = sorted(glob.glob(f'{d}/shot_{arm}_*.png'), key=lambda s: int(re.findall(r'_(\d+)\.png', s)[0]))
    out = []; ctl = None
    for s in shots:
        a = Image.open(s).convert('L'); v = hf(a)
        out.append(f"{re.findall(r'_(\d+)\.png', s)[0]}:{v and round(v, 3)}")
        if ctl is None and v:
            w, h = a.size; ctl = (round(v, 3), round(hf(a.resize((w // 2, h // 2), Image.BOX).resize((w, h), Image.BILINEAR)) or 0, 3))
    print('  hf per shot:', ' '.join(out)); print('  hf_ctl (orig, down/up2):', ctl)
def hf80(a):
    w, h = a.size; a = a.crop((w // 10, h // 10, w - w // 10, h - h // 10)); w, h = a.size
    rt = a.resize((w // 2, h // 2), Image.BOX).resize((w, h), Image.BILINEAR)
    return m(ImageChops.difference(a, rt)) / max(m(ImageChops.difference(a, ImageChops.offset(a, 1, 0))), 1e-6)
for spec in PH:
    name, rect, ts = spec.split(':'); ts = [int(t) for t in ts.split(',')]
    r = None if rect == 'fs' else tuple(int(v) for v in rect.split(','))
    row = []
    for arm in ARMS:
        v = []; c = []
        for t in ts:
            a = Image.open(f'{d}/shot_{arm}_{t}.png').convert('L')
            if r: a = a.crop((r[0], r[1], r[0] + r[2], r[1] + r[3]))
            v.append(hf80(a)); w, h = a.size; c.append(hf80(a.resize((w // 2, h // 2), Image.BOX).resize((w, h), Image.BILINEAR)))
        row.append(f'{arm} hf {sum(v)/len(v):.3f} ctl {sum(c)/len(c):.3f}')
    print('phase', name, ts, ' | '.join(row))
