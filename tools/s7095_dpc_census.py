#!/usr/bin/env python3
"""s7095 DPC register census: every mfc0/mtc0 on a DPC register (cop0 8-15) in the Factor 5 RSP code, decoded from the
ROM words (independent of RSPRecomp), with the bit mask each read is tested against and the constant each write stores,
then each site's value under our model (include/rsp_dpc_macros.h) vs the hardware model (n64brew DPC registers, an
instantly-consuming RDP). Controls: ROM site counts == RSP_DPC_* macro counts in the live pristine-mapped TUs (main, b,
boot); overlay TUs carry exact copies of resident sites (s7091) so their counts must be multiples of the resident
sequence; positive control = a mutated STATUS mask (0x400 -> 0x80 CBUF_READY, which hardware reports 1 when idle) and a
mutated write (0x1 -> 0x2 set XBUS) must both be flagged as model mismatches. Exit 0 iff controls pass and 0 live
mismatches."""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from s7093_su_census import decode, TUS, ROOT, LIVE, C0  # noqa: E402

# DPC_STATUS read bits (n64brew): what an idle, instantly-consuming RDP with XBUS cleared reports, vs our constant 0.
STATUS_BITS = {0x1: ('XBUS_DMEM_DMA', 'last write: clear(0x1)->0 / set(0x2)->1'), 0x2: ('FREEZE', 0), 0x4: ('FLUSH', 0),
               0x8: ('START_GCLK', 1), 0x10: ('TMEM_BUSY', 0), 0x20: ('PIPE_BUSY', 0), 0x40: ('CMD_BUSY', 0),
               0x80: ('CBUF_READY', 1), 0x100: ('DMA_BUSY', 0), 0x200: ('END_VALID', 0), 0x400: ('START_VALID', 0)}
OURS_STATUS = 0


def hw_status(bit, xbus):
    if bit == 0x1: return 1 if xbus else 0
    return STATUS_BITS[bit][1]


def sites(words, base):
    out = []
    for i, w in enumerate(words):
        d = decode(w)
        if d['m'] in ('mfc0', 'mtc0') and 8 <= d['rd'] <= 15:
            prev = decode(words[i - 1])['m'] if i else ''
            s = dict(pc=base + 4 * i, m=d['m'], reg=C0[d['rd']], rt=d['rt'], delay=prev in ('beq', 'bne', 'bgez', 'bgtz', 'blez', 'bltz', 'b', 'j', 'jal', 'jr'))
            if d['m'] == 'mfc0':
                masks = []
                for j in (1, 2):  # the andi testing the read register sits in the next one or two words
                    if i + j < len(words):
                        e = decode(words[i + j])
                        if e['m'] == 'andi' and e['rs'] == d['rt']: masks.append(e['imm'])
                s['mask'] = masks
            else:
                val = None
                for j in (1, 2, 3, 4):  # constant source: ori rt,$zero,imm just before (or in a branch delay slot)
                    if i - j >= 0:
                        e = decode(words[i - j])
                        if e['m'] == 'ori' and e['rt'] == d['rt'] and e['rs'] == 0: val = e['imm']; break
                s['val'] = val
            out.append(s)
    return out


def judge(s, xbus):
    """Return (ours, hw, mismatch) for one site."""
    if s['reg'] == 'DPC_STATUS' and s['m'] == 'mfc0':
        rows = []
        for mk in s['mask']:
            for bit in [b for b in STATUS_BITS if mk & b]:
                rows.append((STATUS_BITS[bit][0], OURS_STATUS & bit, hw_status(bit, xbus)))
        return rows, any((o != 0) != (h != 0) for _, o, h in rows)
    if s['reg'] == 'DPC_STATUS' and s['m'] == 'mtc0':
        v = s['val']
        return [('write', v, 'set_xbus' if v and v & 2 else 'clear_xbus' if v and v & 1 else v)], (v is None or bool(v & ~1))
    return [('register', s['reg'], 'live differential (ROGUESQ_S7095_DPC)')], False


def live_count(name):
    t = (LIVE / name).read_text()
    return len(re.findall(r'^\s*(?:r\d+ = )?RSP_DPC_[A-Z_]+\(', t, re.M))


def main():
    allsites, ok, live_mm = [], True, 0
    for name, rom, off, base, ln in TUS:
        data = (ROOT / rom).read_bytes()[off:off + ln]
        words = [int.from_bytes(data[k:k + 4], 'big') for k in range(0, len(data), 4)]
        ss = sites(words, base)
        lc = live_count(name); want = len(ss) + sum(s['delay'] for s in ss)  # RSPRecomp emits a delay-slot op twice
        print(f'== {name}: ROM DPC sites {len(ss)} ({sum(s["delay"] for s in ss)} in delay slots) -> expected macro uses {want}, live {lc} -> {"OK" if lc == want else "COUNT MISMATCH"}')
        ok &= lc == want
        for s in ss:
            rows, mm = judge(s, xbus=False)
            live_mm += mm
            print(f'  0x{s["pc"]:04X}{"d" if s["delay"] else " "} {s["m"]} {s["reg"]:<12} ' + (f'mask={[hex(m) for m in s["mask"]]} ' if 'mask' in s else '')
                  + (f'val={hex(s["val"]) if s["val"] is not None else None} ' if 'val' in s else '') + f'{rows} {"MISMATCH" if mm else "match"}')
            allsites.append((name, s))
    writes = [s for _, s in allsites if s['m'] == 'mtc0' and s['reg'] == 'DPC_STATUS']
    xbus_ever_set = any(s['val'] is None or s['val'] & 2 for s in writes)
    print(f'STATUS writes: {len(writes)} values {[hex(s["val"]) for s in writes]} -> XBUS ever set: {xbus_ever_set}')
    ok &= not xbus_ever_set
    res = [s for n, s in allsites if n == TUS[0][0]]
    seq = [(s['m'], s['reg']) for s in res]
    for f in sorted(LIVE.glob('factor5_ucode_ovl*_recompiled.c')):
        t = f.read_text()
        got = re.findall(r'^\s*(?:r\d+ = )?RSP_DPC_([A-Z_]+)\(', t, re.M)
        print(f'  overlay {f.name}: {len(got)} DPC macro uses')
        ok &= len(got) in (6, 15)
    # positive controls: mutated read mask and mutated write must be flagged
    st = next(s for _, s in allsites if s['reg'] == 'DPC_STATUS' and s['m'] == 'mfc0' and 0x400 in s['mask'])
    c1 = judge(dict(st, mask=[0x80]), False)[1]
    c2 = judge(dict(writes[0], val=0x2), False)[1]
    print(f'positive controls: mask 0x80 flagged={c1}, write 0x2 flagged={c2}')
    ok &= c1 and c2
    print(f'live mismatches {live_mm}; controls {"pass" if ok else "FAIL"}')
    return 0 if ok and live_mm == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
