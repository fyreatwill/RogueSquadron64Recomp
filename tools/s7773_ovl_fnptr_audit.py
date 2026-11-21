#!/usr/bin/env python3
"""s7773 overlay function-pointer alias audit (HYPOTHESIS-ID ovl-fnptr-alias-audit; sibling of s7772).

Every jalr is generated as LOOKUP_FUNC(reg) -> get_function, which resolves against the sections CURRENTLY loaded
(overlays.cpp func_map). So a function pointer into the shared overlay window (VMA 0x800A5130+) is correct exactly when
its overlay is mapped (hardware semantics); the port-only risk is a pointer that survives its overlay in RESIDENT
storage (.entry/.text image incl. its data, .bss, heap) and is used after a swap.

Static census over raw ELF words (data is embedded in the code sections of this ELF):
  (a) WORD  every 4-aligned word equal to a function start of an overlay, tagged by holding section:
        local     held by the same overlay (dies with it: H-local)
        cross     held by a different overlay
        resident  held by .entry/.text (survives every swap: H-stale candidate)
      and by position: in_func (word inside a function body, i.e. an instruction coincidence) vs data.
  (b) PAIR  lui rX,hi + addiu/ori rY,rX,lo forming an overlay function start (code builds a fn pointer), same tags.
  For every hit: the overlays in which the target is a start (multi = silent alias if the wrong overlay is mapped).
--controls: a word 0x800C58A0 (menuOverlayInit) planted in a .text data gap must classify resident/data/unique, and a
  planted lui/addiu pair in .text must classify resident PAIR; at least one overlay-local data word must exist.
--gate: rc 1 on any resident data WORD / resident PAIR outside KNOWN_FUNCS, or any target that is a start in >1 overlay.
"""
import argparse, bisect, re, struct, sys

ap = argparse.ArgumentParser()
ap.add_argument('--elf', default='../rogue_squadron64/build/roguesquadron.elf')
ap.add_argument('--syms', default='syms/rogue_squadron.syms.toml')
ap.add_argument('--controls', action='store_true')
ap.add_argument('--gate', action='store_true')
ap.add_argument('-v', action='store_true')
a = ap.parse_args()

d = open(a.elf, 'rb').read()
shoff, = struct.unpack('>I', d[0x20:0x24])
se, sn, si = struct.unpack('>HHH', d[0x2E:0x34])
raw = [struct.unpack('>IIIIII', d[shoff + i * se:shoff + i * se + 24]) for i in range(sn)]
stro = raw[si][4]
sname = lambda n: d[stro + n:d.index(b'\0', stro + n)].decode()
CODE = {sname(s[0]): (s[3], s[4], s[5]) for s in raw if s[1] == 1 and s[2] & 4 and s[3]}
RES = ('.entry', '.text')

funcs, cur = {}, None
for line in open(a.syms):
    m = re.match(r'name = "([^"]+)"', line)
    if m:
        cur = m.group(1); funcs[cur] = []; continue
    m = re.search(r'name = "([^"]+)", vram = 0x([0-9A-Fa-f]+), size = 0x([0-9A-Fa-f]+)', line)
    if m and cur:
        funcs[cur].append((int(m.group(2), 16), int(m.group(3), 16), m.group(1)))
for k in funcs:
    funcs[k].sort()
KEYV = {k: [f[0] for f in v] for k, v in funcs.items()}
OVL = [s for s in funcs if s.startswith('.ovl')]
OSTART = {}
for s in OVL:
    for v, _, n in funcs[s]:
        OSTART.setdefault(v, []).append((s, n))


def enclosing(sec, v):
    i = bisect.bisect_right(KEYV.get(sec, []), v) - 1
    if i >= 0 and funcs[sec][i][0] <= v < funcs[sec][i][0] + funcs[sec][i][1]:
        return funcs[sec][i]
    return None


def tag(sec, t):
    owners = sorted(s for s, _ in OSTART[t])
    where = 'local' if sec in owners else ('resident' if sec in RES else 'cross')
    return where, owners


def scan(sec, blob, base):
    hits = []
    n = len(blob) // 4
    W = struct.unpack('>%dI' % n, blob[:n * 4])
    for i, w in enumerate(W):
        if w in OSTART:
            va = base + i * 4
            where, owners = tag(sec, w)
            hits.append(('WORD', sec, va, w, where, 'in_func' if enclosing(sec, va) else 'data', owners))
    for i, w in enumerate(W):
        if w >> 26 != 0x0F:
            continue
        rx, hi = (w >> 16) & 31, w & 0xFFFF
        for j in range(i + 1, min(i + 33, n)):
            x = W[j]; op = x >> 26; rs, rt = (x >> 21) & 31, (x >> 16) & 31
            if op in (0x09, 0x0D) and rs == rx:
                lo = x & 0xFFFF
                v = ((hi << 16) + (lo - 0x10000 if op == 0x09 and lo & 0x8000 else lo)) & 0xFFFFFFFF
                if v in OSTART:
                    va = base + j * 4
                    where, owners = tag(sec, v)
                    hits.append(('PAIR', sec, va, v, where, 'in_func' if enclosing(sec, va) else 'data', owners))
            # stop when rx is overwritten (I-type rt / R-type rd), approximate
            if (op not in (0, 0x2B, 0x29, 0x28, 0x3F, 0x39, 0x04, 0x05) and rt == rx and op != 0x0F) or \
               (op == 0 and ((x >> 11) & 31) == rx) or (op == 0x0F and rt == rx):
                break
    return hits


hits = []
for sec, (va, off, sz) in CODE.items():
    if sec == '.rom_anchor':
        continue
    hits += scan(sec, d[off:off + sz], va)

# s7773-classified resident builders: .text NPC spawners called from loadDatFile / updateActiveGridCellState (mission
# streaming) and mission-overlay code; they pass a mission-overlay handler to spawnNpcOfType (slot dispatch via jalr ->
# LOOKUP_FUNC). Every target is a start in exactly one overlay (multi_start=0), so a stale use aborts loudly, never silently.
KNOWN_FUNCS = ('setupNpcUpdateFunctions', 'spawnDatStructureNpcByType')
KNOWN = set()
cnt = {}
for h in hits:
    k = '%s_%s_%s' % (h[0], h[4], h[5])
    cnt[k] = cnt.get(k, 0) + 1
multi = [h for h in hits if len(h[6]) > 1]
def known(h):
    e = enclosing(h[1], h[2])
    return (h[0], h[2]) in KNOWN or (e is not None and e[2] in KNOWN_FUNCS)
res = [h for h in hits if h[4] == 'resident' and (h[0] == 'PAIR' or h[5] == 'data')]
bad = [h for h in res if not known(h)] + [h for h in hits if len(h[6]) > 1]


def own(h):   # for cross rows: what the target address is inside the HOLDING overlay (coincidence check)
    e = enclosing(h[1], h[3])
    return 'own=' + (('start' if e[0] == h[3] else 'interior') if e else 'data')
for h in hits:
    if a.v or h[4] != 'local' or len(h[6]) > 1:
        e = enclosing(h[1], h[2])
        print('%s %-9s %-7s %-15s 0x%08X %-36s -> 0x%08X %s start_in=%s%s' % (
            h[0], h[4], h[5], h[1], h[2], ('%s+0x%X' % (e[2], h[2] - e[0])) if e else 'OUTSIDE', h[3],
            OSTART[h[3]][0][1], ','.join(h[6]), (' ' + own(h)) if h[4] == 'cross' else (' known' if known(h) else '')))
print('SUMMARY hits=%d %s multi_start=%d resident=%d resident_known=%d new_candidates=%d'
      % (len(hits), ' '.join('%s=%d' % kv for kv in sorted(cnt.items())), len(multi), len(res), len(res) - len([h for h in res if not known(h)]), len(bad)))

rc = 0
if a.controls:
    va, off, sz = CODE['.text']
    blob = bytearray(d[off:off + sz])
    # plant in the last 16 bytes of .text that lie outside every function (data region)
    p = next(x for x in range(sz - 16, 0, -4) if not enclosing('.text', va + x))
    blob[p:p + 4] = struct.pack('>I', 0x800C58A0)
    q = next(x for x in range(p - 16, 0, -4) if not enclosing('.text', va + x) and not enclosing('.text', va + x + 4))
    blob[q:q + 8] = struct.pack('>II', (0x0F << 26) | (8 << 16) | 0x800C, (0x09 << 26) | (8 << 21) | (9 << 16) | 0x58A0)
    ch = scan('.text', bytes(blob), va)
    w = [h for h in ch if h[2] == va + p and h[0] == 'WORD']
    pr = [h for h in ch if h[2] == va + q + 4 and h[0] == 'PAIR']
    loc = [h for h in hits if h[4] == 'local' and h[5] == 'data']
    ok = (len(w) == 1 and w[0][4] == 'resident' and w[0][5] == 'data' and w[0][6] == ['.ovl.menu'] and
          len(pr) == 1 and pr[0][4] == 'resident' and len(loc) > 0)
    print('CONTROLS %s (planted_word=%s planted_pair=%s local_data_words=%d)' % (
        'PASS' if ok else 'FAIL', w[0][4] + '/' + w[0][5] if w else 'MISS', pr[0][4] if pr else 'MISS', len(loc)))
    rc = 0 if ok else 3
if a.gate:
    print('GATE %s new_candidates=%d' % ('RED' if bad else 'GREEN', len(bad)))
    rc = rc or (1 if bad else 0)
sys.exit(rc)
