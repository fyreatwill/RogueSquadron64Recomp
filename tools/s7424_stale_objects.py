#!/usr/bin/env python3
"""s7424 class CG: does the shipped binary match the live source?

Offline audit of build/ (Unix Makefiles generator). Checks, for the game target and every
archive it links:
  A  each compile_commands object exists and is newer than its source and every dep in its .d
  B  each archive's members == its link.txt object list, byte-identical to the .o on disk,
     and the archive is newer than every member
  C  the binary is newer than every object/archive it links
  D  RecompiledFuncs: the CONFIGURE_DEPENDS glob of the live dir == the compiled .c set,
     every source path is the live tree, and no .o without a source (orphan)
  E  RecompiledFuncs: per file, RECOMP_FUNC definitions in the source == defined text
     symbols in the .o (content check that does not trust mtimes)
  F  PatchesLib chain: patches/*.c -> patches.elf -> RecompiledPatches/patches.c ordering
Exit 0 = H-fresh, 1 = H-stale (findings listed), 3 = --control failed.
--control plants one defect per check class in /tmp copies and requires each to be flagged.
"""
import json, os, re, shutil, subprocess, sys, tempfile, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, 'build')
LIVE = os.path.realpath(os.path.join(ROOT, '..', 'N64Recomp', 'RecompiledFuncs'))
RF_RE = re.compile(r'^(?:__attribute__\(\(weak\)\) )?RECOMP_FUNC\s+void\s+(\w+)\s*\(', re.M)
TARGET = 'RogueSquadron64Recomp'


def mt(p):
    return os.stat(p).st_mtime


def parse_d(path):
    txt = open(path, errors='replace').read().replace('\\\n', ' ')
    _, _, deps = txt.partition(':')
    return [d for d in deps.split() if d]


def check_obj(obj, src, dfile):
    """A: obj newer than src and all deps."""
    out = []
    if not os.path.exists(obj):
        return ['A missing-object %s' % obj]
    to = mt(obj)
    if mt(src) > to:
        out.append('A src-newer %s' % src)
    if dfile and os.path.exists(dfile):
        for d in parse_d(dfile):
            if not os.path.exists(d):
                out.append('A dep-missing %s (%s)' % (d, os.path.basename(obj)))
            elif mt(d) > to:
                out.append('A dep-newer %s > %s' % (d, os.path.basename(obj)))
    elif dfile:
        out.append('A no-depfile %s' % dfile)
    return out


def parse_link(link_txt):
    first = open(link_txt).read().split('\n')[0].split()
    return [w.strip('"') for w in first]


def check_archive(arch, objs, workdir):
    """B: members == objs (by basename order), bytes equal, archive newer."""
    out = []
    if not os.path.exists(arch):
        return ['B missing-archive %s' % arch]
    members = subprocess.run(['ar', 't', arch], capture_output=True, text=True).stdout.splitlines()
    members = [m for m in members if not m.startswith('__.SYMDEF')]
    want = [os.path.basename(o) for o in objs]
    if sorted(members) != sorted(want):
        extra = sorted(set(members) - set(want)); miss = sorted(set(want) - set(members))
        out.append('B member-set %s extra=%s missing=%s' % (os.path.basename(arch), extra[:5], miss[:5]))
    if len(set(want)) != len(want):
        return out + ['B dup-basenames %s (byte compare skipped)' % os.path.basename(arch)]
    xd = tempfile.mkdtemp(dir=workdir)
    subprocess.run(['ar', 'x', os.path.abspath(arch)], cwd=xd, check=True)
    ta = mt(arch)
    for o in objs:
        b = os.path.basename(o)
        if not os.path.exists(o):
            continue
        if mt(o) > ta:
            out.append('B obj-newer-than-archive %s > %s' % (b, os.path.basename(arch)))
        x = os.path.join(xd, b)
        if os.path.exists(x) and open(x, 'rb').read() != open(o, 'rb').read():
            out.append('B member-bytes-differ %s in %s' % (b, os.path.basename(arch)))
    shutil.rmtree(xd, ignore_errors=True)
    return out


def defined_text_syms(obj):
    r = subprocess.run(['nm', '-g', '--defined-only', obj], capture_output=True, text=True).stdout
    s = set()
    for ln in r.splitlines():
        p = ln.split()
        if len(p) >= 3 and p[1] in ('T', 't', 'W'):
            s.add(p[2][1:] if p[2].startswith('_') else p[2])
    return s


def check_syms(src, obj):
    """E: every RECOMP_FUNC in src is a defined text symbol in obj, and vice versa (for func_ names)."""
    # RecompiledFuncs is compiled with -Dmain=rs_main (CMakeLists), so a 'main' definition is rs_main in the .o
    defs = set('rs_main' if f == 'main' else f for f in RF_RE.findall(open(src, errors='replace').read()))
    syms = defined_text_syms(obj)
    miss = sorted(defs - syms)
    extra = sorted(s for s in syms - defs if s in ALL_DEFS)
    out = []
    if miss:
        out.append('E src-func-not-in-obj %s %d e.g. %s' % (os.path.basename(src), len(miss), miss[:3]))
    if extra:
        out.append('E obj-func-not-in-src %s %d e.g. %s' % (os.path.basename(src), len(extra), extra[:3]))
    return out, len(defs)


ALL_DEFS = set()


def audit(build=BUILD, live=LIVE, verbose=True):
    find = []
    cc = json.load(open(os.path.join(build, 'compile_commands.json')))
    by_obj = {}
    for e in cc:
        obj = e.get('output') or re.search(r'-o (\S+)', e['command']).group(1)
        # compile_commands 'output' is relative to the top build dir, not the entry's directory
        obj = os.path.normpath(os.path.join(build, obj))
        by_obj[obj] = e['file']
    # link closure: main target objects + archives
    main_link = parse_link(os.path.join(build, 'CMakeFiles', TARGET + '.dir', 'link.txt'))
    linked_objs = [os.path.join(build, t) for t in main_link if t.endswith('.o')]
    linked_arch = []
    for t in main_link:
        if t.endswith('.a') and not t.startswith('/opt/'):
            p = t if t.startswith('/') else os.path.join(build, t)
            if p not in linked_arch:
                linked_arch.append(os.path.normpath(p))
    # archive -> objects via each target's link.txt
    arch_objs = {}
    for lt in glob.glob(os.path.join(build, '**', 'CMakeFiles', '*.dir', 'link.txt'), recursive=True):
        w = parse_link(lt)
        if len(w) > 3 and w[0].endswith('ar') and w[1] == 'qc':
            base = os.path.dirname(os.path.dirname(os.path.dirname(lt)))
            a = os.path.normpath(os.path.join(base, w[2]))
            arch_objs[a] = [os.path.normpath(os.path.join(base, o)) for o in w[3:]]
    work = tempfile.mkdtemp(prefix='s7424_')
    nobj = 0
    all_linked = list(linked_objs)
    for a in linked_arch:
        if a not in arch_objs:
            find.append('B no-link.txt-for-archive %s' % a); continue
        find += check_archive(a, arch_objs[a], work)
        all_linked += arch_objs[a]
    for o in all_linked:
        src = by_obj.get(o)
        if src is None:
            find.append('A obj-without-compile-entry %s' % o); continue
        nobj += 1
        find += check_obj(o, src, o + '.d')
    # C
    binp = os.path.join(build, TARGET)
    tb = mt(binp)
    for p in linked_objs + linked_arch:
        if os.path.exists(p) and mt(p) > tb:
            find.append('C newer-than-binary %s' % p)
    # D
    rf_objs = arch_objs.get(os.path.join(build, 'libRecompiledFuncs.a'), [])
    rf_srcs = [by_obj.get(o) for o in rf_objs]
    for s in rf_srcs:
        if s and os.path.dirname(os.path.realpath(s)) != live:
            find.append('D non-live-source %s' % s)
    globset = set(os.path.realpath(p) for p in glob.glob(os.path.join(live, '*.c')) + glob.glob(os.path.join(live, '*.cpp')))
    compiled = set(os.path.realpath(s) for s in rf_srcs if s)
    for p in sorted(globset - compiled):
        find.append('D live-source-not-compiled %s' % p)
    for p in sorted(compiled - globset):
        find.append('D compiled-source-gone %s' % p)
    rfdir = os.path.join(build, 'CMakeFiles', 'RecompiledFuncs.dir')
    for o in glob.glob(os.path.join(rfdir, '**', '*.o'), recursive=True):
        if os.path.normpath(o) not in set(rf_objs):
            find.append('D orphan-object %s' % o)
    # E
    ALL_DEFS.clear()
    for s in rf_srcs:
        if s and s.endswith('.c'):
            ALL_DEFS.update(RF_RE.findall(open(s, errors='replace').read()))
    nf = 0
    for o, s in zip(rf_objs, rf_srcs):
        if s and s.endswith('.c') and os.path.exists(o):
            f, n = check_syms(s, o); find += f; nf += n
    # F
    pd = os.path.join(ROOT, 'patches'); rp = os.path.join(ROOT, 'RecompiledPatches', 'patches.c')
    elf = os.path.join(pd, 'patches.elf')
    if os.path.exists(elf):
        for c in glob.glob(os.path.join(pd, '*.c')):
            if mt(c) > mt(elf):
                find.append('F patch-src-newer-than-elf %s' % c)
        for d in (elf, os.path.join(ROOT, 'patches.toml'), os.path.join(ROOT, 'tools', 'fixup_patches_host.py')):
            if mt(d) > mt(rp):
                find.append('F newer-than-patches.c %s' % d)
    shutil.rmtree(work, ignore_errors=True)
    if verbose:
        print('objects checked %d (main %d + %d archives), RecompiledFuncs files %d, RECOMP_FUNC defs %d'
              % (nobj, len(linked_objs), len(linked_arch), len(rf_objs), nf))
    return find


def control():
    """Plant one defect per class in /tmp copies; each must be flagged."""
    ok = True
    t = tempfile.mkdtemp(prefix='s7424c_')
    cc = json.load(open(os.path.join(BUILD, 'compile_commands.json')))
    e = next(x for x in cc if x['file'].endswith('/funcs_9.c'))
    obj = os.path.normpath(os.path.join(BUILD, e.get('output')))
    # A: a source copy touched newer than the object
    src = os.path.join(t, 'funcs_9.c'); shutil.copy2(e['file'], src); os.utime(src, None)
    r = check_obj(obj, src, obj + '.d'); ok &= any('src-newer' in x for x in r); print('CONTROL A src-newer', bool(r))
    # A': a dep newer (a planted .d naming a fresh file)
    dep = os.path.join(t, 'x.h'); open(dep, 'w').write('//\n')
    df = os.path.join(t, 'o.d'); open(df, 'w').write('o: %s \\\n %s\n' % (e['file'], dep))
    r = check_obj(obj, e['file'], df); hit = any('dep-newer' in x for x in r); ok &= hit; print('CONTROL A dep-newer', hit)
    # E: planted extra RECOMP_FUNC in a source copy
    s2 = os.path.join(t, 'funcs_9b.c')
    open(s2, 'w').write(open(e['file'], errors='replace').read() + '\nRECOMP_FUNC void func_s7424_planted(uint8_t* rdram, recomp_context* ctx) {}\n')
    r, _ = check_syms(s2, obj); hit = any('src-func-not-in-obj' in x and 'planted' in x for x in r); ok &= hit
    print('CONTROL E planted-func', hit)
    # E clean pair must be silent
    r, n = check_syms(e['file'], obj); print('CONTROL E clean pair findings', len(r), 'defs', n); ok &= (not r and n > 0)
    # B: archive with one member byte-changed
    a = os.path.join(t, 'lib.a'); shutil.copy2(os.path.join(BUILD, 'libPatchesLib.a'), a)
    po = os.path.join(BUILD, 'CMakeFiles', 'PatchesLib.dir', 'RecompiledPatches', 'patches.c.o')
    pc = os.path.join(t, 'patches.c.o'); b = bytearray(open(po, 'rb').read()); b[-1] ^= 0xFF; open(pc, 'wb').write(b)
    os.utime(pc, (mt(a) - 10, mt(a) - 10))
    r = check_archive(a, [pc], t); hit = any('bytes-differ' in x for x in r); ok &= hit; print('CONTROL B bytes-differ', hit)
    r = check_archive(a, [pc, os.path.join(t, 'ghost.c.o')], t); hit = any('member-set' in x for x in r); ok &= hit
    print('CONTROL B member-set', hit)
    r = check_archive(os.path.join(BUILD, 'libPatchesLib.a'), [po], t); print('CONTROL B clean archive findings', r); ok &= not r
    shutil.rmtree(t, ignore_errors=True)
    print('CONTROL', 'PASS' if ok else 'FAIL')
    return ok


def make_n(build=BUILD):
    """G (second line): ask make itself what it would redo; summarise Building/Linking/Generating messages."""
    r = subprocess.run(['make', '-n', TARGET], cwd=build, capture_output=True, text=True).stdout
    msgs = re.findall(r'"((?:Building|Linking|Generating)[^"]*)"', r)
    kinds = {}
    for m in msgs:
        k = 'shader-chain' if '/shaders/' in m else ('spirv-cross' if 'spirv' in m else m)
        kinds[k] = kinds.get(k, 0) + 1
    for k, v in sorted(kinds.items()):
        print('G make-n %4d %s' % (v, k))
    return kinds


if __name__ == '__main__':
    if '--make-n' in sys.argv:
        make_n()
    if '--control' in sys.argv and not control():
        sys.exit(3)
    f = audit()
    for x in f:
        print(x)
    print('findings', len(f))
    print('VERDICT', 'H-fresh' if not f else 'H-stale')
    sys.exit(0 if not f else 1)
