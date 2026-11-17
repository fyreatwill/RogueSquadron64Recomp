#!/usr/bin/env python3
"""s7541 class GB residual scorer: RT64 guest-RAM spans after reads_done (ROGUESQ_S7539_GB_CHK=1, NODRAIN=4, S7541_HOLD=1).
usage: s7541_gb_score.py log... | --controls
Per log: last periodic [s7541-gb] block. kinds 0/1 colour/depth read-in, 2 writeback-pre (clobber), 3 writeback-post (late write),
4 hashTracking. Verdict per log:
  CTL-FAIL   planted != caught on any row with planted > 0, or no row planted at all (instrument unproven)
  STRUCT-FAIL drained rows (as=1/2) with post > 0 (a drained task must finish every access before its post)
  H-none     as=4 diff_n == 0 for kinds 0,1,2,4 (late writes kind 3 reported separately)
  H-readin-torn / H-clobber / H-hash-miss  as=4 diff_n > 0 on kind 0|1 / 2 / 4
exit 0 only if every log scores CTL ok and STRUCT ok."""
import re, sys
K = {0: 'readin_c', 1: 'readin_z', 2: 'wb_pre', 3: 'wb_post', 4: 'hash'}
RX = re.compile(r'\[s7541-gb\] (\S+) as=(\d) kind=(\d) (.*)')
def parse(lines):
    blocks = {}
    for l in lines:
        m = RX.search(l)
        if not m: continue
        tag, a, k, rest = m.group(1), int(m.group(2)), int(m.group(3)), m.group(4)
        d = {kv.split('=')[0]: int(kv.split('=')[1]) for kv in rest.split() if '=' in kv}
        blocks.setdefault(tag, {})[(a, k)] = d
    if not blocks: return None
    last = list(blocks)[-1]
    return last, blocks[last]
def score(rows):
    pl = sum(d['ctl_planted'] for d in rows.values()); ca = sum(d['ctl_caught'] for d in rows.values())
    v = []
    if pl == 0 or pl != ca: v.append('CTL-FAIL')
    if any(d['post'] > 0 for (a, k), d in rows.items() if a in (1, 2)): v.append('STRUCT-FAIL')
    bad = {k: rows.get((4, k), {}).get('diff_n', 0) for k in (0, 1, 2, 4)}
    sel = []
    if bad[0] or bad[1]: sel.append('H-readin-torn')
    if bad[2]: sel.append('H-clobber')
    if bad[4]: sel.append('H-hash-miss')
    v += sel or ['H-none']
    return v, pl, ca
def report(name, lines):
    p = parse(lines)
    if not p: print(f'{name}: no [s7541-gb] lines'); return False
    tag, rows = p
    v, pl, ca = score(rows)
    print(f'== {name} block={tag} verdict={" ".join(v)} ctl={ca}/{pl}')
    print('as kind      n        ar       pre      post     nosnap  bytes        diff_n  diff_b    prev_diff_n')
    for (a, k) in sorted(rows):
        d = rows[(a, k)]
        print(f'{a:<2} {K[k]:<9} {d["n"]:<8} {d["ar"]:<8} {d["pre"]:<8} {d["post"]:<8} {d["nosnap"]:<7} {d["bytes"]:<12} {d["diff_n"]:<7} {d["diff_bytes"]:<9} {d["prev_diff_n"]}')
    return 'CTL-FAIL' not in v and 'STRUCT-FAIL' not in v
def controls():
    def blk(rows): return [f'[s7541-gb] p600 as={a} kind={k} n=10 ar=5 pre=5 post={po} nosnap=0 bytes=100 diff_n={dn} diff_bytes={dn} prev_n=1 prev_diff_n=0 prev_diff_bytes=0 ctl_planted={pl} ctl_caught={ca}' for a, k, po, dn, pl, ca in rows]
    cases = [
        (blk([(4, 0, 5, 0, 2, 2), (2, 0, 0, 0, 0, 0)]), 'H-none'),
        (blk([(4, 0, 5, 3, 2, 2)]), 'H-readin-torn'),
        (blk([(4, 2, 5, 1, 2, 2)]), 'H-clobber'),
        (blk([(4, 4, 5, 1, 2, 2)]), 'H-hash-miss'),
        (blk([(4, 3, 5, 9, 2, 2)]), 'H-none'),       # late writes alone do not select a torn read
        (blk([(4, 0, 5, 0, 2, 1)]), 'CTL-FAIL'),
        (blk([(4, 0, 5, 0, 0, 0)]), 'CTL-FAIL'),
        (blk([(4, 0, 5, 0, 2, 2), (2, 2, 1, 0, 0, 0)]), 'STRUCT-FAIL'),
        (blk([(4, 0, 5, 1, 2, 2)]) + ['[s7541-gb] p1200 as=4 kind=0 n=10 ar=5 pre=5 post=5 nosnap=0 bytes=1 diff_n=0 diff_bytes=0 prev_n=0 prev_diff_n=0 prev_diff_bytes=0 ctl_planted=1 ctl_caught=1'], 'H-none'),  # last block wins
    ]
    ok = 0
    for lines, want in cases:
        v, _, _ = score(parse(lines)[1]); ok += want in v
        if want not in v: print('control FAIL', want, v)
    print(f'controls {ok}/{len(cases)}'); return ok == len(cases)
if __name__ == '__main__':
    if sys.argv[1:] == ['--controls']: sys.exit(0 if controls() else 1)
    good = True
    for f in sys.argv[1:]:
        good &= report(f, open(f, errors='replace'))
    sys.exit(0 if good else 1)
