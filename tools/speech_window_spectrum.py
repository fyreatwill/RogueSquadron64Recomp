#!/usr/bin/env python3
"""Pure-python (no numpy) spectrum stats of raw AI PCM (ROGUESQ_PCM_RAW) around each
[spath] enqueueSpeechClip vs control windows; writes WAVs. Stereo s16 @ RATE (22050).
Usage: speech_window_spectrum.py run.log pcm.raw outdir"""
import re, sys, os, wave, array, cmath, math, statistics as st
log, raw, out = sys.argv[1:4]; rate = int(os.environ.get('RATE', '22050')); os.makedirs(out, exist_ok=True)
pcm = array.array('h'); pcm.frombytes(open(raw, 'rb').read())
offs = {}; enq = []
for l in open(log, errors='replace'):
    m = re.match(r'\[pcm-raw\] n=(\d+) off=(\d+) ns=(\d+)', l)
    if m: offs[int(m[1])] = (int(m[2]), int(m[3]))
    elif '[spath] enqueueSpeechClip' in l: enq.append(len(offs))
keys = sorted(offs)
def fft(a):
    n = len(a)
    if n == 1: return a
    e = fft(a[0::2]); o = fft(a[1::2])
    t = [cmath.exp(-2j * math.pi * k / n) * o[k] for k in range(n // 2)]
    return [e[k] + t[k] for k in range(n // 2)] + [e[k] - t[k] for k in range(n // 2)]
def window(i0, ncb):
    ks = keys[i0:i0 + ncb]
    if not ks: return None
    a = offs[ks[0]][0]; b = offs[ks[-1]][0] + offs[ks[-1]][1]
    return pcm[a:b]
N = 2048
def stats(w):
    x = w[0::2]; nfr = min(24, len(x) // N)
    if nfr < 2: return None
    step = len(x) // nfr; bands = [0, 0, 0, 0]
    for fr in range(nfr):
        seg = x[fr * step: fr * step + N]
        sp = fft([seg[i] * (0.5 - 0.5 * math.cos(2 * math.pi * i / N)) for i in range(N)])[:N // 2]
        for k, c in enumerate(sp):
            f = k * rate / N; b = 0 if f < 300 else 1 if f < 3000 else 2 if f < 8000 else 3
            bands[b] += abs(c) ** 2
    tot = sum(bands) + 1e-9
    zc = sum(1 for i in range(1, len(x)) if (x[i] >= 0) != (x[i - 1] >= 0)) / len(x)
    rms = math.sqrt(sum(v * v for v in x[::8]) / max(1, len(x[::8])))
    rail = sum(1 for v in w[::4] if abs(v) >= 32767) / max(1, len(w[::4]))
    return dict(rms=rms, zcr=zc, lt300=bands[0] / tot, b300_3k=bands[1] / tot, b3k_8k=bands[2] / tot, gt8k=bands[3] / tot, rail=rail)
# positive control: 1 kHz tone must land in 300-3k, white-ish alternating in >8k
tone = array.array('h', [int(10000 * math.sin(2 * math.pi * 1000 * i / rate)) for i in range(N * 6)] ); tt = array.array('h')
for v in tone: tt.extend([v, v])
c = stats(tt); print('control tone b300_3k=%.3f (want ~1)' % c['b300_3k'])
print('callbacks', len(keys), 'enqueues', len(enq), 'samples', len(pcm))
for j, e in enumerate(enq):
    w = window(e, 300)
    if w is None: continue
    s = stats(w)
    if s: print('enq%d' % j, ' '.join('%s=%.3f' % kv for kv in s.items()))
    with wave.open(os.path.join(out, 'enq%d.wav' % j), 'wb') as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(rate); wf.writeframes(w[:len(w) // 2 * 2].tobytes())
ctl = [stats(window(i, 300)) for i in range(100, len(keys) - 300, 400) if all(abs(i - e) > 400 for e in enq)]
ctl = [c for c in ctl if c]
if ctl: print('control n=%d' % len(ctl), ' '.join('%s=%.3f' % (k, st.median([c[k] for c in ctl])) for k in ctl[0]))
