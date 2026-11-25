#!/usr/bin/env python3
"""s7928: name the writer that leaves the MusyX gate byte 0x800A0F50 at 0 at flight entry (s7927: the port SKIPS retail's
flight-entry waitForMusyXAudioTaskDone; musyxNoopStub 0x8008ED00 calls it only when the gate is nonzero).
Reads a present ring written with ROGUESQ_PRESENT_RING + ROGUESQ_S7928_GATEW=1 (src/rsp/s7324_rcp_spill.cpp):
  G <t> pc=<writer> v=<byte after the store>   every guest store to 0x800A0F50 (7 s2031 writer sites, funcs_23.c)
  M <t> ... dur_ms=<d>                          slow waits (s7925)
Positive control (same run): every slow M must have a nonzero G before it (since the previous M) and a musyxNoopStub
noop-exit clear (pc 0x8008ED48 v=0) after it. Exit 0 = table printed, 3 = control failed / no rows. --selftest: planted rings."""
import re, sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from rs64_zopen import zopen
except Exception:
    zopen = open
C = []
SITES = {0x8008E9F8: 'initMusyXEngine:init-success(r2)', 0x8008EA34: 'setDisplayMode:entry(0)',
         0x8008EB40: 'setDisplayMode:success(B40 knob)', 0x8008EB7C: 'reapplyDisplayMode:entry(0)',
         0x8008EC88: 'reapplyDisplayMode:success(r2)', 0x8008ECEC: 'shutdownMusyXEngine:exit(0)',
         0x8008ED48: 'musyxNoopStub:noop-exit(0)'}

def load(path):
    G, M = [], []
    global C; C = []
    with zopen(path) as f:
        for l in f:
            if isinstance(l, bytes): l = l.decode('latin-1')
            if l.startswith('G '):
                pc = int(re.search(r'pc=0x([0-9A-Fa-f]+)', l).group(1), 16); v = int(re.search(r'v=(-?\d+)', l).group(1))
                G.append((float(l.split()[1]), pc, v))
            elif l.startswith('M '):
                M.append(float(l.split()[1]))
            elif l.startswith('C '):
                C.append((float(l.split()[1]), int(re.search(r'pc=0x([0-9A-Fa-f]+)', l).group(1), 16),
                          int(re.search(r'n=(\d+)', l).group(1)), int(re.search(r'g=(-?\d+)', l).group(1))))
    return G, M

def analyse(path, out=print):
    G, M = load(path)
    if not G or not M: return 3, 'no G or M rows (GATEW/ring off?)'
    ok = 0; prev = -1e18
    for i, t in enumerate(M):
        nxt = M[i + 1] if i + 1 < len(M) else 1e18
        setb = any(prev < g < t and v > 0 for g, pc, v in G)
        clr = any(t < g < nxt and pc == 0x8008ED48 and v == 0 for g, pc, v in G)
        ok += setb and clr; prev = t
    t0 = M[0]
    for g, pc, v in G:
        tag = ''
        for t in M:
            if 0 <= t - g < 5: tag = '  <- before slow wait at +%.2f' % (t - t0); break
        out('G %+9.3f  %-36s v=%d%s' % (g - t0, SITES.get(pc, '0x%08X' % pc), v, tag))
    CN = {0x8003E29C: 'mainGameLoop@E29C', 0x8003E360: 'mainGameLoop@E360', 0x800A9C70: 'initSceneForMission@9C70',
          0x800C5A18: 'menuOverlayInit@5A18'}
    for pc in sorted({c[1] for c in C}):
        rows = [c for c in C if c[1] == pc]
        out('C %-26s rows=%d max_n=%d first=%+.3f last=%+.3f  ' % (CN.get(pc, hex(pc)), len(rows), rows[-1][2], rows[0][0] - t0,
            rows[-1][0] - t0) + ' '.join('%+.2f(n%d,g%d)' % (t - t0, n, g) for t, _, n, g in rows[:6]))
    after = [(g, pc, v) for g, pc, v in G if g > M[-1]]
    last = after[-1] if after else None
    out('s7928 control %d/%d %s; writes after last slow wait (+%.2f): %d; final gate write: %s' % (
        ok, len(M), 'PASS' if ok == len(M) else 'FAIL', M[-1] - t0, len(after),
        ('%s v=%d at +%.2f' % (SITES.get(last[1], hex(last[1])), last[2], last[0] - t0)) if last else 'none'))
    return (0 if ok == len(M) else 3), ''

def selftest():
    good = "G 1.0 pc=0x8008E9F8 v=1\nM 2.0 pc=0x80091EB0 dur_ms=140\nG 2.2 pc=0x8008ED48 v=0\nG 3.0 pc=0x8008EB40 v=0\n"
    bad = "G 1.0 pc=0x8008E9F8 v=0\nM 2.0 pc=0x80091EB0 dur_ms=140\n"
    res = []
    for name, txt, want in (('good', good, 0), ('no-set', bad, 3), ('empty', '', 3)):
        fd, p = tempfile.mkstemp(); os.write(fd, txt.encode()); os.close(fd)
        rc, _ = analyse(p, out=lambda *a: None); os.unlink(p); res.append(rc == want)
        print('selftest %s rc=%d want=%d %s' % (name, rc, want, 'ok' if rc == want else 'FAIL'))
    print('selftest %d/%d' % (sum(res), len(res))); return 0 if all(res) else 1

def oracle_callers(path):
    """retail runVideoFrameTick entries (--watch-pc 0x80001354,0x80091EC4 --hit-vi): (vi, caller jal site = ra-8, wait taken)."""
    rows = []
    with zopen(path) as f:
        for l in f:
            if isinstance(l, bytes): l = l.decode('latin-1')
            if not l.startswith('[hit]'): continue
            pc = int(re.search(r' pc=0x([0-9a-f]+)', l).group(1), 16); vi = int(re.search(r' vi=(\d+)', l).group(1))
            if pc == 0x80001354: rows.append([vi, int(re.search(r' ra=0x([0-9a-f]+)', l).group(1), 16) - 8, 0])
            elif pc == 0x80091EC4 and rows and rows[-1][0] == vi: rows[-1][2] = 1
    return rows

def compare(ring, oracle):
    load(ring)
    port = [c for c in C if c[2] <= 16]
    ret = oracle_callers(oracle)
    nm = lambda pc: {0x8003E29C: 'mainGameLoop@E29C', 0x8003E360: 'mainGameLoop@E360', 0x800A9C70: 'initSceneForMission@9C70',
                     0x800C5A18: 'menuOverlayInit@5A18'}.get(pc, hex(pc))
    print('retail: ' + ' '.join('%s(vi%d,%s)' % (nm(pc), vi, 'wait' if w else 'SKIP') for vi, pc, w in ret))
    print('port:   ' + ' '.join('%s(g%d)' % (nm(pc), g) for t, pc, n, g in sorted(port)))
    ctl = sum(w for _, _, w in ret)
    last_r = ret[-1][1] if ret else 0; last_p = sorted(port)[-1][1] if port else 0
    print('s7928 compare: retail calls %d (waits %d/%d) port calls %d (gate set %d); last caller retail %s port %s -> %s' % (
        len(ret), ctl, len(ret), len(port), sum(1 for c in port if c[3] > 0), nm(last_r), nm(last_p),
        'FLIGHT-ENTRY MATCH' if ret and last_r == last_p else 'DIFFER'))
    return 0 if ret and ctl == len(ret) and last_r == last_p else 3

if __name__ == '__main__':
    if sys.argv[1:] == ['--selftest']: sys.exit(selftest())
    if len(sys.argv) == 4 and sys.argv[2] == '--oracle': sys.exit(compare(sys.argv[1], sys.argv[3]))
    rc, msg = analyse(sys.argv[1])
    if msg: print('s7928:', msg)
    sys.exit(rc)
