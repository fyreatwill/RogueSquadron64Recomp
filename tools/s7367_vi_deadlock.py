#!/usr/bin/env python3
"""s7367: classify the guest VI-handshake deadlock (MAIN 0x8011A818 / sched 0x8011A420 / retrace osSendMesg 0x80128CF0 cap 1)
from one ROGUESQ_G1E_TL ring (<file>.<pid>, codes in tools/g1e_tl.py) + its run.log.
Verdicts per run:
  CLEAN   no [stall-dump] line (run.log)
  H-sem   the final CF0 send (code 13) is followed by a CF0 recv RETURN (11/12) in another slot and the sender slot never marks again
          (recv freed the slot but did not restart the blocked sender = lost wakeup)
  H-slow  final CF0 send found the queue already full (two CF0 sends since the last CF0 recv return) and no CF0 recv return after it
  H-flag  printed as a column: the CF0 sends with no MAIN CF0 window open (MAIN = slot that issues the CF0 recvs) since its last recv
Usage: s7367_vi_deadlock.py <tl.bin> <run.log> [--mq 0x80128CF0]
"""
import struct, sys, argparse, re, collections
ap = argparse.ArgumentParser(); ap.add_argument('tl'); ap.add_argument('log'); ap.add_argument('--mq', type=lambda x: int(x, 0), default=0x80128CF0)
a = ap.parse_args()
raw = open(a.tl, 'rb').read(); n = len(raw) // 24
ev = sorted(e for e in ((lambda r: (r[0], r[1], r[2], r[4]))(struct.unpack_from('<qIIii', raw, i * 24)) for i in range(n)) if e[0])
log = open(a.log, 'rb').read().decode('latin1')
stall = re.findall(r'\[stall-dump\] vi=(\d+) stalled_vi=(\d+) fs=(\d+).*?t=([\d.]+)', log)
init = log.count('initMission'); vihz = re.findall(r'\[s7367\] VI_HZ (\d+)', log)
t0 = ev[0][0] if ev else 0
last = collections.defaultdict(int)
for t, c, arg, s in ev: last[s] = t
cf = [(t, c, s) for t, c, arg, s in ev if arg == a.mq and c in (10, 11, 12, 13)]
sends = [(t, s) for t, c, s in cf if c == 13]; rets = [(t, s) for t, c, s in cf if c in (11, 12)]
recv_slots = collections.Counter(s for t, c, s in cf if c in (10, 12)); main = recv_slots.most_common(1)[0][0] if recv_slots else None
print(f'marks={len(ev)} span={(ev[-1][0]-t0)/1e6:.1f}s vihz={vihz[:1]} initMission={init} stall_dumps={len(stall)} first_stall={stall[:1]}')
print(f'CF0 sends={len(sends)} recv_returns={len(rets)} main_slot={main} vi_edges={sum(1 for e in ev if e[1]==1)}')
# double-send windows: >=2 sends between consecutive recv returns
seq = sorted([(t, 'S', s) for t, s in sends] + [(t, 'R', s) for t, s in rets]); run = 0; dbl = 0
for t, k, s in seq:
    if k == 'S':
        run += 1
        if run == 2: dbl += 1
    else: run = 0
print(f'double_send_windows={dbl} (a 2nd CF0 send before MAIN consumed the 1st: blocks on cap 1)')
if not stall:
    print('VERDICT CLEAN'); sys.exit(0)
# Witness = the first [stall-dump]'s CF0 ring (op S/R = entry, s/r = return; valid/fullq at the event) + wait table.
blk = log[log.index('[stall-dump] vi='):]
blk = blk[:blk.index('[stall-dump] vi=', 10)] if blk.count('[stall-dump] vi=') > 1 else blk
ring = [(int(m[0]), m[1], int(m[2]), int(m[3]), int(m[4]), m[5]) for m in
        re.findall(r'\[stall-cf0\] seq=(\d+) .*?op=(\w) tid=(\d+) .*?valid=(\d+) vflag=(\d+) fullq=([0-9A-F]+)', blk)]
waits = dict((int(m[0]), (m[1], m[2], m[3])) for m in re.findall(r'\[stall-wait\] tid=(\d+) (IN|last) op=\w mq=([0-9A-F]+) caller=(\S+)', blk))
S = [r for r in ring if r[1] == 'S']; lastS = S[-1] if S else None
parked = lastS is not None and not any(r[1] == 's' and r[0] > lastS[0] for r in ring)
after = [r for r in ring if lastS and r[0] > lastS[0] and r[1] == 'r']
sem = parked and any(r[5] == '00000000' for r in after)  # receiver returned with the sender list empty, yet no 's' = lost wake
vflag_off = [r for r in S if r[4] == 0]
m3 = waits.get(3)
print(f'ring={len(ring)} final_S_seq={lastS[0] if lastS else None} retrace_parked={parked} main_returns_after={len(after)} '
      f'S_with_vflag0={len(vflag_off)} tid3_wait={m3}')
if sem: print('VERDICT H-sem (receiver drained, parked sender never resumed)')
elif vflag_off: print('VERDICT H-flag (CF0 send with vflag 0)')
elif parked and m3 and m3[0] == 'IN' and m3[1] != '80128CF0':
    print(f'VERDICT H-cycle: retrace parked on FULL CF0 (vflag 1) while MAIN is IN {m3[1]} at {m3[2]}')
else: print('VERDICT ? (see columns)')
