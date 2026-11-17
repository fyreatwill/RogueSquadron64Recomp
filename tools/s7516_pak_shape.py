#!/usr/bin/env python3
"""s7516 class FM: score [s7516-pak] rows (ROGUESQ_LOG_PAK_SHAPE=1, lib/N64ModernRuntime/librecomp/src/cont.cpp + pak.cpp)
against the libultra 2.0D-era Rumble/Controller Pak rules the game links (osMotorStart/Stop at 0x8002D570/0x8002D3D0 check the
per-channel __osMotorinitialized table, return PFS_ERR_INVALID 5 when unset; osMotorInit = __osPfsGetStatus first). The
hardware return is re-derived here from the game's own OSContStatus bytes (st, errno) and the call history, not from the host:
  osMotorInit: errno & 8 -> PFS_ERR_CONTRFAIL 4; status & CONT_CARD_ON(1) == 0 -> PFS_ERR_NOPACK 1; card on -> 0 (the port only
    ever reports a Rumble Pak, never a Controller Pak). Success marks the channel initialised; failure does NOT clear it (2.0D).
  osMotorStart/Stop/__osMotorAccess: channel never initialised -> 5; else 0 with a card on, 1/4 per errno without one.
  osPfs*: errno & 8 -> 4; no card -> 1; card on (rumble) -> any nonzero (a rumble pak has no PFS id area).
Game-side invariants (H-live if broken): a motor Start/Stop with the game's present flag 0 (pfs+104); an osMotorInit while the
game's tried latch pfs+105 is still set and present is 0 (hardware with no pak calls it once per latch; the game itself clears the
latch at mission start / mission end via clearControllerPakPresence 0x80003188, so one re-init per transition is retail design -
s7516 run 1 first used "<= 2 inits per run" and flagged exactly those); an osPfs* call while the save device selector 0x80112720
== 1 (EEPROM: the pak path must be dead).
Usage: s7516_pak_shape.py [--controls] [--ctl CTLLOG] LOG...
  rc 0 clean (+ ctl arm shows Init ok and >= 1 Start/Stop ok), 1 live divergence, 3 ctl arm missing/unproven, 4 no rows."""
import re, sys
from collections import Counter

ROW = re.compile(r'\[s7516-pak\] (.*)')


def parse(lines):
    out = []
    for ln in lines:
        m = ROW.search(ln)
        if m:
            out.append(dict(kv.split('=', 1) for kv in m.group(1).split() if '=' in kv))
    return out


def score(rows):
    """returns (bad list, stats Counter)"""
    bad, st = [], Counter()
    init = {}
    inits = Counter()
    for r in rows:
        fn = r['fn']; ch = int(r['ch']); hr = int(r['host_ret'])
        s = int(r['st']); e = int(r['errno']); pres = int(r['present']); dev = int(r['dev'])
        card = (s & 1) != 0 and s != 0xFF
        noresp = e != 0xFF and (e & 8) != 0
        st[fn + ':ret' + str(hr)] += 1
        if fn == 'osMotorInit':
            inits[ch] += 1
            if int(r['tried']) == 1 and pres == 0:
                bad.append('seq=%s osMotorInit ch=%d with tried latch set and no pak (retry storm)' % (r['seq'], ch))
            hw = 4 if noresp else (0 if card else 1)
            if hw == 0:
                init[ch] = True
            if hr != hw:
                bad.append('seq=%s %s ch=%d ret host=%d hw=%d' % (r['seq'], fn, ch, hr, hw))
        elif fn.startswith('osMotor') or fn.startswith('__osMotor'):
            hw = 5 if not init.get(ch) else (0 if card else (4 if noresp else 1))
            if hr != hw:
                bad.append('seq=%s %s ch=%d ret host=%d hw=%d' % (r['seq'], fn, ch, hr, hw))
            if pres == 0:
                bad.append('seq=%s %s ch=%d game_present=0 (motor call without a pak)' % (r['seq'], fn, ch))
        elif fn.startswith('osPfs'):
            if dev == 1:
                bad.append('seq=%s %s dev=1 (pak path reached with EEPROM device)' % (r['seq'], fn))
            if noresp and hr != 4 or (not noresp and not card and hr != 1) or (card and hr == 0):
                bad.append('seq=%s %s ret host=%d card=%d noresp=%d' % (r['seq'], fn, hr, card, noresp))
        else:
            bad.append('seq=%s unknown fn %s' % (r['seq'], fn))
    st.update({'inits_ch%d' % ch: n for ch, n in inits.items()})
    return bad, st


def ctl_ok(rows):
    st = score(rows)[1]
    return st['osMotorInit:ret0'] >= 1 and (st['osMotorStart:ret0'] + st['osMotorStop:ret0']) >= 1


def controls():
    base = dict(seq='0', t='0', pfs='0x80110520', ch='0', host_ret='1', st='0', errno='0', present='0', tried='0', on='0', dev='1')
    def R(**k):
        d = dict(base); d.update({a: str(b) for a, b in k.items()}); return d
    clean = [R(fn='osMotorInit')]
    ok = [('clean', clean, False),
          ('start_without_pak', clean + [R(fn='osMotorStart', host_ret=5)], True),
          ('init_ok_no_card', [R(fn='osMotorInit', host_ret=0)], True),
          ('retry_storm', clean + [R(fn='osMotorInit', seq=1, tried=1)], True),
          ('reinit_after_clear', [R(fn='osMotorInit', seq=i, tried=0) for i in range(5)], False),
          ('pfs_on_eeprom_dev', clean + [R(fn='osPfsInitPak')], True),
          ('noresp_wrong_code', [R(fn='osMotorInit', ch=1, errno=8, st=255, host_ret=1)], True)]
    good = True
    for name, rows, want in ok:
        got = bool(score(rows)[0])
        print('control %-18s flagged=%d want=%d %s' % (name, got, want, 'PASS' if got == want else 'FAIL'))
        good &= got == want
    cr = [R(fn='osMotorInit', host_ret=0, st=1), R(fn='osMotorStop', host_ret=0, st=1, present=1)]
    c1, c2 = ctl_ok(cr), ctl_ok(clean)
    print('control ctl_detect pos=%d neg=%d %s' % (c1, c2, 'PASS' if c1 and not c2 else 'FAIL'))
    return good and c1 and not c2


def main(a):
    rc = 0
    if '--controls' in a:
        a.remove('--controls')
        if not controls():
            return 2
    ctl = None
    if '--ctl' in a:
        i = a.index('--ctl'); ctl = a[i + 1]; del a[i:i + 2]
    total = 0
    for p in a:
        rows = parse(open(p, errors='replace'))
        total += len(rows)
        b, st = score(rows)
        print('%s rows=%d %s bad=%d' % (p, len(rows), dict(st), len(b)))
        for x in b[:10]:
            print('  BAD', x)
        if b:
            rc = 1
    if ctl:
        rows = parse(open(ctl, errors='replace'))
        b, st = score(rows)
        print('%s (ctl) rows=%d %s bad=%d ctl_ok=%d' % (ctl, len(rows), dict(st), len(b), ctl_ok(rows)))
        for x in b[:10]:
            print('  BAD', x)
        if b:
            rc = 1
        elif not ctl_ok(rows) and rc == 0:
            rc = 3
    if total == 0 and rc == 0:
        rc = 4
    return rc


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
