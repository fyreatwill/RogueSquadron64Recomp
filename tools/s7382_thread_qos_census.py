#!/usr/bin/env python3
"""s7382 class AX: census of every host thread the process can create, with its QoS / priority at creation.

Scope: src/main, src/rsp, lib/rt64/src/{hle,render,common,rhi,gui,apple}, lib/rt64/src/contrib/plume/*.{cpp,mm},
lib/N64ModernRuntime/{ultramodern,librecomp}/src. Creation idioms: std::thread construction (temporary, named, new,
make_unique), pthread_create, SDL_CreateThread, dispatch_queue_create / dispatch_async / dispatch_get_global_queue.
Row key `file|snippet|n` (snippet = normalised creation expression, n = occurrence of that snippet in the file).

Hand verdicts: tools/s7382_thread_qos_reviewed.tsv, columns key, verdict, thread-name, note. Verdicts:
  HOT-COVERED  runs in play with measured CPU share >= 1%; interactive QoS by default (or default QoS measured harmless)
  HOT-FIXED    hot thread whose QoS was raised by default in this class (env gate =0 restores old)
  WARM         runs in play, CPU share < 1% of a core, QoS irrelevant to pacing
  COLD         never runs in play (startup, exit, one-shot, mods disabled, tool binary)
  DIAG         env-gated diagnostic / test thread, default off
  OWNER        hot thread at DEFAULT QoS by default, USER_INTERACTIVE under ROGUESQ_QOS_ALL=1; flipping the default is the owner's
               open call (docs/OWNER-OPT-INS.md "Tell us if it should be on by default"); --check passes and prints them
  GAP          open defect: hot thread at default/utility QoS with no lever
--check        exit 1 on an unreviewed row, a stale review, a GAP verdict, or a control failure.
--runtime L    fold a "[s7382] thr" run log: per thread, QoS, base pri, CPU share of one core per dump interval.
Controls (always run): a planted `std::thread([]{...}).detach()` and a planted pthread_create must be listed; a
`std::thread::id` / this_thread use must NOT be listed; the real RT64 present thread creation must be listed.
"""
import argparse, glob, os, re, sys
from collections import defaultdict, OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REVIEW = os.path.join(ROOT, 'tools', 's7382_thread_qos_reviewed.tsv')
GLOBS = ['src/main/*.cpp', 'src/main/*.mm', 'src/main/*.h', 'src/rsp/*.cpp',
         'lib/rt64/src/hle/*.cpp', 'lib/rt64/src/render/*.cpp', 'lib/rt64/src/common/*.cpp', 'lib/rt64/src/rhi/*.cpp',
         'lib/rt64/src/gui/*.cpp', 'lib/rt64/src/apple/*.mm', 'lib/rt64/src/contrib/plume/*.cpp', 'lib/rt64/src/contrib/plume/*.mm',
         'lib/N64ModernRuntime/ultramodern/src/*.cpp', 'lib/N64ModernRuntime/librecomp/src/*.cpp']
PAT = re.compile(r'(new\s+std::thread\s*\(|std::make_unique<std::thread>\s*\(|std::thread\s*[({]|std::thread\s+\w+\s*[({]'
                 r'|=\s*std::thread\s*[({]|\bpthread_create\s*\(|\bSDL_CreateThread\s*\(|\bdispatch_queue_create\s*\(|\bdispatch_async\s*\(\s*dispatch_get_global_queue)')
SKIP = re.compile(r'std::thread::|this_thread|^\s*//|std::thread\s*\*|std::thread>\s*\w+;|std::thread\s+\w+\s*;')

def scan_text(path, text):
    rows = []; seen = defaultdict(int)
    for i, line in enumerate(text.split('\n'), 1):
        code = line.split('//')[0] if '://' not in line else line
        if SKIP.search(code) and not re.search(r'std::thread\s*[({]|new std::thread|make_unique<std::thread>|pthread_create', code):
            continue
        m = PAT.search(code)
        if not m: continue
        if re.search(r'std::thread::id|this_thread', code[m.start():m.end()]): continue
        snip = re.sub(r'\s+', ' ', code[m.start():m.start() + 60]).strip()
        snip = re.sub(r'[|\t]', ' ', snip)
        seen[snip] += 1
        rows.append((f'{path}|{snip}|{seen[snip]}', i, line.strip()[:140]))
    return rows

def scan():
    rows = []
    for g in GLOBS:
        for p in sorted(glob.glob(os.path.join(ROOT, g))):
            rel = os.path.relpath(p, ROOT)
            if '/tools/' in rel: continue
            rows += scan_text(rel, open(p, errors='replace').read())
    return rows

def controls(rows):
    ok = True
    planted = 'void f(){ std::thread([]{ work(); }).detach(); pthread_create(&t, 0, fn, 0); auto id = std::this_thread::get_id(); std::thread::id x; }'
    pr = scan_text('CTL', planted.replace('; ', ';\n'))
    snips = [r[0] for r in pr]
    c1 = any('std::thread(' in s for s in snips); c2 = any('pthread_create' in s for s in snips); c3 = len(pr) == 2
    c4 = any(r[0].startswith('lib/rt64/src/hle/rt64_present_queue.cpp|') for r in rows)
    for name, v in (('planted std::thread listed', c1), ('planted pthread_create listed', c2), ('this_thread/thread::id not listed', c3),
                    ('real RT64 present thread listed', c4)):
        print(f'CONTROL {"PASS" if v else "FAIL"}: {name}'); ok &= v
    return ok

def load_review():
    rv = OrderedDict()
    if os.path.exists(REVIEW):
        for ln in open(REVIEW):
            if ln.startswith('#') or not ln.strip(): continue
            f = ln.rstrip('\n').split('\t')
            rv[f[0]] = f[1:]
    return rv

QOS = {0x21: 'UI', 0x19: 'UIN', 0x15: 'DEF', 0x11: 'UT', 0x09: 'BG', 0x00: 'UNSPEC'}
def runtime(path):
    dumps = OrderedDict()
    for ln in open(path, errors='replace'):
        if not ln.startswith('[s7382] thr '): continue
        kv = dict(x.split('=', 1) for x in ln.split()[2:] if '=' in x)
        t = float(kv['t']); dumps.setdefault(t, {})[kv['tid']] = kv
    ts = list(dumps)
    ctl = {}
    for ln in open(path, errors='replace'):
        m = re.match(r'\[s7382\] dump t=([\d.]+) threads=\d+ ctl_spin_us=(\d+)', ln)
        if m: ctl[float(m.group(1))] = int(m.group(2))
    if len(ts) < 2: print('runtime: fewer than 2 dumps'); return None
    out = {}
    for a, b in zip(ts, ts[1:]):
        wall = (b - a) * 1e6
        for tid, kv in dumps[b].items():
            pa = dumps[a].get(tid); prev = int(pa['cpu_us']) if pa else 0
            share = (int(kv['cpu_us']) - prev) / wall
            out.setdefault(tid, {'name': kv['name'], 'qos': QOS.get(int(kv['qos'], 16), kv['qos']), 'pri': kv['pri'], 'rt': kv['rt'], 'sh': {}})
            out[tid]['sh'][b] = share; out[tid]['qos'] = QOS.get(int(kv['qos'], 16), kv['qos']); out[tid]['pri'] = kv['pri']; out[tid]['rt'] = kv['rt']
    # control: ctl thread cpu delta vs its own spin wall time
    ctl_ok = None
    cr = [d for d in out.values() if d['name'] == 's7382-ctl']
    if cr and len(ctl) >= 2:
        cpu = {t: int(dumps[t][tid]['cpu_us']) for tid in dumps[ts[-1]] if dumps[ts[-1]][tid]['name'] == 's7382-ctl' for t in ts if tid in dumps[t]}
        a0, a1 = ts[0], ts[-1]
        dc = cpu.get(a1, 0) - cpu.get(a0, 0); ds = ctl.get(a1, 0) - ctl.get(a0, 0)
        ctl_ok = ds > 0 and abs(dc - ds) <= 0.15 * ds
        print(f'CONTROL {"PASS" if ctl_ok else "FAIL"}: s7382-ctl qos={cr[0]["qos"]} pri={cr[0]["pri"]} cpu_delta={dc}us own_spin={ds}us')
        if cr[0]['qos'] != 'BG' or cr[0]['pri'] != '4': print('CONTROL FAIL: ctl QoS/pri not BG/4'); ctl_ok = False
    # per-thread rows >= 2% of a core (unnamed threads need the tid to be attributed)
    print('per-thread >= 2%:')
    for tid, d in sorted(out.items(), key=lambda kv: -max(kv[1]['sh'].values())):
        mx = max(d['sh'].values())
        if mx < 0.02: break
        print(f'  tid={tid} name={d["name"]} qos={d["qos"]} pri={d["pri"]} max={mx*100:.1f}% mean={sum(d["sh"].values())/len(d["sh"])*100:.1f}%')
    # aggregate by name
    agg = defaultdict(lambda: {'n': 0, 'qos': set(), 'pri': set(), 'rt': set(), 'sh': defaultdict(float)})
    for tid, d in out.items():
        g = agg[d['name']]; g['n'] += 1; g['qos'].add(d['qos']); g['pri'].add(d['pri']); g['rt'].add(d['rt'])
        for t, s in d['sh'].items(): g['sh'][t] += s
    print(f'{"name":24} {"n":>3} {"qos":8} {"pri":6} rt  ' + ' '.join(f't{int(t):>4}' for t in ts[1:]) + '   max')
    for name, g in sorted(agg.items(), key=lambda kv: -max(kv[1]['sh'].values() or [0])):
        mx = max(g['sh'].values() or [0])
        print(f'{name[:24]:24} {g["n"]:3d} {",".join(sorted(g["qos"])):8} {",".join(sorted(g["pri"])):6} {",".join(sorted(g["rt"])):3} '
              + ' '.join(f'{g["sh"].get(t, 0)*100:5.1f}' for t in ts[1:]) + f'  {mx*100:5.1f}%')
    return agg

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--check', action='store_true'); ap.add_argument('--runtime'); ap.add_argument('--list', action='store_true')
    a = ap.parse_args()
    if a.runtime: runtime(a.runtime); return 0
    rows = scan(); rv = load_review(); ok = controls(rows)
    keys = {r[0] for r in rows}; cnt = defaultdict(int); bad = 0
    for k, ln, txt in rows:
        v = rv.get(k)
        verdict = v[0] if v else 'UNREVIEWED'; cnt[verdict] += 1
        if a.list or verdict in ('UNREVIEWED', 'GAP'): print(f'{verdict:12} {k.split("|")[0]}:{ln}  {txt}')
        if verdict in ('UNREVIEWED', 'GAP'): bad += 1
    stale = [k for k in rv if k not in keys]
    for k in stale: print(f'STALE review {k}')
    for k, ln, txt in rows:
        v = rv.get(k)
        if v and v[0] == 'OWNER': print(f'OWNER        {k.split("|")[0]}:{ln}  {v[1]}: {v[2][:110]}')
    print(f'rows={len(rows)} ' + ' '.join(f'{k}={v}' for k, v in sorted(cnt.items())) + f' stale={len(stale)}')
    if a.check and (bad or stale or not ok): return 1
    return 0

if __name__ == '__main__': sys.exit(main())
