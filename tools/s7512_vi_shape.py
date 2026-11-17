#!/usr/bin/env python3
"""s7512 class FI: VI register shape vs hardware.

Input: game stderr logs with ROGUESQ_LOG_VI_SHAPE=1 (ultramodern events.cpp update_vi):
  [vi-mode]  n=<commit> ptr=<mode vaddr> w= <20 u32 words of the OSViMode as the VI thread read them>
  [vi-shape] n=<commit> t= rep=<commits of the PREVIOUS tuple> st=<our state> rst=<libultra shadow state> ctl= fld= mode= fb=
             ctrl= orig= width= intr= burst= vsync= hsync= leap= hstart= vstart= vburst= xscale= yscale=
Model (independent of the C commit path): retail libultra __osViSwapContext (ROM 0x80035550, stock) recomputed from the raw
mode words + fb vaddr + field + the libultra shadow state (osViSetMode state=1, osViSwapBuffer |=0x10, osViBlack 0x20):
  origin = K0/K1 phys(fb) + fld.origin; hStart = 0 when BLACK; REPEATLINE -> yScale 0, origin = phys(fb);
  every other register = the mode word. ctrl may differ from the mode ctrl only in osViSetSpecialFeatures bits.
Hardware register widths (n64brew VI page; RT64 decodeVI masks/bitfields are the same widths) -> raw bits outside = out-of-range.
ctl=1 commits are the in-run positive control (shadow forced black for 30 commits): each must classify as a black diff.
Exit: 0 = every non-ctl commit equal + in range + ctl PASS; 1 = live diff/out-of-range; 3 = control failure; 4 = no census.
"""
import re, sys

HW = {  # field -> hardware-implemented bits
    'ctrl': 0x1FFFF, 'orig': 0xFFFFFF, 'width': 0xFFF, 'intr': 0x3FF, 'burst': 0x3FFFFFFF, 'vsync': 0x3FF,
    'hsync': 0x1F0FFF, 'leap': 0x0FFF0FFF, 'hstart': 0x03FF03FF, 'vstart': 0x03FF03FF, 'vburst': 0x03FF03FF,
    'xscale': 0x0FFF0FFF, 'yscale': 0x0FFF0FFF,
}
FIELDS = list(HW)
SPECIAL_BITS = 0x4 | 0x8 | 0x10 | 0x10000 | 0x300  # gamma dither, gamma, divot, dither filter, AA mode
SHAPE = re.compile(r'\[vi-shape\] (.*)')
MODE = re.compile(r'\[vi-mode\] n=(\d+) ptr=([0-9A-F]+) w=((?: [0-9A-F]{8}){20})')


def phys(v):
    # fb 0 = ultramodern's unset framebuffer before the first swap; retail __osViInit seeds K0BASE (0x80000000) -> phys 0.
    if v == 0:
        return 0
    return v & 0x1FFFFFFF if 0x80000000 <= v < 0xC0000000 else None


def expected(w, fb, fld, rst, ctl):
    f = 10 + 5 * fld
    p = phys(fb)
    if p is None:
        return None
    e = {'width': w[2], 'burst': w[3], 'vsync': w[4], 'hsync': w[5], 'leap': w[6], 'hstart': w[7], 'xscale': w[8],
         'orig': (p + w[f]) & 0xFFFFFFFF, 'yscale': w[f + 1], 'vstart': w[f + 2], 'vburst': w[f + 3], 'intr': w[f + 4]}
    if (rst & 0x20) or ctl:
        e['hstart'] = 0
    if rst & 0x40:
        e['yscale'] = 0
        e['orig'] = p
    return e


def parse(path):
    modes, recs = {}, []
    with open(path, errors='replace') as fh:
        for line in fh:
            if '[vi-' not in line:
                continue
            m = MODE.search(line)
            if m:
                modes.setdefault(int(m.group(2), 16), []).append((int(m.group(1)), [int(x, 16) for x in m.group(3).split()]))
                continue
            m = SHAPE.search(line)
            if m:
                d = dict(kv.split('=', 1) for kv in m.group(1).split())
                r = {k: (float(v) if k == 't' else int(v, 16) if k not in ('n', 'rep', 'ctl', 'fld') else int(v))
                     for k, v in d.items()}
                recs.append(r)
    # weights: rep on line i+1 = commits line i's tuple held
    for i, r in enumerate(recs):
        r['cnt'] = recs[i + 1]['rep'] if i + 1 < len(recs) else 1
    return modes, recs


def mode_words(modes, ptr, n):
    best = None
    for (mn, w) in modes.get(ptr, []):
        if mn <= n:
            best = w
    return best


def classify(modes, recs):
    out = {'commits': 0, 'lines': len(recs), 'oor': {}, 'diff': {}, 'black_diff': 0, 'black_diff_ctl': 0, 'ctl_commits': 0,
           'ctrl_extra': 0, 'nomode': 0, 'first_diff': [], 'rst_flags': {}, 'retail_black_commits': 0, 'our_black_commits': 0,
           'max': {}}
    for r in recs:
        c = r['cnt']
        out['commits'] += c
        ctl = r['ctl']
        if ctl:
            out['ctl_commits'] += c
        out['rst_flags'][r['rst'] & 0xFF] = out['rst_flags'].get(r['rst'] & 0xFF, 0) + c
        for f in FIELDS:
            out['max'][f] = max(out['max'].get(f, 0), r[f])
            if r[f] & ~HW[f]:
                out['oor'][f] = out['oor'].get(f, 0) + c
        w = mode_words(modes, r['mode'], r['n'])
        if w is None:
            out['nomode'] += c
            continue
        if (r['ctrl'] ^ w[1]) & ~SPECIAL_BITS:
            out['ctrl_extra'] += c
        e = expected(w, r['fb'], r['fld'], r['rst'], ctl)
        if e is None:
            out['nomode'] += c
            continue
        if (r['rst'] & 0x20) or ctl:
            out['retail_black_commits'] += c
        if r['st'] & 0x20:
            out['our_black_commits'] += c
        for f, v in e.items():
            if r[f] != v:
                if f == 'hstart' and v == 0 and ((r['rst'] & 0x20) or ctl) and not (r['st'] & 0x20):
                    if ctl:
                        out['black_diff_ctl'] += c
                    else:
                        out['black_diff'] += c
                    continue
                out['diff'][f] = out['diff'].get(f, 0) + c
                if len(out['first_diff']) < 6:
                    out['first_diff'].append((r['n'], r['t'], f, hex(r[f]), hex(v)))
    return out


def synth(mut=None):
    """Synthetic census: 1 canonical mode, 4 commits (+ a ctl commit); mutants inject one defect each."""
    w = [0] * 20
    w[1:10] = [0x320E, 320, 0x03E52239, 0x20D, 0xC15, 0x0C150C15, 0x006C02EC, 0x200, 0]
    w[10:15] = [0x280, 0x400, 0x002501FF, 0x000E0204, 2]
    w[15:20] = [0x280, 0x400, 0x002501FF, 0x000E0204, 2]
    modes = {0x80128DA0: [(1, w)]}
    recs = []
    for i, fb in enumerate([0x806C3E00, 0x80700000, 0x806C3E00, 0x80700000, 0x806C3E00]):
        ctl = 1 if i == 4 else 0
        rst = 0x11
        e = expected(w, fb, 0, rst, 0)
        r = dict(n=i + 1, t=float(i), rep=1, st=0x1, rst=rst, ctl=ctl, fld=0, mode=0x80128DA0, fb=fb, ctrl=w[1], **e)
        recs.append(r)
    if mut == 'oor_origin':
        recs[1]['orig'] |= 0x1000000
        recs[1]['fb'] |= 0  # model sees the same fb -> also a diff; oor must fire
    elif mut == 'vstart':
        recs[2]['vstart'] ^= 0x10
    elif mut == 'black':
        recs[3]['rst'] |= 0x20  # retail black, ours shows the fb
    elif mut == 'no_ctl_black':
        recs[4]['hstart'] = 0  # ctl commit already black on our side -> ctl must NOT count it
        recs[4]['st'] |= 0x20
    elif mut == 'ctrl':
        recs[0]['ctrl'] ^= 0x40  # serrate is not a special-features bit
    for i, r in enumerate(recs):
        r['cnt'] = 1
    return classify(modes, recs)


def controls():
    ok = True
    c = synth()
    t = (not c['diff'] and not c['oor'] and c['black_diff'] == 0 and c['black_diff_ctl'] == 1 and c['ctrl_extra'] == 0)
    print(f"  ctl canon: diff={c['diff']} oor={c['oor']} black={c['black_diff']} black_ctl={c['black_diff_ctl']} {'ok' if t else 'FAIL'}")
    ok &= t
    for mut, pred in [('oor_origin', lambda c: c['oor'].get('orig', 0) == 1),
                      ('vstart', lambda c: c['diff'].get('vstart', 0) == 1),
                      ('black', lambda c: c['black_diff'] == 1),
                      ('no_ctl_black', lambda c: c['black_diff_ctl'] == 0),
                      ('ctrl', lambda c: c['ctrl_extra'] == 1)]:
        c = synth(mut)
        t = pred(c)
        print(f"  mutant {mut}: detected={t}")
        ok &= t
    print(f"controls {'PASS' if ok else 'FAIL'} (1 synthetic + 5 mutants)")
    return ok


def main(argv):
    want_ctl = '--controls' in argv
    paths = [a for a in argv if not a.startswith('--')]
    rc = 0
    if want_ctl and not controls():
        rc = 3
    if not paths:
        return rc
    for p in paths:
        modes, recs = parse(p)
        print(f"== {p}")
        if not recs:
            print("   no [vi-shape] census")
            rc = max(rc, 4)
            continue
        c = classify(modes, recs)
        expect_ctl = '[vi-shape-ctl] armed' in open(p, errors='replace').read()
        mx = ' '.join(f"{f}={c['max'][f]:X}" for f in ('orig', 'width', 'xscale', 'yscale', 'ctrl'))
        print(f"   commits={c['commits']} lines={c['lines']} modes={len(modes)} nomode={c['nomode']} oor={c['oor']} diff={c['diff']}"
              f" ctrl_extra={c['ctrl_extra']}")
        print(f"   black: retail={c['retail_black_commits']} ours={c['our_black_commits']} black_diff(live)={c['black_diff']}"
              f" ctl_commits={c['ctl_commits']} black_diff(ctl)={c['black_diff_ctl']} rst_flags={c['rst_flags']}")
        print(f"   max: {mx}")
        if c['first_diff']:
            print(f"   first diffs (n, t, field, ours, model): {c['first_diff']}")
        ctl_ok = (not expect_ctl) or (c['ctl_commits'] == 30 and c['black_diff_ctl'] == 30)
        print(f"   in-run ctl: armed={expect_ctl} {'PASS' if ctl_ok else 'FAIL'}")
        if not ctl_ok:
            rc = max(rc, 3)
        if c['diff'] or c['oor'] or c['ctrl_extra'] or c['black_diff'] or c['nomode']:
            rc = max(rc, 1) if rc != 3 else rc
    return rc


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
