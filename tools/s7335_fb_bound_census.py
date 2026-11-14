#!/usr/bin/env python3
"""s7335: idiom-class census of the frame-buffer layout bound and the memory-top it derives from.

Enumerates, across the generated funcs_*.c asm comments (N64Recomp/RecompiledFuncs), every guest instruction that
  (B) loads/stores/takes the address of the bound global 0x801163E4 (partitionFramebufferMemory output, the
      persistent-arena hi of coalesceFreeHeapBlocks) or its partition siblings 0x801163D8..0x801163F8,
  (M) reads osMemSize 0x80000318,
  (K) materialises a fixed memory-top constant with lui (0x8040, 0x8080, 0x80C0, 0x8100, 0x8180; 0x0040/0x0080 sizes
      are reported only when they feed an or/addu/subu with an osMemSize-like value, so too noisy: listed as K-size),
  (X) masks with 0x00FFFFFF/0x007FFFFF (lui 0x00FF/0x007F + ori 0xFFFF) - a 24/23-bit address clamp.
  (C) touches the heap globals 0x8010FF00..0x8010FF1C (coalesce/init args incl. the stored hi, heap head 0x8010FF18).
Each site is classified from the CLASS table (manual reading, s7335). Exit 1 on any unclassified site (exit 2 = positive control failed), so a
regen that adds a reader fails loudly. """
import re, sys, glob, collections
D = "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/"
ins, fn = {}, {}
for f in sorted(glob.glob(D + "funcs_*.c")):
    cur = None
    for l in open(f, errors="replace"):
        m = re.match(r'RECOMP_FUNC void (\w+)\(', l)
        if m: cur = m.group(1)
        m = re.match(r'\s*// 0x([0-9A-F]{8}): (\S+)\s*(.*)', l)
        if m:
            a = int(m.group(1), 16)
            if a not in ins: ins[a] = (m.group(2), [x.strip() for x in m.group(3).split(',')]); fn[a] = cur

def imm(s):
    s = s.strip(); neg = s.startswith('-'); s = s.lstrip('-')
    v = int(s, 16) if s.lower().startswith('0x') else int(s)
    return -v if neg else v
def memop(arg):
    m = re.match(r'(-?(?:0x)?[0-9A-Fa-f]+)\((\$\w+)\)', arg)
    return (imm(m.group(1)), m.group(2)) if m else None

# per-instruction lui tracking: register -> (hi value, addr of lui); invalidated after 12 insns or on a write
sites = []
addrs = sorted(ins)
live = {}
prev = None
for a in addrs:
    if prev is not None and a - prev > 8: live = {}  # function gap
    prev = a
    op, args = ins[a]
    live = {r: v for r, v in live.items() if a - v[1] <= 48}
    if op == 'lui' and len(args) == 2:
        hv = imm(args[1]) & 0xFFFF
        if hv in (0x8040, 0x8080, 0x80C0, 0x8100, 0x8180):
            sites.append(('K', a, '%s %s' % (op, ','.join(args))))
        if hv in (0x00FF, 0x007F):
            n = ins.get(a + 4)
            if n and n[0] == 'ori' and n[1][-1].lower() == '0xffff':
                sites.append(('X', a, 'mask 0x%04XFFFF' % hv))
        live[args[0]] = (hv << 16, a); continue
    mo = memop(args[-1]) if args else None
    if mo and mo[1] in live:
        ea = (live[mo[1]][0] + mo[0]) & 0xFFFFFFFF
        if 0x801163D8 <= ea <= 0x801163F8: sites.append(('B', a, '%s %s -> 0x%08X' % (op, ','.join(args), ea)))
        if 0x8010FF00 <= ea <= 0x8010FF1C: sites.append(('C', a, '%s %s -> 0x%08X' % (op, ','.join(args), ea)))
        if ea == 0x80000318: sites.append(('M', a, '%s %s -> osMemSize' % (op, ','.join(args))))
    if op == 'addiu' and len(args) == 3 and args[1] in live:
        ea = (live[args[1]][0] + imm(args[2])) & 0xFFFFFFFF
        if 0x801163D8 <= ea <= 0x801163F8: sites.append(('B', a, 'addiu -> &0x%08X' % ea))
        if 0x8010FF00 <= ea <= 0x8010FF1C: sites.append(('C', a, 'addiu -> &0x%08X' % ea))
        if ea == 0x80000318: sites.append(('M', a, 'addiu -> &osMemSize'))
    if args and args[0].startswith('$') and op not in ('sw', 'sh', 'sb', 'sd', 'swc1', 'sdc1', 'j', 'jal', 'jr', 'beq', 'bne', 'beql', 'bnel'):
        live.pop(args[0], None)

# Manual classification (s7335 reading of each site; see PORTING-STATE s7335).
CLASS = {
    # partitionFramebufferMemory (0x80000DD4): top = cfg+0x44&0x2000 ? 0x80400000 : osMemSize|0x80000000;
    # 63E4 = top - zbuf; 63D8..63F8 = fb/aux regions carved downward from 63E4.
    0x80000EB4: 'derives: fixed 4 MB top only when cfg+0x44 bit 0x2000 (4 MB expansion-less mode; never set: see K note)',
    0x80000EBC: 'derives: osMemSize is THE top (librecomp clamps 4..16 MB -> tail end <= 0x81000000 = spill base)',
    0x80000ED8: 'writer: 63E4 = top - zbuf size',
    0x80000EFC: 'writer: 63D8 = 63E4 - fb',
    0x80000F1C: 'writer: 63D8 = top - (fb + 1 MB) (0x2000 branch-free layout)',
    0x80000F2C: 'writer: &63DC (fb1 = 63D8 - fb)',
    0x80000F5C: 'writer: 63E0 = 0 (single fb)',
    0x80000F7C: 'reader: 63D8 region top for aux carve',
    0x80000F8C: 'reader: 63E0', 0x80000F9C: 'reader: 63DC',
    0x80000FAC: 'writer: 63F0 aux', 0x80000FC0: 'writer: 63F0 aux',
    0x80000FD4: 'writer: 63F4 aux', 0x80000FE8: 'writer: 63F4 aux',
    0x80001010: 'writer: 63E8 aux',
    0x80001024: 'writer: 63F8 aux', 0x80001038: 'writer: 63F8 aux',
    0x8000104C: 'writer: 63EC aux', 0x8000105C: 'writer: 63EC aux',
    # thread3_video_handle boot layout + runVideoFrameTick per-scene layout: pass 63E4 as coalesce hi (a3) and
    # 63E4/63E8/63D8../63F8/63EC as the video/scene config (stack args) - all straight from the partition.
    0x80001198: 'consumer: boot coalesce hi = 63E4 (derived)',
    0x80001230: 'consumer: video cfg arg = 63E4', 0x80001238: 'consumer: video cfg arg = 63E8',
    0x80001250: 'consumer: &63D8 table', 0x8000126C: 'consumer: 63F8', 0x8000127C: 'consumer: 63EC',
    0x80001408: 'consumer: scene coalesce hi = 63E4 (s7334 sentinel writer)',
    0x8000143C: 'consumer: video cfg arg = 63E4', 0x80001444: 'consumer: video cfg arg = 63E8',
    0x80001454: 'consumer: &63D8 table', 0x80001470: 'consumer: 63F8', 0x80001480: 'consumer: 63EC',
    # ensureHeapInitialized: heap size = 63E4 - heap base (derived, no constant)
    0x80001930: 'consumer: heap init size = *63E4 - base (derived)',
    0x80000FFC: 'writer: 63E8 aux',
    0x80002680: 'scalar: getUsableRdramSize = 4 MB mode ? 0x400000 : osMemSize; its 2 callers store (size > 4 MB) = expansion flag 0x80130B63 (s7315)',
    # X: 24/23-bit masks
    0x80008600: 'class-D idx 528 (s7321): (ref & 0xFFFFFF)|0x80000000 packed ref chunks, latent alias, 0 spill sources at runtime',
    0x80011568: 'field mask: (w & 0xFFFFFF) == 0x020202 face-group flag compare, not an address',
    0x80011D78: 'field mask: (w & 0xFFFFFF) == 0x020202 face-group flag compare, not an address',
    0x8009419C: 'scalar: 0x7FFFFF - x MusyX pan coefficient, not an address',
    0x80094208: 'scalar: 0x7FFFFF - x MusyX pan coefficient, not an address',
    0x80017E20: 'scalar: 0x80808081 divide-by-255 magic (s7315)', 0x80057548: 'scalar: 0x80808081 divide-by-255 magic (s7315)',
    # C: heap globals 0x8010FF00 (deferred free-list head slot), 0x8010FF08..14 (last coalesce a1,a0,a2,a3 = hi), 0x8010FF18 (heap head).
    # FF08..FF14 are WRITE-ONLY in guest code: no reader re-uses the stored hi; every walker starts at FF18 and stops at the
    # fl=8 sentinel the coalescer wrote at hi-0x10, so the heap end is never re-derived from a constant.
    0x8000218C: 'write-only: initMainHeap args -> FF08', 0x80002194: 'write-only: FF0C', 0x8000219C: 'write-only: FF10', 0x800021A4: 'write-only: FF14',
    0x8000232C: 'write-only: coalesce a1 -> FF08', 0x80002334: 'write-only: coalesce a0 -> FF0C', 0x8000233C: 'write-only: coalesce a2 -> FF10',
    0x80002344: 'write-only: coalesce hi -> FF14',
    0x800021D8: 'heap head: FF18 = base', 0x80002214: 'heap head', 0x800022FC: 'heap head', 0x8000237C: 'heap head', 0x800024CC: 'heap head',
    0x800019D0: 'heap head: walk to sentinel', 0x80001A4C: 'heap head: walk to sentinel', 0x80001B60: 'heap head: walk to sentinel',
    0x80001B74: 'heap head', 0x80001B8C: 'heap head', 0x80001CC4: 'heap head: rs_free walk',
    0x8000184C: 'list head: &FF00 passed to buildHeapFreeList (reads offset 0 only)', 0x8000186C: 'list head: FF00 = 0', 0x80001A24: 'list head: FF00', 0x80001AA8: 'list head: FF00',
    0x80001B48: 'list head: FF00', 0x80001DA8: 'list head: FF00', 0x800022CC: 'list head: FF00 = 0', 0x80002584: 'list head: FF00 = 0',
}
by = collections.Counter(); bad = 0
for k, a, txt in sorted(sites, key=lambda s: s[1]):
    c = CLASS.get(a)
    if c is None and k == 'K': c = '(K listed, not audited)'
    if c is None: c = 'UNCLASSIFIED'; bad += 1
    by[(k, c.split(':')[0])] += 1
    print('%s %08X %-30s %-40s %s' % (k, a, fn[a], txt, c))
# positive control: the s7334-measured caller (scene coalesce hi load) and the bound writer must be found by the tracker
ctl = {0x80000ED8, 0x80001408, 0x80000EBC, 0x8000232C}
miss = ctl - {a for _, a, _ in sites}
print('control:', 'PASS' if not miss else 'FAIL missing %s' % sorted('%08X' % m for m in miss), '(%d sites)' % len(sites))
if miss: sys.exit(2)
print('summary:', dict(by))
print('unclassified B/M/X:', bad)
sys.exit(1 if bad else 0)
