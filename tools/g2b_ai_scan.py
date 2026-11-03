"""s6790 G2b: per-segment AI cadence + PCM gap scan from ROGUESQ_AI_TRACE (t q_before ns width origin) and <trace>.pcm.
Segments = runs of the same VI width. Per segment: buffers, wall span, produced frames/s (DAC 22047), queue-empty count
(q_before==0), max inter-buffer wall gap, PCM: silent-run count (>=64 consecutive stereo frames exactly 0 inside
non-silent audio) and click count (|d| > 8000 between adjacent samples of one channel)."""
import sys, array
def main(path):
    rows = [r for r in (l.split() for l in open(path)) if len(r) >= 5]
    pcm = array.array('h'); pcm.frombytes(open(path + '.pcm', 'rb').read())
    off = 0; segs = []
    for r in rows:
        t, q, ns, w = float(r[0]), int(r[1]), int(r[2]), int(r[3])
        if not segs or segs[-1]['w'] != w:
            segs.append(dict(w=w, t0=t, t1=t, n=0, zero=0, ns=0, gap=0.0, last=t, off0=off, qmin=1 << 30))
        s = segs[-1]; s['gap'] = max(s['gap'], t - s['last']); s['last'] = t; s['t1'] = t
        s['n'] += 1; s['ns'] += ns; s['zero'] += (q == 0); s['qmin'] = min(s['qmin'], q); off += ns; s['off1'] = off
    for s in segs:
        if s['n'] < 20: continue
        x = pcm[s['off0']:s['off1']]; L = x[0::2]
        sil = run = 0; loud = 0; clicks = 0
        for i, v in enumerate(L):
            if v == 0: run += 1
            else:
                if run >= 64 and loud: sil += 1
                run = 0; loud = 1
            if i and abs(v - L[i - 1]) > 8000: clicks += 1
        span = s['t1'] - s['t0']
        rms = (sum(v * v for v in L) / max(1, len(L))) ** .5
        print(f"w={s['w']:4d} t={s['t0']:7.1f}-{s['t1']:7.1f} bufs={s['n']:5d} fps={s['ns']/2/max(span,1e-3):7.0f} "
              f"qzero={s['zero']:4d} qmin={s['qmin']:5d} maxgap_ms={s['gap']*1000:6.1f} rms={rms:6.0f} silruns={sil} clicks={clicks}")
if __name__ == '__main__':
    for p in sys.argv[1:]: print(p); main(p)
