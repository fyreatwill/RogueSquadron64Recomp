#!/usr/bin/env python3
"""s7577: enumerate the signed-overflow / shift UB-capable source sites of an RSP ucode TU.
Compiles the TU (compile_commands.json flags) to -O0 IR with -fsanitize=signed-integer-overflow,shift and lists the static
source locations of every __ubsan handler check, grouped file:line -> kinds. Usage: s7577_ubsan_sites.py <tu-basename-substring> [--check]
--check: every site must match a CLASSES entry (a value-range proof that the signed op cannot overflow / the shift count is
in range for every reachable input); any UNCLASSIFIED site -> rc 1. Run after every ucode regen or rsp*.hpp edit."""
import json, os, re, shlex, subprocess, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pat = sys.argv[1]; CHECK = '--check' in sys.argv
e = next(x for x in json.load(open(os.path.join(ROOT, 'build/compile_commands.json'))) if x['file'].endswith(pat))
a = e.get('arguments') or shlex.split(e['command']); o = []; skip = False
for x in a:
    if skip: skip = False; continue
    if x in ('-o', '-MF', '-MT', '-MQ'): skip = True; continue
    if x in ('-c', '-MD', '-MMD') or x == e['file'] or x.startswith('-O') or x.startswith('-g'): continue
    o.append(x)
o2 = []
for x in o:
    if x.startswith('-inline-threshold') and o2 and o2[-1] == '-mllvm': o2.pop(); continue
    o2.append(x)
o = o2
ir = subprocess.run(o + ['-O0', '-fsanitize=signed-integer-overflow,shift', '-S', '-emit-llvm', '-o', '-', e['file']],
                    cwd=e['directory'], capture_output=True, text=True)
if ir.returncode: print(ir.stderr[-800:]); sys.exit(2)
src = {}; data = {}
for ln in ir.stdout.splitlines():
    m = re.match(r'^(@\.src(?:\.\d+)?) = .*c"([^"]*)\\00"', ln)
    if m: src[m.group(1)] = m.group(2); continue
    m = re.match(r'^(@\d+) = private unnamed_addr global .*\{ ptr (@\.src(?:\.\d+)?), i32 (\d+), i32 (\d+) \}', ln)
    if m: data[m.group(1)] = (m.group(2), int(m.group(3)))
sites = collections.defaultdict(collections.Counter)
for ln in ir.stdout.splitlines():
    m = re.search(r'call void @__ubsan_handle_([a-z_]+?)(?:_abort)?\(ptr (@\d+)', ln)
    if m and m.group(2) in data:
        f, l = data[m.group(2)]; sites[(os.path.relpath(src.get(f, f), ROOT) if src.get(f, f).startswith('/') else src.get(f, f), l)][m.group(1)] += 1
# (name, regex on the source line, proof). C++20: signed << is defined (modular) and >> is arithmetic, so a shift site is UB
# only through its count; a signed add/mul is UB only on overflow.
CLASSES = [
    ('gen-shift-const', r'^r\d+ = S32\((?:U32\(r\d+\)|RSP_SIGNED\(r\d+\)|r\d+)\) (?:<<|>>) \d+;|^r\d+ = S32\((?:U32\(r\d+\)|RSP_SIGNED\(r\d+\)|r\d+|0X[0-9A-F]+) (?:<<|>>) \d+\);', 'constant count < 32'),
    ('gen-shift-masked', r'^r\d+ = S32\((?:U32\(r\d+\)|r\d+)\) (?:<<|>>) \(r\d+ & 31\);|^r\d+ = S32\((?:U32\(r\d+\)|r\d+) (?:<<|>>) \(r\d+ & 31\)\);', 'count masked & 31'),
    ('glue-opbyte', r'\(r19 >> 24\) == 0x', 'constant count 24 on uint32'),
    ('diag-counter', r'\+\+(?:rs64_\w+|s_n)\b|rs64_restart_count % 200|any \+= |for \(int i = 0; i < (?:8|16); i\+\+\) any', 'env/diag counter; < 2^31 increments per process'),
    ('loop-small', r'for \(int i_? = 0; i_? < (?:2|4|8|48); i_?\+\+\)|\(i \+ 2\) \^ 3|RSP_MEM_BU\(offset \+ i, addr\)', 'loop counter <= 48'),
    ('vu-ring', r'RS64_VU_RING\(\d+, vd, vs, vt, e\);', 'macro lane loops i_ < 8/48, reg index < 32'),
    ('s8-imm-scaled', r'rs \+ imm \* (?:2|4|8|16)\b|rs \+ imm\b', 's8 imm * <=16 in [-2048, 2032]'),
    ('elem-bounded', r'start \+ \d+|index \+ offset|<< 7;|>> 7;|\(offset & 7\) << 1|hi << 8 \| lo << 0|rt >> [08];', 'template e <= 15 / byte or element operands, constant count'),
    ('vrcp', r'DIVIN << 16 \| vt|input >> 31|data -= mask|u64\(data\) << shift|\(0x10000 \| result\) << 14|result >> 31 - shift|DIVOUT = result >> 16', 'shift = clz(data!=0) in [0,31]; input > -32768 excludes INT_MIN; rcp table < 0x10000'),
    ('mem-b-kseg0', r'MEM_B\(0, \(int64_t\)\(int32_t\)\(dram_addr \+ \w+ \+ 0x80000000\)\)', 'int64 (sign-extended int32) + 0'),
    ('diag-shift', r'j >> 10|mn >>= 2; mx >>= 2', 'uint64 / int pixel coords, constant count'),
    ('sse2neon-negcount', r'vdupq_n_s16\(-count\)', 'count is a constant shift amount 0..16'),
    ('asan-plant', r's7468 UCODE PLANT|volatile int one = \(int\)\(idx >> 12\)', 'deliberate overflow plant, ASan build + ROGUESQ_S7468_UCODE_PLANT=1 only'),
]
lines = {}
def text(f, l):
    p = f if f.startswith('/') else os.path.join(ROOT, f)
    if p not in lines: lines[p] = open(p, errors='replace').read().split('\n')
    return lines[p][l - 1].strip()
byfile = collections.Counter(); bycls = collections.Counter(); unc = 0
for (f, l), k in sorted(sites.items()):
    byfile[f] += 1; t = text(f, l)
    c = next((n for n, rx, _ in CLASSES if re.search(rx, t)), None)
    if c is None and f.endswith('rsp.hpp') and re.search(r'for \(int i = 0; i < [24]; i\+\+\)', text(f, l)): c = 'loop-small'
    bycls[c or 'UNCLASSIFIED'] += 1; unc += c is None
    print('%s:%d %s [%s] | %s' % (f, l, ' '.join('%s=%d' % kv for kv in sorted(k.items())), c or 'UNCLASSIFIED', t[:110]))
print('FILES', dict(byfile)); print('CLASSES', dict(bycls)); print('SITES %d UNCLASSIFIED %d' % (len(sites), unc))
if CHECK: sys.exit(1 if unc else 0)
