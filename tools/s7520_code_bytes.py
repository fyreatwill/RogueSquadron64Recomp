#!/usr/bin/env python3
"""s7520 class FQ runtime scorer: [s7520] rows from ROGUESQ_S7520_CODEWATCH=1 logs.
Live rows (outside ctl): kind=main bad, kind=ovl state 2/3 (other section resident / no section's bytes) or state 1 that
persists to an iinv or to the next get_function check (exec_diff), kind=exec_diff, kind=gf_stale, kind=gf_funcdiff,
kind=dma_main, any iinv check with state != 0. state 1 (partial) at a swap during a chunked load that turns into 0 is
TRANSIENT (load in progress), reported but not live.
rc: 0 canon (+ctl ok with --ctl), 1 live rows, 3 ctl failed (--ctl: need main ctl=1 row then a main ok row, and an
exec_diff ctl=1 row), 4 no [s7520-sum].  --controls runs synthetic logs through the scorer."""
import bisect, re, subprocess, sys
ELF = '../rogue_squadron64/build/roguesquadron.elf'
_SYMS = None
def syms():
    """(start, end, type, name, shndx) of every sized symbol in the code sections 2-6 of the regen ELF."""
    global _SYMS
    if _SYMS is None:
        out = subprocess.run(['mips64-elf-readelf', '-sW', ELF], capture_output=True, text=True).stdout
        _SYMS = []
        for ln in out.splitlines():
            f = ln.split()
            if len(f) == 8 and f[6] in ('2', '3', '4', '5', '6') and f[3] in ('FUNC', 'OBJECT') and int(f[2], 0 if f[2].startswith('0x') else 10) > 0:
                a = int(f[1], 16); _SYMS.append((a, a + int(f[2]), f[3], f[7], int(f[6])))
    return _SYMS
_GAPS = None
def gapnames():
    """ELF names the rename sweep (tools/rename_generated_symbols.py) maps to data_gap_* (data the splitter called a function)."""
    global _GAPS
    if _GAPS is None:
        _GAPS = set(re.findall(r'"(\w+)": "data_gap_\w+"', open('tools/rename_generated_symbols.py').read()))
    return _GAPS
_SUBS = None
YAML = '../rogue_squadron64/roguesquadron.yaml'
def subsegs():
    """sorted (rom_off, type, name) of every splat subsegment in the decomp yaml (independent code/data map)."""
    global _SUBS
    if _SUBS is None:
        _SUBS = []
        for ln in open(YAML):
            m = re.match(r'\s*-\s*\[\s*(0x[0-9A-Fa-f]+)\s*(?:,\s*([\w.]+))?\s*(?:,\s*"?([^"\]]*)"?)?', ln)
            if m and not ln.lstrip().startswith('#'):
                _SUBS.append((int(m.group(1), 16), (m.group(2) or 'end'), (m.group(3) or '').strip()))
        _SUBS.sort()
    return _SUBS
CODE_TYPES = {'asm', 'hasm', 'c'}
SEC_ROM = {1: (0x80000440, 0x1040), 0: (0x80000400, 0x1000), 2: (0x800A5130, 0xA5D30), 3: (0x800A5130, 0x10C2D0), 4: (0x800A5130, 0x137580)}
def subseg_of(sec, va):
    ram, rom = SEC_ROM[sec]; off = va - ram + rom; ss = subsegs()
    i = bisect.bisect_right([x[0] for x in ss], off) - 1
    return ss[i] if i >= 0 else (0, 'none', '')
SEC2SHN = {0: 2, 1: 3, 2: 4, 3: 5, 4: 6}  # runtime code-section idx -> ELF section index
def classify(sec, va):
    """DATA if va lies in an OBJECT symbol or a data_gap_* symbol of that section, CODE if only in a real FUNC, else NONE."""
    shn = SEC2SHN.get(sec); hits = [x for x in syms() if x[4] == shn and x[0] <= va < x[1]]
    sub = subseg_of(sec, va); where = f'{sub[1]}:{sub[2]}'
    if any(t == 'OBJECT' or n.startswith('data_gap_') or n in gapnames() for _, _, t, n, _ in hits):
        return 'DATA', ','.join(n for *_, n, _ in hits) + '@' + where
    if sub[1] not in CODE_TYPES:
        return 'DATA', ','.join(n for *_, n, _ in hits) + '@' + where
    if hits: return 'CODE', ','.join(n for *_, n, _ in hits) + '@' + where
    return 'NONE', ''

def kv(line):
    return dict(re.findall(r'(\w+)=(\S+)', line))

def score(lines, need_ctl):
    live, trans, ctl_main_bad, ctl_main_ok, ctl_exec, sums, iinv = [], [], False, False, False, [], 0
    last_ovl = None
    data_addrs, ctl_plus = {}, set()
    for ln in lines:
        if '[s7520-w] ' in ln or '[s7520-iw] ' in ln:
            d = kv(ln)
            if d.get('op') in ('reset', '-'):
                if d.get('op') == '-' and d.get('va') in ctl_plus: ctl_main_ok = True
                continue
            sec, va = int(d['sec']), int(d['va'], 16); cls, who = classify(sec, va)
            if cls == 'DATA': data_addrs.setdefault((sec, va), who); continue
            if d.get('ctl') == '1' and cls == 'CODE': ctl_main_bad = True; ctl_plus.add(d['va']); continue
            live.append(ln + f' class={cls} sym={who}'); continue
        if WORDS_MODE[0] and '[s7520] ' in ln and ('kind=main' in ln or 'kind=ovl' in ln): continue
        if '[s7520-sum]' in ln: sums.append(kv(ln)); continue
        if '[s7520] ' not in ln: continue
        d = kv(ln); k = d.get('kind'); c = d.get('ctl') == '1'
        if k == 'main':
            bad = int(d['bad_words'])
            if bad and c: ctl_main_bad = True
            elif bad: live.append(ln)
            elif ctl_main_bad and d.get('why') in ('ctlrestore', 'swap'): ctl_main_ok = True
        elif k == 'ovl':
            st = int(d['state'])
            if d.get('why') == 'iinv':
                iinv += 1
                if st != 0: live.append(ln)
            elif st in (2, 3): live.append(ln)
            elif st == 1: trans.append(ln)
            elif st == 4: trans.append(ln)
        elif k == 'exec_diff':
            if c: ctl_exec = True
            else: live.append(ln)
        elif k in ('gf_stale', 'gf_funcdiff', 'dma_main'):
            live.append(ln)
    if not sums: return 4, live, trans, sums, (ctl_main_bad, ctl_main_ok, ctl_exec), iinv
    ctl_ok = ctl_main_bad and ctl_main_ok and ctl_exec
    rc = 1 if live else (3 if need_ctl and not ctl_ok else 0)
    score.data = data_addrs
    return rc, live, trans, sums, (ctl_main_bad, ctl_main_ok, ctl_exec), iinv

WORDS_MODE = [False]
SUM = '[s7520-sum] why=periodic swaps=300 checks=1 main_bad_checks=0 ovl_ok=1 ovl_partial=0 ovl_other=0 ovl_none=0 ovl_unreg=0 gf_ovl=1 gf_stale=0 gf_funcdiff=0 exec_checks=1 exec_diff=0 dma_main=0 iinv=1 iinv_bad=0 reg=2'
CTL = ['[s7520] kind=main why=swap swap=600 bad_words=1 of=9 first=80001004 ram=1 rom=0 ctl=1',
       '[s7520] kind=main why=ctlrestore swap=660 bad_words=0 of=9 first=00000000 ram=0 rom=0 ctl=1',
       '[s7520] kind=exec_diff addr=800A6000 size=40 bad_words=1 first=800A6004 ram=1 rom=0 reg=2 swap=901 ctl=1']
def controls():
    cases = [('clean+ctl', CTL + [SUM], 0),
             ('no sum', CTL, 4),
             ('no ctl', [SUM], 3),
             ('main live', CTL + [SUM, '[s7520] kind=main why=swap swap=700 bad_words=2 of=9 first=80001000 ram=1 rom=0 ctl=0'], 1),
             ('ovl other', CTL + [SUM, '[s7520] kind=ovl why=swap swap=5 state=2 reg=2 resident_match=3 reg_bad=9 of=9 first=0 ram=0 rom=0 ctl=0'], 1),
             ('iinv partial', CTL + [SUM, '[s7520] kind=ovl why=iinv swap=5 state=1 reg=2 resident_match=-1 reg_bad=9 of=99 first=0 ram=0 rom=0 ctl=0'], 1),
             ('swap partial transient', CTL + [SUM, '[s7520] kind=ovl why=swap swap=5 state=1 reg=2 resident_match=-1 reg_bad=9 of=99 first=0 ram=0 rom=0 ctl=0'], 0),
             ('stale', CTL + [SUM, '[s7520] kind=gf_stale addr=800B0000 reg=3 patch=0 swap=9'], 1),
             ('exec live', CTL + [SUM, '[s7520] kind=exec_diff addr=800A6000 size=40 bad_words=1 first=800A6004 ram=1 rom=0 reg=2 swap=50 ctl=0'], 1)]
    ok = True
    for name, ls, want in cases:
        got = score(ls, True)[0]; good = got == want; ok &= good
        print(f'synthetic {name}: want {want} got {got} {"PASS" if good else "FAIL"}')
    return ok

def main():
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    if '--controls' in sys.argv and not controls(): sys.exit(3)
    worst = 0
    for p in a:
        lines = open(p, errors='replace').read().splitlines()
        WORDS_MODE[0] = any('[s7520-w] ' in l for l in lines)
        rc, live, trans, sums, ctl, iinv = score(lines, '--ctl' in sys.argv)
        s = sums[-1] if sums else {}
        print(f'{p}: rc={rc} live={len(live)} transient={len(trans)} iinv_checks={iinv} ctl(main_bad,main_ok,exec)={ctl} last_sum=' +
              ' '.join(f'{k}={s[k]}' for k in ('swaps','checks','main_bad_checks','ovl_ok','ovl_partial','ovl_other','ovl_none','ovl_unreg',
                                                 'gf_ovl','gf_stale','exec_checks','exec_diff','dma_main','iinv','iinv_bad') if k in s))
        for l in live[:12]: print('  LIVE', l)
        dd = getattr(score, 'data', {})
        if dd: print(f'  DATA words changed: {len(dd)} in ' + ', '.join(sorted(set(dd.values())))[:600])
        for l in trans[:6]: print('  TRANS', l)
        worst = max(worst, rc)
    sys.exit(worst)
main()
