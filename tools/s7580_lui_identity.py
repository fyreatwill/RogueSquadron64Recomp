#!/usr/bin/env python3
"""s7580: prove tools/fixup_lui_unsigned.py is machine-code neutral. Compiles every RecompiledFuncs TU at build/'s real
RecompiledFuncs C flags (minus -g) as-is and LUI-rewritten (copy in <out>, -I the source dir), compares the objects'
disassembly + section contents. Exit 0 = every TU identical and >=1 TU had rewrites; 1 = a diff (listed); 2 = nothing
rewritten (void). Control: --plant makes one rewrite non-neutral (0X8011u -> 0X8012u) and must yield exit 1.
usage: tools/s7580_lui_identity.py <RecompiledFuncs dir> <out dir> [--plant] [-j N]"""
import pathlib, subprocess, sys, concurrent.futures as cf, re
sys.path.insert(0, str(pathlib.Path(__file__).parent)); from fixup_lui_unsigned import rewrite
R = pathlib.Path(__file__).resolve().parent.parent
def flags():
    fm = (R / 'build/CMakeFiles/RecompiledFuncs.dir/flags.make').read_text()
    g = lambda k: re.search(rf'^{k} = (.*)$', fm, re.M).group(1).split()
    return g('C_DEFINES') + g('C_INCLUDES') + [f for f in g('C_FLAGS') if f != '-g']
def dump(o):
    a = subprocess.run(['objdump', '-d', '-r', '--no-show-raw-insn', '--no-leading-addr', str(o)], capture_output=True, text=True).stdout
    b = subprocess.run(['objdump', '-s', str(o)], capture_output=True, text=True).stdout
    return '\n'.join(l for l in (a + b).split('\n') if not l.rstrip().endswith('file format mach-o arm64') and str(o) not in l)
def one(src, out, fl, plant):
    s = src.read_text(errors='surrogateescape'); t, n = rewrite(s)
    if plant and n: t = t.replace('S32(0X8011u << 16)', 'S32(0X8012u << 16)', 1)
    o1 = out / (src.stem + '.a.o'); o2 = out / (src.stem + '.b.o'); c2 = out / src.name
    c2.write_text(t, errors='surrogateescape')
    for c, o in ((src, o1), (c2, o2)):
        subprocess.run(['clang', *fl, '-I', str(src.parent), '-c', str(c), '-o', str(o)], check=True, capture_output=True)
    return src.name, n, dump(o1) == dump(o2)
def main():
    a = sys.argv[1:]; d = pathlib.Path(a[0]); out = pathlib.Path(a[1]); out.mkdir(parents=True, exist_ok=True)
    plant = '--plant' in a; j = int(a[a.index('-j') + 1]) if '-j' in a else 8; fl = flags()
    srcs = sorted(d.glob('*.c'))
    with cf.ThreadPoolExecutor(j) as ex: res = list(ex.map(lambda s: one(s, out, fl, plant), srcs))
    diffs = [r for r in res if not r[2]]; rw = sum(r[1] for r in res)
    for r in diffs: print('DIFF', r[0], 'rewrites', r[1])
    print(f'tus={len(res)} rewrites={rw} diffs={len(diffs)} plant={int(plant)}')
    sys.exit(2 if rw == 0 else (1 if diffs else 0))
if __name__ == '__main__':
    main()
