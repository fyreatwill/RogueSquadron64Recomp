#!/usr/bin/env python3
# s6940 G1e: instruction mix of one function in an object/binary (arm64), to test whether the RSP vector register
# file is memory-resident (q-register loads/stores per NEON op). usage: g1e_fn_mix.py OBJ SYMBOL [OBJ2 ...]
import re, subprocess, sys, collections
args = sys.argv[1:]; sym = args[1]; objs = [args[0]] + args[2:]
def mix(obj):
    out = subprocess.run(['objdump', '-d', '--no-show-raw-insn', f'--disassemble-symbols={sym}', obj],
                         capture_output=True, text=True).stdout
    c = collections.Counter(); n = 0
    for ln in out.splitlines():
        m = re.match(r'\s*[0-9a-f]+:\s+(\S+)\s*(.*)', ln)
        if not m: continue
        op, a = m.group(1), m.group(2); n += 1
        q = re.search(r'\bq\d+', a) is not None
        if op.startswith(('ldr', 'ldur', 'ldp')) and q: c['qload'] += 1
        elif op.startswith(('str', 'stur', 'stp')) and q: c['qstore'] += 1
        elif op.startswith(('ldr', 'ldur', 'ldp', 'ldrb', 'ldrh', 'ldrs')): c['gload'] += 1
        elif op.startswith(('str', 'stur', 'stp', 'strb', 'strh')): c['gstore'] += 1
        elif op in ('bl', 'blr'): c['call'] += 1
        elif op[0] == 'b' or op in ('cbz', 'cbnz', 'tbz', 'tbnz', 'ret', 'br'): c['branch'] += 1
        elif '.' in op or re.search(r'\bv\d+', a): c['neon'] += 1
        else: c['int'] += 1
    return n, c
for o in objs:
    n, c = mix(o)
    print(f'{o}: {n} insns  ' + '  '.join(f'{k}={c[k]}' for k in ('neon','qload','qstore','gload','gstore','int','branch','call'))
          + f'  (qload+qstore)/neon={(c["qload"]+c["qstore"])/max(1,c["neon"]):.2f}')
