#!/usr/bin/env python3
"""s7578: signed-overflow UB site census for the generated GAME C (RecompiledFuncs TUs).
For every compile_commands entry matching TU_RE (default RecompiledFuncs/), build -O0 IR with
-fsanitize=signed-integer-overflow and bucket each __ubsan add/sub/mul/negate/divrem site by a normalised source shape
(identifiers kept, numbers -> N). Prints shape counts + one example each. Shift sites are excluded (-fwrapv does not change
shift semantics in clang; s7577 classes cover the count side). Usage: s7578_gamec_wrap_sites.py OUT.txt"""
import json, os, re, shlex, subprocess, sys, collections
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cc = json.load(open(os.path.join(ROOT, 'build/compile_commands.json')))
tus = [e for e in cc if re.search(os.environ.get('TU_RE', r'RecompiledFuncs/'), e['file'])]
def argv(e):
    a = e.get('arguments') or shlex.split(e['command']); o = []; skip = False
    for x in a:
        if skip: skip = False; continue
        if x in ('-o', '-MF', '-MT', '-MQ'): skip = True; continue
        if x in ('-c', '-MD', '-MMD') or x == e['file'] or x.startswith('-O') or x.startswith('-g'): continue
        if x.startswith('-inline-threshold') and o and o[-1] == '-mllvm': o.pop(); continue
        o.append(x)
    return o + ['-O0', '-fsanitize=signed-integer-overflow', '-S', '-emit-llvm', '-o', '-', e['file']]
def one(e):
    r = subprocess.run(argv(e), cwd=e['directory'], capture_output=True, text=True)
    if r.returncode: return e['file'], None
    src = {}; data = {}; sites = collections.Counter()
    for ln in r.stdout.splitlines():
        m = re.match(r'^(@\.src(?:\.\d+)?) = .*c"([^"]*)\\00"', ln)
        if m: src[m.group(1)] = m.group(2); continue
        m = re.match(r'^(@\d+) = private unnamed_addr global .*\{ ptr (@\.src(?:\.\d+)?), i32 (\d+), i32 (\d+) \}', ln)
        if m: data[m.group(1)] = (m.group(2), int(m.group(3)))
    for ln in r.stdout.splitlines():
        m = re.search(r'call void @__ubsan_handle_([a-z_]+?)(?:_abort)?\(ptr (@\d+)', ln)
        if m and m.group(2) in data and 'shift' not in m.group(1):
            f, l = data[m.group(2)]; sites[(src.get(f, f), l, m.group(1))] += 1
    return e['file'], sites
with ThreadPoolExecutor(12) as ex: res = list(ex.map(one, tus))
cache = {}
def text(d, f, l):
    p = f if f.startswith('/') else os.path.normpath(os.path.join(d, f))
    if p not in cache: cache[p] = open(p, errors='replace').read().split('\n')
    return cache[p][l - 1].strip()
shapes = collections.Counter(); ex1 = {}; byfile = collections.Counter(); fails = []
dirs = {e['file']: e['directory'] for e in tus}
for tu, s in res:
    if s is None: fails.append(tu); continue
    for (f, l, k), n in s.items():
        t = text(dirs[tu], f, l); byfile[os.path.basename(f)] += 1
        sh = re.sub(r'\b0[Xx][0-9A-Fa-f]+\b|\b\d+\b', 'N', t)[:140]
        key = (k, sh); shapes[key] += 1; ex1.setdefault(key, '%s:%d' % (os.path.basename(f), l))
import json as _j
_j.dump([[os.path.normpath(os.path.join(dirs[tu], f)) if not f.startswith('/') else f, l, k, text(dirs[tu], f, l)] for tu, s_ in res if s_ for (f, l, k) in s_], open(sys.argv[1] + '.json', 'w'))
out = open(sys.argv[1], 'w')
for (k, sh), n in shapes.most_common(): print('%6d %-22s %-18s | %s' % (n, k, ex1[(k, sh)], sh), file=out)
print('FILES', dict(byfile.most_common(20)), file=out)
print('SUMMARY tus=%d fails=%d sites=%d shapes=%d' % (len(tus), len(fails), sum(shapes.values()), len(shapes)), file=out)
print(open(sys.argv[1]).read().splitlines()[-1])
