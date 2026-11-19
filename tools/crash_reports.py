#!/usr/bin/env python3
"""s7664: classify macOS crash reports (.ips) of the game so no crash goes unread.

Nothing in the loop read ~/Library/Logs/DiagnosticReports: 8 game reports from 2026-11-15..19 were never folded
(s6534 was the last manual look). An owner crash in normal play would be missed the same way.

Usage:
  python3 tools/crash_reports.py [--since YYYY-MM-DD] [--dir DIR] [--ledger PORTING-STATE.md] [--selftest]
Exit: 0 = every report classified as a known plant / diag-instrument / folded; 1 = at least one NEW report
(read its frames, fold it into the ledger by quoting its basename, e.g. RogueSquadron64Recomp-2026-11-17-053804).

Classes (first match wins):
  FOLDED   the report basename (or its timestamp) is already quoted in the ledger
  PLANT    a deliberate positive control: raise()/exit() reached from rs64_diag_plant*/rs64_store_diag_tick, a
           [s7593] at_quick_exit plant, or the s7660-style injected SIGSEGV (EXC_CRASH on a sleeping main thread)
  DIAG     the faulting frame is inside an env-gated instrument (rs64_sNNNN_* / s7523 model / store tracer): an
           instrument defect, not a game defect; still printed so a recurring one gets fixed
  NEW      everything else: a candidate real crash
"""
import argparse, glob, json, os, re, sys, tempfile

PLANT_FRAMES = re.compile(r'rs64_diag_plant|rs64_store_diag_tick|s7450_plant|s7593')
DIAG_FRAME = re.compile(r'^rs64_s\d{4}_|^\(anonymous namespace\)::(consume|on_read|push|scan_bad)\b')
SIG_FRAMES = {'__pthread_kill', 'pthread_kill', 'raise', 'abort', '__abort_message', 'demangling_terminate_handler()',
              'std::__terminate(void (*)())', 'std::terminate()', '__cxa_finalize_ranges', 'exit'}


def load(path):
    txt = open(path, errors='replace').read()
    head, _, body = txt.partition('\n')
    try:
        return json.loads(head), json.loads(body)
    except ValueError:
        return None, None


def frames(b, ti):
    th = b['threads'][ti]
    imgs = b.get('usedImages', [])
    out = []
    for fr in th.get('frames', []):
        img = imgs[fr['imageIndex']].get('name', '?') if fr.get('imageIndex', -1) < len(imgs) else '?'
        out.append((fr.get('symbol') or ('+0x%x' % fr.get('imageOffset', 0)), img))
    return th, out


def classify(name, b, ledger):
    stamp = re.sub(r'(\.\d+)?\.ips$', '', name.replace('RogueSquadron64Recomp-', ''))   # .000.ips = duplicate report
    ex = b.get('exception', {})
    ft = b.get('faultingThread', 0)
    th, fr = frames(b, ft)
    syms = [s for s, _ in fr]
    game = [s for s, img in fr if img == 'RogueSquadron64Recomp']
    first_own = next((s for s in syms if s not in SIG_FRAMES), '?')
    desc = '%s %s %s thread=%s top=%s' % (ex.get('type'), ex.get('signal'), (ex.get('subtype') or '')[:48],
                                          th.get('name') or ft, ' | '.join(syms[:6]))
    if ledger and (stamp in ledger or stamp[len('2026-'):] in ledger):
        return 'FOLDED', desc
    if any(PLANT_FRAMES.search(s) for s in syms[:14]) and (set(syms[:4]) & SIG_FRAMES):
        return 'PLANT', desc
    if ex.get('type') == 'EXC_CRASH' and syms and syms[0] in ('__semwait_signal', 'mach_msg2_trap') and \
            any('recomp::start' in s or s == 'main' for s in syms[:8]):
        return 'PLANT', desc + '  (signal delivered from outside to an idle main thread: injected control)'
    if game and DIAG_FRAME.search(game[0]):
        return 'DIAG', desc
    if first_own and DIAG_FRAME.search(first_own):
        return 'DIAG', desc
    return 'NEW', desc


def selftest():
    def mk(d, name, exc, tname, syms):
        b = {'exception': exc, 'faultingThread': 0, 'usedImages': [{'name': 'RogueSquadron64Recomp'}, {'name': 'libsystem_c.dylib'}],
             'threads': [{'name': tname, 'frames': [{'symbol': s, 'imageIndex': 0 if not s.startswith('_') else 1} for s in syms]}]}
        open(os.path.join(d, name), 'w').write(json.dumps({'app_name': 'RogueSquadron64Recomp'}) + '\n' + json.dumps(b))
    with tempfile.TemporaryDirectory() as d:
        mk(d, 'RogueSquadron64Recomp-2030-01-01-000001.ips', {'type': 'EXC_BAD_ACCESS', 'signal': 'SIGBUS'}, 'Gfx Thread',
           ['initVec4TripletFromArgs', 'cinematicSplineWalkerNpcHandler'])
        mk(d, 'RogueSquadron64Recomp-2030-01-01-000002.ips', {'type': 'EXC_CRASH', 'signal': 'SIGSEGV'}, '[Game] 0',
           ['__pthread_kill', 'pthread_kill', 'raise', 'rs64_store_diag_tick', 'osViSwapBuffer_recomp'])
        mk(d, 'RogueSquadron64Recomp-2030-01-01-000003.ips', {'type': 'EXC_BAD_ACCESS', 'signal': 'SIGSEGV'}, 'SP Task Thread',
           ['(anonymous namespace)::consume(unsigned int)', 'rs64_s7523_status_read'])
        mk(d, 'RogueSquadron64Recomp-2030-01-01-000004.ips', {'type': 'EXC_BAD_ACCESS', 'signal': 'SIGSEGV'}, 'MAIN',
           ['memcpy_recomp', 'loadTxtFile'])
        want = {'000001': 'NEW', '000002': 'PLANT', '000003': 'DIAG', '000004': 'FOLDED'}
        ok = True
        for p in sorted(glob.glob(os.path.join(d, '*.ips'))):
            h, b = load(p)
            c, _ = classify(os.path.basename(p), b, 'quoted 2030-01-01-000004 here')
            k = os.path.basename(p)[-10:-4]
            ok &= c == want[k]
            print('selftest %s -> %s (want %s)' % (k, c, want[k]))
        print('SELFTEST', 'PASS' if ok else 'FAIL')
        return 0 if ok else 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--since', default='')
    ap.add_argument('--dir', default=os.path.expanduser('~/Library/Logs/DiagnosticReports'))
    ap.add_argument('--ledger', default='PORTING-STATE.md')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    ledger = open(a.ledger, errors='replace').read() if os.path.exists(a.ledger) else ''
    n_new = 0
    tally = {}
    for p in sorted(glob.glob(os.path.join(a.dir, 'RogueSquadron64Recomp*.ips'))):
        name = os.path.basename(p)
        m = re.search(r'(\d{4}-\d{2}-\d{2})-\d{6}', name)
        if a.since and m and m.group(1) < a.since:
            continue
        h, b = load(p)
        if b is None:
            print('UNPARSED %s' % name); n_new += 1; continue
        c, desc = classify(name, b, ledger)
        tally[c] = tally.get(c, 0) + 1
        n_new += c == 'NEW'
        print('%-6s %s  %s' % (c, name, desc))
    print('crash_reports: %s new=%d' % (' '.join('%s=%d' % kv for kv in sorted(tally.items())), n_new))
    return 1 if n_new else 0


if __name__ == '__main__':
    sys.exit(main())
