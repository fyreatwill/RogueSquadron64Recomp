#!/usr/bin/env python3
"""s7517 class FN: VI special features (osViSetSpecialFeatures) + presented-VI shape vs hardware.

Reads game logs carrying ROGUESQ_LOG_VI_FEAT=1 rows:
  [vi-feat] c= ts= func= before= after= modectrl= mode=        every osViSetSpecialFeatures call (ultramodern)
  [vi-feat-commit] c= ts= ctrl= game= ctl= vstart= hstart= mode= st=   committed VI_STATUS / vStart changes
  [vi-feat-rt] p= ts= rep= ctrl= gamma= gbit= dfilt= divot= aa= fb=WxH drawn= tex= vs= ve= hs=   RT64 present tuple changes
  [vi-feat-ctl] armed ...                                       positive control (gamma forced on for 120 commits)

Checks (hardware model re-derived from the ROM's osViSetSpecialFeatures 0x80035340, libultra 2.0D):
  call   : after == rule(before, func, modectrl); func bits only from {01,02,10,20,40,80} (the 12 game sites).
  gamma  : RT64's pow() exponent equals the VI bit (1/2.2 when GAMMA_ON, 1.0 otherwise).
  black  : a present of a zero-line VI (vStart == vEnd, hardware scans no active line = black) must not draw the fb.
  livegam: presents with the gamma bit on, drawn, outside the ctl window (a visible gamma frame; RT64's pow(1/2.2) is an
           approximation of the VI gamma table there) -> reported, not a failure.
  filters: presented time per dither-filter / divot / AA-mode value (RT64 has no VI filter stage: design difference, reported).
  ctl    : with --ctl, at least one log must show ctl commits and a drawn RT64 present with gamma 0.4545 inside the ctl window.
Exit: 0 clean, 1 live divergence, 3 ctl unproven, 4 no rows.  --controls runs synthetic + mutant logs first.
"""
import re, sys, collections

FUNC_OK = {0x01, 0x02, 0x10, 0x20, 0x40, 0x80}
KV = re.compile(r'(\w+)=([0-9A-Fa-fx.]+)')


def rule(before, func, modectrl):
    c = before
    if func & 0x01: c |= 0x8
    if func & 0x02: c &= ~0x8
    if func & 0x04: c |= 0x4
    if func & 0x08: c &= ~0x4
    if func & 0x10: c |= 0x10
    if func & 0x20: c &= ~0x10
    if func & 0x40:
        c |= 0x10000
        c &= ~0x300
    if func & 0x80:
        c &= ~0x10000
        c |= modectrl & 0x300
    return c & 0xFFFFFFFF


def parse(lines):
    calls, commits, rts, ctl_armed = [], [], [], 0
    for ln in lines:
        if ln.startswith('[vi-feat] '):
            d = dict(KV.findall(ln)); calls.append({k: d[k] for k in d})
        elif ln.startswith('[vi-feat-commit]'):
            commits.append(dict(KV.findall(ln)))
        elif ln.startswith('[vi-feat-rt]'):
            d = dict(KV.findall(ln))
            m = re.search(r'fb=(\d+)x(\d+)', ln)
            d['fbw'], d['fbh'] = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
            rts.append(d)
        elif ln.startswith('[vi-feat-ctl]'):
            ctl_armed += 1
    return calls, commits, rts, ctl_armed


def score(lines, want_ctl=False, name='log'):
    calls, commits, rts, armed = parse(lines)
    bad = []
    funcs = collections.Counter()
    for c in calls:
        f = int(c['func'], 16); b = int(c['before'], 16); a = int(c['after'], 16); mc = int(c['modectrl'], 16)
        funcs[f] += 1
        if f not in FUNC_OK: bad.append(f'call func {f:02X} not a game flag')
        if rule(b, f, mc) != a: bad.append(f'call func {f:02X} before {b:05X} after {a:05X} want {rule(b, f, mc):05X}')
    # ctl windows from commits
    wins, start = [], None
    for c in commits:
        ts = float(c['ts']); on = c.get('ctl') == '1'
        if on and start is None: start = ts
        if not on and start is not None: wins.append((start, ts)); start = None
    if start is not None: wins.append((start, 1e18))
    inwin = lambda t: any(a - 0.05 <= t <= b + 0.2 for a, b in wins)
    # RT64 rows: each row's tuple holds until the next row's ts
    dur = collections.Counter(); livegam = 0; zero_rows = 0; ctl_seen = 0
    for i, r in enumerate(rts):
        ts = float(r['ts']); te = float(rts[i + 1]['ts']) if i + 1 < len(rts) else ts
        gb = int(r['gbit']); g = float(r['gamma']); dr = int(r['drawn'])
        vs, ve = int(r['vs']), int(r['ve'])
        want_g = 1 / 2.2 if gb else 1.0
        if abs(g - want_g) > 1e-3: bad.append(f'rt p={r["p"]} gamma {g} with gbit {gb}')
        if vs == ve:
            zero_rows += 1
            if dr: bad.append(f'rt p={r["p"]} zero-line VI vs=ve={vs} drawn (hardware black)')
        if gb and dr:
            if inwin(ts): ctl_seen += 1 if abs(g - 1 / 2.2) < 1e-3 else 0
            else: livegam += 1
        if dr:
            dur[('dfilt', r['dfilt'])] += te - ts; dur[('divot', r['divot'])] += te - ts; dur[('aa', r['aa'])] += te - ts
    # zero-line commits: hardware scans no active line (black); a host that skips the VI keeps the last image. prevluma = mean luma
    # of that image (s7517 second build). held_lit = zero-line episodes whose held image is not black (mean > 8 or lit > 5%).
    zl = [c for c in commits if c.get('zl') == '1']
    held = [(float(c['prevluma']), float(c['prevlit'])) for c in zl if 'prevluma' in c and float(c['prevluma']) >= 0]
    held_lit = sum(1 for m, l in held if m > 8 or l > 0.05)
    rt_zero_presented = sum(1 for r in rts if int(r['vs']) == int(r['ve']))
    nrows = len(calls) + len(commits) + len(rts)
    ctl_ok = (armed > 0 and len(wins) > 0 and ctl_seen > 0)
    info = dict(calls=len(calls), funcs={f'{k:02X}': v for k, v in sorted(funcs.items())}, commits=len(commits), rt=len(rts),
                zero_line_rows=zero_rows, zl_commits=len(zl), zl_rt_presented=rt_zero_presented, held_measured=len(held), held_lit=held_lit,
                held_max=round(max([m for m, l in held], default=-1), 1), live_gamma_drawn=livegam, ctl_windows=len(wins), ctl_gamma_drawn=ctl_seen,
                filters={f'{k}{v}': round(s, 1) for (k, v), s in sorted(dur.items())})
    return nrows, bad, ctl_ok, info


def synth(mut=None):
    L = []
    L.append('[vi-feat] c=10 ts=1.000 func=02 before=0320E after=03206 modectrl=0320E mode=80128C90')
    L.append('[vi-feat] c=10 ts=1.000 func=80 before=03206 after=03206 modectrl=0320E mode=80128C90')
    L.append('[vi-feat] c=10 ts=1.000 func=40 before=03246 after=13046 modectrl=03246 mode=80128E40')
    L.append('[vi-feat-commit] c=11 ts=1.010 ctrl=0320E game=0320E ctl=0 vstart=00350035 hstart=006C02EC mode=80128C90 st=1')
    L.append('[vi-feat-rt] p=5 ts=1.020 rep=0 ctrl=0320E gamma=0.4545 gbit=1 dfilt=0 divot=0 aa=2 fb=0x0 drawn=0 tex=0 vs=53 ve=53 hs=108')
    L.append('[vi-feat-rt] p=8 ts=1.060 rep=2 ctrl=03246 gamma=1.0000 gbit=0 dfilt=0 divot=0 aa=2 fb=640x480 drawn=1 tex=1 vs=35 ve=501 hs=108')
    L.append('[vi-feat-ctl] armed at swap 1500 commit 900')
    L.append('[vi-feat-commit] c=900 ts=20.000 ctrl=0324E game=03246 ctl=1 vstart=002501FF hstart=006C02EC mode=80128DA0 st=1')
    L.append('[vi-feat-rt] p=950 ts=20.020 rep=0 ctrl=0324E gamma=0.4545 gbit=1 dfilt=0 divot=0 aa=2 fb=640x480 drawn=1 tex=1 vs=37 ve=511 hs=108')
    L.append('[vi-feat-commit] c=1020 ts=22.000 ctrl=03246 game=03246 ctl=0 vstart=002501FF hstart=006C02EC mode=80128DA0 st=1')
    L.append('[vi-feat-rt] p=1070 ts=22.020 rep=119 ctrl=03246 gamma=1.0000 gbit=0 dfilt=0 divot=0 aa=2 fb=640x480 drawn=1 tex=1 vs=37 ve=511 hs=108')
    if mut == 'wrong_after': L[2] = L[2].replace('after=13046', 'after=13346')
    if mut == 'bad_func': L[0] = L[0].replace('func=02', 'func=04').replace('after=03206', 'after=0320E')
    if mut == 'zero_drawn': L[4] = L[4].replace('fb=0x0 drawn=0 tex=0', 'fb=640x8 drawn=1 tex=1')
    if mut == 'gamma_ignored': L[8] = L[8].replace('gamma=0.4545', 'gamma=1.0000')
    if mut == 'no_ctl': L = [l for l in L if 'ctl=1' not in l and '[vi-feat-ctl]' not in l]
    if mut == 'live_gamma': L.append('[vi-feat-rt] p=2000 ts=40.000 rep=0 ctrl=0324E gamma=0.4545 gbit=1 dfilt=0 divot=0 aa=2 fb=640x480 drawn=1 tex=1 vs=37 ve=511 hs=108')
    return L


def controls():
    ok = True
    for mut, want_bad, want_ctl, want_live in [(None, 0, 1, 0), ('wrong_after', 1, 1, 0), ('bad_func', 1, 1, 0), ('zero_drawn', 1, 1, 1),
                                               ('gamma_ignored', 1, 0, 0), ('no_ctl', 0, 0, 1), ('live_gamma', 0, 1, 1)]:
        n, bad, c, info = score(synth(mut))
        got = (1 if bad else 0, 1 if c else 0, 1 if info['live_gamma_drawn'] else 0)
        p = got == (want_bad, want_ctl, want_live)
        ok &= p
        print(f'control {mut or "clean":14s} bad={got[0]} ctl={got[1]} live={got[2]} want={want_bad}/{want_ctl}/{want_live} {"PASS" if p else "FAIL"}')
    return ok


def main(argv):
    want_ctl = '--ctl' in argv
    if '--controls' in argv and not controls():
        print('controls FAIL'); return 5
    files = [a for a in argv if not a.startswith('--')]
    rc = 0; any_rows = False; any_ctl = False
    for f in files:
        n, bad, c, info = score(open(f, errors='ignore').read().splitlines(), want_ctl, f)
        any_rows |= n > 0
        print(f'{f} rows={n} bad={len(bad)} ctl_ok={int(c)} {info}')
        for b in bad[:10]: print('   BAD', b)
        if bad: rc = max(rc, 1)
        any_ctl |= c
    if not any_rows: return 4
    # the ctl can land on a still screen (RT64 re-presents the last swap's VI snapshot, s7517), so one log showing it suffices
    if want_ctl and not any_ctl and rc == 0: rc = 3
    return rc


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
