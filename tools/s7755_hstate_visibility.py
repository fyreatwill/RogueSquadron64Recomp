#!/usr/bin/env python3
"""s7755: is a mid-task RAM rewrite (H-state gfx task, s7754) VISIBLE?  For a snap pair <snap.bin> + <snap>_end.bin
(ROGUESQ_S7751_SNAP), replays OUR ucode on the begin image and on a hybrid (end RAM + begin DMEM/header/tail), renders live tail,
begin replay and end replay with angrylion (tools/s7752_port_task), and pixel-diffs them (max 5-bit channel delta).
Controls (both must PASS or exit 2): (1) one-pixel flip reported (s7752_render_diff --ctl); (2) shade sensitivity: +16 (8-bit)
on the base red of every triangle that differs live-vs-begin must produce >=1 px at >=2 LSB, proving the renderer sees those tris.
Verdict: VISIBLE if any px differs by >=2 LSB between live/begin/end, else INVISIBLE.  exit 0 invisible, 1 visible, 2 control fail.
usage: s7755_hstate_visibility.py <snap.bin> [--cap 65536] [--tg 0] [--out DIR]"""
import os, sys, re, struct, subprocess, argparse, importlib.util, tempfile
T = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, T)
from s7751_rdp_compare import load, split
sp = importlib.util.spec_from_file_location('g', os.path.join(T, 's7753_rdp_output_gate.py')); g = importlib.util.module_from_spec(sp); sp.loader.exec_module(g)
H, R, DIFF = os.path.join(T, 's7752_port_task/harness'), os.path.join(T, 's7752_port_task/rdp_render'), os.path.join(T, 's7752_render_diff.py')

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('snap'); ap.add_argument('--cap', default='65536'); ap.add_argument('--tg', default='0')
    ap.add_argument('--out', default=None); o = ap.parse_args()
    D = o.out or tempfile.mkdtemp(prefix='s7755_'); os.makedirs(D, exist_ok=True); P = lambda n: os.path.join(D, n)
    end = o.snap[:-4] + '_end.bin'; B = open(o.snap, 'rb').read(); E = open(end, 'rb').read(); n = struct.unpack_from('<I', B, 16)[0]
    open(P('hyb.bin'), 'wb').write(B[:20 + 4096] + E[20 + 4096:20 + 4096 + n] + B[20 + 4096 + n:])
    open(P('live.rdp'), 'wb').write(g.tail(o.snap))
    env = dict(os.environ, ROGUESQ_UCODE_CAP=o.cap, ROGUESQ_G5B_TG_FIX=o.tg)
    subprocess.run([H, o.snap, P('begin.rdp')], env=env, capture_output=True, check=True)
    subprocess.run([H, P('hyb.bin'), P('end.rdp')], env=env, capture_output=True, check=True)
    L = list(split(load(P('live.rdp')))); Bg = list(split(load(P('begin.rdp'))))
    raw = bytearray(open(P('live.rdp'), 'rb').read()); off = 0; nt = 0
    for (oa, a), (ob, b) in zip(L, Bg):
        if a != b and 0x0C <= oa <= 0x0F:
            r = int.from_bytes(raw[off + 32:off + 34], 'big'); raw[off + 32:off + 34] = ((r + 16) & 0xFFFF).to_bytes(2, 'big'); nt += 1
        off += len(a)
    open(P('shadectl.rdp'), 'wb').write(raw)
    for k in ('live', 'begin', 'end', 'shadectl'): subprocess.run([R, o.snap, P(k + '.rdp'), P(k + '.ram')], capture_output=True, check=True)
    def cmp(a, b, ctl=False):
        out = subprocess.run([sys.executable, DIFF, P('live.rdp'), P(a + '.ram'), P(b + '.ram')] + (['--ctl'] if ctl else []), capture_output=True, text=True).stdout
        px = int(re.search(r'total differing px=(\d+)', out).group(1)); ge2 = 0
        for m in re.finditer(r'2-3:(\d+) 4-7:(\d+) >=8:(\d+)', out): ge2 += sum(map(int, m.groups()))
        return px, ge2
    res = {f'{a}-{b}': cmp(a, b) for a, b in (('live', 'begin'), ('live', 'end'), ('begin', 'end'))}
    c1 = cmp('live', 'live', True)[0] >= 1; sc = cmp('live', 'shadectl'); c2 = nt > 0 and sc[1] >= 1
    print(f'stream lens live={len(L)} cmds, diff tris live-vs-begin={nt}')
    for k, (px, ge2) in res.items(): print(f'{k}: px={px} ge2LSB={ge2}')
    print(f'CTL flip {"PASS" if c1 else "FAIL"}; CTL shade+16 on {nt} tris: px={sc[0]} ge2LSB={sc[1]} {"PASS" if c2 else "FAIL"}')
    if not (c1 and c2): print('VERDICT CONTROL-FAIL'); return 2
    vis = any(ge2 for _, ge2 in res.values()); print('VERDICT', 'VISIBLE' if vis else 'INVISIBLE'); return 1 if vis else 0

if __name__ == '__main__': sys.exit(main())
