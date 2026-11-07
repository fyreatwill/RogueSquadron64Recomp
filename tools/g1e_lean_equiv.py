#!/usr/bin/env python3
# s6940 G1e: prove the lean gfx ucode arm (src/rsp/factor5_ucode_lean.cpp) is the main TU with only the hook/probe gates
# set to 0. Preprocesses both with the build's own compile line, maps main -> lean (type RS64_RSP_GFX -> RS64_RSP_LEAN,
# function name, `if (rs64_rsp_hooks_on` -> `if (0`, probe gate -> 0, debug_file paths), and diffs. Expect only the
# "Unhandled jump target ... factor5_ucode" printf string. Run from the repo root after a build. Exit 1 on any other diff.
import json, re, subprocess, sys, difflib, os, shlex
root = os.getcwd(); out = 'scratch/s6940'; os.makedirs(out, exist_ok=True)
cmd = next(e['command'] for e in json.load(open('build/compile_commands.json')) if e['file'].endswith('factor5_ucode_recompiled.c'))
base = re.sub(r' -o \S+ -c \S+', '', cmd).replace(' -g ', ' ')
def pp(src, extra, dst):
    subprocess.run(f'{base} {extra} -E -P -o {root}/{dst} {src}', shell=True, cwd='build', check=True, stderr=subprocess.DEVNULL)
pp(f'{root}/build/factor5_ucode/factor5_ucode_recompiled.c', '', f'{out}/main.i')
pp(f'{root}/src/rsp/factor5_ucode_lean.cpp', '-URSP -DRSP=RS64_RSP_LEAN', f'{out}/lean.i')
m = open(f'{out}/main.i').read(); l = open(f'{out}/lean.i').read()
if os.environ.get('MUTANT'): l = l.replace('VMADN', 'VMADH', 1)  # positive control: must exit 1
nh = len(re.findall(r'if \(rs64_rsp_hooks_on', m)); np_ = m.count('__builtin_expect(rs64_g1e_probes, 0)')
m = re.sub(r'\bfactor5_ucode\b', 'factor5_ucode_lean', m.replace('RS64_RSP_GFX', 'RS64_RSP_LEAN'))
m = re.sub(r'if \(rs64_rsp_hooks_on', 'if (0', m).replace('__builtin_expect(rs64_g1e_probes, 0)', '__builtin_expect(0, 0)')
norm = lambda t: [x for x in re.sub(r'debug_file = "[^"]*"', 'debug_file = F', t).splitlines() if x.strip()]
d = [x for x in difflib.unified_diff(norm(m), norm(l), lineterm='', n=0) if not x.startswith(('---', '+++', '@@'))]
d = [x for x in d if 'Unhandled jump target' not in x]
print(f'gates mapped: hooks={nh} probes={np_}; other diff lines={len(d)}')
for x in d[:20]: print(x[:200])
sys.exit(1 if d or nh == 0 or np_ == 0 else 0)
