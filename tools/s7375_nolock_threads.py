#!/usr/bin/env python3
"""s7375 class AS: thread attribution for the s7366 NOLOCK containers.

s7366 counted 98 host containers that are never touched under a lock and assumed "thread-confined or handed off by
queue" without checking. s7374 found exactly that assumption false once (rs64_s7012_cap: a guest-only helper later given a
gfx-thread caller). This tool gives every accessing function of every NOLOCK container a set of calling threads.

Method (name-based, lower fidelity than TSan, covers every path):
  * function index over the s7366 scope (FUNC regex of s7365; params kept so recompiled-guest signatures are visible);
  * a thread lambda (`std::thread(...[..]{ body })`) is its own root, so a container used inside one is not attributed to
    the function that spawned it;
  * call sites by name (`name(` not preceded by `::~` or a word char), restricted for short/generic names (<=6 chars or
    GENERIC) to callers in the same file or in a file that names the defining file's basename (include/neighbour);
  * BFS up the callers, depth <= DEPTH, until a ROOT (thread entry by (file, name)), a GUEST function (params carry
    `recomp_context`/name ends `_recomp`), or `main`.
Per container: the union of threads over its accessing functions.
  AUTO-CONFINED   exactly one thread label reached, every accessing function resolved
  AUTO-GUEST      only GUEST reached (guest threads run one at a time: ultramodern run-one handoff, s7374)
  REVIEW          two+ labels, or an accessing function with no root within DEPTH -> hand verdict in
                  s7375_nolock_reviewed.tsv: CONFINED / GUEST-SERIAL / HANDOFF / INIT-ONLY / CALLER-LOCKED / NOT-SHARED
                  (a local or per-instance object misread as shared) / FIXED (defect fixed this session).
--selftest: planted one-thread / two-thread / guest / thread-lambda containers must classify exactly, and the s7374
            positive control (a helper called from a guest hook and from gfx_thread_func) must come out REVIEW with
            labels {guest, gfx}.
--check: exit 1 on a REVIEW row with no hand verdict.  -v: print every row.
--lockless: the containers in files with NO lock anywhere (s7366 skipped them as 'nothing can be inconsistent';
            a lock-free file can still be touched from two threads). 144 rows at s7375: class AS2, the next unit."""
import re, sys, os
from collections import defaultdict, Counter, deque
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s7363_hostarr_census as an
import s7365_invalidation_census as ap
import s7366_lockset_census as aq

DEPTH = 6
GENERIC = {'add', 'use', 'get', 'set', 'clear', 'reset', 'evict', 'erase', 'find', 'replace', 'init', 'update', 'run',
           'loop', 'push', 'pop', 'size', 'empty', 'begin', 'end', 'insert', 'remove', 'snap', 'isEmpty', 'record', 'open',
           'close', 'read', 'write', 'start', 'stop', 'apply', 'flush', 'wait', 'notify', 'process', 'submit', 'create'}
# thread entry functions: (file suffix or None, function name) -> label
ROOTS = {
    ('events.cpp', 'gfx_thread_func'): 'gfx', ('events.cpp', 'task_thread_func'): 'task',
    ('events.cpp', 'vi_thread_func'): 'vi', (None, 'main'): 'main',
    ('rt64_workload_queue.cpp', 'renderThreadLoop'): 'rt64_render', ('rt64_workload_queue.cpp', 'idleThreadLoop'): 'rt64_idle',
    ('rt64_present_queue.cpp', 'threadLoop'): 'rt64_present', ('rt64_buffer_uploader.cpp', 'threadLoop'): 'rt64_uploader',
    ('rt64_raster_shader_cache.cpp', 'loop'): 'rt64_shadercomp', ('rt64_texture_cache.cpp', 'loop'): 'rt64_texstream',
    ('rt64_texture_cache.cpp', 'uploadThreadLoop'): 'rt64_texupload',
    ('rt64_raster_shader.cpp', 'threadCreatePipelines'): 'rt64_pipeline',
    ('pi.cpp', 'saving_thread_func'): 'save', ('timer.cpp', 'timer_thread'): 'timer',
    ('threads.cpp', '_thread_func'): 'guest', ('threads.cpp', 'thread_cleaner_func'): 'cleaner',
    ('mods.cpp', 'dirty_mod_configuration_thread_process'): 'modcfg', ('threads.cpp', 'sampler_loop'): 'sampler',
}
THREADLAMBDA = re.compile(r'std::(?:thread|jthread)\s*[({]\s*(?:\[[^\]]*\]\s*(?:\([^)]*\))?\s*(?:mutable\s*)?\{)')

def root_label(path, name):
    for (suf, n), lab in ROOTS.items():
        if n == name and (suf is None or path.endswith(suf)):
            return lab
    return None

class Index:
    def __init__(self, files):
        self.text = {}
        self.funcs = {}          # path -> [(name, s, e, params)]
        self.defs = defaultdict(list)   # name -> [path]
        self.lambdas = {}        # path -> [(s, e, label)]
        for f in files:
            self.add(f, open(f, errors='replace').read())

    def add(self, path, raw):
        t = an.strip_comments(raw)
        self.text[path] = t
        fl = []
        for m in ap.FUNC.finditer(t):
            if m.group(1) in ap.KW or m.group(1) in an.NOTTYPE:
                continue
            b = m.end()
            fl.append((m.group(1), b, an.block_end(t, b), m.group(2)))
            self.defs[m.group(1)].append(path)
        self.funcs[path] = fl
        lam = []
        for m in THREADLAMBDA.finditer(t):
            b = m.end()
            lam.append((b, an.block_end(t, b), 'lambda@%s:%d' % (os.path.basename(path), t.count('\n', 0, m.start()) + 1)))
        self.lambdas[path] = lam

    def enclosing(self, path, pos):
        best = None
        for (n, s, e, p) in self.funcs[path]:
            if s <= pos <= e and (best is None or s > best[1]):
                best = (n, s, e, p)
        return best

    def lambda_at(self, path, pos):
        for s, e, lab in self.lambdas[path]:
            if s <= pos <= e:
                return lab
        return None

    def is_guest(self, path, name):
        for (n, s, e, p) in self.funcs[path]:
            if n == name and ('recomp_context' in p or name.endswith('_recomp')):
                return True
        return name.endswith('_recomp')

    def callers(self, name, defpaths):
        """[(path, caller_name, pos, locked)]"""
        if not hasattr(self, '_cc'):
            self._cc = {}
        if name in self._cc:
            return self._cc[name]
        out = []
        rx = re.compile(r'(?<![\w~])%s\s*\(' % re.escape(name))
        restrict = len(name) <= 6 or name in GENERIC
        bases = {os.path.splitext(os.path.basename(d))[0] for d in defpaths}
        for path, t in self.text.items():
            if restrict and path not in defpaths and not any(b in t for b in bases):
                continue
            for m in rx.finditer(t):
                pre = t[max(0, m.start() - 2):m.start()]
                if pre.endswith('::') and restrict and path not in defpaths:
                    pass
                lab = self.lambda_at(path, m.start())
                f = self.enclosing(path, m.start())
                if f is None:
                    continue
                if f[0] == name and abs(f[1] - m.end()) < 3:
                    continue  # the definition itself
                # a definition (body follows the paren) is not a call
                if f[1] > m.start() and f[1] - m.start() < 400 and f[0] == name:
                    continue
                locked = bool(aq.locks_at(t, f[1], f[2], m.start()))
                out.append((path, lab or f[0], m.start(), locked))
        self._cc[name] = out
        return out

    def threads_of(self, path, fname, lab=None):
        """(set of thread labels, unresolved bool, all_edges_locked bool)"""
        if lab:
            return {lab}, False, False
        seen = set()
        labels, unresolved = set(), False
        alllocked = True
        q = deque([(path, fname, 0, False)])
        while q:
            p, n, d, lk = q.popleft()
            if (p, n) in seen:
                continue
            seen.add((p, n))
            if n.startswith('lambda@'):
                labels.add(n); alllocked &= lk; continue
            r = root_label(p, n)
            if r:
                labels.add(r); alllocked &= lk; continue
            if self.is_guest(p, n):
                labels.add('guest'); alllocked &= lk; continue
            if d >= DEPTH:
                unresolved = True; continue
            cs = self.callers(n, self.defs.get(n, [p]))
            if not cs:
                unresolved = True; continue
            for cp, cn, pos, locked in cs:
                q.append((cp, cn, d + 1, lk or locked))
        return labels, unresolved, alllocked and bool(labels)

def nolock_rows(idx, files, lockless=False):
    rows = []
    for f in files:
        txt = open(f, errors='replace').read()
        mem = aq.declared(an.strip_comments(txt))
        if f.endswith(('.cpp', '.cc', '.mm')):
            for h in (f.rsplit('.', 1)[0] + '.h', f.rsplit('.', 1)[0] + '.hpp'):
                if os.path.exists(h):
                    for k, v in aq.declared(an.strip_comments(open(h, errors='replace').read())).items():
                        mem.setdefault(k, v)
        haslock = bool(re.search(r'\b(?:lock_guard|unique_lock|scoped_lock|shared_lock|\.lock\s*\()', txt))
        if haslock == lockless:
            continue  # default: s7366's file set (files with a lock); --lockless: the files s7366 skipped (next unit)
        rows += aq.scan(f, txt, mem)
    return [x for x in aq.classify(rows) if x[2] == 'NOLOCK']

def attribute(idx, cls):
    out = []
    for path, name, _, _, rs in cls:
        labels, unres, fnrep = set(), False, {}
        for r in rs:
            t = idx.text[path]
            # recover the position of this access line to test thread-lambda membership
            ln = r[1]
            lines = t.split('\n')
            pos = sum(len(l) + 1 for l in lines[:ln - 1]) + max(0, lines[ln - 1].find(name))
            lab = idx.lambda_at(path, pos)
            key = lab or r[3]
            if key in fnrep:
                continue
            L, U, LK = idx.threads_of(path, r[3], lab)
            fnrep[key] = (sorted(L), U, LK)
            labels |= L
            unres |= U
        if unres or len(labels) > 1 or not labels:
            k = 'REVIEW'
        elif labels == {'guest'}:
            k = 'AUTO-GUEST'
        else:
            k = 'AUTO-CONFINED'
        out.append((path, name, k, sorted(labels), unres, fnrep))
    return out

SELFTEST = {
'events.cpp': r'''
void gfx_thread_func(uint8_t* rdram, void* r, void* w) { while (1) { helper_cap(1); gfx_only(); } }
void task_thread_func(uint8_t* rdram, void* r) { task_only(); both_side(); }
''',
'thing.cpp': r'''
#include <mutex>
std::mutex mtx;
static std::vector<int> capVec;
static std::vector<int> gfxVec;
static std::vector<int> twoVec;
static std::vector<int> guestVec;
static std::vector<int> lamVec;
static void helper_cap(int v) { capVec.push_back(v); }
void gfx_only() { gfxVec.push_back(1); twoVec.push_back(1); }
void both_side() { twoVec.clear(); }
void task_only() { std::lock_guard<std::mutex> lk(mtx); }
void osFoo_recomp(uint8_t* rdram, recomp_context* ctx) { helper_cap(2); guestVec.push_back(3); }
void spawner() { std::thread([] { lamVec.push_back(1); }).detach(); }
''',
}
EXPECT = {'capVec': ('REVIEW', ['gfx', 'guest']), 'gfxVec': ('AUTO-CONFINED', ['gfx']),
          'twoVec': ('REVIEW', ['gfx', 'task']), 'guestVec': ('AUTO-GUEST', ['guest']),
          'lamVec': ('AUTO-CONFINED', ['lambda@thing.cpp:14'])}

REVIEWED = {}
_rv = os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7375_nolock_reviewed.tsv')
if os.path.exists(_rv):
    for ln in open(_rv):
        p = ln.rstrip('\n').split('\t')
        if len(p) >= 3 and not ln.startswith('#'):
            REVIEWED[(p[0], p[1])] = p[2]

def main():
    if '--selftest' in sys.argv:
        import tempfile
        d = tempfile.mkdtemp()
        files = []
        for n, body in SELFTEST.items():
            fp = os.path.join(d, n); open(fp, 'w').write(body); files.append(fp)
        idx = Index(files)
        res = {r[1]: (r[2], r[3]) for r in attribute(idx, nolock_rows(idx, files))}
        ok = all(res.get(k) == v for k, v in EXPECT.items())
        print('selftest', 'PASS' if ok else 'FAIL', res)
        sys.exit(0 if ok else 1)
    files = an.scope(True)
    idx = Index(files)
    res = attribute(idx, nolock_rows(idx, files, '--lockless' in sys.argv))
    c = Counter(r[2] for r in res)
    print('NOLOCK containers', len(res), dict(sorted(c.items())))
    vc = Counter()
    bad = 0
    for path, name, k, labels, unres, fnrep in sorted(res):
        v = REVIEWED.get((path, name))
        if v:
            vc[v] += 1
        if k == 'REVIEW' and not v:
            bad += 1
        if (k == 'REVIEW' and not v) or '-v' in sys.argv:
            fns = ';'.join('%s=%s%s' % (f, '|'.join(L), '?' if U else '') for f, (L, U, LK) in sorted(fnrep.items()))
            print('%s\t%s\t%s\t%s\t%s' % (path, name, k, fns[:220], v or ''))
    print('VERDICTS', dict(sorted(vc.items())))
    print('OPEN', bad)
    if '--check' in sys.argv:
        sys.exit(1 if bad else 0)

if __name__ == '__main__':
    main()
