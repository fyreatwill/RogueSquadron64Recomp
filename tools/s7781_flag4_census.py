#!/usr/bin/env python3
"""s7781: static census of rs_malloc (0x80001ACC) call sites whose flag argument a1 has bit 4 set (the frame-scoped FB scratch
arena, head 0x8010FEFC, dropped each frame by clearFrameReadyFlag). Source: the asm comments in N64Recomp/RecompiledFuncs/funcs_*.c.
For each jal the a1 value is resolved by a backward walk (delay slot first, then up to 24 insns back in the same function) over
addiu/ori/addu/or/move/lui writes to $a1. Then a forward walk (up to 40 insns after the delay slot) follows $v0: where it is first
stored (sw $v0 / copies to s-regs and their sw: base register sp = LOCAL, lui-global = GLOBAL, other = HEAP/STRUCT), and whether
rs_free (resolved by name from the generated code) is called within the function. Prints one row per flag-4 site, a class tally and
the unresolved count. rc 0 always for the census; rc 2 if the positive control fails (no site resolves a1 at all).
s7782: instructions are keyed per FUNCTION (overlay functions share addresses; the s7781 first-seen-by-address map mixed them, so
e.g. initCinematicSceneAssets 0x800AE5C8 walked back into another overlay's prologue and read UNRESOLVED). Sites whose a1 is not a
local constant are classified by hand in KNOWN (value + proof); a KNOWN entry that no longer matches an unresolved site is STALE
(rc 1), and an unresolved site not in KNOWN is open (rc 1). --controls: with KNOWN emptied the census must report unresolved>0
(proves KNOWN is what closes it) and a planted fake KNOWN entry must read STALE.
usage: s7781_flag4_census.py [--all] [--controls]"""
import re, sys, glob
D = "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/"
FINS, calls = {}, {}
for f in sorted(glob.glob(D + "funcs_*.c")):
    cur = None
    for l in open(f, errors="replace"):
        m = re.match(r'RECOMP_FUNC void (\w+)\(', l)
        if m: cur = m.group(1); FINS.setdefault(cur, {})
        m = re.match(r'\s*// 0x([0-9A-F]{8}): (\S+)\s*(.*)', l)
        if m and cur:
            a = int(m.group(1), 16)
            if a not in FINS[cur]: FINS[cur][a] = (m.group(2), [x.strip() for x in m.group(3).split(',')])
        m = re.match(r'\s*(\w+)\(rdram, ctx\);', l)
        if m and cur: calls.setdefault(cur, set()).add(m.group(1))
def imm(s):
    s = s.strip(); neg = s.startswith('-'); s = s.lstrip('-')
    v = int(s, 16) if s.lower().startswith('0x') else int(s)
    return -v if neg else v
def resolve(reg, a, depth=0):
    """value of reg just before insn a (walk back in the same function)"""
    if reg == '$zero': return 0
    b = a - 4
    for _ in range(24):
        if b not in ins: return None
        op, ar = ins[b]
        if op in ('jal', 'jalr'): return None
        if ar and ar[0] == reg:
            try:
                if op == 'addiu' and ar[1] == '$zero': return imm(ar[2]) & 0xFFFFFFFF
                if op == 'ori' and ar[1] == '$zero': return imm(ar[2]) & 0xFFFF
                if op == 'lui': return (imm(ar[1]) & 0xFFFF) << 16
                if op in ('addu', 'or', 'daddu') and '$zero' in ar[1:]:
                    src = ar[2] if ar[1] == '$zero' else ar[1]
                    return resolve(src, b, depth + 1) if depth < 4 else None
                if op in ('ori', 'addiu') and depth < 4:
                    v = resolve(ar[1], b, depth + 1)
                    if v is None: return None
                    return (v | (imm(ar[2]) & 0xFFFF)) if op == 'ori' else (v + imm(ar[2])) & 0xFFFFFFFF
                if op == 'andi' and depth < 4:
                    v = resolve(ar[1], b, depth + 1)
                    return None if v is None else v & imm(ar[2])
            except Exception: return None
            return None
        b -= 4
    return None
FREE = {n for n in set().union(*calls.values()) if 'free' in n.lower()}
rows = []
for F in FINS:
  ins = FINS[F]
  for a in sorted(ins):
      op, ar = ins[a]
      if op != 'jal' or not ar or ar[0].upper() != '0X80001ACC': continue
      d = ins.get(a + 4); a1 = None
      if d and d[1] and d[1][0] == '$a1':
          # delay slot writes a1: resolve as if the delay insn were the last writer
          dop, dar = d
          try:
              if dop == 'addiu' and dar[1] == '$zero': a1 = imm(dar[2]) & 0xFFFFFFFF
              elif dop == 'ori' and dar[1] == '$zero': a1 = imm(dar[2]) & 0xFFFF
              elif dop in ('addu', 'or') and '$zero' in dar[1:]: a1 = 0 if dar[1] == dar[2] == '$zero' else resolve(dar[2] if dar[1] == '$zero' else dar[1], a)
              elif dop == 'andi': v = resolve(dar[1], a); a1 = None if v is None else v & imm(dar[2])
          except Exception: a1 = None
      else: a1 = resolve('$a1', a)
      # forward: follow v0
      regs = {'$v0'}; dest = []; c = a + 8
      for _ in range(40):
          if c not in ins: break
          o, r = ins[c]
          if o in ('jal', 'jalr'):
              if '$v0' in regs: regs.discard('$v0')
          if o in ('sw', 'sd') and r and r[0] in regs:
              m = re.match(r'(-?(?:0x)?[0-9A-Fa-f]+)\((\$\w+)\)', r[1])
              if m:
                  base = m.group(2)
                  kind = 'LOCAL' if base == '$sp' else ('GLOBAL' if resolve(base, c) is not None and resolve(base, c) >= 0x80000000 else 'STRUCT')
                  dest.append('%s:%s' % (kind, r[1]))
          if o in ('addu', 'or', 'move') and len(r) >= 2 and any(x in regs for x in r[1:]) and '$zero' in r[1:]: regs.add(r[0])
          elif r and r[0] in regs and o not in ('sw', 'sd', 'sb', 'sh', 'beq', 'bne', 'beqz', 'bnez'): regs.discard(r[0])
          c += 4
      frees = sorted(calls.get(F, set()) & FREE)
      rows.append((a, F, a1, dest, frees))
# wrappers that forward a caller's flag: load_asset_with_malloc_flags(name, flags) -> rs_malloc(size, flags & 0xFFFF);
# flag-4-constant wrappers reached by jal (rs_zcalloc) or by function pointer (mallocWithFallbackStrategy: lui/addiu ref).
WRAP = {0x800647E0: 'load_asset_with_malloc_flags', 0x8000527C: 'rs_zcalloc', 0x80005224: 'mallocWithFallbackStrategy'}
wrows = []
for F in FINS:
  ins = FINS[F]
  for a in sorted(ins):
      op, ar = ins[a]
      if op == 'jal' and ar and int(ar[0], 16) in WRAP:
          t = int(ar[0], 16); d = ins.get(a + 4); v = None
          if t == 0x800647E0:
              if d and d[1] and d[1][0] == '$a1' and d[0] == 'addiu' and d[1][1] == '$zero': v = imm(d[1][2]) & 0xFFFFFFFF
              elif d and d[1] and d[1][0] == '$a1' and d[0] in ('addu', 'or'): v = resolve(d[1][2] if d[1][1] == '$zero' else d[1][1], a)
              else: v = resolve('$a1', a)
          wrows.append(('jal', a, F, WRAP[t], v))
      if op == 'addiu' and len(ar) == 3 and ar[1] != '$zero':
          b = resolve(ar[1], a)
          if b is not None and ((b + imm(ar[2])) & 0xFFFFFFFF) in WRAP and ((b + imm(ar[2])) & 0xFFFFFFFF) != 0x800647E0:
              wrows.append(('fnptr', a, F, WRAP[(b + imm(ar[2])) & 0xFFFFFFFF], None))
print("wrapper uses:")
for k, a, f, w, v in wrows:
    print(f"  {k:5s} 0x{a:08X} {f:44s} -> {w:28s} flags={'?' if v is None else hex(v)}{'  FLAG4' if v is not None and v & 4 else ''}")
JPEG = "JPEG decoder flags halfword state+0xE (lhu $a1,0xE): resetJfifDecodeState zmemcpy's the 0x30-byte param struct into the state; " \
       "sole caller of loadJfifAsset is openBackdropJpegAssets, param struct sp+0x40 whose word sp+0x4C is sw $zero (0x800B267C) -> 0"
KNOWN = {  # s7782, read by hand: addr -> (function, a1 value, proof)
    0x80055804: ("loadTxtFile", 0, "branch target L_800557F4 reached only by bne 0x80055744 whose delay slot 0x80055748 is addu $a1,$zero,$zero"),
    0x80064818: ("load_asset_with_malloc_flags", None, "forwards caller flags & 0xFFFF: every caller is a 'wrapper uses' row above"),
}
for _a, _f in [(0x800C6A08, "loadJfifAsset"), (0x800C78C0, "paserJfifSOSMarker"), (0x800C8454, "buildJpegHuffmanSizeTable"),
               (0x800C85F0, "buildJpegHuffmanCodeTable"), (0x800C8AE4, "buildJpegYccRgbTables"), (0x800C8AF4, "buildJpegYccRgbTables"),
               (0x800C8B04, "buildJpegYccRgbTables"), (0x800C8B14, "buildJpegYccRgbTables"), (0x800C9AA8, "buildJpegRangeLimitTables"),
               (0x800C9B20, "buildJpegRangeLimitTables"), (0x800C9BA0, "allocJpegDecoderState")]:
    KNOWN[_a] = (_f, 0, JPEG)
JPEG_STORE_OK = {  # s7782, read by hand: stores at 0xC-0xF whose base is NOT the decoder state
    ("parseJfifSOF0Marker", 0x800C73C4): "base $a1 = state + 0x6F8 + comp*44 (component table, 0x800C7310-0x800C7328)",
    ("openBackdropJpegAssets", 0x800B2864): "caller-side backdrop object, not the decoder state (state lives inside loadJfifAsset)",
    ("openBackdropJpegAssets", 0x800B283C): "caller-side backdrop object", ("openBackdropJpegAssets", 0x800B290C): "caller-side object $s2 (arg a1)",
    ("openBackdropJpegAssets", 0x800B2910): "caller-side object $s2 (arg a1)",
}
def jpeg_proof():
    """store side of the JPEG rows: no JPEG function stores a halfword/word at 0xE/0xC of a base, and loadJfifAsset's only caller
    is openBackdropJpegAssets, which zeroes sp+0x4C"""
    jf = [f for f in FINS if re.search(r'jfif|jpeg', f, re.I)]
    bad = [(f, hex(a)) for f in jf for a, (o, r) in FINS[f].items() if o in ('sh', 'sw', 'sb') and len(r) > 1
           and re.match(r'0x[CDEF]\(', r[1]) and not r[1].endswith('($sp)') and (f, a) not in JPEG_STORE_OK]
    callers = {f for f in FINS for a, (o, r) in FINS[f].items() if o == 'jal' and r and r[0].upper() == '0X800C6970'}
    zero = FINS.get('openBackdropJpegAssets', {}).get(0x800B267C) == ('sw', ['$zero', '0x4C($sp)'])
    return (not bad and callers == {'openBackdropJpegAssets'} and zero), (bad, sorted(callers), zero)
wcall = {r[1] for r in wrows if r[0] == 'jal' and r[3] == 'load_asset_with_malloc_flags'}
def score(known):
    unres = [r for r in rows if r[2] is None]
    open_ = [r for r in unres if r[0] not in known or known[r[0]][0] != r[1]]
    stale = [a for a, (f, v, w) in known.items() if not any(r[0] == a and r[1] == f for r in unres)]
    return unres, open_, stale
res = [r for r in rows if r[2] is not None]
f4 = [r for r in res if r[2] & 4]
unres, open_, stale = score(KNOWN)
jok, jdet = jpeg_proof()
kf4 = [a for a in KNOWN if KNOWN[a][1] is not None and KNOWN[a][1] & 4]
print(f"rs_malloc call sites={len(rows)} a1 resolved={len(res)} known={len(unres) - len(open_)} unresolved={len(open_)} stale={len(stale)} flag4={len(f4) + len(kf4)}")
print(f"jpeg store-side proof: {'ok' if jok else 'FAILED'} {jdet}")
show = rows if '--all' in sys.argv else f4 + unres
for a, f, a1, dest, frees in show:
    k = KNOWN.get(a) if a1 is None else None
    cls = ('KNOWN' if k and k[0] == f else 'UNRESOLVED') if a1 is None else ('FLAG4' if a1 & 4 else 'plain')
    val = hex(a1) if a1 is not None else ('fwd' if k and k[1] is None else (hex(k[1]) if k else '?'))
    print(f"{cls:10s} 0x{a:08X} {f:44s} a1={val:6s} v0->{','.join(dest[:3]) or 'reg-only'} free={','.join(frees) or '-'}")
for a in stale: print(f"STALE known entry 0x{a:08X} {KNOWN[a][0]}: no unresolved site matches it")
if not res: print("CONTROL FAIL: no a1 resolved"); sys.exit(2)
if '--controls' in sys.argv:
    u0, o0, s0 = score({})
    u1, o1, s1 = score({**KNOWN, 0x80001234: ("plantedFake", 0, "planted")})
    ok = len(o0) == len(u0) > 0 and s1 == [0x80001234] and not o1
    print(f"control empty-known open={len(o0)} (must be >0), planted-fake stale={[hex(x) for x in s1]} (must be the plant): {'PASS' if ok else 'FAIL'}")
    if not ok: sys.exit(2)
    print("CONTROLS PASS")
sys.exit(1 if (open_ or stale or not jok) else 0)
