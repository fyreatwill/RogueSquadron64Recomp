#!/usr/bin/env python3
"""s7381 class AW: census of every host busy-wait / poll loop that waits on another thread's state.

Scope: src/main, src/rsp, lib/rt64/src/{hle,render,common,rhi,apple,gui,shared}, lib/rt64/src/contrib/plume/plume_metal.cpp,
lib/N64ModernRuntime/{ultramodern,librecomp}/src (other contrib excluded). Plus the guest side: every recompiled game
function that calls osYieldThread_recomp (host std::this_thread::yield, ../N64Recomp/RecompiledFuncs/funcs_*.c).

Host loop classes (automatic, from the loop body text):
  PURE-SPIN  do/while or while loop whose body only polls (mutex lock / atomic load / flag test / empty body) and
             never blocks, sleeps or yields -> burns a core while the condition is false
  YIELD      body yields (std::this_thread::yield / sched_yield) but never sleeps -> burns a core on an idle P-core
  SLEEP      body sleeps (sleep_for / usleep / SDL_Delay / nanosleep) -> bounded poll, no burn
Loops whose body blocks (condvar wait, semaphore, read, recv) are not spins and are not listed.
Generic iteration loops (for/while that do not poll and contain none of the above) are not listed.

Hand verdicts: tools/s7381_spin_reviewed.tsv, key `file|function|class|n` (n = occurrence of that class in the function);
guest rows `guest|function|YIELD|n`. Verdicts: IDLE <why> (never iterates in play / measured 0 spin), BOUNDED <why>
(sleeps or measured spin time negligible), EXIT <why> (exit/teardown only), DIAG <why> (env-gated diagnostic, default off),
FIXED <how>, BURN (open defect).
--check     exit 1 on an unreviewed row, a stale review, a BURN verdict, or a control failure.
--runtime L fold a "[s7381]" run log: print per-site spin counters (last dump) and per-RA guest yield rates.
Controls (always run): a planted pure-spin do/while must classify PURE-SPIN; a planted sleep poll SLEEP; a planted
yield poll YIELD; a planted condvar wait loop must NOT be listed; the real WorkloadQueue::advanceToNextWorkload must be
listed (its ROGUESQ_S7381_BARRIER_CV=0 spin branch stays in the source, verdict FIXED).
"""
import argparse, glob, os, re, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECOMP = os.path.join(os.path.dirname(ROOT), 'N64Recomp', 'RecompiledFuncs')
DIRS = ['src/main', 'src/rsp', 'lib/rt64/src/hle', 'lib/rt64/src/render', 'lib/rt64/src/common', 'lib/rt64/src/rhi',
        'lib/rt64/src/apple', 'lib/rt64/src/gui', 'lib/rt64/src/shared', 'lib/N64ModernRuntime/ultramodern/src',
        'lib/N64ModernRuntime/librecomp/src']
EXTRA = ['lib/rt64/src/contrib/plume/plume_metal.cpp']
TSV = os.path.join(ROOT, 'tools', 's7381_spin_reviewed.tsv')
EXT = ('.cpp', '.c', '.mm', '.h', '.hpp')
BLOCK_RE = re.compile(r'\.wait\s*\(|wait_for\s*\(|wait_until\s*\(|sem_wait|dispatch_semaphore_wait|\bread\s*\(|recv\s*\(|'
                      r'SDL_WaitEvent|\.acquire\s*\(|pthread_cond_wait|waitUntilCompleted|\bjoin\s*\(|getline|fgets|'
                      r'osRecvMesg|wait_for_|\.get\s*\(\s*\)|select\s*\(|poll\s*\(')
SLEEP_RE = re.compile(r'sleep_for|sleep_until|usleep\s*\(|SDL_Delay|nanosleep|\bsleep\s*\(|Sleep\s*\(|precise_sleep|sleep_milliseconds')
YIELD_RE = re.compile(r'this_thread::yield|sched_yield|SwitchToThread|_mm_pause|__builtin_arm_yield')
POLL_RE = re.compile(r'\.load\s*\(|scoped_lock|unique_lock|lock_guard|\.lock\s*\(|volatile|clock_gettime|clock::now|total_vis')
FUNC_RE = re.compile(r'^\s*(?:[\w:<>,\*&~]+\s+)+?\**([\w:~]+)\s*\([^;{}]*\)\s*(?:const\s*)?(?:override\s*)?(?:noexcept\s*)?\{')
CTRL = {'if', 'for', 'while', 'switch', 'catch', 'return', 'else', 'do'}


def strip(text):
    text = re.sub(r'/\*.*?\*/', lambda m: '\n' * m.group(0).count('\n'), text, flags=re.S)
    out = []
    for line in text.split('\n'):
        line = re.sub(r'"(?:\\.|[^"\\])*"', '""', line)
        line = re.sub(r"'(?:\\.|[^'\\])'", "''", line)
        out.append(line.split('//')[0])
    return out


def match_brace(text, i):
    """text[i] == '{' -> index of matching '}'."""
    d = 0
    for j in range(i, len(text)):
        c = text[j]
        if c == '{': d += 1
        elif c == '}':
            d -= 1
            if d == 0: return j
    return -1


def match_paren(text, i):
    d = 0
    for j in range(i, len(text)):
        c = text[j]
        if c == '(': d += 1
        elif c == ')':
            d -= 1
            if d == 0: return j
    return -1


def scan_text(rel, raw):
    lines = strip(raw)
    text = '\n'.join(lines)
    starts = [0]
    for ln in lines: starts.append(starts[-1] + len(ln) + 1)

    def lineno(pos):
        lo, hi = 0, len(starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if starts[mid] <= pos: lo = mid
            else: hi = mid - 1
        return lo + 1

    funcs = []
    for n, ln in enumerate(lines):
        m = FUNC_RE.match(ln)
        if m and m.group(1).split('::')[-1] not in CTRL:
            funcs.append((n + 1, m.group(1)))

    def func_at(line):
        name = '?'
        for l, f in funcs:
            if l <= line: name = f
            else: break
        return name

    rows = []
    # do { body } while (cond);
    for m in re.finditer(r'\bdo\s*\{', text):
        b0 = m.end() - 1
        b1 = match_brace(text, b0)
        if b1 < 0: continue
        w = re.match(r'\s*while\s*\(', text[b1 + 1:])
        if not w: continue
        c0 = b1 + 1 + w.end() - 1
        c1 = match_paren(text, c0)
        rows.append((m.start(), text[b0 + 1:b1], text[c0 + 1:c1]))
    # while (cond) body / for(;;) body
    for m in re.finditer(r'\b(while|for)\s*\(', text):
        pre = text[:m.start()].rstrip()
        if m.group(1) == 'while' and pre.endswith('}'):
            continue  # tail of do-while
        c0 = m.end() - 1
        c1 = match_paren(text, c0)
        if c1 < 0: continue
        cond = text[c0 + 1:c1]
        rest = text[c1 + 1:]
        r = re.match(r'\s*', rest)
        k = c1 + 1 + r.end()
        if k < len(text) and text[k] == '{':
            e = match_brace(text, k)
            body = text[k + 1:e] if e > 0 else ''
        elif k < len(text) and text[k] == ';':
            body = ''
        else:
            e = text.find(';', k)
            body = text[k:e + 1]
        if m.group(1) == 'for' and not re.match(r'\s*;\s*;', cond):
            # counted for-loops only matter when they sleep/yield (bounded polls)
            pass
        rows.append((m.start(), body, cond))

    out = []
    for pos, body, cond in rows:
        body = re.sub(r'\bs7381\w*\+\+\s*;?', '', body)  # our own census counters must not hide a site
        both = body + ' ' + cond
        if BLOCK_RE.search(body):
            continue
        # nested loops: only classify on the innermost statement that actually waits; drop bodies with nested loops that
        # themselves sleep (the inner loop gets its own row)
        inner = re.search(r'\b(while|for)\s*\(|\bdo\s*\{', body)
        if SLEEP_RE.search(body):
            cls = 'SLEEP'
            if inner and SLEEP_RE.search(body[inner.start():]) and not SLEEP_RE.search(body[:inner.start()]):
                continue
        elif YIELD_RE.search(body):
            cls = 'YIELD'
            if inner and YIELD_RE.search(body[inner.start():]) and not YIELD_RE.search(body[:inner.start()]):
                continue
        else:
            if inner: continue
            empty = body.strip() in ('', ';', '{}')
            polls = bool(POLL_RE.search(both)) or (empty and '(' in cond)
            # pure spin: polls shared state and does nothing else of substance
            stmts = [s for s in re.split(r'[;\n]', body) if s.strip()]
            if not polls: continue
            if not (empty or len(stmts) <= 4): continue
            if re.search(r'\bbreak\b|\breturn\b|\+\+\w|\w\+\+|\+=', body) and not empty and 'lock' not in body:
                continue
            if re.search(r'fprintf|printf|push_back|emplace|memcpy|\[', body) and not empty:
                continue
            cls = 'PURE-SPIN'
        line = lineno(pos)
        out.append({'file': os.path.basename(rel), 'rel': rel, 'line': line, 'func': func_at(line), 'cls': cls,
                    'cond': ' '.join(cond.split())[:90]})
    return out


def host_rows():
    files = []
    for d in DIRS:
        for p in sorted(glob.glob(os.path.join(ROOT, d, '**', '*'), recursive=True)):
            if p.endswith(EXT) and '/contrib/' not in p and '.orig' not in p:
                files.append(p)
    files += [os.path.join(ROOT, e) for e in EXTRA]
    rows = []
    for p in files:
        try:
            raw = open(p, encoding='utf-8', errors='replace').read()
        except OSError:
            continue
        rows += scan_text(os.path.relpath(p, ROOT), raw)
    return rows


def guest_rows():
    rows = []
    for p in sorted(glob.glob(os.path.join(RECOMP, 'funcs_*.c'))):
        fn = '?'
        for line in open(p, encoding='utf-8', errors='replace'):
            m = re.match(r'^RECOMP_FUNC\s+\w+\s+(\w+)\(', line)
            if m: fn = m.group(1)
            if 'osYieldThread_recomp(' in line and not line.startswith('RECOMP_FUNC'):
                rows.append({'file': 'guest', 'rel': os.path.basename(p), 'line': 0, 'func': fn, 'cls': 'YIELD', 'cond': 'osYieldThread'})
    return rows


def keyed(rows):
    cnt = defaultdict(int)
    for r in rows:
        k0 = f"{r['file']}|{r['func']}|{r['cls']}"
        cnt[k0] += 1
        r['key'] = f"{k0}|{cnt[k0]}"
    return rows


def controls():
    ok = True
    plant = {
        'PURE-SPIN': 'void A::f() {\n bool w;\n do {\n const std::scoped_lock lock(m);\n w = (a == b);\n } while (w);\n}\n',
        'SLEEP': 'void A::g() {\n while (!flag.load()) {\n std::this_thread::sleep_for(std::chrono::milliseconds(1));\n }\n}\n',
        'YIELD': 'void A::h() {\n uint64_t c = total_vis;\n while (c == total_vis) {\n std::this_thread::yield();\n }\n}\n',
        None: 'void A::k() {\n std::unique_lock<std::mutex> l(m);\n while (!ready) {\n cv.wait(l);\n }\n}\n',
    }
    for want, src in plant.items():
        got = [r['cls'] for r in scan_text('ctl.cpp', src)]
        if (want is None and got) or (want is not None and got != [want]):
            print(f'CONTROL FAIL: planted {want} -> {got}'); ok = False
        else:
            print(f'control ok: planted {want} -> {got}')
    return ok


def runtime(path):
    last = {}
    yields = {}
    t = 0
    for line in open(path, encoding='utf-8', errors='replace'):
        if '[s7381] site=' in line:
            m = dict(re.findall(r'(\w+)=([\w\.]+)', line.split('[s7381]', 1)[1]))
            last[m['site']] = m
            if m['site'] == 'workload_barrier': t += 1
        elif '[s7381] yield ra=' in line:
            m = dict(re.findall(r'(\w+)=([\w\.]+)', line.split('[s7381]', 1)[1]))
            yields.setdefault(m['ra'], []).append((t, int(m['n']), float(m['yield_us'])))
    print(f'dumps={t} (10 s each)')
    for s, m in last.items():
        print(f"  {s:18s} calls={m['calls']} spun={m['spun']} iters={m['iters']} spin_us={m['spin_us']} max_us={m['max_us']}")
    for ra, seq in sorted(yields.items(), key=lambda kv: -kv[1][-1][1]):
        t1, n1, us1 = seq[-1]
        # peak 10 s window rate
        peak = 0; pt = 0
        for (ta, na, _), (tb, nb, _) in zip(seq, seq[1:]):
            r = (nb - na) / max(1, (tb - ta) * 10)
            if r > peak: peak, pt = r, tb
        print(f'  yield ra={ra} n={n1} yield_us={us1:.0f} mean_rate={n1 / max(1, t1 * 10):.0f}/s peak10s={peak:.0f}/s @dump{pt}')
    return last, yields


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--runtime')
    ap.add_argument('--list', action='store_true')
    a = ap.parse_args()
    if a.runtime:
        runtime(a.runtime); return 0
    ok = controls()
    rows = keyed(host_rows()) + keyed(guest_rows())
    if not any(r['func'].endswith('advanceToNextWorkload') for r in rows):
        print('CONTROL FAIL: real site WorkloadQueue::advanceToNextWorkload not listed'); ok = False
    rev = {}
    if os.path.exists(TSV):
        for line in open(TSV):
            if line.startswith('#') or not line.strip(): continue
            k, v, *note = line.rstrip('\n').split('\t')
            rev[k] = (v, note[0] if note else '')
    bad = 0
    by = defaultdict(int)
    for r in rows:
        v = rev.get(r['key'], ('UNREVIEWED', ''))[0]
        by[(r['cls'], v.split()[0])] += 1
        if a.list or v in ('UNREVIEWED', 'BURN'):
            print(f"{r['cls']:9s} {v:10s} {r['rel']}:{r['line']} {r['func']}  ({r['cond']})  key={r['key']}")
        if v in ('UNREVIEWED', 'BURN'): bad += 1
    keys = {r['key'] for r in rows}
    stale = [k for k in rev if k not in keys]
    for k in stale: print(f'STALE review: {k}')
    print(f'rows={len(rows)} host={sum(1 for r in rows if r["file"] != "guest")} guest={sum(1 for r in rows if r["file"] == "guest")}')
    for (c, v), n in sorted(by.items()): print(f'  {c:9s} {v:10s} {n}')
    print(f'unreviewed/burn={bad} stale={len(stale)} controls={"PASS" if ok else "FAIL"}')
    if a.check and (bad or stale or not ok): return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
