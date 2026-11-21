#!/usr/bin/env python3
"""s7719 regen-replay drift gate (class GR/CF/H-lost as one live gate).

Does a pristine regen + the whole fixup chain (tools/regen_replay.sh) still reproduce the LIVE RecompiledFuncs tree?
Before s7719 this was only answerable by hand (s7421/s7423 need a fresh replay tree; the last one was s7558, ~160 sessions
old), so the sweep could not see drift. This gate builds the replay itself, text level only (no compile, one CPU):
  1. tools/regen_front.sh  -> pristine N64Recomp output (make_elf -> N64Recomp, real sizes)   (~1 s)
  2. RS64_REPLAY_TREE_ONLY=1 tools/regen_replay.sh on a copy  (fixer chain + rename, no host-code census gates)  (~3.5 min)
  3. tools/s7423_live_stale.py <live> <replay> --control            regen-only statements = patches the live build lacks
  4. tools/s7423_live_stale.py <live> <replay> --reverse --control  live-only statements = hand edits that die at regen
Both scans walk every function and carry planted controls (guest store -> BEHAVIOUR, env-gated print -> DIAG, known lines).
  5. (s7735) tools/s7734_compiled_reader_census.py --tree <replay>: every compiled ROGUESQ_* reading of the REPLAYED tree models
     to a live script/host signature (0 unreviewed HIDDEN/NOREF), plus a planted control: the replay's funcs_23 B40 line put
     back to its pre-s7734 form must read HIDDEN. Catches a fixup that stops reproducing a hand-synced compiled reading.
  6. (s7740, --strict) byte identity: every source file (*.c *.h *.cpp *.inl) of live and replay must be identical and present on
     both sides. Since s7739 live == replay byte-for-byte, so ANY difference is a hand edit or a fixup that stopped reproducing.
     Controls: a symlink farm of live with one planted line in one file, and one with an extra file, must each read exactly that
     one file. The sweep runs --strict.
VERDICT H-mirrored: both directions have 0 open BEHAVIOUR rows and both controls PASS. rc 0 ok, 1 drift, 3 control/chain fail.
usage: s7719_regen_gate.py [--strict] [--live ../N64Recomp/RecompiledFuncs] [--tree <existing replay dir>] [--keep <dir>]
"""
import os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sh(cmd, env=None):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env=dict(os.environ, **(env or {})))
    return p.returncode, p.stdout + p.stderr


B40_NEW = 'getenv("ROGUESQ_M5_B40_VALUE")[0] && getenv("ROGUESQ_M5_B40_VALUE")[0] != \'0\') ? ctx->r2 : 0)'
B40_OLD = 'getenv("ROGUESQ_M5_B40_VALUE")[0] == \'0\') ? 0 : ctx->r2)'


def reader_census(tree, tmp):
    """s7735: s7734 census on the replay tree (rc 0 wanted) + planted pre-s7734 B40 reading (must read HIDDEN, rc 1)."""
    rc, out = sh([sys.executable, 'tools/s7734_compiled_reader_census.py', '--tree', tree])
    tail = [l for l in out.splitlines() if l.startswith(('distinct', 'unreviewed', 'HIDDEN', 'NOREF', 'control', 'skip'))]
    for l in tail:
        print('reader: %s' % l[:240])
    ctl = os.path.join(tmp, 'reader_ctl')
    shutil.rmtree(ctl, ignore_errors=True); os.makedirs(ctl)
    hit = 0
    for f in sorted(os.listdir(tree)):
        src = os.path.join(tree, f)
        if not f.endswith('.c'):
            continue
        txt = open(src, errors='replace').read()
        if B40_NEW in txt:
            hit += txt.count(B40_NEW)
            open(os.path.join(ctl, f), 'w').write(txt.replace(B40_NEW, B40_OLD))
        else:
            os.symlink(os.path.abspath(src), os.path.join(ctl, f))
    crc, cout = sh([sys.executable, 'tools/s7734_compiled_reader_census.py', '--tree', ctl])
    ok = hit > 0 and crc == 1 and 'HIDDEN ROGUESQ_M5_B40_VALUE' in cout
    print('reader: CONTROL planted pre-s7734 B40 line (%d site) -> rc %d %s' % (hit, crc, 'PASS' if ok else 'FAIL'))
    shutil.rmtree(ctl, ignore_errors=True)
    if not ok:
        return 3
    return 0 if rc == 0 and 'skip' not in out else 1


SRC_EXT = ('.c', '.h', '.cpp', '.inl')


def strict_diff(live, tree):
    """s7740: names of source files that differ or exist on one side only (byte compare)."""
    names = lambda d: {f for f in os.listdir(d) if f.endswith(SRC_EXT) and os.path.isfile(os.path.join(d, f))}
    L, R = names(live), names(tree)
    bad = sorted('only-live:' + f for f in L - R) + sorted('only-replay:' + f for f in R - L)
    for f in sorted(L & R):
        with open(os.path.join(live, f), 'rb') as x, open(os.path.join(tree, f), 'rb') as y:
            if x.read() != y.read():
                bad.append('differs:' + f)
    return bad


def strict_gate(live, tree, tmp):
    """rc 0 identical + controls PASS, 1 any difference, 3 control fail."""
    bad = strict_diff(live, tree)
    print('strict: %d source files compared, %d differ%s' % (
        len([f for f in os.listdir(live) if f.endswith(SRC_EXT)]), len(bad), (' ' + ' '.join(bad[:12])) if bad else ''))
    ok = True
    for kind in ('edit', 'extra'):
        farm = os.path.join(tmp, 'strict_ctl_' + kind)
        shutil.rmtree(farm, ignore_errors=True); os.makedirs(farm)
        cs = sorted(f for f in os.listdir(live) if f.endswith('.c'))
        victim = cs[len(cs) // 2]
        for f in os.listdir(live):
            if not f.endswith(SRC_EXT):
                continue
            if kind == 'edit' and f == victim:
                open(os.path.join(farm, f), 'w').write(open(os.path.join(live, f), errors='replace').read() + '/* s7740 planted */\n')
            else:
                os.symlink(os.path.abspath(os.path.join(live, f)), os.path.join(farm, f))
        want = ['differs:' + victim]
        if kind == 'extra':
            open(os.path.join(farm, 'funcs_s7740_planted.c'), 'w').write('int s7740;\n')
            want = ['only-live:funcs_s7740_planted.c']
        got = strict_diff(farm, tree)
        # the planted farm must show exactly the plant on top of whatever the real tree already shows
        hit = set(want) <= set(got) and set(got) == set(bad) | set(want)
        print('strict: CONTROL planted %s (%s) -> %s %s' % (kind, want[0], len(got), 'PASS' if hit else 'FAIL'))
        ok &= hit
        shutil.rmtree(farm, ignore_errors=True)
    if not ok:
        return 3
    return 1 if bad else 0


def main(a):
    live = a[a.index('--live') + 1] if '--live' in a else os.path.join(ROOT, '..', 'N64Recomp', 'RecompiledFuncs')
    tmp = None
    if '--tree' in a:
        tree = a[a.index('--tree') + 1]
    else:
        tmp = a[a.index('--keep') + 1] if '--keep' in a else tempfile.mkdtemp(prefix='s7719gate')
        pr, tree = os.path.join(tmp, 'pristine'), os.path.join(tmp, 'replay')
        for d in (pr, pr + '.work', tree):
            shutil.rmtree(d, ignore_errors=True)
        rc, out = sh(['zsh', 'tools/regen_front.sh', pr])
        print(out.strip().splitlines()[-1] if out.strip() else 'regen_front: no output')
        if rc:
            print('VERDICT CHAIN-FAIL (regen_front rc %d)' % rc); return 3
        shutil.copytree(pr, tree)
        rc, out = sh(['zsh', 'tools/regen_replay.sh', tree, os.path.join(tmp, 'replay.log')], {'RS64_REPLAY_TREE_ONLY': '1'})
        print(out.strip())
        if rc:
            print('VERDICT CHAIN-FAIL (regen_replay rc %d, log %s)' % (rc, os.path.join(tmp, 'replay.log'))); return 3
    res = {}
    for name, extra in (('forward', []), ('reverse', ['--reverse'])):
        rc, out = sh([sys.executable, 'tools/s7423_live_stale.py', live, tree, '--control'] + extra)
        keep = [l for l in out.splitlines() if l.startswith(('CONTROL', 'OPEN', 'VERDICT', 'class counts'))]
        for l in keep:
            print('%s: %s' % (name, l[:240]))
        res[name] = rc
        if name == 'reverse':  # s7737: a DIAG row whose live-only probe a live tool/recipe still reads = the next regen loses it
            rp = os.path.join(tmp or tempfile.gettempdir(), 's7737_rev.txt'); open(rp, 'w').write(out)
            rc2, out2 = sh([sys.executable, 'tools/s7737_diag_consumers.py', rp, live, tree, '--control'])
            for l in out2.splitlines():
                if l.startswith(('CONTROL', 'rows', 'VERDICT', 'CONSUMED')): print('diag-consumers: %s' % l[:240])
            res['diag-consumers'] = rc2
    res['reader'] = reader_census(tree, tmp or tempfile.mkdtemp(prefix='s7735ctl'))
    if '--strict' in a:
        res['strict'] = strict_gate(live, tree, tmp or tempfile.mkdtemp(prefix='s7740ctl'))
    if tmp and '--keep' not in a:
        shutil.rmtree(tmp, ignore_errors=True)
    if 3 in res.values():
        print('VERDICT CONTROL-FAIL', res); return 3
    if any(res.values()):
        print('VERDICT H-drift', res, '(forward = live build lacks a fixup line; diag-consumers = a live-only probe a live tool reads; reverse = live hand edit no fixup reproduces; reader = replay tree reads an env differently; strict = a source file is not byte-identical to the replay)')
        return 1
    print('VERDICT H-mirrored (forward and reverse: 0 open BEHAVIOUR, replay readers 0 HIDDEN, %scontrols PASS)' % ('live == replay byte-for-byte, ' if '--strict' in a else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
