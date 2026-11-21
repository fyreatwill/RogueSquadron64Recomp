#!/usr/bin/env python3
"""s7742 fixup_factor5_ucode.py contract gate: idempotent on the live files CMake feeds it, and a fresh-regen tool where it can be.

Why: CMakeLists.txt runs tools/fixup_factor5_ucode.py at every configure on factor5_ucode, factor5_ucode_b and factor5_boot,
and never checked the exit code. s7742 measured: main rc 0 / 0 diff, but ucode_b and boot rc 1 ("FIXUP 24 ANCHOR FAILED (0)":
fixup 24, s4751, anchors on the main file's 0x1DB0 dispatch switch and was not gated on file kind), so any new fixup for those
two files would silently never land. Overlay files (not compiled into anything) would get retail control flow rewritten.
Contract checked here, on private temp copies (build/ is never written):
  A live idempotence: a copy of the live tree, fixup run on main, ucode_b, boot in CMake order -> each rc 0, tree byte-identical.
  B fresh regen: pristine RSPRecomp ucode_b and boot (siblings live) -> fixup -> rc 0 and byte-identical to live.
    (the main file is not fresh-regenerable, s7091: tools/ucode_regen.sh + tools/s7741_ucode_regen_gate.py own it.)
  C refusal: every overlay file -> rc 2, unchanged.
Controls (iron rule 1):
  strip   live main with the s7522 imem-residency hooks removed -> fixup must re-insert them byte-for-byte (proves A's
          "0 diff" comes from a fixup that writes, not one that bails).
  red     a copy of the fixup with the s7742 fixup-24 scope removed -> live boot must exit 1 (the pre-s7742 defect).
Usage: s7742_fixup_idem_gate.py [--controls]   exit 0 GREEN, 1 RED, 2 regen failed, 3 control not caught."""
import filecmp, glob, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import s7741_ucode_regen_gate as g  # noqa: E402

LIVE = g.LIVE
FIXUP = os.path.join(ROOT, 'tools/fixup_factor5_ucode.py')
MAIN, UB, BOOT = 'factor5_ucode_recompiled.c', 'factor5_ucode_b_recompiled.c', 'factor5_boot_recompiled.c'
CMAKE_ORDER = (MAIN, UB, BOOT)
FS = '/* fixup: s7522 imem residency */'


def run(f, script=FIXUP):
    p = subprocess.run([sys.executable, script, f], capture_output=True, text=True)
    return p.returncode, (p.stderr.strip().splitlines() or [''])[-1][:120]


def same(a, b):
    return filecmp.cmp(a, b, shallow=False)


def tree_diff(d):
    return [os.path.basename(f) for f in sorted(glob.glob(os.path.join(LIVE, '*.c')))
            if not os.path.exists(os.path.join(d, os.path.basename(f))) or not same(f, os.path.join(d, os.path.basename(f)))]


def strip_s7522(text):
    o28_new = ("{ rs64_e9prov_ovl_route(0x28, 0x1DB0); if (__builtin_expect(rs64_s7521_on, 0)) "
               "rs64_s7522_ovl28(RSP_MEM_W_LOAD(0X10, r1) + 0x220); r17 = RSP_ADD32(r17, 0X20); goto L_10D8; }")
    o28_old = "{ rs64_e9prov_ovl_route(0x28, 0x1DB0); r17 = RSP_ADD32(r17, 0X20); goto L_10D8; }"
    out = []
    for ln in text.splitlines(keepends=True):
        if FS in ln:
            if ln.startswith('extern "C" int rs64_s7521_on;'):
                continue
            if ln.lstrip().startswith('if (__builtin_expect(rs64_s7521_on, 0)) rs64_s7522_disp('):
                continue
        out.append(ln)
    return ''.join(out).replace(o28_new, o28_old)


def main():
    if not os.path.isdir(LIVE): print('live tree missing:', LIVE); return 2
    tmp = tempfile.mkdtemp(prefix='s7742_')
    rc = 0
    try:
        r = g.regen(tmp)
        if r is None: return 2
        pri, _ = r
        bad = []
        # A
        a = os.path.join(tmp, 'A'); shutil.copytree(LIVE, a)
        for b in CMAKE_ORDER:
            x, msg = run(os.path.join(a, b)); print('A live %-34s rc=%d %s' % (b, x, msg))
            if x: bad.append('A rc %s' % b)
        d = tree_diff(a); print('A tree diff vs live:', d or 'none')
        bad += ['A diff %s' % f for f in d]
        # B
        bdir = os.path.join(tmp, 'B'); shutil.copytree(LIVE, bdir)
        for b in (UB, BOOT):
            shutil.copy(os.path.join(pri, b), os.path.join(bdir, b))
            pre_same = same(os.path.join(bdir, b), os.path.join(LIVE, b))
            x, msg = run(os.path.join(bdir, b))
            ok = x == 0 and same(os.path.join(bdir, b), os.path.join(LIVE, b))
            print('B fresh %-33s pristine==live:%s rc=%d -> %s' % (b, pre_same, x, '== live' if ok else 'DIFFERS ' + msg))
            if pre_same: bad.append('B pristine already live %s' % b)
            if not ok: bad.append('B %s' % b)
        d = tree_diff(bdir); print('B tree diff vs live:', d or 'none'); bad += ['B diff %s' % f for f in d]
        # C
        c = os.path.join(tmp, 'C'); shutil.copytree(LIVE, c)
        ovl = sorted(f for f in os.listdir(c) if f.endswith('.c') and f not in CMAKE_ORDER)
        refused = 0
        for b in ovl:
            x, _ = run(os.path.join(c, b))
            refused += x == 2 and same(os.path.join(c, b), os.path.join(LIVE, b))
        print('C overlays refused unchanged: %d/%d' % (refused, len(ovl)))
        if refused != len(ovl) or not ovl: bad.append('C refusal')
        if '--controls' in sys.argv:
            s = os.path.join(tmp, 'S'); shutil.copytree(LIVE, s)
            live_main = open(os.path.join(LIVE, MAIN)).read()
            stripped = strip_s7522(live_main)
            open(os.path.join(s, MAIN), 'w').write(stripped)
            x, _ = run(os.path.join(s, MAIN))
            ok = stripped != live_main and FS not in stripped and x == 0 and same(os.path.join(s, MAIN), os.path.join(LIVE, MAIN))
            print('control strip  removed %d line(s) -> rc=%d %s' % (live_main.count('\n') - stripped.count('\n'), x,
                                                                    'restored == live (caught)' if ok else 'NOT CAUGHT'))
            if not ok: rc = 3
            red = os.path.join(tmp, 'red_fixup.py')
            src = open(FIXUP).read()
            scoped = 'if is_main_ucode and OVL2C_DROP_MARKER not in text'
            open(red, 'w').write(src.replace(scoped, 'if OVL2C_DROP_MARKER not in text', 1))
            rd = os.path.join(tmp, 'R'); shutil.copytree(LIVE, rd)
            x, msg = run(os.path.join(rd, BOOT), red)
            ok = scoped in src and x == 1 and 'FIXUP 24' in msg
            print('control red    unscoped fixup 24 on live boot -> rc=%d %s %s' % (x, msg, '(caught)' if ok else 'NOT CAUGHT'))
            if not ok: rc = 3
            print('CONTROL', 'PASS' if rc == 0 else 'FAIL')
        if bad:
            print('VERDICT RED:', '; '.join(bad)); return rc or 1
        print('VERDICT GREEN: fixup idempotent on %d CMake files, fresh-regen ucode_b+boot == live, %d overlays refused'
              % (len(CMAKE_ORDER), len(ovl)))
        return rc
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
