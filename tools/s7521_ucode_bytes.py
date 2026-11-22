#!/usr/bin/env python3
"""s7521 class FR: executed RSP code bytes vs the images RSPRecomp compiled.

Static part (always): each RSPRecomp toml's text image is read from its rom_file_path; the main gfx toml and ucode B must be the
retail ROM bytes at the task ucode addresses (gfx 0x80024A10 -> rom 0x25610, audio 0x80099FE0 -> rom 0x9ABE0), and the boot bin
the ROM bytes at rom 0x831D0.
Log part (ROGUESQ_S7521_UCODEWATCH=1 [+ ROGUESQ_S7521_CTL=1] logs): every task tuple must point at those images; every DIFF row
on boot/text outside ctl is LIVE; data DIFF rows are listed by DMEM offset (dispatch-table offsets the tomls baked in are LIVE,
others are task inputs the compiled code reads dynamically: DATA); every distinct IMEM DMA must carry ROM bytes (state=ROM)
and those bytes must equal what some compiled image holds at that IMEM address (main/ovl composites for gfx, B for audio).
--ctl requires the planted flips caught: text/boot/data DIFF rows with ctl=1 and the imem flip caught=1.
Exit 0 clean, 1 live row, 3 ctl unproven, 4 no [s7521-sum]. --controls runs synthetic logs first.
"""
import glob, os, re, sys
import os as _os; sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); from rs64_zopen import zopen, zbytes  # s7805: zst-only retained inputs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROM = os.path.join(ROOT, 'rogue_squadron.z64')
GFX_UCODE, AUD_UCODE, BOOT_ROM, DELTA = 0x80024A10, 0x80099FE0, 0x831D0, 0xC00
# DMEM dispatch tables whose targets the tomls compiled as extra_indirect_branch_targets (factor5_rsp.toml comment)
TABLES = [(0x64, 0x76), (0x76, 0x80), (0xD6, 0xF0)]


def tomls():
    out = []
    for t in sorted(glob.glob(os.path.join(ROOT, 'factor5*_rsp*.toml'))):
        kv = {}
        for line in open(t):
            m = re.match(r'\s*(\w+)\s*=\s*("([^"]*)"|0x[0-9A-Fa-f]+)', line)
            if m: kv[m.group(1)] = m.group(3) if m.group(3) is not None else int(m.group(2), 16)
        p = os.path.join(ROOT, kv['rom_file_path'])
        if not os.path.exists(p): out.append((os.path.basename(t), None, kv)); continue
        d = open(p, 'rb').read()
        out.append((os.path.basename(t), d[kv['text_offset']:kv['text_offset'] + kv['text_size']], kv))
    return out


def static_check(rom, imgs):
    bad = []
    by = {n: (img, kv) for n, img, kv in imgs}
    for n, img, kv in imgs:
        if img is None: bad.append(f'{n}: image file missing')
    exp = {'factor5_rsp.toml': GFX_UCODE - 0x80000000 + DELTA, 'factor5b_rsp.toml': AUD_UCODE - 0x80000000 + DELTA,
           'factor5_boot_rsp.toml': BOOT_ROM}
    for n, ro in exp.items():
        img, kv = by[n]
        if img is None or img != rom[ro:ro + len(img)]: bad.append(f'{n}: compiled image != ROM@{ro:X}')
    return bad


def imem_images(imgs, aud):
    """(name, bytes, imem_base) of images that can run at an IMEM address for this task kind"""
    r = []
    for n, img, kv in imgs:
        if img is None: continue
        isb = n == 'factor5b_rsp.toml'
        if n == 'factor5_boot_rsp.toml' or isb != bool(aud): continue
        r.append((n, img, kv['text_address'] & 0xFFF))
    return r


def match_imem(imgs, rom, mem, romoff, ln, aud):
    src = rom[romoff:romoff + ln]
    full, part = [], []
    o = mem & 0xFFF
    for n, img, base in imem_images(imgs, aud):
        a = o - base
        if a < 0 or a >= len(img): continue
        seg = img[a:a + ln]
        same = sum(1 for i in range(len(seg)) if seg[i] == src[i])
        if len(seg) == ln and same == ln: full.append(n)
        elif same: part.append(f'{n}:{same}/{ln}')
    return full, part


OVL28_WORDS = ['26310020', '8c220010', '340312a0', '3404032f', '24420220', '0900048b', '341f10d8']
OVL28_ROUTE = 'rs64_e9prov_ovl_route(0x28, 0x1DB0); r17 = RSP_ADD32(r17, 0X20); goto L_10D8;'


def known_route(rom, dr, ln):
    """IMEM 0x1DB0 images with no composite: overlay 0 (main L_1DB0, scored by the window model) and overlay 0x28 (hand route)."""
    ro = dr + DELTA
    if (dr, ln) == (0x025748, 0xD4) and rom[ro:ro + ln] == rom[0x26348:0x26348 + 0xD4]:
        return ['OVL0=main L_1DB0 boot-placement (window model)']
    if (dr, ln) == (0x026748, 0x1C) and [rom[ro + i:ro + i + 4].hex() for i in range(0, 0x1C, 4)] == OVL28_WORDS:
        c = open(os.path.join(ROOT, 'build/factor5_ucode/factor5_ucode_recompiled.c')).read()
        # addiu $17,32; restore DMA main text+0x220 -> IMEM 0x12A0 len 0x330 (= main's compiled bytes); return 0x10D8
        # s7522 inserts the passive restore-model call between the route and the r17 update: strip it before matching
        c = c.replace(' if (__builtin_expect(rs64_s7521_on, 0)) rs64_s7522_ovl28(RSP_MEM_W_LOAD(0X10, r1) + 0x220);', '')
        if OVL28_ROUTE in c: return ['OVL28 hand route (r17+=32, restore-DMA of main L_12A0 no-op, goto L_10D8)']
    return []


def score(paths, want_ctl, imgs, rom, quiet=False):
    live, rc = [], 0
    tot = {}
    for p in paths:
        L = zopen(p, errors='replace').read().splitlines()
        sums = [l for l in L if l.startswith('[s7521-sum]')]
        if not sums:
            if not quiet: print(f'{p}: no [s7521-sum]')
            rc = max(rc, 4); continue
        ctl = {'text': 0, 'boot': 0, 'data': 0, 'imem': 0, 'l1db0': 0}
        datarows, nlive = {}, 0
        for l in L:
            if l.startswith('[s7521-tuple]'):
                m = re.search(r'type=(\d+) boot=([0-9A-F]+)/([0-9A-F]+) ucode=([0-9A-F]+)/([0-9A-F]+) data=([0-9A-F]+)/([0-9A-F]+)', l)
                ty, bt, tx = int(m.group(1)), int(m.group(2), 16), int(m.group(4), 16)
                want = {1: GFX_UCODE, 2: AUD_UCODE}.get(ty)
                if want is None or tx != want or (bt and (bt & 0x1FFFFFFF) + DELTA != BOOT_ROM):
                    live.append(f'{p}: TUPLE {l}'); nlive += 1
            elif l.startswith('[s7521-reg]'):
                c = int(re.search(r'ctl=(\d+)', l).group(1))
                reg = re.search(r'region=(\w+)', l).group(1)
                if c:
                    if 'kind=DIFF' in l: ctl[reg] += 1
                    continue
                if 'kind=NONROM' in l: live.append(f'{p}: {l}'); nlive += 1; continue
                if 'kind=TAIL' in l: continue   # ROM-backed prefix compared; the tail is the overlay window (same RDRAM on hardware)
                off = int(re.search(r' off=([0-9A-F]+)', l).group(1), 16)
                ty = int(re.search(r'type=(\d+)', l).group(1))
                if reg == 'data':
                    tab = ty == 1 and any(a <= off < b for a, b in TABLES)
                    if tab: live.append(f'{p}: TABLE {l}'); nlive += 1
                    datarows.setdefault((ty, off & ~0xF), []).append(l)
                else:
                    live.append(f'{p}: {l}'); nlive += 1
            elif l.startswith('[s7521-ctl] imem'):
                if 'caught=1' in l: ctl['imem'] += 1
            elif l.startswith('[s7521-ctl] l1db0'):
                if 'caught=1' in l: ctl['l1db0'] += 1
            elif l.startswith('[s7521-imem] new') or l.startswith('[s7521-imem] bad'):
                m = re.search(r'mem=([0-9A-F]+) dram=([0-9A-F]+) len=([0-9A-F]+) aud=(\d)', l)
                mem, dr, ln, aud = (int(m.group(i), 16) for i in range(1, 5))
                if 'state=ROM' not in l: live.append(f'{p}: {l}'); nlive += 1; continue
                full, part = match_imem(imgs, rom, mem, dr + DELTA, ln, aud)
                if not full and not aud and mem == 0x1DB0: full = known_route(rom, dr, ln)
                tag = ','.join(full) if full else ('PARTIAL ' + ' '.join(part) if part else 'NONE')
                key = (mem, dr, ln, aud)
                tot.setdefault(key, tag)
                if not full: live.append(f'{p}: IMEM-UNCOMPILED mem={mem:04X} dram={dr:06X} len={ln:X} aud={aud} -> {tag}'); nlive += 1
        last = sums[-1]
        # window model at the last sum: L_1DB0 (main init, the port's route for DMEM 0x153 not in the spliced set) is the
        # boot-placement image; with overlay 0 resident (ROM 0x26348 at 0x1DB0, 8 bytes lower) hardware's j 0x1E5C skips
        # mtc0 DPC_START/END, so path A (b5) under win=ovl0 is LIVE, and any L_1DB0 entry under another overlay is LIVE.
        si = max(i for i, l in enumerate(L) if l.startswith('[s7521-sum]'))
        wl = {}
        # s7522: the three window rows follow the last sum but other threads' stderr lines interleave (L10 soak s7521:
        # an [s2020-svc] pair landed between them), so take the first row per window after the sum, not a fixed slice.
        for l in L[si + 1:si + 200]:
            if len(wl) == 3: break
            m = re.match(r'\[s7521-l1db0\] why=\S+ win=(\w+) entry=(\d+) b0=(\d+) b1=(\d+) b2=(\d+) b3=(\d+) b4=(\d+) b5=(\d+)', l)
            if m: wl[m.group(1)] = [int(m.group(i)) for i in range(2, 9)]
        if want_ctl and len(wl) != 3: live.append(f'{p}: no l1db0 window rows'); nlive += 1
        if wl.get('ovl0', [0] * 7)[6]: live.append(f'{p}: L1DB0-PATHA-UNDER-OVL0 {wl["ovl0"]}'); nlive += 1
        if wl.get('other', [0])[0]: live.append(f'{p}: L1DB0-UNDER-OTHER-OVERLAY {wl["other"]}'); nlive += 1
        if not quiet: print(f'   l1db0 window [entry,b0..b5]: {wl}')
        ctl_ok = all(ctl.values())
        if not quiet:
            print(f'{p}: live={nlive} data_diff_groups={len(datarows)} ctl={ctl} last_sum={last[12:]}')
            for (ty, o), rows in sorted(datarows.items())[:12]:
                print(f'   data type={ty} dmem={o:03X}.. rows={len(rows)} e.g. {rows[0][12:]}')
        if want_ctl and not ctl_ok: rc = max(rc, 3)
    if not quiet:
        for k, v in sorted(tot.items()):
            print(f'  imem mem={k[0]:04X} dram={k[1]:06X} len={k[2]:X} aud={k[3]} -> {v}')
        for l in live[:40]: print('LIVE', l)
    if live and rc != 4: rc = 1 if rc == 0 else rc
    return rc


def controls(imgs, rom):
    import tempfile
    d = tempfile.mkdtemp()
    base = ['[s7521-tuple] type=1 boot=800825D0/D0 ucode=80024A10/1000 data=80038D00/800 flags=0 task=1',
            '[s7521-imem] new mem=1080 dram=024A10 len=F80 aud=0 rom=25610 state=ROM bad=0 first=0 task=1']
    ctlr = ['[s7521-reg] kind=DIFF region=boot type=1 va=800825D0 off=10 ram=00 rom=5A romoff=0 task=600 ctl=1',
            '[s7521-reg] kind=DIFF region=text type=1 va=80024A10 off=100 ram=00 rom=5A romoff=0 task=600 ctl=1',
            '[s7521-reg] kind=DIFF region=data type=1 va=80038D00 off=40 ram=00 rom=5A romoff=0 task=600 ctl=1',
            '[s7521-ctl] imem flip mem=1DB0 dram=025A10 len=210 bad=1 caught=1 task=900',
            '[s7521-ctl] l1db0 forced current win=0 ev=5 caught=1 task=1 gfx=700']
    W = lambda o5: ['[s7521-l1db0] why=periodic win=boot entry=10 b0=0 b1=0 b2=0 b3=0 b4=10 b5=0',
                    f'[s7521-l1db0] why=periodic win=ovl0 entry=5 b0=0 b1=0 b2=0 b3=0 b4=5 b5={o5}',
                    '[s7521-l1db0] why=periodic win=other entry=0 b0=0 b1=0 b2=0 b3=0 b4=0 b5=0']
    s = ['[s7521-sum] why=periodic tasks=2000'] + W(0)
    cases = [('clean+ctl', base + ctlr + s, True, 0), ('no ctl', base + s, True, 3),
             ('live text', base + ctlr + ['[s7521-reg] kind=DIFF region=text type=1 va=80024A10 off=200 ram=00 rom=11 romoff=0 task=7 ctl=0'] + s, True, 1),
             ('wrong tuple', ['[s7521-tuple] type=1 boot=800825D0/D0 ucode=80100000/1000 data=80038D00/800 flags=0 task=1'] + ctlr + s, True, 1),
             ('uncompiled imem', base + ctlr + ['[s7521-imem] new mem=1080 dram=030000 len=100 aud=0 rom=30C00 state=ROM bad=0 first=0 task=3'] + s, True, 1),
             ('interleaved rows', base + ctlr + ['[s7521-sum] why=periodic tasks=2000', '[s2020-svc] edge=entry call=1',
                                                  '[s2020-svc] edge=exit call=1'] + W(0), True, 0),
             ('interleaved path A', base + ctlr + ['[s7521-sum] why=periodic tasks=2000', '[s2020-svc] edge=entry call=1'] + W(1), True, 1),
             ('path A under ovl0', base + ctlr + ['[s7521-sum] why=periodic tasks=2000'] + W(1), True, 1),
             ('no sum', base, False, 4)]
    ok = True
    for n, lines, wc, want in cases:
        p = os.path.join(d, n.replace(' ', '_') + '.txt'); open(p, 'w').write('\n'.join(lines) + '\n')
        got = score([p], wc, imgs, rom, quiet=True)
        print(f'synthetic {n}: want {want} got {got} {"PASS" if got == want else "FAIL"}'); ok &= got == want
    return ok


def main():
    a = sys.argv[1:]
    want_ctl = '--ctl' in a; ctrl = '--controls' in a
    paths = [x for x in a if not x.startswith('--')]
    rom = open(ROM, 'rb').read()
    imgs = tomls()
    sb = static_check(rom, imgs)
    print(f'static: {len(imgs)} toml images, {len(sb)} defects' + ''.join('\n  ' + b for b in sb))
    if ctrl and not controls(imgs, rom): sys.exit(5)
    rc = score(paths, want_ctl, imgs, rom) if paths else 0
    if sb: rc = max(rc, 1)
    sys.exit(rc)


if __name__ == '__main__':
    main()
