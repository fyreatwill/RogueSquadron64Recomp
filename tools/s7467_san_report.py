#!/usr/bin/env python3
"""s7467 class DW: score an ASan+UBSan soak (tools/build_asan.sh build, scratch/agent/soak_queue/s7467_asan_flight.sh).

usage: s7467_san_report.py <R dir> <arm>... [--plant <arm>] [--known tools/s7467_san_reviewed.tsv]
--known: groups matching a KNOWN (kind prefix, file basename) row are reviewed; exit 1 only on a NEW group.
Per arm reads <R>/san_<arm>.* (ASAN_OPTIONS/UBSAN_OPTIONS log_path) and <R>/log_<arm>.txt (stderr fallback).
Groups reports by (kind, first frame in our code). The plant arm must show BOTH planted reports
(heap-buffer-overflow in rs64_s7467_asan_plant, signed-integer-overflow at the plant line) = positive control.
Prints one line per arm and one line per non-plant group; exit 0 = control PASS and 0 non-plant groups,
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


def is_plant(kind, site):
    # The plant is inlined into main(), so match by source line, not function name.
    if 'main.cpp' not in site or not _plant_line(site):
        return False
    return kind == 'asan:heap-buffer-overflow' or kind.startswith('ubsan:signed integer overflow')


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
    if '--plant' in a:
        k = a.index('--plant'); plant = a[k + 1]; del a[k:k + 2]
    R, arms = a[0], a[1:]
    groups = {}
    ctl = None
    for arm in arms:
        reps = arm_reports(R, arm)
        np = [(k, s) for k, s in reps if not is_plant(k, s)]
        pa = sum(1 for k, s in reps if is_plant(k, s) and k.startswith('asan'))
        pu = sum(1 for k, s in reps if is_plant(k, s) and k.startswith('ubsan'))
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
    if plant is not None:
        print('s7467 control=%s' % ('PASS' if ctl else 'FAIL'))
        if not ctl:
            return 3
    return 1 if (new if known else groups) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
