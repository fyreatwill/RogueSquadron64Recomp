#!/usr/bin/env python3
"""s7601 class BS: host accesses to guest RAM through the byte-swapped host view with the wrong swizzle for their width.

Contract on this little-endian host (guest RAM stored as native-endian 32-bit words):
  byte at guest A      rdram[A ^ 3]
  halfword at A        *(uint16_t*)(rdram + (A ^ 2))          (A 2-aligned)
  word at A            *(uint32_t*)(rdram + A)                (A 4-aligned, no xor)
  multi-word span      memcpy/hash of whole words is byte-order agnostic only if its consumer is (named)
Scope: src/, librecomp/src, ultramodern/src, lib/rt64/src (skips tests/tools/contrib/examples/demos/gui), // and /* */ comments
stripped. Views: rdram, RDRAM, g_rdram_for_submit (all uint8_t*; checked: no uint32_t* view of that name in scope).
Part A, raw-view sites  `V[e]`, `&V[e]`, `V + e`.  Auto verdicts:
  ok-byte     V[e] with e ending in ^3 (byte read/write)
  ok-half     uint16_t/int16_t cast or 2-byte memcpy with e ending in ^2
  ok-word     32-bit cast (uint32_t/int32_t/float/u32/s32) or 4-byte memcpy, no xor in e, and e aligned: literal %4==0,
              or masked with a ...C / ~3 mask (word alignment stated in the expression)
  symmetric   byte-order agnostic: != 0 / nonzero / any_nonzero, compare against a shadow of the same view, memcmp, XXH3/fnv
              hash, memset 0, shadow copies (insert/assign/memcpy into or out of a same-layout host shadow)
  bound       a range guard: pointer compared against V (b < rdram || b >= rdram + N)
Everything else needs a ROW (tools/s7601_bs_rows.py: (file, line-substring) -> verdict) or it is OPEN.  Row verdict prefixes:
  ok-*        as above, proven by the row note (e.g. word alignment by construction)
  consumer    bulk span / pointer alias whose consumer handles the word layout (named)
  gated       env-gated diagnostic / dump / log, or a path off in the owner recipe (gate named); byte order in a log is cosmetic
  BAD         wrong swizzle on a default path (defect row: must be 0 after fixes)
Part B, structs reached through TO_PTR / _arg<PTR(T)> (guest memory used as a host struct): every sub-word member must sit in
  its word in reversed order (BE offset o -> host offset o ^ 3 for bytes, o ^ 2 for halves).  STRUCTS below names each type's
  retail big-endian member order; the scanner reads the ultra64.h declaration and checks the swizzle.
Part C, MEM_B/MEM_H/MEM_W/... macro sites: ok-macro by construction (recomp.h applies ^3/^2), counted.
--controls: (1) plant `rdram[a]` byte read with no ^3 into a copy of dpc_bridge.cpp -> OPEN; (2) plant
`*(uint16_t*)(rdram + (a ^ 3))` -> OPEN (wrong xor for a half); (3) drop one row -> OPEN; (4) swap OSIoMesgHdr's u8 pair in a
copy of ultra64.h -> struct BAD.  Exit 0 only if 0 open + 0 BAD + 0 stale rows + 4/4 controls.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
DIRS = ["src", "lib/N64ModernRuntime/librecomp/src", "lib/N64ModernRuntime/ultramodern/src", "lib/rt64/src"]
SKIP = re.compile(r"/(tests?|tools|contrib|examples?|demos?|gui|imgui)/")
EXT = (".cpp", ".cc", ".c", ".h", ".hpp", ".mm")
ULTRA = "lib/N64ModernRuntime/ultramodern/include/ultramodern/ultra64.h"
VIEW = r"(?:rdram|RDRAM|g_rdram_for_submit)"
SITE = re.compile(r"(&\s*)?(?<![\w.>])(?:(?:app->core\.|state->|this->)?)(" + VIEW + r")\s*(\[|\+(?!\+))")
XOR3 = re.compile(r"\^\s*(?:3|0x3)[uU]?\s*\)*\s*(?:&\s*0x[0-9a-fA-F]*[37bBfF][uU]?\s*|-\s*0x[0-9a-fA-F]*[048cC]0*[uU]?\s*)?\)*\s*$")
# ^3 may be followed by a mask keeping bits 0-1 (& 0x..F/7/B/3) or minus a multiple of 4 (e.g. - 0x80000000u): same byte lane
XOR2 = re.compile(r"\^\s*(?:2|0x2)[uU]?\s*\)*\s*$")
W32 = r"(?:const\s+)?(?:volatile\s+)?(?:const\s+)?(?:uint32_t|int32_t|float|u32|s32|unsigned)"
W16 = r"(?:const\s+)?(?:volatile\s+)?(?:const\s+)?(?:uint16_t|int16_t|u16|s16)"

def strip_comments(src):
    src = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), src, flags=re.S)
    return [re.sub(r"//.*$", "", l) for l in src.split("\n")]

def load(over=None):
    files = {}
    for d in DIRS:
        for r, _, fs in os.walk(os.path.join(ROOT, d)):
            for f in fs:
                p = os.path.join(r, f); rel = os.path.relpath(p, ROOT)
                if SKIP.search("/" + rel) or not f.endswith(EXT): continue
                src = open(p, errors="ignore").read()
                if over and rel in over: src = over[rel]
                files[rel] = strip_comments(src)
    return files

def balanced(s, i, open_c, close_c):
    """s[i] is just after an opening char; return index of the matching close (or len)."""
    d = 1
    while i < len(s):
        if s[i] == open_c: d += 1
        elif s[i] == close_c:
            d -= 1
            if d == 0: return i
        i += 1
    return len(s)

def addend(s, i):
    """Expression after `V +` up to the enclosing close paren / comma / semicolon at depth 0."""
    d = 0; j = i
    while j < len(s):
        c = s[j]
        if c in "([": d += 1
        elif c in ")]":
            if d == 0: break
            d -= 1
        elif c in ",;" and d == 0: break
        j += 1
    return s[i:j].strip()

def aligned(e):
    e = e.strip()
    while e.startswith("(") and balanced(e, 1, "(", ")") == len(e) - 1: e = e[1:-1].strip()
    m = re.fullmatch(r"(0x[0-9a-fA-F]+|\d+)[uU]?", e)
    if m: return int(m.group(1), 0) % 4 == 0
    if re.search(r"&\s*(?:0x[0-9a-fA-F]*[cC]|~\s*3[uU]?|~\s*0x3[uU]?|kSubmitRamMask)\s*[uU]?\s*\)*\s*$", e): return True
    return False

def classify(line, m):
    amp, view, kind = m.group(1), m.group(2), m.group(3)
    pre = line[:m.start()]
    if kind == "[":
        close = balanced(line, m.end(), "[", "]"); e = line[m.end():close]; post = line[close + 1:]
    else:
        e = addend(line, m.end()); post = line[m.end() + len(e):]
    ptr = kind == "+" or bool(amp)
    if not ptr:
        if XOR3.search(e): return "ok-byte", e
        if re.match(r"\s*!=\s*0\b", post) or re.search(r"(nonzero|any_nonzero|\bnz)\s*(\+=|\|=)\s*$", pre): return "symmetric", e
        if re.search(r"!=\s*[\w.]+\[[^\]]*\]", post) and re.search(r"\[\s*" + re.escape(e.strip()) + r"\s*\]", post): return "symmetric", e
        if re.search(r"\w+\[\w+\]\s*!=\s*$", pre): return "symmetric", e
        if re.search(r"\b(uint8_t|u8)\s*\(\s*$", pre) is None and re.match(r"\s*\^=\s*0x5A", post): return "byte-flip", e
        return "byte", e
    # pointer: find the cast or call it is wrapped in
    t = pre.rstrip()
    if re.search(r"reinterpret_cast<\s*" + W32 + r"\s*\*\s*>\s*\(\s*$", t) or re.search(r"\(\s*" + W32 + r"\s*\*\s*\)\s*\(\s*$", t) \
       or re.search(r"\(\s*" + W32 + r"\s*\*\s*\)\s*$", t):
        if "^" in e: return "word-xor", e
        return ("ok-word" if aligned(e) else "word"), e
    if re.search(r"reinterpret_cast<\s*" + W16 + r"\s*\*\s*>\s*\(\s*$", t) or re.search(r"\(\s*" + W16 + r"\s*\*\s*\)\s*\(\s*$", t):
        return ("ok-half" if XOR2.search(e) else "half"), e
    mc = re.search(r"\b(memcpy|memcmp|memset|memmove)\s*\((.*)$", t)
    if mc:
        rest = line[m.start():]
        args = re.split(r",(?![^()]*\))", line[mc.start(1) + len(mc.group(1)) + 1: balanced(line, mc.start(1) + len(mc.group(1)) + 1, "(", ")")])
        n = args[-1].strip() if args else ""
        if mc.group(1) == "memset" and len(args) >= 2 and args[1].strip() in ("0", "0x00"): return "symmetric", e
        if n in ("4", "sizeof(uint32_t)", "sizeof(value)", "sizeof(aligned)", "sizeof(explicit_read)", "sizeof(v)"):
            if "^" in e: return "word-xor", e
            return ("ok-word" if aligned(e) else "word"), e
        if n in ("2", "sizeof(uint16_t)"): return ("ok-half" if XOR2.search(e) else "half"), e
        if mc.group(1) == "memcmp": return "symmetric", e
        return "bulk", e
    if re.search(r"\b(XXH3_64bits\w*|XXH3_64bits_update|fnv|rs64LrepHash)\s*\(\s*(&\w+\s*,\s*)?$", t): return "symmetric", e
    if re.search(r"\.(insert|assign)\s*\([^;]*$", t): return "symmetric", e
    if re.search(r"[<>]=?\s*$", t) or re.match(r"\s*\)?\s*[<>]", post) and re.search(r"\b\w+\s*[<>]=?\s*$", t): return "bound", e
    if re.search(r"\b(fwrite|\.write)\s*\(\s*$", t): return "dump", e
    return "alias", e

# ---- Part B: guest structs ------------------------------------------------------------------------------------------------
# retail big-endian member order (name, size) per type, from libultra os.h / os_pi.h / os_cont.h / os_vi.h / os_thread.h
STRUCTS = {
    "OSThread_t": [("next", 4), ("priority", 4), ("queue", 4), ("pad2", 4), ("state", 2), ("flags", 2), ("id", 4), ("pad3", 4),
                   ("context", 4), ("sp", 4)],
    "OSIoMesgHdr": [("type", 2), ("pri", 1), ("status", 1), ("retQueue", 4)],
    "OSPiHandle": [("next", 4), ("type", 1), ("latency", 1), ("pageSize", 1), ("relDuration", 1), ("pulse", 1), ("domain", 1),
                   ("padding", 2), ("baseAddress", 4), ("speed", 4)],
    "OSContStatus": [("type", 2), ("status", 1), ("err_no", 1)],
    "OSViMode": [("type", 1), ("padding", 3)],
    "OSPfs_tail": [("banks", 1), ("activebank", 1), ("padding", 2)],
}
SIZES = {"u8": 1, "s8": 1, "uint8_t": 1, "int8_t": 1, "u16": 2, "s16": 2, "uint16_t": 2, "int16_t": 2}

def struct_check(src_lines):
    """For each STRUCTS type, read its member declarations from ultra64.h and check every sub-word member's host offset
    equals its BE offset swizzled (^3 byte, ^2 half) within its word.  Word members are layout-neutral."""
    text = "\n".join(src_lines); out = []
    for name, be in STRUCTS.items():
        tname = "OSPfs" if name == "OSPfs_tail" else name
        m = re.search(r"(?:typedef\s+)?struct\s+" + tname + r"\s*\{(.*?)\}", text, re.S) or \
            re.search(r"typedef\s+struct\s*\{((?:(?!typedef).)*?)\}\s*" + tname + r"\s*;", text, re.S)
        if not m: out.append((name, "MISSING", "type not found in ultra64.h")); continue
        mem = []
        for decl in m.group(1).split(";"):
            d = decl.strip()
            if not d: continue
            mm = re.match(r"(?:PTR\([^)]*(?:\([^)]*\))?[^)]*\)|[\w:]+(?:\s*\*)?)\s+(\w+)\s*(?:\[(\d+)\])?\s*$", d.replace("\n", " "))
            if not mm: continue
            typ = d.split()[0]
            sz = SIZES.get(typ, 4) * (int(mm.group(2)) if mm.group(2) else 1)
            mem.append((mm.group(1), sz, SIZES.get(typ, 4)))
        if name == "OSPfs_tail":
            mem = [x for x in mem if x[0] in ("padding", "activebank", "banks")]
        host, o = {}, 0
        for nm, sz, el in mem:
            if el < 4 and o % el: o += el - o % el
            host[nm] = (o, el); o += sz
        beo, o = {}, 0
        for nm, sz in be: beo[nm] = o; o += sz
        if name == "OSPfs_tail":
            base = min(v[0] for v in host.values()); host = {k: (v[0] - base, v[1]) for k, v in host.items()}
        bad = []
        for nm, sz in be:
            if sz >= 4 or nm.startswith("pad"): continue
            if nm not in host: bad.append(f"{nm} missing"); continue
            ho, el = host[nm]; want = beo[nm] ^ (3 if sz == 1 else 2)
            if ho != want: bad.append(f"{nm} host+{ho} want+{want}")
        out.append((name, "BAD" if bad else "ok-swizzled", "; ".join(bad) or f"{sum(1 for _, s in be if s < 4)} sub-word members swizzled"))
    return out

def run(over=None, rows=None, ultra_src=None, verbose=False):
    import s7601_bs_rows as R
    rows = R.ROWS if rows is None else rows
    files = load(over)
    sites, auto = [], {}
    for rel, lines in files.items():
        for i, l in enumerate(lines):
            if "#define" in l: continue
            for m in SITE.finditer(l):
                v, e = classify(l, m)
                sites.append((rel, i + 1, v, e, l.strip()))
    used = set(); res = {}; open_ = []; bad = []
    for rel, ln, v, e, l in sites:
        if v in ("ok-byte", "ok-half", "ok-word", "symmetric", "bound"):
            res[v] = res.get(v, 0) + 1; continue
        hit = None
        for k, (f, sub, verdict) in enumerate(rows):
            if rel.endswith(f) and sub in l: hit = k; break
        if hit is None: open_.append((rel, ln, v, l[:150])); continue
        used.add(hit); verdict = rows[hit][2]
        key = verdict.split()[0]
        res["row:" + key] = res.get("row:" + key, 0) + 1
        if key == "BAD": bad.append((rel, ln, verdict, l[:150]))
    stale = [rows[k] for k in range(len(rows)) if k not in used]
    usrc = ultra_src if ultra_src is not None else open(os.path.join(ROOT, ULTRA)).read()
    st = struct_check(strip_comments(usrc))
    sbad = [s for s in st if s[1] != "ok-swizzled"]
    macro = 0
    for rel, lines in files.items():
        for l in lines:
            if "#define" not in l: macro += len(re.findall(r"\bMEM_(?:B|BU|H|HU|W|WU|D|DU)\s*\(", l))
    return dict(sites=len(sites), res=res, open=open_, bad=bad, stale=stale, structs=st, sbad=sbad, macro=macro)

def report(r):
    print(f"[s7601-bs] sites={r['sites']} open={len(r['open'])} bad={len(r['bad'])} stale_rows={len(r['stale'])} "
          f"struct_bad={len(r['sbad'])} macro_sites={r['macro']}")
    print("  verdicts: " + " ".join(f"{k}={v}" for k, v in sorted(r["res"].items())))
    for s in r["structs"]: print(f"  struct {s[0]}: {s[1]} ({s[2]})")
    for o in r["open"]: print("  OPEN", o[0] + ":" + str(o[1]), o[2], "|", o[3])
    for b in r["bad"]: print("  BAD ", b[0] + ":" + str(b[1]), b[2], "|", b[3])
    for s in r["stale"]: print("  STALE", s)

def controls():
    import s7601_bs_rows as R
    ok = 0
    dp = "src/rsp/dpc_bridge.cpp"; src = open(os.path.join(ROOT, dp)).read()
    r = run({dp: src + "\nstatic uint8_t s7601_plant1(uint32_t a) { return g_rdram_for_submit[a + 0x40]; }\n"})
    c1 = any("s7601_plant1" in o[3] for o in r["open"]); ok += c1; print(f"[s7601-ctl] 1 byte-no-xor plant -> {'OPEN' if c1 else 'MISSED'}")
    r = run({dp: src + "\nstatic uint16_t s7601_plant2(uint32_t a) { return *(uint16_t*)(g_rdram_for_submit + (a ^ 3)); }\n"})
    c2 = any("s7601_plant2" in o[3] for o in r["open"]); ok += c2; print(f"[s7601-ctl] 2 half-with-^3 plant -> {'OPEN' if c2 else 'MISSED'}")
    rows = list(R.ROWS); drop = rows.pop(0)
    r = run(rows=rows)
    c3 = any(o[0].endswith(drop[0]) and drop[1] in o[3] for o in r["open"]); ok += c3
    print(f"[s7601-ctl] 3 drop row {drop[0]}:{drop[1][:40]!r} -> {'OPEN' if c3 else 'MISSED'}")
    u = open(os.path.join(ROOT, ULTRA)).read()
    u2 = u.replace("    u8 status;                 /* Return status */\n    u8 pri;", "    u8 pri;\n    u8 status;                 /* Return status */", 1)
    r = run(ultra_src=u2)
    c4 = u2 != u and any(s[0] == "OSIoMesgHdr" and s[1] == "BAD" for s in r["structs"]); ok += c4
    print(f"[s7601-ctl] 4 OSIoMesgHdr u8 pair swapped -> {'BAD' if c4 else 'MISSED'}")
    return ok

if __name__ == "__main__":
    r = run(); report(r)
    good = not r["open"] and not r["bad"] and not r["stale"] and not r["sbad"]
    if "--controls" in sys.argv:
        n = controls(); print(f"[s7601-ctl] {n}/4"); good = good and n == 4
    sys.exit(0 if good else 1)
