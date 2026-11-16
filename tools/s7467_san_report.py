#!/usr/bin/env python3
"""s7467 class DW: score an ASan+UBSan soak (tools/build_asan.sh build, scratch/agent/soak_queue/s7467_asan_flight.sh).

usage: s7467_san_report.py <R dir> <arm>... [--plant <arm>] [--uplant <arm>] [--known tools/s7467_san_reviewed.tsv]
--known: groups matching a KNOWN (kind prefix, file basename) row are reviewed; exit 1 only on a NEW group.
Per arm reads <R>/san_<arm>.* (ASAN_OPTIONS/UBSAN_OPTIONS log_path) and <R>/log_<arm>.txt (stderr fallback).
Groups reports by (kind, first frame in our code). The plant arm must show BOTH planted reports
(heap-buffer-overflow in rs64_s7467_asan_plant, signed-integer-overflow at the plant line) = positive control.
--uplant (s7468 class DY): that arm must ALSO show the ucode-TU plant (global-buffer-overflow + signed overflow at the\n"s7468 UCODE PLANT" lines of src/rsp/factor5_ucode_nmac.cpp) = proof the ucode TUs are instrumented.\nPrints one line per arm and one line per non-plant group; exit 0 = control PASS and 0 non-plant groups,
1 = control PASS and >=1 non-plant group (H-asan-hit), 3 = control FAIL (instrument blind, result void).
"""
import glob, os, re, sys

ASAN_HDR = re.compile(r'ERROR: AddressSanitizer: ([\w-]+)')
UBSAN_HDR = re.compile(r'^(\S+?):(\d+):(\d+): runtime error: (.*)$')
FRAME = re.compile(r'^\s*#(\d+) 0x[0-9a-f]+ in (\S+) (\S+)')


def parse(text):
    """Yield (kind, site) per report."""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        ln = lines[i]
        m = ASAN_HDR.search(ln)
        if m:
            kind = 'asan:' + m.group(1)
            site = '?'
            for j in range(i + 1, min(i + 40, len(lines))):
                f = FRAME.match(lines[j])
                if not f:
                    continue
                fn, loc = f.group(2), f.group(3)
                if any(k in loc for k in ('libclang_rt', 'libsystem', 'libc++', '/usr/lib')) or fn.startswith('__') or fn in ('wrap_memcpy', 'wrap_memmove', 'wrap_memset', 'malloc', 'free'):
                    continue
                site = fn + ' ' + re.sub(r'.*?/(src|lib)/', r'\1/', loc, count=1)
                break
            yield kind, site
            i += 1
            continue
        m = UBSAN_HDR.match(ln.strip())
        if m:
            what = re.sub(r'0x[0-9a-f]+|-?\d+', 'N', m.group(4))[:90]
            yield 'ubsan:' + what, re.sub(r'.*?/(src|lib)/', r'\1/', m.group(1), count=1) + ':' + m.group(2)
        i += 1


def arm_reports(R, arm):
    seen_text = set()
    out = []
    for p in sorted(glob.glob(os.path.join(R, 'san_%s*' % arm))) + [os.path.join(R, 'log_%s.txt' % arm)]:
        if not os.path.isfile(p):
            continue
        t = open(p, errors='replace').read()
        for kind, site in parse(t):
            out.append((kind, site, os.path.basename(p)))
    # The same report can be in both the log_path file and stderr; dedupe by (kind, site) count per source kind.
    by_src = {}
    for k, s, src in out:
        key = 'log' if src.startswith('log_') else 'san'
        by_src.setdefault(key, []).append((k, s))
    return by_src.get('san') or by_src.get('log') or []


def is_uplant(kind, site):
    # s7468 class DY: the ucode-TU plant (src/rsp/factor5_ucode_nmac.cpp rs64_s7468_ucode_plant).
    # Generated ucode lines are attributed to factor5_ucode_recompiled.c, so any frame AT factor5_ucode_nmac.cpp is the
    # plant's own code; no line-number match (line numbers shift with edits and broke re-scoring of old logs, s7468).
    if 'factor5_ucode_nmac.cpp' not in site:
        return False
    return (kind == 'asan:global-buffer-overflow' and 'rs64_s7468_ucode_plant' in site) or kind.startswith('ubsan:signed integer overflow')


def is_plant(kind, site):
    if is_uplant(kind, site):
        return True
    # The plant is inlined into main(). s7468: match by the plant's frame (main / rs64_s7467_asan_plant in main.cpp) for the
    # heap read, and by its exact message for the overflow (INT_MAX + 1 in type int), not by line: lines shift with edits.
    if 'main.cpp' not in site:
        return False
    if kind == 'asan:heap-buffer-overflow':
        return site.split(' ')[0] in ('main', 'rs64_s7467_asan_plant') or _plant_line(site)
    return kind == "ubsan:signed integer overflow: N + N cannot be represented in type 'int'" or (
        kind.startswith('ubsan:signed integer overflow') and _plant_line(site))


_PL = None


def _plant_line(site):
    global _PL
    if _PL is None:
        _PL = set()
        try:
            for n, l in enumerate(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'main', 'main.cpp')), 1):
                if 'UBSan signed-integer-overflow' in l or 'heap-buffer-overflow READ of size 1' in l or l.strip() == 'rs64_s7467_asan_plant();':
                    _PL.add(n)
        except OSError:
            pass
    m = re.search(r'main\.cpp:(\d+)', site)
    return bool(m) and int(m.group(1)) in _PL


def main(a):
    if len(a) < 2:
        print(__doc__); return 2
    plant = None
    known = []
    if '--known' in a:
        k = a.index('--known')
        for l in open(a[k + 1]):
            f = l.rstrip('\n').split('\t')
            if len(f) == 3 and f[0] == 'KNOWN':
                known.append((f[1], f[2]))
        del a[k:k + 2]
    uplant = None
    if '--uplant' in a:
        k = a.index('--uplant'); uplant = a[k + 1]; del a[k:k + 2]
    uctl = None
    if '--plant' in a:
        k = a.index('--plant'); plant = a[k + 1]; del a[k:k + 2]
    R, arms = a[0], a[1:]
    groups = {}
    ctl = None
    for arm in arms:
        reps = arm_reports(R, arm)
        np = [(k, s) for k, s in reps if not is_plant(k, s)]
        pa = sum(1 for k, s in reps if is_plant(k, s) and k.startswith('asan'))
        pu = sum(1 for k, s in reps if is_plant(k, s) and not is_uplant(k, s) and k.startswith('ubsan'))
        pa -= sum(1 for k, s in reps if is_uplant(k, s) and k.startswith('asan'))
        ua = sum(1 for k, s in reps if is_uplant(k, s) and k.startswith('asan'))
        uu = sum(1 for k, s in reps if is_uplant(k, s) and k.startswith('ubsan'))
        if arm == uplant:
            uctl = ua >= 1 and uu >= 1
            print('s7468 arm=%s uplant_asan=%d uplant_ubsan=%d' % (arm, ua, uu))
        for k, s in np:
            groups.setdefault((k, s), set()).add(arm)
        print('s7467 arm=%s reports=%d plant_asan=%d plant_ubsan=%d nonplant=%d nonplant_groups=%d' % (
            arm, len(reps), pa, pu, len(np), len(set(np))))
        if arm == plant:
            ctl = pa >= 1 and pu >= 1
    new = 0
    for (k, s), arms_ in sorted(groups.items()):
        base = re.sub(r':\d+$', '', s.split(' ')[-1]).rsplit('/', 1)[-1]
        kn = any(k.startswith(kp) and base == b for kp, b in known)
        new += 0 if kn else 1
        print('s7467 group kind=%s site=%s arms=%s%s' % (k, s.replace(' ', '@'), ','.join(sorted(arms_)), ' known' if kn else ' NEW'))
    if known:
        print('s7467 new_groups=%d' % new)
    if uplant is not None:
        print('s7468 ucode_control=%s' % ('PASS' if uctl else 'FAIL'))
        if not uctl:
            return 3
    if plant is not None:
        print('s7467 control=%s' % ('PASS' if ctl else 'FAIL'))
        if not ctl:
            return 3
    return 1 if (new if known else groups) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
