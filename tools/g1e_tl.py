#!/usr/bin/env python3
"""s6711 G1e per-frame timeline join (ROGUESQ_G1E_TL=<file> ring, mesgqueue.cpp rs64_tl).

Marks (<qIIii: t_us, code, arg, osid, pad): 1 VI edge, 3/4 update_screen begin/end (Gfx thread), 5 osSpTaskStart kick
(arg=type), 6 Gfx thread task start, 7 RSP ucode exit, 8 send_dl return, 9 dp_complete, 10 blocking recv on empty mq,
11 its return, 12 blocking recv that found a message, 13 osSendMesg, 14 host enqueue_external, 15 osViSwapBuffer.
KICK-CENTRIC (latency check only): a frame = one gfx kick to the next. The game's ack recv returns ~3 ms AFTER the next
kick (kick at VI+0.2 ms, ack at VI+3 ms), so only atypical frames join; use it for q/wake latencies, not for budgets.
The SWAP-CENTRIC table at the end is the primary per-frame view. Segments (contiguous, so they sum to the kick interval):
  q     kick -> Gfx thread task start        rsp  task start -> RSP exit     rdp  RSP exit -> send_dl return
  dpc   send_dl return -> dp_complete        wake dp_complete -> game recv return on the done mq
  post  done recv -> ack recv start (swap, cpu) ack  ack wait                cpu  ack return -> next kick
Threads are keyed by the unique g1b slot (pad field); the game thread = the slot issuing osViSwapBuffer.
Usage: g1e_tl.py <file.bin> [--done-mq 0x8011A7E8] [--ack-mq 0x80128CF0] [--skip-s 60]
"""
import struct, sys, argparse, statistics as st
ap = argparse.ArgumentParser(); ap.add_argument('f')
ap.add_argument('--done-mq', type=lambda x: int(x, 0), default=0x8011A7E8); ap.add_argument('--ack-mq', type=lambda x: int(x, 0), default=0x80128CF0)
ap.add_argument('--skip-s', type=float, default=60.0); ap.add_argument('--slow-ms', type=float, default=20.0)
a = ap.parse_args()
raw = open(a.f, 'rb').read(); n = len(raw) // 24
ev = sorted((lambda r: (r[0], r[1], r[2], r[4]))(struct.unpack_from('<qIIii', raw, i * 24)) for i in range(n))  # (t, code, arg, slot)
nz = sum(1 for e in ev if e[0] == 0); ev = [e for e in ev if e[0] != 0]  # t=0: slot claimed but not yet stamped at flush
t0 = ev[0][0]; tend = ev[-1][0]
ev = [e for e in ev if e[0] - t0 >= a.skip_s * 1e6]
print(f'marks={n} unstamped={nz} span={(tend - t0) / 1e6:.1f}s analysed_from={a.skip_s}s')
import collections
G = collections.Counter(e[3] for e in ev if e[1] == 15).most_common(1)[0][0]
kicks = [i for i, e in enumerate(ev) if e[1] == 5 and e[2] == 1]
R = collections.Counter(e[3] for e in ev if e[1] == 13 and e[2] == a.done_mq).most_common(1)[0][0]  # relay: sends the done msg
print(f'game slot (swapper) = {G}; gfx kick slots {dict(collections.Counter(ev[i][3] for i in kicks))}; '
      f'{len(kicks) / ((ev[-1][0] - ev[0][0]) / 1e6):.1f} tasks/s')
# senders of the two watched mqs
snd = {}
for e in ev:
    if e[1] in (13, 14) and e[2] in (a.done_mq, a.ack_mq): snd[(e[2], e[1], e[3])] = snd.get((e[2], e[1], e[3]), 0) + 1
for k, v in sorted(snd.items()): print(f'  send mq=0x{k[0]:08X} {"guest" if k[1] == 13 else "host"} slot={k[2]}: {v}')
vis = [e[0] for e in ev if e[1] == 1]
K = collections.Counter(ev[i][3] for i in kicks).most_common(1)[0][0]
pre = collections.Counter()  # what woke the kicker thread right before each kick, and who sent to that mq
for i in kicks:
    for x in range(i - 1, max(0, i - 400), -1):
        if ev[x][3] == K and ev[x][1] in (11, 12): pre[(ev[x][1], ev[x][2])] += 1; break
print('kicker slot', K, 'woken before kick by:', ', '.join(f'{"blk" if c == 11 else "ready"} mq=0x{m:08X} x{v}' for (c, m), v in pre.most_common(4)))
for (c, m), v in pre.most_common(2):
    who = collections.Counter((e[1], e[3]) for e in ev if e[1] in (13, 14) and e[2] == m)
    print(f'  senders of 0x{m:08X}:', ', '.join(f'{"guest" if c2 == 13 else "host"} slot={sl} x{v2}' for (c2, sl), v2 in who.most_common(4)))
import bisect
def nxt(i, pred, lim):
    for j in range(i + 1, lim):
        if pred(ev[j]): return j
    return None
rows = []; bad = 0
for ki in range(len(kicks) - 1):
    i, inext = kicks[ki], kicks[ki + 1]
    ts = nxt(i, lambda e: e[1] == 6, inext + 400)
    if ts is None: bad += 1; continue
    rx = nxt(ts, lambda e: e[1] == 7, inext + 400); sd = nxt(ts, lambda e: e[1] == 8, inext + 400); dp = nxt(ts, lambda e: e[1] == 9, inext + 400)
    dn = nxt(i, lambda e: e[1] in (11, 12) and e[2] == a.done_mq and e[3] == G, inext)
    ak0 = nxt(dn, lambda e: e[1] in (10, 12) and e[2] == a.ack_mq and e[3] == G, inext) if dn is not None else None  # the ack wait after this task's done
    ak1 = None
    if ak0 is not None: ak1 = ak0 if ev[ak0][1] == 12 else nxt(ak0, lambda e: e[1] == 11 and e[2] == a.ack_mq and e[3] == G, inext)
    sw = nxt(i, lambda e: e[1] == 15 and e[3] == G, inext)
    if None in (rx, sd, dp, dn, ak0, ak1) or not (ev[i][0] <= ev[ts][0] <= ev[rx][0] <= ev[sd][0] <= ev[dp][0] <= ev[dn][0] <= ev[ak0][0] <= ev[ak1][0] <= ev[inext][0]):
        bad += 1; continue
    T = [ev[x][0] for x in (i, ts, rx, sd, dp, dn, ak0, ak1, inext)]
    seg = [(T[k + 1] - T[k]) / 1e3 for k in range(8)]
    # Gfx thread in update_screen at kick time? VI phase: ack return and kick relative to the previous VI edge
    p = bisect.bisect_right(vis, T[7]) - 1; ph_ack = (T[7] - vis[p]) / 1e3 if p >= 0 else float('nan')
    p2 = bisect.bisect_right(vis, T[0]) - 1; ph_kick = (T[0] - vis[p2]) / 1e3 if p2 >= 0 else float('nan')
    us = sum((ev[x][0] if ev[x][1] == 4 else -ev[x][0]) for x in range(i, ts) if ev[x][1] in (3, 4) and ev[x][3] == -1)
    nus = sum(1 for x in range(i, ts) if ev[x][1] == 3)
    hs = None
    for x in range(i - 1, max(0, i - 400), -1):
        if ev[x][1] == 13 and ev[x][3] == G: hs = (T[0] - ev[x][0]) / 1e3; break
    # wake split: dp_complete -> relay thread recv return -> relay send to done mq -> game recv return
    w1 = nxt(dp, lambda e: e[1] in (11, 12) and e[3] == R, dn); w2 = nxt(w1, lambda e: e[1] == 13 and e[2] == a.done_mq and e[3] == R, dn) if w1 else None
    wsp = [(ev[w1][0] - T[4]) / 1e3, (ev[w2][0] - ev[w1][0]) / 1e3, (T[5] - ev[w2][0]) / 1e3] if w1 and w2 else None
    rows.append(dict(wsp=wsp, hand=hs, seg=seg, tot=(T[8] - T[0]) / 1e3, ph_ack=ph_ack, ph_kick=ph_kick, nus=nus, swap=sw is not None, ack_blk=ev[ak0][1] == 10,
                     vis=bisect.bisect_right(vis, T[8]) - bisect.bisect_right(vis, T[0])))
names = ['q', 'rsp', 'rdp', 'dpc', 'wake', 'post', 'ack', 'cpu']
print(f'relay slot (done-mq sender) = {R}\nKICK-CENTRIC (latency only, biased: joins only frames whose ack returned before the next kick): joined={len(rows)} unjoined={bad}')
ctl = max(abs(sum(r['seg']) - r['tot']) for r in rows)
print(f'positive control: max |sum(seg) - kick interval| = {ctl:.4f} ms; swap seen in {sum(r["swap"] for r in rows)}/{len(rows)}')
def pct(v, q): v = sorted(v); return v[min(len(v) - 1, int(q * len(v)))]
def table(rs, label):
    if not rs: print(f'{label}: none'); return
    print(f'{label}: n={len(rs)} interval med {st.median(r["tot"] for r in rs):.2f} ms, VIs/frame mean {st.mean(r["vis"] for r in rs):.2f}, '
          f'ack blocked {sum(r["ack_blk"] for r in rs)}/{len(rs)}, kicks with update_screen before task start {sum(r["nus"] > 0 for r in rs)}')
    print('   seg    mean   med    p90')
    for k, nm in enumerate(names):
        v = [r['seg'][k] for r in rs]; print(f'   {nm:5s} {st.mean(v):6.2f} {st.median(v):6.2f} {pct(v, .9):6.2f}')
    for nm in ('ph_ack', 'ph_kick'):
        v = [r[nm] for r in rs]; print(f'   {nm} (ms after VI edge) mean {st.mean(v):.2f} med {st.median(v):.2f} p90 {pct(v, .9):.2f}')
    hv = [r['hand'] for r in rs if r['hand'] is not None]
    if hv: print(f'   handoff (last game-thread osSendMesg -> kick, inside cpu) mean {st.mean(hv):.2f} med {st.median(hv):.2f} p90 {pct(hv, .9):.2f}')
    ws = [r['wsp'] for r in rs if r['wsp']]
    if ws: print(f'   wake split (n={len(ws)}): dpc->relay recv ' + ' / '.join(f'{st.mean(w[k] for w in ws):.2f}' for k in range(3)) + ' ms (relay recv, relay->send, send->game recv) means; p90 ' + ' / '.join(f'{pct([w[k] for w in ws], .9):.2f}' for k in range(3)))
    cg = [r['seg'][0] + r['seg'][1] + r['seg'][2] + r['seg'][3] + r['seg'][4] + r['seg'][5] + r['seg'][7] for r in rs]
    print(f'   busy (all but ack) mean {st.mean(cg):.2f} med {st.median(cg):.2f}')
table([r for r in rows if r['tot'] <= a.slow_ms], f'FAST (<= {a.slow_ms} ms)')
table([r for r in rows if r['tot'] > a.slow_ms], f'SLOW (> {a.slow_ms} ms)')

# ---- swap-centric view: one game frame = one osViSwapBuffer by the game thread to the next ----
# Per frame: VI edges crossed, game-thread blocked ms per mq (10->11 pairs), running ms (= interval - blocked; includes
# ready-not-scheduled), the gfx task (kick -> RSP exit) that completed inside the frame, and the phase (ms after the
# previous VI edge) of the game's last ack return and of the frame's kick.
sw = [i for i, e in enumerate(ev) if e[1] == 15 and e[3] == G]
blk_open = {}
fr = []
gi = 0
for k in range(len(sw) - 1):
    a0, a1 = sw[k], sw[k + 1]; ta, tb = ev[a0][0], ev[a1][0]
    b = collections.Counter(); op = None
    for x in range(a0, a1):
        e = ev[x]
        if e[3] != G: continue
        if e[1] == 10: op = (e[2], e[0])
        elif e[1] == 11 and op and op[0] == e[2]: b[e[2]] += (e[0] - op[1]) / 1e3; op = None
    if op: b[op[0]] += (tb - op[1]) / 1e3
    kk = [x for x in range(a0, a1) if ev[x][1] == 5 and ev[x][2] == 1]
    rs = [x for x in range(a0, a1) if ev[x][1] == 7]
    nvi = bisect.bisect_right(vis, tb) - bisect.bisect_right(vis, ta)
    p = bisect.bisect_right(vis, ta) - 1
    fr.append(dict(T=(tb - ta) / 1e3, nvi=nvi, blk=b, run=(tb - ta) / 1e3 - sum(b.values()), nk=len(kk),
                   rsp=sum((ev[r][0] - ev[[x for x in range(a0 - 300, r) if ev[x][1] == 6][-1]][0]) / 1e3 for r in rs) if rs else 0.0,
                   ph_swap=(ta - vis[p]) / 1e3 if p >= 0 else float('nan')))
print(f'\nSWAP-CENTRIC: frames={len(fr)} ({len(fr) / ((ev[-1][0] - ev[0][0]) / 1e6):.1f}/s)')
for nv in sorted(set(f['nvi'] for f in fr)):
    rs_ = [f for f in fr if f['nvi'] == nv]
    if len(rs_) < 5: continue
    mqs = collections.Counter()
    for f in rs_: mqs.update(f['blk'])
    top = ', '.join(f'0x{m:08X} {v / len(rs_):.2f}' for m, v in mqs.most_common(4))
    print(f' VIs/frame={nv}: n={len(rs_)} T {st.mean(f["T"] for f in rs_):.2f} run {st.mean(f["run"] for f in rs_):.2f} '
          f'(p90 {pct([f["run"] for f in rs_], .9):.2f}) rsp {st.mean(f["rsp"] for f in rs_):.2f} kicks {st.mean(f["nk"] for f in rs_):.2f} '
          f'swap phase {st.median(f["ph_swap"] for f in rs_):.2f} | blocked ms/frame: {top}')
# P(frame spans >= 2 VIs) per gfx-task (task start -> RSP exit) bin: the RSP budget that still makes one VI.
print(' rsp ms bin -> n, P(>=2 VIs), mean run ms')
for lo, hi in ((0, 4), (4, 6), (6, 8), (8, 10), (10, 12), (12, 14), (14, 16), (16, 99)):
    b_ = [f for f in fr if lo <= f['rsp'] < hi]
    if b_: print(f'   [{lo:2d},{hi:2d}) n={len(b_):5d} P2={sum(f["nvi"] >= 2 for f in b_) / len(b_):.2f} run={st.mean(f["run"] for f in b_):.2f}')
