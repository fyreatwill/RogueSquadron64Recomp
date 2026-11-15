#!/usr/bin/env python3
"""s7380 class AV: census of every host std::condition_variable wait / notify pair.

Files: the RT64 queue/render sources plus the port's own condvar users (src/main). Condvars are discovered from
`std::condition_variable NAME` declarations in those files and their headers (contrib/ and tools/ excluded).

Per WAIT site: the mutex its unique_lock holds (waiter mutex), predicate present (lambda) or NONE, the state
identifiers the predicate reads.
Per NOTIFY site, automatic class:
  LOCKED    every write in the notifying function (before the notify) to a predicate identifier happens with the
            waiter mutex lexically held (scoped_lock / unique_lock / lock_guard in an open brace scope, explicit
            M.lock()..M.unlock(), or an empty `{ lock(M); }` handshake after the store and before the notify)
  LOST?     a predicate write before the notify with the waiter mutex NOT held and no handshake -> lost-wakeup window
  NOWRITE   no predicate write in the function (state written elsewhere -> hand verdict)
Per thread-loop function: START-RACE when the loop function itself stores `FLAG = true` for the flag its
`while (FLAG)` tests (the owner's destructor can store false before the thread's own store lands -> join hangs).

Hand verdicts: tools/s7380_condvar_reviewed.tsv, key `file|function|cv-or-flag|kind|n` (n = occurrence in function).
Verdicts: LOCKED / HANDOFF <why> / SHUTDOWN <why> / CFG-DEAD <why> / FIXED <how> / LOST (open defect).
--check : exit 1 on an unreviewed site, a stale review, any LOST verdict, an automatic LOST?/START-RACE row whose verdict
          is not SHUTDOWN/CFG-DEAD/FIXED, or a control failure.
--rev R : analyse lib/rt64 at submodule revision R (HEAD = committed upstream state = the pre-fix control).
Controls (always run): planted unlocked write -> LOST?; planted locked write -> LOCKED; planted handshake -> LOCKED;
planted self-store loop -> START-RACE; real site PresentQueue::skipInterpolation must be LOCKED.
"""
import argparse, os, re, subprocess, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUB = os.path.join(ROOT, 'lib', 'rt64')
FILES = [('rt64', 'src/hle/rt64_workload_queue.cpp'), ('rt64', 'src/hle/rt64_present_queue.cpp'),
         ('rt64', 'src/render/rt64_raster_shader.cpp'), ('rt64', 'src/render/rt64_buffer_uploader.cpp'),
         ('rt64', 'src/render/rt64_raster_shader_cache.cpp'), ('rt64', 'src/render/rt64_texture_cache.cpp'),
         ('main', 'src/main/rt64_render_context.cpp'), ('main', 'src/main/main.cpp')]
HEADERS = [('rt64', 'src/hle/rt64_workload_queue.h'), ('rt64', 'src/hle/rt64_present_queue.h'),
           ('rt64', 'src/hle/rt64_shared_queue_resources.h'), ('rt64', 'src/render/rt64_raster_shader.h'),
           ('rt64', 'src/render/rt64_buffer_uploader.h'), ('rt64', 'src/render/rt64_raster_shader_cache.h'),
           ('rt64', 'src/render/rt64_texture_cache.h')]
TSV = os.path.join(ROOT, 'tools', 's7380_condvar_reviewed.tsv')
KW = set('return true false const auto this if else for while int bool uint32_t uint64_t size_t'.split())
FUNC_RE = re.compile(r'^\s*(?:[\w:<>,\*&~]+\s+)*?([\w:~]+)\s*\([^;{}]*\)\s*(?:const\s*)?(?:override\s*)?\{\s*$')
CTRL = {'if', 'for', 'while', 'switch', 'catch', 'return', 'else'}
LOCK_RE = re.compile(r'(?:scoped_lock|unique_lock|lock_guard)\s*(?:<[^>]*>)?\s*\w*\s*[\({]\s*([\w\.\->]+)\s*[,\)}]')


def load(kind, rel, rev):
    if kind == 'rt64' and rev:
        return subprocess.run(['git', '-C', SUB, 'show', f'{rev}:{rel}'], capture_output=True, text=True, check=True).stdout
    base = SUB if kind == 'rt64' else ROOT
    with open(os.path.join(base, rel), encoding='utf-8', errors='replace') as f:
        return f.read()


def strip(line):
    line = re.sub(r'"(?:\\.|[^"\\])*"', '""', line)
    return line.split('//')[0]


def short(expr):
    return re.split(r'\.|->', expr)[-1]


def analyse(fname, text, cvs):
    """Return (waits, notifies, starts) for one file."""
    lines = [strip(l) for l in text.split('\n')]
    depth = 0
    func, fdepth = '?', None
    locks = []          # (mutex, depth) scoped
    explicit = set()    # mutexes locked with .lock()
    writes = []         # (lineno, ident, held:set, func)
    handshakes = []     # (lineno, mutex, func)
    waits, notifies, starts = [], [], []
    occ = defaultdict(int)
    loopflags = {}      # func -> flag tested by while(FLAG)
    selfstores = defaultdict(list)
    self_locals = defaultdict(set)
    for i, l in enumerate(lines, 1):
        m = FUNC_RE.match(l)
        if m and m.group(1).split('::')[-1] not in CTRL and not re.match(r'\s*(?:if|for|while|switch|else)\b', l):
            func, fdepth = m.group(1).split('::')[-1] if '::' not in m.group(1) else '::'.join(m.group(1).split('::')[-2:]), depth
            locks = [(mx, d) for mx, d in locks if d <= depth]
            explicit = set()
            writes = [w for w in writes if False]
            handshakes = []
        held = {mx for mx, _ in locks} | explicit
        for mm in LOCK_RE.finditer(l):
            mx = short(mm.group(1))
            # empty handshake scope `{ lock(M); }` on one line
            if re.search(r'\{\s*[^{}]*' + re.escape(mm.group(0)) + r'[^{}]*;\s*\}', l) and not re.search(r'=|\.push|emplace', l.split(mm.group(0))[1]):
                handshakes.append((i, mx, func))
            locks.append((mx, depth + l[:mm.start()].count('{') - l[:mm.start()].count('}')))
        for mm in re.finditer(r'([\w\.\->]+)\.(lock|unlock|try_lock)\(\)', l):
            mx = short(mm.group(1))
            if mm.group(2) == 'unlock':
                explicit.discard(mx)
            elif mm.group(2) == 'lock':
                explicit.add(mx)
        held = {mx for mx, _ in locks} | explicit
        # writes: IDENT = / ++ / -- / += / container mutators
        for mm in re.finditer(r'\b(\w+)\s*(?:=(?!=)|\+\+|--|\+=|-=|\^=)|(?:\+\+|--)\s*(\w+)\b|\b(\w+)\s*\.\s*(?:push|push_back|emplace|emplace_back|pop|pop_front|pop_back|clear|insert)\s*\(', l):
            ident = mm.group(1) or mm.group(2) or mm.group(3)
            if ident and ident not in KW:
                writes.append((i, ident, set(held), func))
        for mm in re.finditer(r'(?:\b(?:int|int32_t|uint32_t|uint64_t|int64_t|size_t|bool|auto|double|float)\b|&)\s*(\w+)\s*(?:=|;|\{)', l):
            self_locals[func].add(mm.group(1))
        wm = re.search(r'(\w+)\.wait(?:_for|_until)?\(\s*(\w+)\s*(,?)', l)
        if wm and wm.group(1) in cvs:
            cv, lk = wm.group(1), wm.group(2)
            wmx = '?'
            for j in range(i, max(0, i - 40), -1):
                mm = re.search(r'unique_lock\s*(?:<[^>]*>)?\s*' + re.escape(lk) + r'\s*\(\s*([\w\.\->]+)', lines[j - 1])
                if mm:
                    wmx = short(mm.group(1))
                    break
            # predicate text: from the wait to the closing `});`
            pred = ''
            if wm.group(3):
                k = i
                while k <= len(lines):
                    pred += lines[k - 1] + '\n'
                    if '});' in lines[k - 1] or (k > i and ');' in lines[k - 1]):
                        break
                    k += 1
                pred = pred[pred.index(wm.group(0)):] if wm.group(0) in pred else pred
                pred = pred.split('{', 1)[1] if '{' in pred else pred
                pred = pred.split('}', 1)[0]
            pred = re.sub(r'(\w+)\s*(?:\.|->)\s*\w+\s*\(', r'\1 ', pred)  # container.method( -> container
            pred = re.sub(r'\b\w+\s*(?:\.|->)\s*(?=\w)', '', pred)  # obj.field / obj->field -> field
            pred = re.sub(r'\b\w+\s*\(', '(', pred)                     # drop called method names
            ids = sorted({t for t in re.findall(r'\b([A-Za-z_]\w*)\b', pred) if t not in KW and not t[0].isupper()})
            occ[(func, cv, 'wait')] += 1
            waits.append(dict(file=fname, line=i, func=func, cv=cv, mutex=wmx, pred='lambda' if wm.group(3) else 'NONE', ids=ids,
                              n=occ[(func, cv, 'wait')]))
        nm = re.search(r'(\w+)\.notify_(one|all)\(\)', l)
        if nm and nm.group(1) in cvs:
            occ[(func, nm.group(1), 'notify')] += 1
            notifies.append(dict(file=fname, line=i, func=func, cv=nm.group(1), kind=nm.group(2), n=occ[(func, nm.group(1), 'notify')],
                                 writes=list(writes), hs=list(handshakes), locals=set(self_locals[func])))
        lm = re.search(r'while\s*\(\s*(\w*[Rr]unning)\s*\)', l)
        if lm:
            loopflags[func] = lm.group(1)
        sm = re.search(r'\b(\w*[Rr]unning)\s*=\s*true\b', l)
        if sm:
            selfstores[func].append((i, sm.group(1)))
        depth += l.count('{') - l.count('}')
        locks = [(mx, d) for mx, d in locks if d <= depth]
    for f, flag in loopflags.items():
        for ln, fl in selfstores.get(f, []):
            if fl == flag:
                starts.append(dict(file=fname, line=ln, func=f, cv=flag, kind='start', n=1))
    return waits, notifies, starts


def classify(notifies, waits):
    wmap = defaultdict(list)
    for w in waits:
        wmap[w['cv']].append(w)
    out = []
    for nt in notifies:
        ws = wmap.get(nt['cv'], [])
        ids = set().union(*[set(w['ids']) for w in ws]) if ws else set()
        ids -= nt.get('locals', set())
        mxs = {w['mutex'] for w in ws}
        rel = [(ln, ident, held) for ln, ident, held, f in nt['writes'] if ident in ids and f == nt['func'] and ln <= nt['line']]
        if not rel:
            cls = 'NOWRITE'
        else:
            bad = []
            for ln, ident, held in rel:
                if held & mxs:
                    continue
                if any(hl > ln and hm in mxs and hf == nt['func'] for hl, hm, hf in nt['hs']):
                    continue
                bad.append(f'{ident}@{ln}')
            cls = 'LOST?' if bad else 'LOCKED'
            nt['bad'] = bad
        nt['cls'] = cls
        nt['mx'] = ','.join(sorted(mxs)) or '?'
        out.append(nt)
    return out


def discover_cvs(texts):
    cvs = set()
    for t in texts:
        for m in re.finditer(r'condition_variable(?:_any)?\s+([\w\s,]+);', t):
            for n in m.group(1).split(','):
                cvs.add(n.strip())
    return cvs


def run_controls():
    ok = True
    planted = {
        'unlocked': ('struct S { std::condition_variable c; };\n    void Q::stop() {\n        flagRunning = false;\n        c.notify_all();\n    }\n'
                     '    void Q::loop() {\n        std::unique_lock<std::mutex> lk(mtx);\n        c.wait(lk, [&]() { return !flagRunning; });\n    }\n', 'LOST?'),
        'locked': ('struct S { std::condition_variable c; };\n    void Q::stop() {\n        {\n            std::scoped_lock l(mtx);\n            flagRunning = false;\n        }\n        c.notify_all();\n    }\n'
                   '    void Q::loop() {\n        std::unique_lock<std::mutex> lk(mtx);\n        c.wait(lk, [&]() { return !flagRunning; });\n    }\n', 'LOCKED'),
        'handshake': ('struct S { std::condition_variable c; };\n    void Q::stop() {\n        flagRunning = false;\n        { std::scoped_lock l(mtx); }\n        c.notify_all();\n    }\n'
                      '    void Q::loop() {\n        std::unique_lock<std::mutex> lk(mtx);\n        c.wait(lk, [&]() { return !flagRunning; });\n    }\n', 'LOCKED'),
    }
    for name, (txt, want) in planted.items():
        w, n, s = analyse('ctl', txt, {'c'})
        got = [x['cls'] for x in classify(n, w)]
        if got != [want]:
            print(f'CONTROL FAIL {name}: got {got} want [{want}]')
            ok = False
    txt = '    void T::loop() {\n        flagRunning = true;\n        while (flagRunning) {\n        }\n    }\n'
    if len(analyse('ctl', txt, set())[2]) != 1:
        print('CONTROL FAIL start-race not detected')
        ok = False
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--rev', default=None)
    a = ap.parse_args()
    texts = {}
    for kind, rel in FILES + HEADERS:
        try:
            texts[(kind, rel)] = load(kind, rel, a.rev)
        except Exception as e:  # noqa
            print(f'missing {rel}: {e}')
    cvs = discover_cvs(texts.values()) | {'cv', 'cv_job', 'cv_idle'}
    rows = []
    allw = []
    for kind, rel in FILES:
        if (kind, rel) not in texts:
            continue
        w, n, s = analyse(os.path.basename(rel), texts[(kind, rel)], cvs)
        allw += w
        rows.append((w, n, s))
    rev = {}
    if os.path.exists(TSV):
        for line in open(TSV):
            if line.strip() and not line.startswith('#'):
                p = line.rstrip('\n').split('\t')
                rev[p[0]] = (p[1], p[2] if len(p) > 2 else '')
    seen, fails = set(), []
    cnt = defaultdict(int)
    print(f'condvars: {len(cvs)}  ({" ".join(sorted(cvs))})')
    for w, n, s in rows:
        for x in w:
            key = f"{x['file']}|{x['func']}|{x['cv']}|wait|{x['n']}"
            seen.add(key)
            v = rev.get(key, ('UNREVIEWED', ''))[0]
            cnt['wait:' + x['pred']] += 1
            print(f"WAIT   {x['file']}:{x['line']} {x['func']} {x['cv']} mutex={x['mutex']} pred={x['pred']} ids={','.join(x['ids'])} -> {v}")
            if v == 'UNREVIEWED' or x['pred'] == 'NONE' and not v.startswith(('HANDOFF', 'FIXED')):
                fails.append(key)
        for x in classify(n, allw):
            key = f"{x['file']}|{x['func']}|{x['cv']}|notify|{x['n']}"
            seen.add(key)
            v = rev.get(key, ('UNREVIEWED', ''))[0]
            cnt['notify:' + x['cls']] += 1
            print(f"NOTIFY {x['file']}:{x['line']} {x['func']} {x['cv']}.{x['kind']} waiter={x['mx']} auto={x['cls']} {' '.join(x.get('bad', []))} -> {v}")
            if v == 'UNREVIEWED' or v.startswith('LOST') or (x['cls'] == 'LOST?' and not v.startswith(('SHUTDOWN', 'CFG-DEAD', 'FIXED'))):
                fails.append(key)
        for x in s:
            key = f"{x['file']}|{x['func']}|{x['cv']}|start|1"
            seen.add(key)
            v = rev.get(key, ('UNREVIEWED', ''))[0]
            cnt['start-race'] += 1
            print(f"START  {x['file']}:{x['line']} {x['func']} {x['cv']}=true inside its own loop auto=START-RACE -> {v}")
            if not v.startswith(('SHUTDOWN', 'CFG-DEAD', 'FIXED')):
                fails.append(key)
    stale = sorted(k for k in rev if k not in seen and not (k.endswith('|start|1') and rev[k][0] == 'FIXED'))  # a fixed start race leaves no row
    print('summary:', ' '.join(f'{k}={v}' for k, v in sorted(cnt.items())))
    ctl = run_controls()
    print('controls:', 'PASS' if ctl else 'FAIL')
    # real-site control: skipInterpolation's notify must be LOCKED
    real = [x for w, n, s in rows for x in classify(n, allw) if x['func'].endswith('skipInterpolation')]
    if not real or real[0]['cls'] != 'LOCKED':
        print('CONTROL FAIL real skipInterpolation not LOCKED:', [x['cls'] for x in real])
        ctl = False
    for k in stale:
        print('STALE review', k)
    for k in fails:
        print('FAIL', k)
    if a.check and (fails or stale or not ctl):
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
