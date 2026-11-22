#!/usr/bin/env python3
"""s7805: argv-borne retained-format check (companion of s7804_zst_blind_lint).

s7804 lints tools whose capture path is a source literal. This one covers paths
that only travel on the command line: every command cited in the docs of the
shape `[python3 [-I]] tools/X.py ... scratch/...` whose scratch/ argument
resolves ONLY as <path>.zst (raw deleted by s7780 retention) is run once; a
traceback / FileNotFoundError / "No such file" in its output = RED (the s7616
failure mode). Raw-present and gone (neither raw nor .zst) arguments are
counted, not run. Commands that time out are UNRUNNABLE (not a verdict).

Controls (same run, planted tools + a planted doc in a temp dir):
  RAW-opener over a zst-only arg -> RED; rs64_zopen-opener -> GREEN.

Usage: s7805_cited_cmd_zst_check.py [--docs a.md b.md ...] [--timeout 60]
Exit 0 iff controls PASS and 0 RED.
"""
import os, re, shlex, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DOCS = ['docs/CURRENT-TRUTH.md', 'docs/OWNER-OPT-INS.md', 'docs/OWNER-REVIEW-QUEUE.md',
                'docs/PROJECT-OVERVIEW.md', 'PORTING-STATE.md', 'scratch/agent/NEXT.md']
CMD = re.compile(r'(?:python3 (?:-I )?)?(tools/[A-Za-z0-9_]+\.py)((?:[ \t]+[^\s`|;]+)*)')
FAIL = re.compile(r'FileNotFoundError|No such file or directory')
TRACE = re.compile(r'Traceback \(most recent call last\)')
GLOBBY = set('*{?<>$')


def classify(arg, base):
    a = arg.strip('(),.:\'"[]')
    if '=scratch/' in a:
        a = a.split('=', 1)[1]
    if not a.startswith('scratch/'):
        return None, a
    if any(c in a for c in GLOBBY):
        return 'glob', a
    p = os.path.join(base, a)
    if os.path.exists(p):
        return 'raw', a
    if os.path.exists(p + '.zst'):
        return 'zst', a
    return 'gone', a


def scan(docs, base):
    """-> counts, candidates[(doc, line, tool, argv_list, zst_args)]"""
    counts, cands, seen = {}, [], set()
    for d in docs:
        path = os.path.join(base, d) if not os.path.isabs(d) else d
        if not os.path.exists(path):
            continue
        for ln, line in enumerate(open(path, errors='replace'), 1):
            for m in CMD.finditer(line):
                tool, args = m.group(1), m.group(2).split()
                zs, ok = [], True
                for a in args:
                    k, a2 = classify(a, base)
                    if k is None:
                        continue
                    counts[k] = counts.get(k, 0) + 1
                    if k == 'zst':
                        zs.append(a2)
                    if k in ('gone', 'glob'):
                        ok = False
                if not zs:
                    continue
                # argv = flags, the value right after a flag, and scratch/ paths; prose words dropped.
                keep, prev_flag = [], False
                for a in args:
                    a2 = a.strip('(),.:\'"')
                    if a2.startswith('--') or re.fullmatch(r'-[A-Za-z]', a2):
                        keep.append(a2); prev_flag = True; continue
                    if a2.startswith('scratch/') or '=scratch/' in a2:
                        keep.append(a2)
                    elif prev_flag and re.fullmatch(r'[\w.:=/-]+', a2) and not a2.startswith('->'):
                        keep.append(a2)
                    prev_flag = False
                key = (tool, tuple(keep))
                if key in seen:
                    continue
                seen.add(key)
                cands.append((d, ln, tool, keep, zs, ok))
    return counts, cands


MUTATOR = re.compile(r'tools/(apply_|fixup_|make_|rename)')


def run(tool, argv, base, timeout):
    if not os.path.exists(os.path.join(base, tool)):
        return 'NOTOOL', ''
    if MUTATOR.match(tool):
        return 'SKIP-MUTATOR', 'edits generated code; not run'
    try:
        p = subprocess.run([sys.executable, tool] + argv, cwd=base, capture_output=True, text=True,
                           timeout=timeout, errors='replace')
    except subprocess.TimeoutExpired:
        return 'UNRUNNABLE', 'timeout'
    out = (p.stdout or '') + (p.stderr or '')
    m = FAIL.search(out)
    if m:
        tail = [l for l in out.splitlines() if l.strip()][-1:] or ['']
        return 'RED', tail[0][:160]
    if TRACE.search(out):  # crashed for another reason (e.g. the ledger line omits required argv): not a format verdict
        tail = [l for l in out.splitlines() if l.strip()][-1:] or ['']
        return 'ERR-OTHER', tail[0][:160]
    if p.returncode == 2 and re.search(r'^usage: |: error: ', out, re.M):  # argparse: the ledger line omits argv values
        return 'ERR-ARGV', [l for l in out.splitlines() if l.strip()][-1][:160]
    if 'STALE-BINARY' in out:  # replay bound to the binary the capture came from (s7427 atos symbolization)
        return 'ERR-STALE', 'needs the capture-time binary'
    return 'GREEN', 'rc=%d' % p.returncode


def controls(timeout):
    res = []
    with tempfile.TemporaryDirectory(prefix='s7805ctl') as t:
        os.makedirs(os.path.join(t, 'tools')); os.makedirs(os.path.join(t, 'scratch/ctl'))
        import shutil
        shutil.copy(os.path.join(ROOT, 'tools/rs64_zopen.py'), os.path.join(t, 'tools'))
        raw = os.path.join(t, 'scratch/ctl/in.txt')
        open(raw, 'w').write('hello\n')
        subprocess.run(['zstd', '-q', '--rm', raw], check=True)
        open(os.path.join(t, 'tools/ctl_raw.py'), 'w').write(
            'import sys\nprint(len(open(sys.argv[1]).read()))\n')
        open(os.path.join(t, 'tools/ctl_zopen.py'), 'w').write(
            'import sys,os\nsys.path.insert(0,os.path.dirname(__file__))\nfrom rs64_zopen import zopen\n'
            'print(len(zopen(sys.argv[1]).read()))\n')
        open(os.path.join(t, 'doc.md'), 'w').write(
            'run `python3 tools/ctl_raw.py scratch/ctl/in.txt` then\n'
            'run `python3 tools/ctl_zopen.py scratch/ctl/in.txt`.\n')
        _, cands = scan([os.path.join(t, 'doc.md')], t)
        got = {c[2]: run(c[2], c[3], t, timeout)[0] for c in cands}
        res = (got.get('tools/ctl_raw.py'), got.get('tools/ctl_zopen.py'))
    return res, res == ('RED', 'GREEN')


def main():
    a = sys.argv[1:]
    docs, timeout = DEFAULT_DOCS, 60
    if '--timeout' in a:
        timeout = int(a[a.index('--timeout') + 1])
    if '--docs' in a:
        i = a.index('--docs') + 1
        docs = []
        while i < len(a) and not a[i].startswith('--'):
            docs.append(a[i]); i += 1
    ctl, ok = controls(timeout)
    print('CONTROL (raw-opener, zopen-opener) =', ctl, 'PASS' if ok else 'FAIL')
    counts, cands = scan(docs, ROOT)
    print('args:', ' '.join('%s=%d' % kv for kv in sorted(counts.items())), 'zst-only commands=%d' % len(cands))
    tally = {}
    for d, ln, tool, argv, zs, _ in cands:
        v, why = run(tool, argv, ROOT, timeout)
        tally[v] = tally.get(v, 0) + 1
        print('%-10s %s:%d %s %s  [%s]' % (v, d, ln, tool, ' '.join(argv)[:110], why))
    print('TALLY', ' '.join('%s=%d' % kv for kv in sorted(tally.items())))
    red = tally.get('RED', 0)
    if not ok:
        print('VERDICT CONTROL-FAIL'); return 2
    print('VERDICT %s: %d cited commands crash on zst-only args' % ('GREEN' if red == 0 else 'RED', red))
    return 0 if red == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
