#!/usr/bin/env python3
"""s7771: census of every jal (and j) whose target is NOT a function start, read from raw ELF words.

Scans every 4-aligned word of each code section separately (.text and each .ovl.*: overlays share VMA 0x800A5130, so a
target is resolved against the call site's own section first, as N64Recomp's resolve_jal does). Function starts come from
syms/rogue_squadron.syms.toml (the list N64Recomp recompiles). For each jal word report: call-site section, enclosing
function (+offset, or OUTSIDE if the word is in no function = data/padding), target status:
  start        exact function start in the call site's own section, or in .text/.entry (always mapped)
  start_ovl    start only in a different overlay (H-ovl: N64Recomp emits a lookup; correct when that overlay is mapped)
  interior     inside a function of the call site's section (H-interior/H-split: N64Recomp emits static_<sec>_<addr>)
  interior_ovl inside a function of another overlay only
  nofunc       in no function at all (H-data candidate, or a call outside the code image)
Only jal is classified (j targets inside the own function are ordinary jumps); j words to other functions are tail calls
and are listed under --tail.
  --controls  planted rows: a mid-body jal must be interior, a jal __osEnqueueThread must be start; rc 3 on failure.
  --gen DIR   for every non-start row, grep the generated tree for how the target is called (static_/LOOKUP_FUNC/name).
  --gate      regression gate: rc 1 on any NEW code-site interior/interior_ovl/nofunc row (KNOWN = the 3 s7771 rows:
              0x800B58B8 + 0x8005EE64 are unreferenced 3-word stubs (H-data: 0 jal/j/word/lui-pair refs), 0x80092F8C is the
              s7081 jump-table tail of resampleVoiceLutSamplesPacked). Data-site rows (462 nofunc, 12 interior) are ignored.
Prints SUMMARY jal=N start=.. start_ovl=.. interior=.. interior_ovl=.. nofunc=.. (call-site OUTSIDE counted separately)."""
import argparse, bisect, os, re, struct, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument('--elf', default='../rogue_squadron64/build/roguesquadron.elf')
ap.add_argument('--syms', default='syms/rogue_squadron.syms.toml')
ap.add_argument('--gen', default=None)
ap.add_argument('--controls', action='store_true')
ap.add_argument('--tail', action='store_true')
ap.add_argument('--gate', action='store_true', help='rc 1 if a jal/j from a real function body (not OUTSIDE/data_gap/'
                '__OSGlobalIntMask) lands mid-function and is not in KNOWN (s7771 classified)')
a = ap.parse_args()

d = open(a.elf, 'rb').read()
shoff, = struct.unpack('>I', d[0x20:0x24])
shentsize, shnum, shstrndx = struct.unpack('>HHH', d[0x2E:0x34])
raw = [struct.unpack('>IIIIII', d[shoff + i * shentsize:shoff + i * shentsize + 24]) for i in range(shnum)]
stro = raw[shstrndx][4]
sname = lambda n: d[stro + n:d.index(b'\0', stro + n)].decode()
CODE = {sname(s[0]): (s[3], s[4], s[5]) for s in raw if s[1] == 1 and s[2] & 4 and s[3]}

funcs = {}                                   # section -> sorted [(vram, size, name)]
cur = None
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
STARTS = {k: set(v) for k, v in KEYV.items()}
ALWAYS = ('.entry', '.text')


def enclosing(sec, v):
    i = bisect.bisect_right(KEYV.get(sec, []), v) - 1
    if i >= 0:
        fv, fs, fn = funcs[sec][i]
        if fv <= v < fv + fs:
            return fv, fs, fn
    return None


def status(site_sec, t):
    own = [site_sec] + [s for s in ALWAYS if s != site_sec]
    for s in own:
        if t in STARTS.get(s, ()):
            return 'start', s
    for s in funcs:
        if s not in own and t in STARTS[s]:
            return 'start_ovl', s
    for s in own:
        if enclosing(s, t):
            return 'interior', s
    for s in funcs:
        if s not in own and enclosing(s, t):
            return 'interior_ovl', s
    return 'nofunc', '-'


def scan(sec, extra=()):
    va, off, size = CODE[sec]
    out = []
    items = [(va + i, struct.unpack('>I', d[off + i:off + i + 4])[0]) for i in range(0, size - 3, 4)] + list(extra)
    for pc, w in items:
        op = w >> 26
        if op not in (2, 3):
            continue
        t = (pc & 0xF0000000) | ((w & 0x3FFFFFF) << 2)
        enc = enclosing(sec, pc)
        if op == 2 and enc and enc[0] <= t < enc[0] + enc[1]:
            continue                                   # intra-function j
        st, tsec = status(sec, t)
        tenc = enclosing(tsec, t) if st.startswith('interior') else None
        out.append(dict(sec=sec, pc=pc, op='jal' if op == 3 else 'j', t=t, st=st, tsec=tsec,
                        site=('%s+0x%X' % (enc[2], pc - enc[0])) if enc else 'OUTSIDE',
                        tgt=('%s+0x%X' % (tenc[2], t - tenc[0])) if tenc else '-'))
    return out


rows = []
for sec in CODE:
    rows += scan(sec)
jal = [r for r in rows if r['op'] == 'jal']
inside = [r for r in jal if r['site'] != 'OUTSIDE']
cnt = lambda rs, k: sum(r['st'] == k for r in rs)
KEYS = ('start', 'start_ovl', 'interior', 'interior_ovl', 'nofunc')
gen_cache = {}


def gen_hits(t):
    if not a.gen:
        return ''
    pat = '%08X' % t
    if pat not in gen_cache:
        p = subprocess.run(['grep', '-rhoE', r'(static_[0-9]+_%s|LOOKUP_FUNC\(0x%s\)|LOOKUP_FUNC\(0x%s\))' % (pat, pat, pat.lower()),
                            a.gen], capture_output=True, text=True)
        hs = sorted(set(p.stdout.split()))
        defn = subprocess.run(['grep', '-rlE', r'^RECOMP_FUNC void static_[0-9]+_%s\(' % pat, a.gen], capture_output=True, text=True)
        gen_cache[pat] = ' gen=' + (','.join(hs) or 'none') + (' defined_in=' + os.path.basename(defn.stdout.split()[0]) if defn.stdout.split() else '')
    return gen_cache[pat]


for r in jal + ([x for x in rows if x['op'] == 'j'] if a.tail else []):
    if r['st'] != 'start':
        print('%-4s %-15s site=0x%08X %-42s -> 0x%08X %-12s %-15s %s%s' % (r['op'], r['sec'], r['pc'], r['site'], r['t'], r['st'],
                                                                         r['tsec'], r['tgt'], gen_hits(r['t'])))
print('SUMMARY jal=%d ' % len(jal) + ' '.join('%s=%d' % (k, cnt(jal, k)) for k in KEYS) +
      ' | site-in-function: ' + ' '.join('%s=%d' % (k, cnt(inside, k)) for k in KEYS) +
      ' | distinct_targets=%d' % len({(r['sec'] if r['st'] == 'start' else '', r['t']) for r in jal}))
rc = 0
KNOWN = {0x800B58B8, 0x8005EE64, 0x80092F8C}
isdata = lambda r: r['site'] == 'OUTSIDE' or r['site'].startswith(('data_gap_', '__OSGlobalIntMask'))
if a.gate:
    live = [r for r in rows if r['st'] not in ('start', 'start_ovl') and not isdata(r)]
    new = [r for r in live if r['pc'] not in KNOWN]
    for r in new:
        print('GATE-NEW %s 0x%08X %s -> 0x%08X %s %s' % (r['op'], r['pc'], r['site'], r['t'], r['st'], r['tgt']))
    print('GATE %s code_site_nonstart=%d known=%d new=%d' % ('RED' if new else 'GREEN', len(live), len(live) - len(new), len(new)))
    rc = 1 if new else 0
if a.controls:
    v, s, n = next(f for f in funcs['.text'] if f[2] == 'resampleVoiceLutSamplesPacked')
    e, _, _ = next(f for f in funcs['.text'] if f[2] == '__osEnqueueThread')
    site = v + 4
    mk = lambda t: (3 << 26) | ((t >> 2) & 0x3FFFFFF)
    va, off, size = CODE['.text']
    neg = [r for r in scan('.text', [(site, mk(v + 0x20)), (site, mk(e))]) if r['pc'] == site and r['t'] in (v + 0x20, e)]
    st = {r['t']: r['st'] for r in neg if r['op'] == 'jal'}
    ok = st.get(v + 0x20) == 'interior' and st.get(e) == 'start'
    print('CONTROLS %s (mid-body=%s enqueue=%s)' % ('PASS' if ok else 'FAIL', st.get(v + 0x20), st.get(e)))
    rc = rc if ok else 3
sys.exit(rc)
