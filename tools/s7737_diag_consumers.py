#!/usr/bin/env python3
"""s7737 live-only DIAG consumer census.

s7736 found that a DIAG row of the s7719 reverse gate (live-only statements no fixup reproduces) can hide a probe a live
recipe still uses (s6201 [g1d-alloc], read by tools/s7386_route_ab.zsh). The gate calls every DIAG row harmless. This
splits them: for each DIAG/ORDER-DIAG/REGEN-FUNC-DIAG row, take the live-only lines of that function (multiset diff vs the
replay), pull the env names they read (getenv("X") + helpers they call whose src/ or live-prelude definition reads an env) and the
"[tag]" log prefixes they print, and look for a live CONSUMER: a tools/ script, a pending soak recipe, docs/OWNER-OPT-INS.md.
  CONSUMED  - some name/tag has a consumer outside the PORTING-STATE ledger -> the next regen loses an instrument in use
  ACCEPTED  - CONSUMED but reviewed in tools/s7737_diag_consumer_accept.tsv (file<TAB>func<TAB>reason)
  ORPHAN    - no consumer (dead probe; losing it at regen is fine)
exit 0 = H-none, 1 = H-more (an unreviewed CONSUMED row), 3 = control FAIL.
usage: s7737_diag_consumers.py <rev.txt from s7423_live_stale.py --reverse> <live dir> <replay dir> [--control]
--control plants a fake row whose live-only line reads ROGUESQ_LOG_G1D_TASK (s7736's consumed name) and must be CONSUMED,
and a row reading ROGUESQ_S7737_NOBODY that must be ORPHAN.
"""
import collections, os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV = re.compile(r'getenv\("(ROGUESQ_[A-Z0-9_]+)"\)')
TAG = re.compile(r'fprintf\(stderr,\s*"\[([A-Za-z0-9_.-]{3,})\]')
CALL = re.compile(r'\b((?:rs64_|rs\d{4}_|s\d{4}_)[A-Za-z0-9_]+)\s*\(')

def body(path, fn):
    t = open(path, errors='replace').read()
    m = re.search(r'^RECOMP_FUNC \w+ %s\(' % re.escape(fn), t, re.M)
    if not m: return []
    n = re.search(r'^RECOMP_FUNC ', t[m.end():], re.M)
    return t[m.start(): m.end() + n.start() if n else len(t)].splitlines()

def live_only(lv, rp, f, fn):
    a = collections.Counter(l.strip() for l in body(os.path.join(lv, f), fn))
    b = collections.Counter(l.strip() for l in body(os.path.join(rp, f), fn))
    return [l for l in a for _ in range(a[l] - b.get(l, 0))]

_src = None
LIVE = None
def helper_envs(name):
    global _src
    if _src is None:
        _src = {}
        for d, _, fs in list(os.walk(os.path.join(ROOT, 'src'))) + ([(LIVE, None, os.listdir(LIVE))] if LIVE else []):
            for x in fs:
                if x.endswith(('.c', '.cpp', '.h')): _src[os.path.join(d, x)] = open(os.path.join(d, x), errors='replace').read()
    out = set()
    for t in _src.values():
        m = re.search(r'\b%s\s*\([^;{]*\)\s*\{' % re.escape(name), t)
        if not m: continue
        i, depth = m.end(), 1
        while i < len(t) and depth:
            depth += {'{': 1, '}': -1}.get(t[i], 0); i += 1
        out |= set(ENV.findall(t[m.end(): i]))
    return out

def consumers(key):
    paths = ['tools', 'scratch/agent/soak_queue', 'docs/OWNER-OPT-INS.md']
    try:
        out = subprocess.run(['grep', '-rlF', '--exclude-dir=done', '--exclude-dir=cancelled', '--exclude-dir=running', '--exclude-dir=running_manual', '--exclude=s7737_diag_consumers.py',
                              '--exclude=fixup_*.py', '--exclude=apply_*.py', '--exclude=*.tsv', '--exclude-dir=__pycache__',
                              '--exclude=*census*', '--exclude=*audit*', '--exclude=*gate*', '--exclude=rename*', key] + paths,
                             cwd=ROOT, capture_output=True, text=True).stdout.split()
    except Exception: out = []
    return out

def classify(lines):
    envs, tags, helpers = set(), set(), set()
    for l in lines:
        envs |= set(ENV.findall(l)); tags |= set(TAG.findall(l)); helpers |= set(CALL.findall(l))
    for h in helpers: envs |= helper_envs(h)
    hits = {}
    for k in sorted(envs) + ['[%s]' % t for t in sorted(tags)]:
        c = consumers(k)
        if c: hits[k] = c
    return ('CONSUMED' if hits else 'ORPHAN'), envs, tags, hits

def main(a):
    global LIVE
    rev, lv, rp = a[0], a[1], a[2]
    LIVE = lv
    rows = []
    for l in open(rev):
        p = l.split()
        if p and p[0] in ('DIAG', 'ORDER-DIAG', 'REGEN-FUNC-DIAG') and len(p) >= 3: rows.append((p[0], p[1], p[2]))
    acc = {}
    ap = os.path.join(ROOT, 'tools', 's7737_diag_consumer_accept.tsv')
    if os.path.exists(ap):
        for l in open(ap):
            p = l.rstrip('\n').split('\t')
            if len(p) >= 3 and not l.startswith('#'): acc[(p[0], p[1])] = p[2]
    n = collections.Counter()
    for kind, f, fn in rows:
        v, envs, tags, hits = classify(live_only(lv, rp, f, fn))
        if v == 'CONSUMED' and (f, fn) in acc: v = 'ACCEPTED'; hits = {'accept': [acc[(f, fn)]]}
        n[v] += 1
        print(f'{v:9s} {kind:15s} {f:11s} {fn}  env={",".join(sorted(envs)) or "-"} tags={",".join(sorted(tags)) or "-"}'
              + ''.join(f'\n    consumer {k}: {" ".join(c[:4])}' for k, c in hits.items()))
    rc = 0
    if '--control' in a:
        c1 = classify(['if (getenv("ROGUESQ_LOG_G1D_TASK")) fprintf(stderr, "[g1d-alloc] x\\n");'])[0]
        c2 = classify(['if (getenv("ROGUESQ_S7737_NOBODY")) fprintf(stderr, "[s7737nobody] x\\n");'])[0]
        ok = c1 == 'CONSUMED' and c2 == 'ORPHAN'
        print(f'CONTROL {"PASS" if ok else "FAIL"} consumed={c1} orphan={c2}'); rc |= 0 if ok else 2
    print(f'rows {len(rows)} CONSUMED {n["CONSUMED"]} ACCEPTED {n["ACCEPTED"]} ORPHAN {n["ORPHAN"]}')
    print('VERDICT', 'H-more' if n['CONSUMED'] else 'H-none')
    return 3 if rc else (1 if n['CONSUMED'] else 0)
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
