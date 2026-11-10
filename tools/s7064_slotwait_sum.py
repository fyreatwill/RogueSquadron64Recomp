#!/usr/bin/env python3
"""s7064: summarise a ROGUESQ_S7064 slot-wait dump. Per episode (busy anyAudioSlotActive polls until idle): duration, caller
function, active slots at start, mask-change times, synth frames inside (rate vs whole-run rate), deactivateVoice events
(time, slot, caller), lag from the last slot going idle (last M/D) to the episode end, and per slot the guest words that
change across synth-frame snapshots. Usage: s7064_slotwait_sum.py <sw.txt> [min_ms=20] [--words]"""
import sys, re, glob, bisect, collections
P = sys.argv[1]; MIN = float(sys.argv[2]) if len(sys.argv) > 2 and not sys.argv[2].startswith('-') else 20.0; WORDS = '--words' in sys.argv
# address -> function name from the generated code ("RECOMP_FUNC void name(" followed by "// 0xADDR:" comments)
starts = []
for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c'):
    fn = None
    for line in open(f, errors='replace'):
        if line.startswith('RECOMP_FUNC void '):
            fn = line[17:line.index('(')]; first = True
        elif fn and first and line.lstrip().startswith('// 0x'):
            starts.append((int(line.split()[1][2:10].rstrip(':'), 16), fn)); first = False
starts.sort(); keys = [a for a, _ in starts]
def name(ra):
    i = bisect.bisect_right(keys, ra - 8) - 1
    return f"{starts[i][1]}+0x{ra - 8 - starts[i][0]:X}" if i >= 0 else hex(ra)
G = None; eps = []; cur = None; deacts = []
for line in open(P):
    k = line[0]; p = line.split()
    if k == 'G': G = line.strip(); continue
    t = float(p[1])
    if k == 'B':
        cur = dict(t=t, ra=int(p[2][3:], 16), mask=int(p[3][5:], 16), n=p[4], ev=[], snaps=collections.defaultdict(list), F=0)
    elif cur is None: 
        if k == 'D': deacts.append((t, p[2], p[3]))
        continue
    elif k == 'S': cur['snaps'][int(p[2])].append((t, [int(x, 16) for x in p[3:]]))
    elif k == 'M': cur['ev'].append((t, 'M', int(p[2][5:], 16)))
    elif k == 'F': cur['F'] += 1; cur.setdefault('ft', []).append(t)
    elif k == 'D': cur['ev'].append((t, 'D', p[2], p[3]))
    elif k in 'EX':
        cur['end'] = t; cur['kind'] = k; cur['tail'] = ' '.join(p[2:]); eps.append(cur); cur = None
gm = re.search(r'synth=(\d+).*span_ms=([\d.]+)', G); rate = int(gm.group(1)) / float(gm.group(2)) * 1000
print(G, f"-> synth {rate:.1f}/s whole run;", len(eps), "episodes")
byra = collections.Counter(); long_ = 0
for e in eps:
    d = e['end'] - e['t']; byra[(name(e['ra']), d >= MIN)] += 1
    if d < MIN: continue
    long_ += 1
    lastidle = max([x[0] for x in e['ev'] if (x[1] == 'M' and x[2] == 0) or x[1] == 'D'] or [e['t']])
    sm = [i for i in range(64) if e['mask'] >> i & 1]
    gaps = [b - a for a, b in zip(e.get('ft', []), e.get('ft', [])[1:])]
    print(f"\n{e['kind']} t={e['t']:.1f} dur={d:.1f}ms {e['tail']} caller={name(e['ra'])} slots={sm} synthF={e['F']} "
          f"({e['F'] / d * 1000 if d else 0:.0f}/s, max gap {max(gaps) if gaps else 0:.1f}ms) last-idle->end={e['end'] - lastidle:.1f}ms")
    for x in e['ev'][:12]:
        print("   ", f"+{x[0] - e['t']:.1f}", x[1], (f"{x[2]:X}" if x[1] == 'M' else ' '.join(x[2:])) + (f" ({name(int(x[3][3:], 16))})" if x[1] == 'D' else ''))
    if WORDS:
        for i, sn in sorted(e['snaps'].items()):
            if i not in sm: continue
            ch = [j for j in range(34) if len({s[1][j] for s in sn}) > 1]
            print(f"    slot {i}: {len(sn)} snaps, w0={sn[0][1][0]:08X}; changing words " +
                  ', '.join(f"[{j*4:02X}] {sn[0][1][j]:08X}->{sn[-1][1][j]:08X}" for j in ch[:8]))
print("\nper caller (name, >=MIN):", dict(byra))
print("deacts outside episodes:", len(deacts))
