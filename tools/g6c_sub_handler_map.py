#!/usr/bin/env python3
"""s7682 G6c: map every DAT subtype to its NPC update handler and its stand-in model source.

setupNpcUpdateFunctions (0x800653B4) switches on item+0 (sub - 0xC, 0x47 cases) and passes the handler in $a0
(lui/addiu) to spawnNpcOfType. For each subtype this prints the handler, whether the handler directly calls
addNpcToVisibilityBucket (0x80057C8C, the path the stand-in handoff detector watches) or the view-test wrapper
0x8005940C (the inline path npcShieldUpdate uses, s7681), and whether src/main/rs64_standins.cpp gives the
subtype a stand-in (names_in_item -> item+0x5C, handler_model_name -> rodata name, else none).

Usage: tools/g6c_sub_handler_map.py [RecompiledFuncs dir]   (default ../N64Recomp/RecompiledFuncs)
Exit 1 when a subtype has a stand-in but its handler shows neither draw call (the detector could be blind to it).
"""
import glob, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '..', 'N64Recomp', 'RecompiledFuncs')

funcs = {}      # name -> body text
entry = {}      # address -> name
for path in sorted(glob.glob(os.path.join(src_dir, 'funcs_*.c'))):
    text = open(path, errors='replace').read()
    for m in re.finditer(r'^RECOMP_FUNC void (\w+)\(uint8_t\* rdram, recomp_context\* ctx\) \{\n(.*?)^;?\}', text, re.S | re.M):
        name, body = m.group(1), m.group(2)
        funcs[name] = body
        a = re.search(r'// 0x([0-9A-F]{8}):', body)
        if a:
            entry[int(a.group(1), 16)] = name
if 'setupNpcUpdateFunctions' not in funcs:
    sys.exit(f'setupNpcUpdateFunctions not found under {src_dir}')

body = funcs['setupNpcUpdateFunctions']
cases = {int(c): l for c, l in re.findall(r'case (\d+): goto (L_[0-9A-F]+);', body)}
# the instruction comments, in order, de-duplicated (delay slots are emitted twice)
ins, seen = [], set()
for a, t in re.findall(r'// 0x([0-9A-F]{8}): +(.*)', body):
    if a not in seen:
        seen.add(a); ins.append((int(a, 16), re.sub(r'\s+', ' ', t.strip())))
idx = {a: i for i, (a, _) in enumerate(ins)}


def s16(v):
    v &= 0xFFFF
    return v - 0x10000 if v & 0x8000 else v


def handler_at(label):
    i = idx.get(int(label[2:], 16))
    hi = None
    for a, t in ins[i:i + 12] if i is not None else []:
        m = re.match(r'lui \$a0, 0x([0-9A-F]+)$', t)
        if m:
            hi = int(m.group(1), 16) << 16
            continue
        m = re.match(r'addiu \$a0, \$a0, (-?)0x([0-9A-F]+)$', t)
        if m and hi is not None:
            return (hi + (-1 if m.group(1) else 1) * int(m.group(2), 16)) & 0xFFFFFFFF
        if t.startswith('j ') or t.startswith('jal '):
            break
    return None


st = open(os.path.join(ROOT, 'src', 'main', 'rs64_standins.cpp')).read()
nii = re.search(r'bool names_in_item\(uint16_t sub\) \{(.*?)\n\}', st, re.S).group(1)
hmn = re.search(r'uint32_t handler_model_name\(uint16_t sub\) \{(.*?)\n\}', st, re.S).group(1)
in_item = {int(x, 16) for x in re.findall(r'case 0x([0-9A-F]+):', nii)}
by_handler = {int(x, 16) for x in re.findall(r'case 0x([0-9A-F]+): return', hmn)}

calls = {n: {int(x, 16) for x in re.findall(r'// 0x[0-9A-F]{8}: +jal +0x([0-9A-F]{8})', b)} for n, b in funcs.items()}


def reaches(name, target, depth=4):
    # direct or via callees up to `depth` jal levels (bounded so shared helpers do not make everything reach everything)
    frontier, seen_n = {name}, set()
    for _ in range(depth):
        nxt = set()
        for n in frontier:
            if n in seen_n:
                continue
            seen_n.add(n)
            for t in calls.get(n, ()):
                if t == target:
                    return True
                if t in entry:
                    nxt.add(entry[t])
        frontier = nxt
    return False


# positive control (s7681): npcShieldUpdate calls the 0x8005940C view-test wrapper directly
if not reaches('npcShieldUpdate', 0x8005940C, 1):
    sys.exit('positive control failed: npcShieldUpdate -> 0x8005940C not seen; jal parsing is broken')

blind = 0
print('sub  handler                                    addr        bucket vt940C standin')
for c in sorted(cases):
    sub = c + 0xC
    h = handler_at(cases[c])
    name = entry.get(h, '?') if h else '(default/none)'
    bucket = reaches(name, 0x80057C8C)
    vt = reaches(name, 0x8005940C)
    stand = 'item+0x5C' if sub in in_item else ('handler' if sub in by_handler else '-')
    flag = ''
    if stand != '-' and h and not bucket and not vt:
        flag = '  <- stand-in, no direct draw call'; blind += 1
    print(f'0x{sub:02X} {name:42s} {("0x%08X" % h) if h else "-":10s}  {"y" if bucket else "-":6s} {"y" if vt else "-":6s} {stand}{flag}')
print(f'subtypes={len(cases)} standin_subs={len(in_item | by_handler)} flagged={blind}')
sys.exit(1 if blind else 0)
