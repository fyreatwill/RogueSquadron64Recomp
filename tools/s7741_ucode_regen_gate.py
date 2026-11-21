#!/usr/bin/env python3
"""s7741 strict ucode regen gate: build/factor5_ucode == fresh RSPRecomp pass + tools/ucode_fixed/*.patch, byte-for-byte.

Why: s7740 made the RecompiledFuncs regen gate strict, but nothing re-ran tools/ucode_regen.sh verify. s7741 found
factor5_ucode_recompiled.c DIFF (4 lines: the s7522 imem-residency hooks fixup_factor5_ucode.py added on 2026-11-17 after
the 2026-11-16 patch snapshot), so a fresh rebuild of build/ (gitignored) would have silently lost them.
This runs the whole regen in a private temp dir (does not touch scratch/ucode_regen, which s7093/s7507 read), then requires:
  - the live file set == the regenerated file set == the patch target set (no one-sided file),
  - every file byte-identical,
  - tools/s7091_ucode_insn_census.py on pristine vs regenerated: 0 unexplained, 0 splice breaks.
Controls (iron rule 1), on a scratch copy of the live tree: a planted comment line, an extra file and a missing file must
each read RED, and the unplanted copy GREEN.
Fix for a RED: if fixup_factor5_ucode.py changed on purpose, `zsh tools/ucode_regen.sh snapshot`; else fold the hand edit
into tools/fixup_factor5_ucode.py.
Usage: s7741_ucode_regen_gate.py [--controls]   exit 0 GREEN, 1 RED, 2 regen failed, 3 control not caught."""
import filecmp, glob, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE = os.path.join(ROOT, 'build/factor5_ucode')
RSPRECOMP = os.environ.get('RSPRECOMP', os.path.join(ROOT, '../N64Recomp/build/RSPRecomp'))
TOMLS = sorted(glob.glob(os.path.join(ROOT, 'factor5_rsp*.toml')) + [os.path.join(ROOT, 'factor5b_rsp.toml'),
                                                                     os.path.join(ROOT, 'factor5_boot_rsp.toml')])
PATCHES = sorted(glob.glob(os.path.join(ROOT, 'tools/ucode_fixed/*.patch')))


def regen(tmp):
    pri, res = os.path.join(tmp, 'pristine'), os.path.join(tmp, 'result')
    os.makedirs(pri); os.makedirs(res)
    for t in TOMLS:
        txt = open(t).read()
        m = re.search(r'^output_file_path = "build/factor5_ucode/(.*)"', txt, re.M)
        if not m: print('no output_file_path in', t); return None
        txt = re.sub(r'^output_file_path = ".*"', 'output_file_path = "%s/%s"' % (pri, m.group(1)), txt, flags=re.M)
        txt = re.sub(r'^rom_file_path = "(.*)"', lambda r: 'rom_file_path = "%s"' % os.path.join(ROOT, r.group(1)), txt, flags=re.M)
        tt = os.path.join(tmp, os.path.basename(t))
        open(tt, 'w').write(txt)
        p = subprocess.run([RSPRECOMP, tt], cwd=ROOT, capture_output=True, text=True)
        if p.returncode: print('RSPRecomp failed:', os.path.basename(t), p.stdout[-300:], p.stderr[-300:]); return None
    for f in glob.glob(os.path.join(pri, '*.c')): shutil.copy(f, res)
    for pt in PATCHES:
        tgt = os.path.join(res, os.path.basename(pt)[:-len('.patch')])
        if not os.path.exists(tgt): print('patch without regenerated target:', os.path.basename(pt)); return None
        p = subprocess.run(['patch', '-s', tgt], stdin=open(pt), capture_output=True, text=True)
        if p.returncode: print('patch failed:', os.path.basename(pt), p.stdout[-300:]); return None
    return pri, res


def compare(res, live):
    a = {os.path.basename(f) for f in glob.glob(os.path.join(res, '*.c'))}
    b = {os.path.basename(f) for f in glob.glob(os.path.join(live, '*.c'))}
    rows = ['ONLY-REGEN %s' % f for f in sorted(a - b)] + ['ONLY-LIVE %s' % f for f in sorted(b - a)]
    rows += ['DIFF %s' % f for f in sorted(a & b) if not filecmp.cmp(os.path.join(res, f), os.path.join(live, f), shallow=False)]
    return rows, len(a & b)


def main():
    if not os.path.isdir(LIVE): print('live tree missing:', LIVE); return 2
    tmp = tempfile.mkdtemp(prefix='s7741_')
    try:
        r = regen(tmp)
        if r is None: return 2
        pri, res = r
        rc = 0
        if '--controls' in sys.argv:
            farm = os.path.join(tmp, 'farm')
            cases = {'clean': lambda d: None,
                     'planted-line': lambda d: open(os.path.join(d, 'factor5_ucode_recompiled.c'), 'a').write('/* s7741 plant */\n'),
                     'extra-file': lambda d: open(os.path.join(d, 'factor5_s7741_extra.c'), 'w').write('\n'),
                     'missing-file': lambda d: os.remove(os.path.join(d, 'factor5_boot_recompiled.c'))}
            for name, plant in cases.items():
                shutil.rmtree(farm, ignore_errors=True); shutil.copytree(LIVE, farm); plant(farm)
                rows, _ = compare(res, farm)
                ok = (not rows) if name == 'clean' else bool(rows)
                print('control %-13s rows=%d %s' % (name, len(rows), 'caught' if ok else 'NOT CAUGHT'))
                if not ok: rc = 3
            print('CONTROL', 'PASS' if rc == 0 else 'FAIL')
        rows, same = compare(res, LIVE)
        for x in rows: print(x)
        cen = subprocess.run([sys.executable, os.path.join(ROOT, 'tools/s7091_ucode_insn_census.py'), pri, res],
                             capture_output=True, text=True)
        v = [l for l in cen.stdout.splitlines() if l.startswith('verdict')]
        cen_ok = cen.returncode == 0 and v and re.search(r'\b0 unexplained, 0 splice breaks', v[0])
        print('census:', v[0] if v else 'no verdict (rc %d)' % cen.returncode)
        if rows or not cen_ok:
            print('VERDICT RED: %d row(s) live vs regen%s' % (len(rows), '' if cen_ok else ', census not clean'))
            return rc or 1
        print('VERDICT GREEN: %d files, live == regen byte-for-byte, %d patches, census clean' % (same, len(PATCHES)))
        return rc
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
