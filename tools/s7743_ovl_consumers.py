#!/usr/bin/env python3
"""s7743: who consumes the 9 overlay ucode translations (build/factor5_ucode/factor5_ucode_ovl*_recompiled.c)?

s7742 found no CMakeLists.txt/src reference to them (they are not compiled). Hypotheses:
  H-dead        nothing reads them; only the regen gates carry them -> deletable.
  H-tool-input  something reads them as an input or oracle, so they must stay byte-true.
Arms (all in private temp dirs; build/ and scratch/ucode_regen are only read):
  A configure: tools/fixup_factor5_ucode.py on a copy of live main WITHOUT any overlay beside it -> rc and byte-identity
    (what CMake runs at every configure). Positive control per overlay: strip that overlay's splice marker from the
    copy -> the fixup must exit 1 with "INPUT MISSING" naming that overlay file (it reads it to re-splice).
  B oracle: tools/s7091_ucode_insn_census.py <pristine> <live> with all overlays vs with the overlays removed from the
    pristine copy. Positive control: its verdict must change (spliced records lose their source).
  C static: which tools/*.py|sh|zsh name an overlay file (per overlay id).
Usage: s7743_ovl_consumers.py   exit 0 = measured (controls fired), 3 = a control did not fire."""
import glob, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE = os.path.join(ROOT, 'build/factor5_ucode')
PRI = os.path.join(ROOT, 'scratch/ucode_regen/pristine')
FIX = os.path.join(ROOT, 'tools/fixup_factor5_ucode.py')
CEN = os.path.join(ROOT, 'tools/s7091_ucode_insn_census.py')
MAIN = 'factor5_ucode_recompiled.c'
OVLS = ['4', '10', '12', '14', '18', '1c', '20', '24', '2c']
MARK = {o: ('/* fixup: clipsplice */' if o == '4' else None) for o in OVLS}


def markers():
    src = open(FIX).read()
    for o in OVLS:
        if MARK[o]: continue
        m = re.search(r'^OVL%s_MARKER\s*=\s*"([^"]+)"' % o.upper(), src, re.M)
        MARK[o] = m.group(1) if m else None


def run_fix(d):
    p = subprocess.run([sys.executable, FIX, os.path.join(d, MAIN)], capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr)


def arm_a(tmp):
    bad = 0
    d = os.path.join(tmp, 'a_clean'); os.makedirs(d)
    shutil.copy(os.path.join(LIVE, MAIN), d)
    rc, out = run_fix(d)
    same = open(os.path.join(d, MAIN), 'rb').read() == open(os.path.join(LIVE, MAIN), 'rb').read()
    print('A clean (no overlays present): rc=%d byte_identical=%d' % (rc, same))
    live_text = open(os.path.join(LIVE, MAIN)).read()
    for o in OVLS:
        mk = MARK[o]
        d = os.path.join(tmp, 'a_' + o); os.makedirs(d)
        n = live_text.count(mk) if mk else 0
        open(os.path.join(d, MAIN), 'w').write(live_text.replace(mk, '/* stripped */') if mk else live_text)
        rc, out = run_fix(d)
        named = ('INPUT MISSING' in out) and ('factor5_ucode_ovl%s_recompiled.c' % o in out or 'factor5_rsp_ovl%s.toml' % o in out)
        fired = rc == 1 and named
        bad += not fired
        print('A ctl ovl%-3s marker=%r count=%d -> rc=%d input_missing_named=%d %s' %
              (o, mk, n, rc, named, 'FIRED' if fired else 'NOT-FIRED'))
    return bad


def census(pri, live):
    p = subprocess.run([sys.executable, CEN, pri, live], capture_output=True, text=True)
    v = [l for l in (p.stdout + p.stderr).splitlines() if l.startswith('verdict')]
    return p.returncode, (v[-1] if v else (p.stdout + p.stderr).strip().splitlines()[-1:])


def arm_b(tmp):
    full = os.path.join(tmp, 'b_full'); stripped = os.path.join(tmp, 'b_noovl')
    shutil.copytree(PRI, full); shutil.copytree(PRI, stripped)
    for f in glob.glob(os.path.join(stripped, 'factor5_ucode_ovl*_recompiled.c')):
        if not f.endswith('ovl20_recompiled.c'):  # ovl20 is itself a compared FILE; keep it so only the oracle role is cut
            os.remove(f)
    r1, v1 = census(full, LIVE); r2, v2 = census(stripped, LIVE)
    print('B s7091 census, all overlays : rc=%d %s' % (r1, v1))
    print('B s7091 census, 8 removed    : rc=%d %s' % (r2, v2))
    changed = (r1, v1) != (r2, v2)
    print('B oracle role %s' % ('CONFIRMED (output changed)' if changed else 'NOT SEEN (output unchanged)'))
    return 0 if changed else 1


def arm_c():
    files = [f for e in ('py', 'sh', 'zsh') for f in glob.glob(os.path.join(ROOT, 'tools', '*.' + e))]
    files = [f for f in files if not f.endswith('s7743_ovl_consumers.py')]
    for o in OVLS:
        pat = re.compile(r'ovl%s_recompiled|ucode_ovl%s\b|[\'"]ovl%s[\'"]|ucode_ovl\*|ucode_ovl%%s|ucode_ovl\{' % (o, o, o))
        hit = sorted(os.path.basename(f) for f in files if pat.search(open(f, errors='replace').read()))
        print('C ovl%-3s readers(%d): %s' % (o, len(hit), ' '.join(hit)))


def main():
    markers()
    missing = [o for o in OVLS if not MARK[o]]
    if missing: print('no marker constant for', missing)
    with tempfile.TemporaryDirectory(prefix='s7743_') as tmp:
        a = arm_a(tmp); b = arm_b(tmp)
    arm_c()
    verdict = ('H-tool-input' if a == 0 and b == 0 else 'controls-incomplete')
    print('verdict=%s a_not_fired=%d b_not_seen=%d' % (verdict, a, b))
    return 0 if verdict == 'H-tool-input' else 3


if __name__ == '__main__':
    sys.exit(main())
