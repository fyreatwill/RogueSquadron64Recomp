#!/usr/bin/env python3
"""s7384 class AZ: census of every NON-atomic mutable static / file-scope variable in host code, attributed to the host
threads that can reach the functions touching it (call-graph reachability from named thread roots).

Scope: src/main, src/rsp, lib/rt64/src/{hle,render}, lib/N64ModernRuntime/{ultramodern,librecomp}/src.
Variables: function-local `static T v` and file/namespace-scope `[static] T v [= ...];` that are not const / constexpr /
std::atomic / thread_local / mutex / condition_variable / once_flag / semaphore types, not function declarations.

Thread roots (all guest OSThreads count as ONE root GUEST: ultramodern runs exactly one guest thread at a time):
  GUEST   functions called from ../N64Recomp/RecompiledFuncs + librecomp *_recomp + the guest-side callbacks
  TASK    task_thread_func (+ get_rsp_microcode, aspMain: audio and other non-GFX LLE tasks)
  GFX     gfx_thread_func + functions called from build/factor5_ucode/*.c (gfx LLE ucode runs inside send_dl)
                  VI  vi_thread_func          MAIN  main / create_gfx / create_window / update_gfx
  RT64R   WorkloadQueue::renderThreadLoop   RT64I idleThreadLoop   PRESENT PresentQueue::threadLoop
  UPLOAD  BufferUploader::threadLoop   SHADER CompilationThread::loop / threadCreatePipelines   TEX StreamThread::loop,
          uploadThreadLoop   TIMER timer_thread   SAVE saving_thread_func   CLEAN thread_cleaner_func
Calls resolve by last name component (same-class method preferred) -> conservative over-attribution.

Per variable, automatic class:
  INIT-ONCE  never written after its initializer (C++ magic statics are thread-safe) -> fine
  UNWRITTEN-UNREACHED / UNROOTED  no root reaches any accessor (dead code, diag lambda threads) -> listed, not gated
  CONFINED   every accessor is reached by exactly one root -> fine (root named)
  LOCKED     every writing function holds a lock_guard / unique_lock / scoped_lock / std::lock -> fine (auto, heuristic)
  MULTI      written, accessors reached by >=2 roots, writers not all locked -> needs a hand verdict
Verdicts (tools/s7384_static_reviewed.tsv, key `file|var`): CONFINED <thread, why the graph over-merged> |
  LOCKED <mutex> | DIAG <env gate; value only printed / rate-limits a log> | BENIGN <idempotent init race, same value
  written by every racer> | INITORDER <written before the reader thread is created> | ARTEFACT <misparse> |
  FIXED <how> | RACE (open defect).
--why <substr>  one shortest call path per root to an accessor (review evidence).
--check   exit 1 on an unreviewed MULTI, a stale verdict, a RACE verdict, or a control failure.
--controls  planted two-root writer -> MULTI; planted locked writer -> LOCKED; planted init-only -> INIT-ONCE (always run).
"""
import argparse, glob, os, re, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRS = ['src/main', 'src/rsp', 'lib/rt64/src/hle', 'lib/rt64/src/render', 'lib/N64ModernRuntime/ultramodern/src',
        'lib/N64ModernRuntime/librecomp/src']
TSV = os.path.join(ROOT, 'tools', 's7384_static_reviewed.tsv')
GEN_GUEST = os.path.join(ROOT, '..', 'N64Recomp', 'RecompiledFuncs')
GEN_TASK = os.path.join(ROOT, 'build', 'factor5_ucode')
EXT = ('.cpp', '.c', '.mm', '.h', '.hpp', '.inl')
KW = {'if', 'for', 'while', 'switch', 'return', 'sizeof', 'catch', 'decltype', 'alignof', 'static_assert', 'defined',
      'static_cast', 'reinterpret_cast', 'const_cast', 'dynamic_cast', 'new', 'delete', 'throw', 'do', 'else',
      'case', 'typeid', 'noexcept', 'alignas', '__attribute__', 'operator'}
# Calls made from inside a thread-spawn lambda run on the spawned thread, not the enclosing function's thread.
# (caller, callee) edges cut from the graph; the callee is seeded on the thread the lambda really runs on.
EDGE_CUTS = {('recomp::start', 'wait_for_game_started'),   # recomp.cpp game_thread lambda -> GUEST (game thread)
             ('recomp::start', 'run_rs64_main'),
             ('main', 'recomp::start_game')}                 # main.cpp gfx_init_callback lambda -> GFX
KNOWN_CLASSES = set()
STL_NAMES = {'resize', 'store', 'load', 'find', 'clear', 'insert', 'erase', 'get', 'set', 'reset', 'push', 'pop',
             'push_back', 'emplace', 'emplace_back', 'begin', 'end', 'data', 'size', 'empty', 'wait', 'notify_one',
             'notify_all', 'lock', 'unlock', 'swap', 'count', 'at', 'front', 'back', 'join', 'detach', 'write', 'read',
             'flush', 'close', 'open', 'start', 'stop', 'update', 'init', 'add', 'remove', 'release', 'acquire',
             'apply', 'copy', 'fill', 'append', 'enqueue', 'dequeue', 'try_dequeue', 'signal', 'exchange', 'contains'}
ROOTS = {
    'GFX': ['gfx_thread_func', 'recomp::start_game'], 'VI': ['vi_thread_func'], 'TASK': ['task_thread_func', 'get_rsp_microcode', 'aspMain'],
    'MAIN': ['main', 'create_gfx', 'create_window', 'update_gfx'],
    'RT64R': ['WorkloadQueue::renderThreadLoop'], 'RT64I': ['WorkloadQueue::idleThreadLoop'],
    'PRESENT': ['PresentQueue::threadLoop'], 'UPLOAD': ['BufferUploader::threadLoop'],
    'SHADER': ['CompilationThread::loop', 'RasterShaderUber::threadCreatePipelines'],
    'TEX': ['StreamThread::loop', 'TextureCache::uploadThreadLoop'], 'TIMER': ['timer_thread'],
    'SAVE': ['saving_thread_func'], 'CLEAN': ['thread_cleaner_func'],
    'GUEST': ['wait_for_game_started', 'queue_samples', 'get_frames_remaining', 'set_frequency', 'poll_input', 'get_n64_input', 'set_rumble',
              'get_connected_device_info'],
}
BAD_TYPES = re.compile(r'\b(const|constexpr|consteval|thread_local|__thread|std::atomic|atomic_\w+|std::mutex|'
                       r'std::recursive_mutex|std::shared_mutex|std::condition_variable\w*|std::once_flag|mutex|'
                       r'LightweightSemaphore|std::atomic_flag|typedef|using|extern|friend|struct|class|enum|union|'
                       r'return|goto|template|operator|namespace)\b')
MUTATORS = ('push_back|emplace_back|emplace|insert|erase|clear|resize|assign|reserve|pop_back|pop_front|push_front|'
            'push|pop|swap|reset|try_emplace|insert_or_assign|append|store|set|fill|merge|extract|shrink_to_fit')
BUFW = re.compile(r'\b(snprintf|sprintf|vsnprintf|memcpy|memset|memmove|strcpy|strncpy|strcat|strncat|fread|fgets|'
                  r'strftime|localtime_r|gmtime_r)\s*\(\s*&?\s*(\w+)')
LOCK_RE = re.compile(r'\b(lock_guard|unique_lock|scoped_lock|std::lock\s*\(|shared_lock|\.lock\s*\(\s*\))')


def strip(text):
    """Remove comments, string and char literals (keep newlines)."""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c == '/' and i + 1 < n and text[i + 1] == '/':
            j = text.find('\n', i)
            i = n if j < 0 else j
        elif c == '/' and i + 1 < n and text[i + 1] == '*':
            j = text.find('*/', i + 2)
            j = n if j < 0 else j + 2
            out.append('\n' * text.count('\n', i, j)); i = j
        elif c == 'R' and text.startswith('R"', i):
            m = re.match(r'R"([^(]*)\(', text[i:])
            if m:
                end = text.find(')' + m.group(1) + '"', i)
                end = n if end < 0 else end + len(m.group(1)) + 2
                out.append('""' + '\n' * text.count('\n', i, end)); i = end
            else:
                out.append(c); i += 1
        elif c in '"\'':
            j = i + 1
            while j < n and text[j] != c:
                if text[j] == '\\': j += 1
                elif text[j] == '\n': break
                j += 1
            out.append(c + c); i = j + 1
        else:
            out.append(c); i += 1
    return ''.join(out)


def files():
    out = []
    for d in DIRS:
        for f in glob.glob(os.path.join(ROOT, d, '**', '*'), recursive=True):
            if f.endswith(EXT) and '/thirdparty/' not in f and '/contrib/' not in f:
                out.append(f)
    return sorted(out)


CALL_RE = re.compile(r'((?:[A-Za-z_]\w*::)*)([A-Za-z_]\w*)\s*(?:<[^<>;(){}]*>)?\s*\(')
HEAD_RE = re.compile(r'((?:[A-Za-z_~]\w*::)*~?[A-Za-z_]\w*)\s*\(')


def parse(rel, raw):
    """-> funcs: list of dict(name, rel, start, end, body, cls); statics: list of dict(var, rel, line, kind, func, decl)."""
    text = strip(raw)
    lines = text.split('\n')
    # line offsets
    offs, o = [], 0
    for L in lines:
        offs.append(o); o += len(L) + 1
    def lineno(pos):
        lo, hi = 0, len(offs) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if offs[mid] <= pos: lo = mid
            else: hi = mid - 1
        return lo + 1
    funcs, stack, stmt_start, cls_names, class_ranges = [], [], 0, [], []
    quals = set()
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c in ';':
            stmt_start = i + 1
        elif c == '{':
            head = text[stmt_start:i]
            in_func = any(k == 'func' for k, _ in stack)
            ns_name = ''
            kind = 'block'
            if in_func:
                kind = 'block'
            elif re.search(r'\bnamespace\b[^()]*$|extern\s*""\s*$', head):
                kind = 'ns'
                mns = re.search(r'\bnamespace\s+([\w:]+)\s*$', head)
                ns_name = mns.group(1) if mns else ('<anon>' if re.search(r'\bnamespace\s*$', head) else '')
            elif re.search(r'\b(class|struct|union|enum)\b[^()]*$', head):
                kind = 'class'
                m = re.search(r'\b(?:class|struct|union)\s+(?:alignas\([^)]*\)\s*)?(?:[A-Za-z_]\w*::)*([A-Za-z_]\w*)', head)
                cls_names.append(m.group(1) if m else '?')
                if m: KNOWN_CLASSES.add(m.group(1))
            elif ')' in head and not re.search(r'=\s*[^=]*$', head.split(')')[0] if '=' in head else ''):
                # function definition head: first ident( in the statement
                hm = None
                for m in HEAD_RE.finditer(head):
                    if m.group(1).split('::')[-1] not in KW:
                        hm = m; break
                if hm and not re.search(r'=\s*\[', head):
                    kind = 'func'
                    name = hm.group(1)
                    if '::' in name: quals.add(name.rsplit('::', 1)[0].split('::')[-1])
                    cur_cls = next((nm[0] for k, nm in reversed(stack) if k == 'class'), None)
                    if '::' not in name and cur_cls:
                        name = cur_cls + '::' + name
                        KNOWN_CLASSES.add(cur_cls)
                    is_static = bool(re.search(r'(?:^|\s)static\s', head)) and not cur_cls and not rel.endswith(('.h', '.hpp', '.inl'))
                    enc_ns = tuple(p for k, nm in stack if k == 'ns' and nm for p in nm.split('::'))
                    if '<anon>' in enc_ns and not rel.endswith(('.h', '.hpp', '.inl')):
                        is_static = True   # anonymous-namespace function: internal linkage
                    stack.append((kind, (name, i, is_static, enc_ns)))
                    i += 1; stmt_start = i
                    continue
            elif re.search(r'=\s*\[[^\]]*\]\s*\([^)]*\)[^=]*$|=\s*\[[^\]]*\]\s*$', head):
                # file-scope lambda: static auto f = [](){...}
                m = re.search(r'([A-Za-z_]\w*)\s*=\s*\[', head)
                if m:
                    stack.append(('func', (m.group(1), i, True))); i += 1; stmt_start = i; continue
            stack.append((kind, (cls_names[-1], i) if kind == 'class' else (ns_name if kind == 'ns' else None)))
            stmt_start = i + 1
        elif c == '}':
            if stack:
                kind, info = stack.pop()
                if kind == 'func' and not any(k == 'func' for k, _ in stack):
                    name, start = info[0], info[1]
                    funcs.append({'name': name, 'rel': rel, 'start': lineno(start), 'end': lineno(i),
                                  'body': text[start:i + 1], 'static': info[2] if len(info) > 2 else False,
                                  'ns': info[3] if len(info) > 3 else ()})
                if kind == 'class' and cls_names:
                    cls_names.pop()
                if kind == 'class':
                    class_ranges.append((info[1], i))
            stmt_start = i + 1
        i += 1
    # statics
    statics = []
    in_class = set()
    for a, b in class_ranges:
        for ln in range(lineno(a) + 1, lineno(b) + 1):
            in_class.add(ln)
    for f in funcs:
        f['classes'] = None
    # compute function membership per line
    owner = {}
    for f in funcs:
        for ln in range(f['start'], f['end'] + 1):
            owner[ln] = f
    decl_re = re.compile(r'^\s*(static\s+)?((?:inline\s+|volatile\s+|unsigned\s+|signed\s+|long\s+)*'
                         r'[A-Za-z_][\w:]*(?:\s*<[^;=(){}]*>)?(?:\s*[\*&]+\s*|\s+)(?:volatile\s+)?)'
                         r'([A-Za-z_]\w*)\s*(\[[^\]]*\])*\s*(=|;|\{|\[)')
    for ln, L in enumerate(lines, 1):
        s = L.strip()
        if not s or s.startswith('#'):
            continue
        f = owner.get(ln)
        local = f is not None and (ln != f['start'] or re.search(r'\{.*\bstatic\s', L) is not None)
        if not local and ln in in_class:
            continue
        if local and not re.search(r'(?:^\s*|[{;]\s*)static\s', L):
            continue
        if local and not re.match(r'^\s*static\s', L):
            L = L[re.search(r'(?:^\s*|[{;]\s*)(static\s)', L).start(1):]
        m = decl_re.match(L)
        if not m:
            continue
        typ = (m.group(1) or '') + m.group(2)
        var = m.group(3)
        if BAD_TYPES.search(typ) or var in KW or m.group(2).strip() in ('return', 'else', 'case', 'goto', 'delete'):
            continue
        if not local:
            # file scope: must be at namespace scope (not inside class); require static or a plain global with init/;
            # exclude member declarations inside classes (heuristic: inside a class body -> indentation inside class)
            if f is not None:
                continue
            if not m.group(1) and not re.match(r'^(?:\s{0,4})[A-Za-z_]', L):
                continue
        # skip functions declared like `static void foo(` -- decl_re requires = ; { [ after the name, so `(` excluded
        if re.match(r'^\s*static\s+[^=;]*\(\s*\*?\s*\w+\s*\)\s*\(', L):
            pass  # function pointer variable: keep
        statics.append({'var': var, 'rel': rel, 'line': ln, 'kind': 'local' if local else 'file',
                        'func': f['name'] if local else None, 'decl': s[:140], 'flocal': f if local else None})
    return funcs, statics


def write_lines(var, body):
    v = re.escape(var)
    pats = [re.compile(r'(?<![\w.>:])' + v + r'\s*(?:\[[^\]]*\]\s*)*(?:\.\w+\s*)*(?:=(?!=)|\+=|-=|\*=|/=|\|=|&=|\^=|<<=|>>=|\+\+|--)'),
            re.compile(r'(?:\+\+|--)\s*' + v + r'\b'),
            re.compile(r'(?<![\w.>:])' + v + r'\s*(?:\[[^\]]*\]\s*)*(?:\.|->)\s*(?:' + MUTATORS + r')\s*\('),
            re.compile(r'&\s*' + v + r'\b(?!\s*[)\],;]?\s*==)'),
            re.compile(r'\bstd::(?:swap|exchange|fill|copy|sort)\s*\(\s*' + v + r'\b')]
    hits = []
    for k, L in enumerate(body.split('\n')):
        if any(p.search(L) for p in pats):
            hits.append(k)
        else:
            for m in BUFW.finditer(L):
                if m.group(2) == var: hits.append(k)
    return hits


def is_method(f):
    if '::' not in f['name']:
        return f.get('inclass', False)
    return f['name'].rsplit('::', 1)[0].split('::')[-1] in KNOWN_CLASSES


def func_ns(f):
    if 'nsfull' not in f:
        parts = f['name'].split('::')[:-1]
        quals = [p for p in parts if p not in KNOWN_CLASSES]
        f['nsfull'] = tuple(f.get('ns', ())) + tuple(quals)
    return f['nsfull']


def build_graph(funcs):
    by_last = defaultdict(list)
    for f in funcs:
        by_last[f['name'].split('::')[-1]].append(f)
    for f in funcs:
        cls = f['name'].rsplit('::', 1)[0] if '::' in f['name'] else None
        callees = set()
        body = f['body']
        for m in CALL_RE.finditer(body):
            last = m.group(2)
            if last in KW or last not in by_last:
                continue
            cands = [c for c in by_last[last] if not c.get('static') or c['rel'] == f['rel']]
            if not cands:
                continue
            q = m.group(1).rstrip(':')
            pre = body[max(0, m.start() - 2):m.start()]
            is_member = pre.endswith('.') or pre.endswith('->')
            if is_member and not q:
                cands = [c for c in cands if is_method(c)]
                same = [c for c in cands if c['rel'] == f['rel']]
                if last in STL_NAMES:
                    # obj.resize( / .store( / .find( is far more often a std:: container / atomic call than the
                    # same-named RT64 method; only same-file methods resolve
                    cands = same
                else:
                    cands = same or cands
            elif not q:
                own = [c for c in cands if cls and c['name'] == cls + '::' + last]
                if own:
                    cands = own
                else:
                    free = [c for c in cands if not is_method(c)]
                    # an unqualified call reaches a namespaced free function only from inside that namespace (or file)
                    fns = func_ns(f)
                    free = [c for c in free if c['rel'] == f['rel'] or fns[:len(func_ns(c))] == func_ns(c)]
                    cands = free or [c for c in cands if is_method(c) and cls]
            if q:
                qq = q.split('::')[-1]
                if qq in ('std', 'moodycamel', 'plume', 'SDL', 'fmt', 'ImGui', 'chrono', 'this_thread', 'filesystem'):
                    continue
                cands = [c for c in cands if c['name'].endswith(qq + '::' + last)]
            for c in cands:
                if c is not f and (f['name'], c['name']) not in EDGE_CUTS: callees.add(id(c))
        f['callees'] = callees
    return by_last


def reach(funcs, by_last, seeds):
    idx = {id(f): f for f in funcs}
    out = {}
    for root, names in seeds.items():
        work = []
        for nm in names:
            last = nm.split('::')[-1]
            for f in by_last.get(last, []):
                if '::' in nm and not f['name'].endswith(nm):
                    continue
                work.append(id(f))
        par = {k: None for k in work}
        q = list(work)
        while q:
            k = q.pop(0)
            for c in idx[k]['callees']:
                if c not in par:
                    par[c] = k; q.append(c)
        PARENTS[root] = (par, idx)
        for k in par:
            out.setdefault(k, set()).add(root)
    return out


PARENTS = {}


def why(acc_funcs, root):
    par, idx = PARENTS.get(root, ({}, {}))
    best = None
    for f in acc_funcs:
        k = id(f)
        if k not in par: continue
        p = []
        while k is not None:
            p.append(idx[k]['name']); k = par[k]
        if best is None or len(p) < len(best): best = p
    return ' <- '.join(best) if best else None


def gen_called(path, names):
    found = set()
    if not os.path.isdir(path):
        return found
    # host calls from generated code pass rdram/ctx first (hooks, *_recomp imports) or carry an rs64 prefix; generic
    # tokens (start, init, free, find, apply) are guest-side C names or casts, not host entries.
    tok = re.compile(r'\b([A-Za-z_]\w*)\s*\(\s*(?:rdram\b|ctx\b|PASS_RDRAM)|\b((?:rs64|g_rs64|rsp_)\w*)\s*\(')
    for fn in glob.glob(os.path.join(path, '*.c')) + glob.glob(os.path.join(path, '*.cpp')):
        with open(fn, errors='replace') as fh:
            for L in fh:
                for m in tok.finditer(L):
                    nm = m.group(1) or m.group(2)
                    if nm in names: found.add(nm)
    return found


def analyse(named, seeds_extra=None, gen=True):
    funcs, statics = [], []
    for rel, raw in named:
        fs, ss = parse(rel, raw)
        funcs += fs; statics += ss
    by_last = build_graph(funcs)
    seeds = {k: list(v) for k, v in ROOTS.items()}
    if gen:
        names = set(by_last)
        g = gen_called(GEN_GUEST, names) - {'main'}
        seeds['GUEST'] += sorted(g)
        seeds['GUEST'] += [nm for nm in names if nm.endswith('_recomp')]
        # build/factor5_ucode/*.c is the F5 GFX ucode: it runs inside send_dl on the Gfx thread
        # (submit_rsp_task routes M_GFXTASK to the gfx action queue, events.cpp:1818), never on the task thread.
        seeds['GFX'] += sorted(gen_called(GEN_TASK, names))
    for k, v in (seeds_extra or {}).items():
        seeds.setdefault(k, []).extend(v)
    roots_of = reach(funcs, by_last, seeds)
    file_funcs = defaultdict(list)
    for f in funcs:
        file_funcs[f['rel']].append(f)
    rows = []
    for s in statics:
        if s['kind'] == 'local':
            acc = [s['flocal']]
        else:
            vr = re.compile(r'(?<![\w.>])' + re.escape(s['var']) + r'\b')
            static_link = s['decl'].startswith('static') or s['rel'].endswith(('.c', '.cpp', '.mm'))
            pool = file_funcs[s['rel']] if static_link else funcs
            acc = [f for f in pool if vr.search(f['body'])]
        writers = []
        for f in acc:
            body = f['body']
            if s['kind'] == 'local':
                # drop the declaration line itself (initializer)
                hits = [h for h in write_lines(s['var'], body) if f['start'] + h != s['line']]
            else:
                hits = write_lines(s['var'], body)
            if hits:
                writers.append((f, hits))
        roots, wroots = set(), set()
        for f in acc:
            roots |= roots_of.get(id(f), set())
        for f, _ in writers:
            wroots |= roots_of.get(id(f), set())
        if not writers:
            cls = 'INIT-ONCE'
        elif not roots:
            cls = 'UNROOTED'
        elif len(roots) == 1:
            cls = 'CONFINED'
        elif all(LOCK_RE.search(f['body']) for f, _ in writers):
            cls = 'LOCKED'
        else:
            cls = 'MULTI'
        rows.append({'key': s['rel'] + '|' + s['var'] + ('@' + s['func'] if s['func'] else ''), 'cls': cls,
                     'roots': sorted(roots), 'wroots': sorted(wroots), 'line': s['line'], 'decl': s['decl'], 'rel': s['rel'],
                     'writers': [f['name'] for f, _ in writers], 'acc': acc})
    return rows, funcs


CTL = [('ctl/a.cpp', '''
static int g_ctl_multi;
static int g_ctl_locked;
static std::mutex m;
int ctl_writer() { g_ctl_multi++; return 0; }
void ctl_locked_writer() { std::lock_guard<std::mutex> lk(m); g_ctl_locked = 3; }
int ctl_once() { static int ctl_init_only = compute(); return ctl_init_only; }
void ctl_root_a() { ctl_writer(); ctl_locked_writer(); ctl_once(); }
void ctl_root_b() { ctl_writer(); ctl_locked_writer(); ctl_once(); }
''')]


def controls():
    rows, _ = analyse(CTL, seeds_extra={'CTL_A': ['ctl_root_a'], 'CTL_B': ['ctl_root_b']}, gen=False)
    got = {r['key'].split('|')[1]: r['cls'] for r in rows}
    want = {'g_ctl_multi': 'MULTI', 'g_ctl_locked': 'LOCKED', 'ctl_init_only@ctl_once': 'INIT-ONCE'}
    ok = all(got.get(k) == v for k, v in want.items())
    print('controls:', 'PASS' if ok else 'FAIL', {k: got.get(k) for k in want})
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--list', default='')
    ap.add_argument('--tsv-out', default='')
    ap.add_argument('--why', default='', help='substring of a key: print one call path per root to an accessor')
    a = ap.parse_args()
    ok = controls()
    named = []
    for f in files():
        with open(f, errors='replace') as fh:
            named.append((os.path.relpath(f, ROOT), fh.read()))
    rows, funcs = analyse(named)
    rev = {}
    if os.path.exists(TSV):
        for L in open(TSV):
            if L.startswith('#') or not L.strip(): continue
            k, v = L.rstrip('\n').split('\t', 1)
            rev[k] = v
    cnt = defaultdict(int)
    for r in rows: cnt[r['cls']] += 1
    rootcnt = defaultdict(int)
    for f in funcs: pass
    print(f'files {len(named)} funcs {len(funcs)} statics {len(rows)}', dict(sorted(cnt.items())))
    multi = [r for r in rows if r['cls'] == 'MULTI']
    unrev = [r for r in multi if r['key'] not in rev]
    keys = {r['key'] for r in multi}
    stale = [k for k in rev if k not in keys]
    races = [k for k, v in rev.items() if v.startswith('RACE')]
    vcnt = defaultdict(int)
    for r in multi:
        if r['key'] in rev: vcnt[rev[r['key']].split()[0]] += 1
    print(f'MULTI {len(multi)}: reviewed {len(multi) - len(unrev)} {dict(vcnt)} unreviewed {len(unrev)} stale {len(stale)} RACE {len(races)}')
    if a.list:
        for r in rows:
            if a.list == 'all' or r['cls'] == a.list:
                print(f"{r['cls']}\t{r['key']}\t{r['line']}\t{','.join(r['roots'])}\tW={','.join(sorted(set(r['writers'])))[:120]}\t{r['decl'][:90]}")
    if a.tsv_out:
        with open(a.tsv_out, 'w') as fh:
            for r in rows:
                fh.write(f"{r['cls']}\t{r['key']}\t{r['line']}\t{','.join(r['roots'])}\t{','.join(r['wroots'])}\t{','.join(sorted(set(r['writers'])))}\t{r['decl']}\n")
    if a.why:
        for r in rows:
            if a.why in r['key']:
                print('WHY', r['cls'], r['key'], r['line'])
                for root in r['roots']:
                    print('   ', root, ':', why(r['acc'], root))
    for k in stale[:20]: print('STALE', k)
    for k in races: print('RACE', k, rev[k])
    if a.check:
        bad = (not ok) or unrev or stale or races
        for r in unrev[:40]: print('UNREVIEWED', r['key'], r['line'], ','.join(r['roots']))
        sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
