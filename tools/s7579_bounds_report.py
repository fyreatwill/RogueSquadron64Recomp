#!/usr/bin/env python3
"""s7579: group UBSan reports from build_ubsanb arms (tools/build_ubsanc.sh SAN=array-bounds,signed-integer-overflow).

usage: tools/s7579_bounds_report.py <dir> [--plant-arm p2]
Reads <dir>/san_<arm>.* (UBSAN_OPTIONS log_path files), classifies each "runtime error:" line as bounds (index ... out of
bounds) or overflow, groups by file:line per arm. Exit 0 = plant arm reported the s7578_ubsanc_plant.h bounds control AND no
non-plant report in any arm; 1 = a real report (H-diag-oob / H-game-oob, listed); 2 = control did not fire (null is void).
"""
import glob, os, re, sys, collections

def main():
    d = sys.argv[1]; plant = 'p2'
    if '--plant-arm' in sys.argv: plant = sys.argv[sys.argv.index('--plant-arm') + 1]
    rx = re.compile(r'^(\S+?):(\d+):\d+: runtime error: (.*)$')
    per = collections.defaultdict(collections.Counter); ctl = False
    for f in sorted(glob.glob(os.path.join(d, 'san_*'))):
        arm = os.path.basename(f)[4:].split('.')[0]
        for ln in open(f, errors='replace'):
            m = rx.match(ln.strip())
            if not m: continue
            path, line, msg = m.groups()
            kind = 'bounds' if 'out of bounds' in msg else ('overflow' if 'overflow' in msg else 'other')
            if 's7578_ubsanc_plant.h' in path:
                if arm == plant and kind == 'bounds': ctl = True
                continue
            per[arm][(os.path.basename(path), int(line), kind, msg[:90])] += 1
    real = 0
    for arm in sorted(per):
        for (p, l, k, msg), n in per[arm].most_common():
            real += 1; print(f'{arm} {k} {p}:{l} x{n} {msg}')
    print(f'control_fired={int(ctl)} real_sites={real} arms_with_logs={len(set(os.path.basename(f)[4:].split(".")[0] for f in glob.glob(os.path.join(d, "san_*"))))}')
    sys.exit(2 if not ctl else (1 if real else 0))

if __name__ == '__main__':
    main()
