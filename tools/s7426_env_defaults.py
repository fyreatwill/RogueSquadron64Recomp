#!/usr/bin/env python3
"""s7426 class CI: env-default drift audit (offline).

Question: does every ROGUESQ_* runtime default compiled into build/ match what the owner docs say, and is each
documented variable parsed the same way everywhere it is read?

Checks
  A ORDER   main() applies policy defaults with setenv() (dd bundle, aspect, OSMEM ...). A reader whose value is
            latched by a FILE-SCOPE static initializer runs before main(), so it never sees that policy.
  B DOC     docs/OWNER-OPT-INS.md claims per variable: "ON" (`X=0` turns it off / restores) => unset must behave
            like a set non-zero value and differently from "0"; "opt-in" (`X=V`, V != 0) => unset must differ from V.
            Each read site is evaluated by compiling its lambda (fake getenv, values unset/""/"0"/"1"/"tog") or, for
            statement forms, by a regex classifier; unclassifiable documented sites need a row in
            tools/s7426_env_accept.tsv.
  C PRESENCE `getenv("X") ? a : b`, `if (getenv("X"))`, `!getenv("X")` on a documented variable: "X=0" then means ON.
  D SPLIT   two sites of one documented variable disagree on unset/"0"/"1" truthiness.

Exit: 0 consistent, 1 drift, 3 control failed.   --control plants a flipped default, a presence test and a file-scope
policy reader and requires all three to be flagged.
"""
import json, os, re, subprocess, sys, tempfile, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
G = re.compile(r'(?:std::)?getenv\(\s*"((?:ROGUESQ|RS64)_[A-Z0-9_]+)"\s*\)')
HELPER = re.compile(r'\b(env_flag|rs6031_env|envd|s7397_env|s7396_env|s6919_mode|rs64_s7355_env_is|ev)\(\s*"((?:ROGUESQ|RS64)_[A-Z0-9_]+)"\s*(?:,\s*([^)]*))?\)')
VALS = [None, "", "0", "1", "tog"]
ACCEPT = 'tools/s7426_env_accept.tsv'


def sources():
    d = json.load(open('build/compile_commands.json'))
    fs = sorted({x['file'] for x in d if x['file'].endswith(('.c', '.cpp', '.cc', '.mm', '.m'))})
    for root in ['src', 'include', 'lib/N64ModernRuntime/librecomp', 'lib/N64ModernRuntime/ultramodern', 'lib/rt64/src/hle',
                 'lib/rt64/src/render', 'lib/rt64/src/gbi', 'lib/rt64/src/common', 'lib/rt64/src/gui', 'lib/rt64/src/preset']:
        for dp, _, names in os.walk(root):
            fs += [os.path.join(dp, n) for n in names if n.endswith(('.h', '.hpp', '.inl'))]
    return fs


def strip(t):
    """Blank comments and string/char literal contents (keep length) so brace depth is reliable."""
    out = list(t); i = 0; n = len(t)
    while i < n:
        c = t[i]
        if t.startswith('//', i):
            j = t.find('\n', i); j = n if j < 0 else j
            for k in range(i, j): out[k] = ' '
            i = j
        elif t.startswith('/*', i):
            j = t.find('*/', i + 2); j = n if j < 0 else j + 2
            for k in range(i, j):
                if out[k] != '\n': out[k] = ' '
            i = j
        elif c in '"\'':
            j = i + 1
            while j < n and t[j] != c:
                j += 2 if t[j] == '\\' else 1
            for k in range(i + 1, min(j, n)): out[k] = ' '
            i = j + 1
        else:
            i += 1
    return ''.join(out)


def scope_map(t, s):
    """For each offset, True when inside a function/lambda body (brace depth > 0 excluding namespace/extern C/class)."""
    depth_fn = 0; stack = []; marks = []
    nonfn = re.compile(r'(namespace\s*\w*|extern\s+"C"|\b(?:struct|class|union|enum)\b[^;{}()]*)\s*$')
    for m in re.finditer(r'[{}]', s):
        if m.group() == '{':
            pre = s[max(0, m.start() - 120):m.start()]
            # extern "C" has its literal blanked: check raw text too
            raw = t[max(0, m.start() - 120):m.start()]
            isnon = bool(nonfn.search(pre)) or bool(re.search(r'extern\s+"C"\s*$', raw))
            # aggregate initializers at file scope ("= {") are data, not code
            if re.search(r'=\s*$', pre) and depth_fn == 0: isnon = True
            stack.append(isnon)
            if not isnon: depth_fn += 1
        else:
            if stack:
                if not stack.pop(): depth_fn -= 1
        marks.append((m.start(), depth_fn))
    return marks


def depth_at(marks, off):
    lo, hi, d = 0, len(marks) - 1, 0
    while lo <= hi:
        mid = (lo + hi) // 2
        if marks[mid][0] < off: d = marks[mid][1]; lo = mid + 1
        else: hi = mid - 1
    return d


def lambda_at(t, s, off):
    """Return the lambda text `[..](..){..}` whose body contains offset, if one starts on the same statement."""
    ls = s.rfind('\n', 0, off) + 1
    seg = s[max(0, ls - 400):off]
    best = None
    for m in re.finditer(r'\[[^\]\[]*\]\s*(\([^()]*\))?\s*(?:mutable\s*)?(?:->\s*[\w:]+\s*)?\{', seg):
        best = m
    if not best: return None
    start = max(0, ls - 400) + best.start(); b = max(0, ls - 400) + best.end() - 1
    depth = 0
    for i in range(b, min(len(s), b + 4000)):
        if s[i] == '{': depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0:
                if i < off: return None
                if best.group(1) and best.group(1).strip('() '): return None   # takes parameters
                return (t[start:i + 1], start)
    return None


def collect(files, extra=None):
    sites = []
    items = [(f, None) for f in files] + list(extra or [])
    for f, text in items:
        try: t = text if text is not None else open(f, errors='replace').read()
        except OSError: continue
        if 'ROGUESQ_' not in t and 'RS64_' not in t: continue
        s = strip(t); marks = scope_map(t, s)
        for m in list(G.finditer(t)) + list(HELPER.finditer(t)):
            var = m.group(1) if m.re is G else m.group(2)
            if s[m.start()] == ' ': continue      # inside comment / string
            ln = t.count('\n', 0, m.start()) + 1
            ls = t.rfind('\n', 0, m.start()) + 1; le = t.find('\n', m.end())
            le = len(t) if le < 0 else le
            la = lambda_at(t, s, m.start()) if m.re is G else None
            fsc = depth_at(marks, la[1] if la else m.start()) == 0
            sites.append(dict(var=var, file=f, line=ln, off=m.start(), end=m.end(), text=t[ls:le], tail=t[m.start():le], pre=t[ls:m.start()],
                              before=t[max(0, m.start() - 6):m.start()], filescope=fsc,
                              lam=la[0] if la else None,
                              helper=None if m.re is G else (m.group(1), m.group(3))))
    return sites


def policy_vars(files):
    """setenv targets inside main.cpp main()-reachable code, with the setenv line."""
    pv = {}
    for f in files:
        if not f.endswith('src/main/main.cpp'): continue
        t = open(f, errors='replace').read()
        for m in re.finditer(r'\bsetenv\(\s*"((?:ROGUESQ|RS64)_[A-Z0-9_]+)"', t):
            pv.setdefault(m.group(1), t.count('\n', 0, m.start()) + 1)
        for m in re.finditer(r'for\s*\(\s*const\s+char\s*\*\s*(\w+)\s*:\s*\{([^}]*)\}\s*\)\s*setenv\(\s*\1\b', t):
            for n in re.findall(r'"((?:ROGUESQ|RS64)_[A-Z0-9_]+)"', m.group(2)):
                pv.setdefault(n, t.count('\n', 0, m.start()) + 1)
    return pv


def eval_lambdas(sites):
    """Compile each distinct lambda with a fake getenv; return {lambda_text: {val: result_str}} for those that compile."""
    lams = sorted({x['lam'] for x in sites if x['lam']})
    hdr = ('#include <cstdlib>\n#include <cstring>\n#include <cstdio>\n#include <cmath>\n#include <cstdint>\n#include <string>\n'
           'static const char* g_name; static const char* g_val;\n'
           'static char* fake_getenv(const char* n){ return (g_val && !strcmp(n,g_name)) ? (char*)g_val : nullptr; }\n'
           '#include <type_traits>\n'
           'template<class F> static double run(F L){ using R = decltype(L()); if constexpr (std::is_arithmetic_v<R>) return (double)L(); else return -999.0; }\n')
    def body(i, L):
        L2 = re.sub(r'(?:std::|::)?\bgetenv\b', 'fake_getenv', L)
        return f'static double f{i}(){{ auto L = {L2}; return run(L); }}\n'
    alive = set(range(len(lams)))
    td = tempfile.mkdtemp(prefix='s7426_')
    src = os.path.join(td, 'ev.cpp'); exe = os.path.join(td, 'ev')
    for _ in range(6):
        code = hdr; lineof = {}
        for i in sorted(alive):
            lineof[i] = code.count('\n') + 1
            code += body(i, lams[i])
        open(src, 'w').write(code)
        r = subprocess.run(['clang++', '-std=c++17', '-w', '-ferror-limit=0', '-fsyntax-only', src], capture_output=True, text=True)
        bad = set()
        for m in re.finditer(r'ev\.cpp:(\d+):\d+: error', r.stderr):
            ln = int(m.group(1))
            cand = [i for i in alive if lineof[i] <= ln]
            if cand: bad.add(max(cand, key=lambda i: lineof[i]))
        if not bad: break
        alive -= bad
    names = sorted({v for x in sites if x['lam'] for v in [x['var']]})
    code += '#include <map>\nint main(){\n const char* vals[] = {nullptr, "", "0", "1", "tog"};\n'
    code += ' struct E{int i; const char* n;};\n'
    pairs = []
    for i in sorted(alive):
        for v in sorted(set(G.findall(lams[i]))):
            pairs.append((i, v))
    code += ' E es[] = {' + ','.join(f'{{{i},"{v}"}}' for i, v in pairs) + '};\n'
    code += ' double (*fs[])() = {' + ','.join(f'f{i}' if i in alive else 'nullptr' for i in range(len(lams))) + '};\n'
    code += ' for (auto& e : es) { printf("%d %s", e.i, e.n); for (auto v : vals) { g_name = e.n; g_val = v; printf(" %.17g", fs[e.i]()); } printf("\\n"); }\n}\n'
    open(src, 'w').write(code)
    res = {}
    r = subprocess.run(['clang++', '-std=c++17', '-w', '-O0', src, '-o', exe], capture_output=True, text=True)
    if r.returncode != 0:
        return res, len(lams), 0
    out = subprocess.run([exe], capture_output=True, text=True, timeout=60, cwd=td).stdout
    for ln in out.splitlines():
        p = ln.split()
        tup = tuple(float(x) for x in p[2:])
        if -999.0 not in tup: res[(lams[int(p[0])], p[1])] = tup
    return res, len(lams), len(alive)


def regex_class(x):
    """Statement-form classifier -> tuple over VALS or None. Uses the variable the getenv result is bound to."""
    tail = x['tail']; v = None
    m = re.match(r'(?:std::)?getenv\("[A-Z0-9_]+"\)', tail)
    pre = x['pre']
    bm = re.search(r'(?:const\s+)?char\s*\*\s*(\w+)\s*=\s*$', pre) or re.search(r'\b(\w+)\s*=\s*$', pre)
    rest = tail[m.end():] if m else tail
    if bm: v = bm.group(1)
    if not v:
        if re.match(r'\s*\)?\s*\?', rest) or re.search(r'(if\s*\(|!)\s*$', pre): return 'PRESENCE'
        return None
    V = re.escape(v); P = rf'(?:\*{V}|{V}\[0\])'
    r = rest[:260]
    T = lambda u, e, z, o, g: (u, e, z, o, g)
    pats = [
        (rf'!\s*\(\s*{V}\s*&&\s*{P}\s*==\s*\'0\'\s*\)', T(1, 1, 0, 1, 1)),
        (rf'\(\s*{V}\s*&&\s*{P}\s*==\s*\'0\'\s*\)\s*\?\s*0', T(1, 1, 0, 1, 1)),
        (rf'{V}\s*&&\s*{P}\s*&&\s*{P}\s*!=\s*\'0\'', T(0, 0, 0, 1, 1)),
        (rf'{V}\s*&&\s*{P}\s*==\s*\'1\'', T(0, 0, 0, 1, 0)),
        (rf'{V}\s*&&\s*{P}\s*&&\s*(?:std::)?atoi\({V}\)\s*==\s*0\s*\)\s*return', T(1, 1, 0, 1, 1)),
        (rf'!\s*{V}\s*\|\|\s*!\s*{P}\s*\|\|\s*{P}\s*==\s*\'0\'\s*\?\s*0', T(0, 0, 0, 1, 1)),
        (rf'md\s*=\s*1;\s*if\s*\(\s*{V}\s*&&\s*\*{V}\s*\)\s*md\s*=.*atoi\({V}\)\s*!=\s*0', T(1, 1, 0, 1, 2)),
        (rf'=\s*{V}\s*\?\s*(?:std::)?atoi\({V}\)\s*:\s*([1-9])', T(1, 0, 0, 1, 0)),
        (rf'=\s*{V}\s*\?\s*(?:std::)?atoi\({V}\)\s*:\s*0', T(0, 0, 0, 1, 0)),
        (rf'\(\s*{V}\s*&&\s*\*{V}\s*\)\s*\?\s*\(?\w*\)?\s*(?:std::)?ato[fi]\({V}\)\s*:\s*\(?[\w ]*\)?\s*[1-9]', T(1, 1, 0, 1, 0)),
        (rf'\(\s*{V}\s*&&\s*\*{V}\s*\)\s*\?\s*\(?\w*\)?\s*(?:std::)?ato[fi]\({V}\)\s*:\s*0', T(0, 0, 0, 1, 0)),
        (rf'{V}\s*&&\s*\*{V}\s*&&\s*{V}\[0\]\s*!=\s*\'0\'', T(0, 0, 0, 1, 1)),
    ]
    for p, tup in pats:
        if re.search(p, r): return tup
    if re.match(rf'\s*;?\s*\)?\s*\{{?', rest) and re.search(r'if\s*\(\s*(?:const\s+)?char\s*\*\s*\w+\s*=\s*$', pre):
        return None   # if (const char* v = getenv(..)) { ... } : value test lives in the body
    return None


def truth(tup):
    return tuple(1 if (isinstance(a, (int, float)) and a != 0) else 0 for a in tup)


def doc_claims(path='docs/OWNER-OPT-INS.md'):
    t = open(path).read()
    units = [u for u in re.split(r'\n(?=\|)|\n\n', t) if 'ROGUESQ_' in u]
    on = re.compile(r'turns? (?:it|them)? ?(?:back )?off|restores?|brings? it back|shows? them|= ?old|old (?:look|path|size|shape|fixed)|back off', re.I)
    cl = collections.defaultdict(set)
    for u in units:
        for m in re.finditer(r'`([^`]*)`', u):
            for a in re.finditer(r'(?<![A-Z_])(ROGUESQ_[A-Z0-9_]+)=([^\s`]+)', m.group(1)):
                v, val = a.group(1), a.group(2)
                ctx = u[m.end():m.end() + 60]
                if val == '0' and on.search(ctx): cl[v].add('ON')
                elif val == '0': cl[v].add('ZERO')
                else: cl[v].add('SET:' + val)
    return cl


def load_accept():
    acc = {}
    if os.path.exists(ACCEPT):
        for ln in open(ACCEPT):
            if ln.startswith('#') or not ln.strip(): continue
            p = ln.rstrip('\n').split('\t')
            acc.setdefault((p[0], p[1]), []).append(p[2:])
    return acc


def acc_row(acc, x):
    for row in acc.get((os.path.basename(x['file']), x['var']), []):
        if len(row) > 1 and row[1] and row[1] in x['text']: return row
    return None


def audit(files, extra=None, quiet=False):
    sites = collect(files, extra)
    pv = policy_vars(files)
    cl = doc_claims()
    ev, nl, nc = eval_lambdas(sites)
    acc = load_accept()
    flags = []
    per = collections.defaultdict(list)
    for x in sites:
        key = (os.path.basename(x['file']), x['var'])
        sem = None; how = None
        if x['lam'] and (x['lam'], x['var']) in ev:
            sem = truth(ev[(x['lam'], x['var'])]); how = 'compiled'
        elif x['helper']:
            name, dflt = x['helper']
            how = f'helper {name}'
        else:
            r = regex_class(x)
            if r == 'PRESENCE': how = 'presence'; sem = (0, 1, 1, 1, 1)
            elif r: sem = r; how = 'regex'
        a = acc_row(acc, x); x['acc'] = a
        if a and sem is None:
            how = 'accept'; sem = tuple(int(c) for c in a[0]) if a[0] != '-' else None
            if sem is None: how = 'accept-na'
        x['sem'] = sem; x['how'] = how
        per[x['var']].append(x)
        # A: file-scope static reading a policy var (before main's setenv)
        if x['var'] in pv and x['filescope'] and not a:
            flags.append(('ORDER', x, f'file-scope initializer reads {x["var"]} before main.cpp:{pv[x["var"]]} setenv'))
        if x['var'] in cl and how == 'presence' and not a:
            flags.append(('PRESENCE', x, f'presence test on documented {x["var"]} ({sorted(cl[x["var"]])}): "=0" acts as set'))
    # B / D per documented var
    unres = []
    for v, cs in sorted(cl.items()):
        ss = per.get(v, [])
        if not ss:
            flags.append(('DOC', dict(var=v, file='docs/OWNER-OPT-INS.md', line=0, text=''), f'{v} documented ({sorted(cs)}) but never read'))
            continue
        for x in ss:
            key = (os.path.basename(x['file']), x['var'])
            if x['sem'] is None:
                if x['how'] and (x['how'].startswith('helper') or x['how'] == 'accept-na'): continue
                unres.append(x); continue
            u, e, z, o, g = x['sem']
            if 'ON' in cs and not (u == 1 and z == 0) and not x['acc']:
                flags.append(('DOC', x, f'doc says {v} default ON (=0 off) but site gives unset={u} "0"={z} "1"={o}'))
            if any(c.startswith('SET:') for c in cs) and 'ON' not in cs and u == 1 and z == 1 and key not in acc \
                    and all(c in ('SET:1',) for c in cs if c.startswith('SET:')) and not x['acc']:
                flags.append(('DOC', x, f'doc says {v} opt-in (=1) but site is on when unset'))
        boolean = all(c in ('ON', 'ZERO', 'SET:1') for c in cs)
        known = [x for x in ss if x['sem'] is not None and x['how'] != 'presence' and not (x['acc'] and 'SPLIT-OK' in x['acc'])] if boolean else []
        uz = {(x['sem'][0], x['sem'][2], x['sem'][3]) for x in known}
        if len(uz) > 1:
            flags.append(('SPLIT', known[0], f'{v} parsed {len(uz)} ways: ' + '; '.join(f'{os.path.basename(x["file"])}:{x["line"]} {x["how"]} u/0/1={x["sem"][0]}{x["sem"][2]}{x["sem"][3]}' for x in known)))
    for x in unres:
        if all(c in ('ON', 'ZERO', 'SET:1') for c in cl[x['var']]) and not x['acc']:
            flags.append(('UNRES', x, f'documented {x["var"]} site not classified (add a row to {ACCEPT})'))
    stats = dict(sites=len(sites), vars=len({x['var'] for x in sites}), filescope=sum(x['filescope'] for x in sites),
                 lambdas=nl, compiled=nc, policy=len(pv), documented=len(cl),
                 doc_sites=sum(len(per.get(v, [])) for v in cl))
    return flags, stats, sites, pv


def report(flags, stats):
    print('[s7426] ' + ' '.join(f'{k}={v}' for k, v in stats.items()))
    for kind, x, msg in flags:
        print(f'  {kind:8s} {os.path.relpath(x["file"], ROOT) if x["file"].startswith("/") else x["file"]}:{x["line"]}  {msg}')


def control(files):
    plant = 'planted/s7426_plant.cpp'
    text = ('#include <cstdlib>\n'
            'static const bool p1 = [] { const char* e = std::getenv("ROGUESQ_CULL_SPIKE"); return e && *e && *e != \'0\'; }();\n'
            'static const bool p3 = [] { const char* e = std::getenv("ROGUESQ_OSMEM_MB"); return e && *e; }();\n'
            'int p2(int d) { return std::getenv("ROGUESQ_TILEPOOL") ? 1 : d; }\n')
    flags, _, _, _ = audit(files, extra=[(plant, text)])
    got = {k for k, x, m in flags if x['file'] == plant}
    need = {'DOC', 'PRESENCE', 'ORDER'}
    ok = need <= got
    print(f'[s7426] CONTROL {"PASS" if ok else "FAIL"}: planted flipped default / presence test / file-scope policy reader -> {sorted(got)}')
    return ok


def main():
    files = sources()
    rc = 0
    if '--control' in sys.argv and not control(files): return 3
    flags, stats, sites, pv = audit(files)
    report(flags, stats)
    if '--dump' in sys.argv:
        with open('/tmp/s7426_sites.tsv', 'w') as f:
            for x in sites:
                f.write(f'{x["var"]}\t{os.path.basename(x["file"])}:{x["line"]}\t{int(x["filescope"])}\t{x["how"]}\t{x["sem"]}\t{x["text"].strip()[:200]}\n')
    real = [f for f in flags if f[0] != 'UNRES']
    print(f'[s7426] VERDICT {"H-drift" if flags else "H-consistent"} ({len(real)} drift, {len(flags) - len(real)} unresolved)')
    return 1 if flags else 0


if __name__ == '__main__':
    sys.exit(main())
