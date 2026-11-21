#!/usr/bin/env python3
"""s7752: classify every residual difference between the port's raw RDP stream (ROGUESQ_S7751_SNAP .bin tail) and an
independent RSP's stream for the same task (tools/s7751_cxd4_task/replay output), using a difflib alignment of whole
commands. Per opcode block: equal / replace (same length: which 32-bit words differ) / insert (port-only) / delete
(ref-only), plus detection of moved blocks (port-only run whose bytes appear as a ref-only run elsewhere).
usage: s7752_rdp_residual.py <port.snap.bin> <ref.rdp> [--show N] [--json out]
exit 0 = identical, 1 = differences classified, 2 = usage error."""
import sys, difflib, collections, json, argparse, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s7751_rdp_compare import load, split, tri_info

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('port'); ap.add_argument('ref')
    ap.add_argument('--show', type=int, default=6); ap.add_argument('--json')
    o = ap.parse_args()
    A, B = split(load(o.port)), split(load(o.ref))
    a = [c for _, c in A]; b = [c for _, c in B]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    eq = 0; rep = []; ins = []; dele = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal': eq += i2 - i1
        elif tag == 'replace':
            if i2 - i1 == j2 - j1: rep += list(zip(range(i1, i2), range(j1, j2)))
            else: ins.append((i1, i2)); dele.append((j1, j2))
        elif tag == 'insert': dele.append((j1, j2))
        elif tag == 'delete': ins.append((i1, i2))
    print(f'port={len(A)} ref={len(B)} equal={eq} ({100.0*eq/max(len(A),1):.2f}%) replaced={len(rep)} '
          f'port-only={sum(e-s for s,e in ins)} in {len(ins)} runs, ref-only={sum(e-s for s,e in dele)} in {len(dele)} runs')
    # replaced: word-level diff
    wc = collections.Counter(); byop = collections.Counter(); out = {'replace': [], 'ins': [], 'del': [], 'moved': []}
    for i, j in rep:
        op = A[i][0]; ca, cb = a[i], b[j]
        if len(ca) != len(cb): byop[(op, 'len')] += 1; continue
        ws = [k for k in range(0, len(ca), 4) if ca[k:k+4] != cb[k:k+4]]
        byop[op] += 1
        for k in ws: wc[(op, k)] += 1
        out['replace'].append(dict(port=i, ref=j, op=op, words=ws, pa=[ca[k:k+4].hex() for k in ws], rb=[cb[k:k+4].hex() for k in ws]))
    print('replaced by op: ' + ' '.join(f'{k if isinstance(k,str) else (f"{k:02X}" if isinstance(k,int) else k)}:{v}' for k, v in sorted(byop.items(), key=str)))
    print('replaced word offsets (op,byte): ' + ' '.join(f'{op:02X}@{k}:{v}' for (op, k), v in sorted(wc.items())))
    for r in out['replace'][:o.show]:
        print(f"  rep port#{r['port']} ref#{r['ref']} op={r['op']:02X} words={r['words']} port={r['pa']} ref={r['rb']}")
    # moved-block detection
    refruns = {}
    for s, e in dele: refruns.setdefault(b''.join(b[s:e]), []).append((s, e))
    for s, e in ins:
        key = b''.join(a[s:e]); m = refruns.get(key)
        ops = collections.Counter(A[k][0] for k in range(s, e))
        rec = dict(port=(s, e), n=e-s, ops={f'{k:02X}': v for k, v in ops.items()}, moved_to=m[0] if m else None)
        (out['moved'] if m else out['ins']).append(rec)
    for s, e in dele:
        key = b''.join(b[s:e])
        if not any(r['moved_to'] == (s, e) for r in out['moved']):
            ops = collections.Counter(B[k][0] for k in range(s, e))
            out['del'].append(dict(ref=(s, e), n=e-s, ops={f'{k:02X}': v for k, v in ops.items()}))
    print(f"moved runs (port run == ref run elsewhere): {len(out['moved'])} cmds={sum(r['n'] for r in out['moved'])}")
    for r in out['moved'][:o.show]: print(f"  moved port{r['port']} -> ref{r['moved_to']} n={r['n']} ops={r['ops']}")
    print(f"port-only runs: {len(out['ins'])} cmds={sum(r['n'] for r in out['ins'])}")
    for r in out['ins'][:o.show]:
        s, e = r['port']; extra = ''
        tri = [k for k in range(s, e) if 0x08 <= A[k][0] <= 0x0F]
        if tri:
            t = tri_info(A[tri[0]][0], a[tri[0]]); extra = f" tri0 y={t['yh']:.2f}/{t['ym']:.2f}/{t['yl']:.2f} x={t['xh']:.1f}/{t['xm']:.1f}/{t['xl']:.1f}"
        print(f"  port-only port{r['port']} n={r['n']} ops={r['ops']}{extra}")
    print(f"ref-only runs: {len(out['del'])} cmds={sum(r['n'] for r in out['del'])}")
    for r in out['del'][:o.show]: print(f"  ref-only ref{r['ref']} n={r['n']} ops={r['ops']}")
    if o.json: json.dump(out, open(o.json, 'w'), default=list)
    return 0 if (len(A) == len(B) and eq == len(A)) else 1

if __name__ == '__main__':
    sys.exit(main())
