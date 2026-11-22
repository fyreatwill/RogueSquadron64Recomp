#!/usr/bin/env python3
"""s7522 class FS: at every port dispatch (do_indirect_jump), is the code the port routes to the code hardware has resident?

Runtime (ROGUESQ_S7521_UCODEWATCH=1, src/rsp/s7521_ucode_watch.cpp): a per-word model of gfx IMEM, i.e. the RDRAM source of
every IMEM word, is updated from the IMEM DMA stream (plus the restore DMA the ovl28 hand route skips). Each dispatch is
counted by (target, DMEM 0x153, modelled source of the target word, ctl). The rows are dumped at every [s7522-sum].

Offline (this script): the port's route for (target, 0x153) is rebuilt by parsing the dispatch switch in
build/factor5_ucode/factor5_ucode_recompiled.c. The label prefix names the image RSPRecomp compiled (L_ = main toml,
CLIP_ = ovl4, OVLnn_ = ovlnn composite, 0x28 = ovl28 hand route). The bytes of that image from the target to the end of
the resident DMA extent are compared with the ROM bytes the model says are resident:
  canon   every compared word equal (the port runs the resident code)
  fr      target 0x1DB0, route main, ovl0 resident: the 8-byte placement case FR resolved as H-dead (s7521: path A never taken)
  live    a word differs (the port runs other code than hardware), or route rs64_clip_stray / unhandled, or src unmodelled
ctl rows (fs_ctl perturb, model shifted 8 bytes for one real 0x1DB0 overlay) must score live at least once.
Exit 0 clean + ctl caught, 1 live row, 3 ctl unproven, 4 no [s7522-sum]. --controls runs synthetic logs first.
"""
import glob, os, re, sys
import os as _os; sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); from rs64_zopen import zopen, zbytes  # s7805: zst-only retained inputs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROM = os.path.join(ROOT, 'rogue_squadron.z64')
SRC = os.path.join(ROOT, 'build', 'factor5_ucode', 'factor5_ucode_recompiled.c')
DELTA, OVL0, OVL28, MAIN_DRAM = 0xC00, 0x025748, 0x026748, 0x024A10
PREFIX = {'L': 'factor5_rsp.toml', 'CLIP': 'factor5_rsp_ovl4.toml', 'OVL12': 'factor5_rsp_ovl12.toml',
          'OVL10': 'factor5_rsp_ovl10.toml', 'OVL14': 'factor5_rsp_ovl14.toml', 'OVL18': 'factor5_rsp_ovl18.toml',
          'OVL1C': 'factor5_rsp_ovl1c.toml', 'OVL20': 'factor5_rsp_ovl20.toml', 'OVL24': 'factor5_rsp_ovl24.toml',
          'OVL2C': 'factor5_rsp_ovl2c.toml'}


def images():
    out = {}
    for t in glob.glob(os.path.join(ROOT, 'factor5_rsp*.toml')):
        kv = {}
        for line in open(t):
            m = re.match(r'\s*(\w+)\s*=\s*("([^"]*)"|0x[0-9A-Fa-f]+)', line)
            if m: kv[m.group(1)] = m.group(3) if m.group(3) is not None else int(m.group(2), 16)
        d = open(os.path.join(ROOT, kv['rom_file_path']), 'rb').read()
        out[os.path.basename(t)] = (d[kv['text_offset']:kv['text_offset'] + kv['text_size']], kv['text_address'] & 0xFFF)
    return out


def parse_switch(path=SRC):
    """{target: ([(set_of_b153, label), ...], fallback_label)}"""
    L = open(path, errors='replace').read().splitlines()
    s = next(i for i, l in enumerate(L) if 'switch ((jump_target | 0x1000) & 0X1FFF)' in l)
    e = next(i for i in range(s + 1, len(L)) if L[i].startswith('    }'))
    body = '\n'.join(L[s + 1:e])
    sw = {}
    for m in re.finditer(r'case (0x[0-9A-Fa-f]+):(.*?)(?=\n\s*case 0x|\Z)', body, re.S):
        t, ch = int(m.group(1), 16), m.group(2)
        rules, fb = [], None
        stmts = []
        for ln in ch.split('\n'):
            if 'rs64_2c_mode' in ln:  # default ROGUESQ_OVL2C_MODE=0 -> OVL2C route
                g = re.search(r'rs64_2c_mode == 0\) \{[^}]*goto (\w+);', ln)
                rules.append(({0x2C}, g.group(1))); continue
            stmts += re.split(r'(?<=\})\s+', ln)
        for st in stmts:
            st = st.strip()
            if not st: continue
            c = re.match(r'if \(((?:RSP_MEM_BU\(0X153, 0\) == 0x[0-9A-Fa-f]+(?: \|\| )?)+)\) (?:\{(.*?)\}|(goto \w+;))', st)
            if c:
                vals = {int(v, 16) for v in re.findall(r'== (0x[0-9A-Fa-f]+)', c.group(1))}
                blk = c.group(2) if c.group(2) is not None else c.group(3)
                g = re.search(r'goto (\w+);', blk)
                lab = 'OVL28' if 'L_10D8' in blk and 0x28 in vals else g.group(1)
                rules.append((vals, lab))
                rest = st[c.end():]
                g2 = re.search(r'goto (\w+);', rest)
                if g2: fb = g2.group(1)
                continue
            g = re.search(r'goto (\w+);', st)
            if g and fb is None: fb = g.group(1)
        sw[t] = (rules, fb)
    return sw


def route(sw, t, b):
    if t not in sw: return 'UNHANDLED'
    rules, fb = sw[t]
    for vals, lab in rules:
        if b in vals: return lab
    return fb or 'UNHANDLED'


def extents(lines):
    """known gfx IMEM DMA extents (dram, len) from the FR [s7521-imem] new rows, plus the ovl28 restore"""
    ex = set()
    for l in lines:
        m = re.match(r'\[s7521-imem\] new mem=([0-9A-F]+) dram=([0-9A-F]+) len=([0-9A-F]+) aud=0', l)
        if m: ex.add((int(m.group(2), 16), int(m.group(3), 16)))
        m = re.match(r'\[s7522-src28\] gen=\d+ src=([0-9A-F]+)', l)
        if m: ex.add((int(m.group(1), 16), 0x330))
    return ex


def classify(sw, imgs, rom, ex, t, b, src):
    lab = route(sw, t, b)
    if lab in ('UNHANDLED', 'rs64_clip_stray'): return 'live', lab, 'no compiled route'
    if src == 0: return 'live', lab, 'unmodelled'
    if lab == 'OVL28':
        return ('canon' if src == OVL28 and t == 0x1DB0 else 'live'), lab, f'ovl28 hand route src={src:06X}'
    pre = lab.split('_')[0]
    if pre not in PREFIX: return 'live', lab, 'unknown label'
    if lab == 'L_1DB0' and src == OVL0: return 'fr', lab, 'ovl0 8-byte placement (s7521 H-dead)'
    img, base = imgs[PREFIX[pre]]
    run = [d + n - src for d, n in ex if d <= src < d + n]
    if not run: return 'live', lab, f'src {src:06X} in no known DMA extent'
    span = min(min(run), (len(img) - (t - 0x1000 - base)))  # bytes from t to the end of the resident run / port image
    pi, ro = t - 0x1000 - base, src + DELTA
    for k in range(0, span - 3, 4):
        if img[pi + k:pi + k + 4] != rom[ro + k:ro + k + 4]:
            return 'live', lab, f'word {k // 4} of {span // 4} differs'
    return 'canon', lab, f'{span // 4} words equal'


def score(paths, want_ctl, sw, imgs, rom, quiet=False):
    rc = 0
    for p in paths:
        L = zopen(p, errors='replace').read().splitlines()
        sums = [i for i, l in enumerate(L) if l.startswith('[s7522-sum]')]
        if not sums:
            if not quiet: print(f'{p}: no [s7522-sum]')
            rc = max(rc, 4); continue
        hdr = L[sums[-1]]
        gen = re.search(r'gen=(\d+)', hdr).group(1)
        ex = extents(L)
        rows = []
        for l in L[sums[-1]:]:
            m = re.match(r'\[s7522-disp\] gen=(\d+) t=([0-9A-F]+) b153=([0-9A-F]+) src=([0-9A-F]+) ctl=(\d) n=(\d+)', l)
            if m and m.group(1) == gen: rows.append(tuple(int(m.group(i), 16) for i in (2, 3, 4)) + (int(m.group(5)), int(m.group(6))))
        cnt, live, ctl_live, ctl_n = {}, [], 0, 0
        win = {'w12A0': 0, 'w1DB0': 0, 'other': 0}
        for t, b, src, c, n in rows:
            k, lab, why = classify(sw, imgs, rom, ex, t, b, src)
            if c:
                ctl_n += n
                if k == 'live': ctl_live += n
                continue
            cnt[k] = cnt.get(k, 0) + n
            win['w12A0' if 0x12A0 <= t < 0x15D0 else 'w1DB0' if t >= 0x1DB0 else 'other'] += n
            if k == 'live': live.append(f't={t:04X} b153={b:02X} src={src:06X} route={lab} n={n}: {why}')
        n28 = int(re.search(r'n28=(\d+)', hdr).group(1))
        s28 = [l for l in L if l.startswith(f'[s7522-src28] gen={gen} ')]
        bad28 = [l for l in s28 if not l.endswith('src=024C30')]
        if bad28: live.append(f'ovl28 restore source not main L_12A0: {bad28}')
        ctl_ok = (not want_ctl) or (ctl_live > 0 and 'ctl_dmas=1' in hdr)
        r = 1 if live else (0 if ctl_ok else 3)
        rc = max(rc, r)
        if not quiet:
            print(f'{p}: score={r} keys={len(rows)} {cnt} windows={win} n28={n28} ctl_rows_n={ctl_n} ctl_live_n={ctl_live} hdr={hdr}')
            for x in live[:40]: print('  LIVE', x)
    return rc


def controls(sw, imgs, rom):
    import tempfile
    d = tempfile.mkdtemp()
    ex = ['[s7521-imem] new mem=1080 dram=024A10 len=F80 aud=0 rom=25610 state=ROM bad=0 first=0 task=1',
          '[s7521-imem] new mem=1DB0 dram=025A70 len=230 aud=0 rom=26670 state=ROM bad=0 first=0 task=2',
          '[s7521-imem] new mem=12A0 dram=026660 len=E4 aud=0 rom=27260 state=ROM bad=0 first=0 task=2',
          '[s7521-imem] new mem=12A0 dram=026508 len=158 aud=0 rom=27108 state=ROM bad=0 first=0 task=2',
          '[s7521-imem] new mem=1DB0 dram=025748 len=D4 aud=0 rom=26348 state=ROM bad=0 first=0 task=2']
    H = lambda c: [f'[s7522-sum] gen=1 why=periodic ndisp=9 keys=3 n28=1 src28=1 ctl_dmas={c} fs_ctl=3', '[s7522-src28] gen=1 src=024C30']
    clean = ['[s7522-disp] gen=1 t=1504 b153=00 src=024E94 ctl=0 n=5',            # main resident, main route
             '[s7522-disp] gen=1 t=1DB0 b153=0C src=025A70 ctl=0 n=4',            # ovl12 resident, OVL12_1DB0
             '[s7522-disp] gen=1 t=1DB0 b153=00 src=025748 ctl=0 n=4',            # FR case
             '[s7522-disp] gen=1 t=12A0 b153=24 src=026660 ctl=0 n=4']            # ovl24 resident, OVL24_12A0
    ctlr = ['[s7522-disp] gen=1 t=1DB0 b153=0C src=025A78 ctl=1 n=2']             # model shifted 8
    cases = [('clean+ctl', ex + H(1) + clean + ctlr, True, 0), ('no ctl', ex + H(0) + clean, True, 3),
             ('wrong overlay', ex + H(1) + clean + ctlr + ['[s7522-disp] gen=1 t=1DB0 b153=0C src=025748 ctl=0 n=1'], True, 1),
             ('ovl20 leftover under ovl24 route', ex + H(1) + clean + ctlr + ['[s7522-disp] gen=1 t=12A0 b153=24 src=026508 ctl=0 n=1'], True, 1),
             ('stray', ex + H(1) + clean + ctlr + ['[s7522-disp] gen=1 t=1E1C b153=00 src=025A70 ctl=0 n=1'], True, 1),
             ('stale gen ignored', ex + ['[s7522-disp] gen=0 t=1DB0 b153=0C src=025748 ctl=0 n=1'] + H(1) + clean + ctlr, True, 0),
             ('no sum', ex, False, 4)]
    ok = True
    for n, lines, wc, want in cases:
        p = os.path.join(d, n.replace(' ', '_') + '.txt'); open(p, 'w').write('\n'.join(lines) + '\n')
        got = score([p], wc, sw, imgs, rom, quiet=True)
        print(f'synthetic {n}: want {want} got {got} {"PASS" if got == want else "FAIL"}'); ok &= got == want
    return ok


def main():
    a = sys.argv[1:]
    want_ctl, ctrl = '--ctl' in a, '--controls' in a
    paths = [x for x in a if not x.startswith('--')]
    rom, imgs, sw = open(ROM, 'rb').read(), images(), parse_switch()
    print(f'switch: {len(sw)} cases, {sum(len(r) for r, _ in sw.values())} 0x153 rules; images {sorted(imgs)}')
    if ctrl and not controls(sw, imgs, rom): sys.exit(5)
    sys.exit(score(paths, want_ctl, sw, imgs, rom) if paths else 0)


if __name__ == '__main__':
    main()
