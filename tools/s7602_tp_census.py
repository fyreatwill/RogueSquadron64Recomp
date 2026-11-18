#!/usr/bin/env python3
"""s7602 class TP: guest memory dereferenced as a HOST TYPE (TO_PTR(T, x), _arg<N, T*>, GET_MEMBER(T, ...)).

Residual of class BS (s7601), which checked raw rdram views and 6 struct layouts.  Note: PTR(T) expands to int32_t in this
build (ultra64.h), so `_arg<N, PTR(T)>` is an integer and never dereferences; only TO_PTR / _arg<N, T*> / GET_MEMBER are views.
On this little-endian host guest RAM is native 32-bit words, so a host type T read through the view is correct iff:
  word scalar     T is 32-bit (u32/s32/OSMesg/PTR(..))                                        -> ok-word
  word struct     every member T touches is 32-bit (host offset == BE offset)                  -> ok-word
  swizzled        sub-word members sit reversed in their word; proven by s7601 struct_check     -> ok-swizzled
  risky member    sub-word member not proven swizzled, or a 64-bit/host-pointer member: allowed only if no typed
                  variable of T ever accesses it (scan `v->m` / `v.m` for every `T* v` in the file), else it needs a
                  TYPE_ROWS entry (host-private: written and read only by host code) or it is OPEN
  scalar sub-word T is u8/s8/char/u16/s16/int16_t/void: needs a SITE_ROWS entry (consumer named, gated, or address-only)
Scope: src/, librecomp/{src,include}, ultramodern/{src,include}; tests skipped, comments stripped, #define lines skipped.
--controls: (1) plant `TO_PTR(uint16_t, a)[0]` read into a copy of cont.cpp -> OPEN; (2) drop one site row -> OPEN;
(3) add a u16 member to OSMesgQueue in a copy of ultra64.h and access it -> OPEN; (4) plant `OSContPad* p = TO_PTR(OSContPad,
d); p->stick_x` (host decl NOT swizzled) -> OPEN; (5) drop the OSTimer type row -> OPEN.  Exit 0 only if 0 open, 0 stale rows,
s7601 structs all ok-swizzled and 5/5 controls.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import s7601_bs_census as BS

L = "lib/N64ModernRuntime"
DIRS = ["src", L + "/librecomp/src", L + "/librecomp/include", L + "/ultramodern/src", L + "/ultramodern/include"]
ULTRA = BS.ULTRA
WORD_SCALARS = {"uint32_t", "u32", "s32", "int32_t", "OSMesg", "OSId", "OSPri", "OSEvent", "int", "unsigned", "float", "gpr32"}
SUB_SCALARS = {"uint8_t", "u8", "int8_t", "s8", "char", "uint16_t", "u16", "int16_t", "s16", "void"}
SIZE = {"u8": 1, "s8": 1, "uint8_t": 1, "int8_t": 1, "char": 1, "u16": 2, "s16": 2, "uint16_t": 2, "int16_t": 2,
        "u64": 8, "s64": 8, "uint64_t": 8, "int64_t": 8, "OSTime": 8, "double": 8}

# Members of a 64-bit / unproven kind that host code does touch, each proven host-private.
TYPE_ROWS = {
    ("OSThread", "context"): "host-private: UltraThreadContext* lives in the guest OSThread's register-save area, which no "
        "guest code reads (libultra thread switching is replaced by ultramodern; s7601 checked flags/state)",
    ("OSTimer", "interval"): "host-private: ultramodern/src/timer.cpp declares its own OSTimer; interval/timestamp are written "
        "by host osSetTimer / the timer thread and read only there (std::set comparator, reload); libultra's timer list is "
        "replaced, the guest only hands the struct address over. Halves are word-swapped vs retail u64 order, invisible "
        "unless the guest reads OSTimer+8..+23. Second source (s7602, /tmp/s7419_canon.dis): the only live guest timer is 0x801128F0 (installPeriodicCallback, s7397); its base is formed once as mq-32 and passed to osSetTimer; no load/store at 0x801128F8..0x80112907 (lo 10488-10503) or at -24..-9 off the mq base in installPeriodicCallback/periodicCallbackWorker",
    ("OSTimer", "timestamp"): "host-private: see OSTimer.interval",
}
# Sub-word scalar views, (file suffix, line substring, verdict).
SITE_ROWS = [
    ("librecomp/src/ai.cpp", "TO_PTR(uint8_t, (uint64_t)(int32_t)addr)",
     "consumer: every read is p[(i) ^ 3] (byte lane swizzled); gated title/hangar AI-buffer FNV diag"),
    ("ultramodern/src/audio.cpp", "TO_PTR(int16_t, audio_data_));",
     "gated: [pcm-boundary-source] FNV over raw host bytes (order is cosmetic in a log hash) under phase_allowed diag"),
    ("ultramodern/src/audio.cpp", "audio_callbacks.queue_samples(TO_PTR(int16_t, audio_data_)",
     "consumer: src/main/main.cpp queue_samples rebuilds each sample from n64_bytes[(i*2)^3]<<8 | [(i*2+1)^3] (s4242)"),
    ("librecomp/src/heap.cpp", "recomp::free(rdram, TO_PTR(void, to_free))",
     "addr: host allocator takes the address only, no data access"),
]

def load(over=None):
    files = {}
    for d in DIRS:
        for r, _, fs in os.walk(os.path.join(ROOT, d)):
            for f in fs:
                p = os.path.join(r, f); rel = os.path.relpath(p, ROOT)
                if BS.SKIP.search("/" + rel) or not f.endswith(BS.EXT): continue
                src = open(p, errors="ignore").read()
                if over and rel in over: src = over[rel]
                files[rel] = BS.strip_comments(src)
    return files

def parse_structs(text):
    """name -> [(member, elem_size_or_type)] for struct/union bodies (typedef'd or tagged)."""
    out = {}
    for m in re.finditer(r"(?:typedef\s+)?(struct|union)\s*(\w*)\s*\{", text):
        end = BS.balanced(text, m.end(), "{", "}")
        body = text[m.end():end]
        after = re.match(r"\s*(\w+)\s*;", text[end + 1:])
        names = [n for n in (m.group(2), after.group(1) if after else None) if n]
        mem = []
        for decl in re.sub(r"\{[^{}]*\}", "", body).split(";"):
            d = " ".join(decl.split())
            if not d: continue
            mm = re.match(r"(.*?)(\w+)\s*(?:\[\w+\])?$", d)
            if not mm: continue
            typ = mm.group(1).strip()
            if not typ: continue
            if "*" in typ: el = 8
            elif typ.startswith("PTR("): el = 4
            else:
                t = typ.replace("struct ", "").replace("const ", "").strip()
                el = SIZE.get(t, t if t not in WORD_SCALARS and t[0].isupper() else 4)
            mem.append((mm.group(2), el))
        for n in names:
            out.setdefault(n.replace("_t", "") if n == "OSThread_t" else n, mem)
    return out

def proven(struct_res):
    """(type, member) pairs whose swizzle s7601 struct_check proved."""
    ok = set()
    for name, be in BS.STRUCTS.items():
        res = [s for s in struct_res if s[0] == name]
        if not res or res[0][1] != "ok-swizzled": continue
        t = {"OSThread_t": "OSThread", "OSPfs_tail": "OSPfs"}.get(name, name)
        for nm, sz in be:
            if sz < 4: ok.add((t, nm))
    return ok

def risky(t, structs, prov, seen=()):
    """Members of t (flattened by name) that are not 32-bit-safe: (member, why)."""
    if t not in structs or t in seen: return None
    out = []
    for nm, el in structs[t]:
        if isinstance(el, str):
            sub = risky(el, structs, prov, seen + (t,))
            if sub is None: out.append((nm, f"unknown member type {el}"))
            else: out += sub
        elif el < 4 and (t, nm) not in prov and not nm.startswith("pad"): out.append((nm, f"{el}-byte unproven"))
        elif el == 8: out.append((nm, "64-bit/host-pointer"))
    return out

SITE = re.compile(r"\bTO_PTR\s*\(\s*|\b_arg<\s*\d+\s*,\s*(?=[\w:]+\s*\*\s*>)|\bGET_MEMBER\s*\(\s*")

def site_type(l, m):
    s = l[m.end():]
    if m.group(0).startswith("_arg"): return re.match(r"([\w:]+)", s).group(1)
    d = 0
    for i, c in enumerate(s):
        if c in "(<": d += 1
        elif c in ")>": d -= 1
        elif c == "," and d == 0: return " ".join(s[:i].replace("const", "").split())
    return s.strip()

def run(over=None, ultra_src=None, site_rows=None, type_rows=None):
    site_rows = SITE_ROWS if site_rows is None else site_rows
    type_rows = TYPE_ROWS if type_rows is None else type_rows
    files = load(over)
    usrc = ultra_src if ultra_src is not None else open(os.path.join(ROOT, ULTRA)).read()
    if over is None or ULTRA not in over:
        files[ULTRA] = BS.strip_comments(usrc)
    st = BS.struct_check(BS.strip_comments(usrc)); sbad = [s for s in st if s[1] != "ok-swizzled"]
    prov = proven(st)
    gstructs = parse_structs("\n".join(BS.strip_comments(usrc)))
    res, open_, used_s, used_t, sites = {}, [], set(), set(), 0
    per_type = {}
    for rel, lines in files.items():
        text = "\n".join(lines)
        structs = dict(gstructs); structs.update(parse_structs(text))
        for i, l in enumerate(lines):
            if re.search(r"#\s*define", l): continue
            for m in SITE.finditer(l):
                t = site_type(l, m); sites += 1
                per_type[t] = per_type.get(t, 0) + 1
                if t.startswith("PTR(") or t in WORD_SCALARS: v = "ok-word"
                elif t.startswith("std::remove_pointer_t"): v = "generic"   # helpers.hpp _arg template; instantiations counted
                elif t in SUB_SCALARS:
                    hit = next((k for k, (f, sub, _) in enumerate(site_rows) if rel.endswith(f) and sub in l), None)
                    if hit is None: open_.append((rel, i + 1, f"sub-word scalar {t}", l.strip()[:150])); continue
                    used_s.add(hit); v = "row:" + site_rows[hit][2].split(":")[0]
                else:
                    rk = risky(t, structs, prov)
                    if rk is None: open_.append((rel, i + 1, f"unknown type {t}", l.strip()[:150])); continue
                    # typed variables of t in this file, plus direct TO_PTR(t, x)->m
                    vars_ = set(re.findall(r"\b" + re.escape(t) + r"\s*\*\s*(\w+)", text))
                    acc = []
                    for nm, why in rk:
                        pat = re.compile(r"(?:\b(?:" + "|".join(map(re.escape, vars_ or {"__none__"})) + r")|TO_PTR\s*\(\s*"
                                         + re.escape(t) + r"\s*,[^;]*?\))\s*(?:->|\.)\s*(?:\w+\s*\.\s*)?" + re.escape(nm) + r"\b")
                        if pat.search(text): acc.append((nm, why))
                    bad = [(nm, why) for nm, why in acc if (t, nm) not in type_rows]
                    for nm, _ in acc:
                        if (t, nm) in type_rows: used_t.add((t, nm))
                    if bad:
                        open_.append((rel, i + 1, f"{t} risky member(s) accessed: " + ", ".join(f"{a} ({b})" for a, b in bad),
                                      l.strip()[:150])); continue
                    v = "host-private" if acc else ("ok-swizzled" if any((t, x) in prov for x, _ in structs.get(t, [])) else "ok-word")
                res[v] = res.get(v, 0) + 1
    stale = [site_rows[k] for k in range(len(site_rows)) if k not in used_s] + [k for k in type_rows if k not in used_t]
    return dict(sites=sites, res=res, open=open_, stale=stale, structs=st, sbad=sbad, per_type=per_type)

def report(r):
    print(f"[s7602-tp] sites={r['sites']} open={len(r['open'])} stale_rows={len(r['stale'])} struct_bad={len(r['sbad'])}")
    print("  verdicts: " + " ".join(f"{k}={v}" for k, v in sorted(r["res"].items())))
    print("  types: " + " ".join(f"{k}={v}" for k, v in sorted(r["per_type"].items(), key=lambda x: -x[1])))
    for o in r["open"]: print("  OPEN", o[0] + ":" + str(o[1]), o[2], "|", o[3])
    for s in r["stale"]: print("  STALE", s)

def controls():
    ok = 0
    cp = L + "/librecomp/src/cont.cpp"; src = open(os.path.join(ROOT, cp)).read()
    r = run({cp: src + "\nstatic uint16_t s7602_plant1(uint8_t* rdram, int32_t a) { return TO_PTR(uint16_t, a)[0]; }\n"})
    c = any("s7602_plant1" in o[3] for o in r["open"]); ok += c; print(f"[s7602-ctl] 1 u16 scalar view plant -> {'OPEN' if c else 'MISSED'}")
    rows = list(SITE_ROWS); drop = rows.pop(0); r = run(site_rows=rows)
    c = any(o[0].endswith(drop[0]) and drop[1] in o[3] for o in r["open"]); ok += c
    print(f"[s7602-ctl] 2 drop site row {drop[0]} -> {'OPEN' if c else 'MISSED'}")
    u = open(os.path.join(ROOT, ULTRA)).read()
    u2 = u.replace("    s32 validCount;", "    u16 s7602_half;\n    u16 s7602_pad;\n    s32 validCount;", 1)
    mq = L + "/ultramodern/src/mesgqueue.cpp"; msrc = open(os.path.join(ROOT, mq)).read()
    r = run({mq: msrc + "\nstatic int s7602_plant3(uint8_t* rdram, int32_t a) { OSMesgQueue* q3 = TO_PTR(OSMesgQueue, a); return q3->s7602_half; }\n"},
            ultra_src=u2)
    c = u2 != u and any("s7602_half" in o[2] for o in r["open"]); ok += c
    print(f"[s7602-ctl] 3 u16 member added to OSMesgQueue and read -> {'OPEN' if c else 'MISSED'}")
    r = run({cp: src + "\nstatic int s7602_plant4(uint8_t* rdram, int32_t d) { OSContPad* p4 = TO_PTR(OSContPad, d); return p4->stick_x; }\n"})
    c = any("stick_x" in o[2] for o in r["open"]); ok += c
    print(f"[s7602-ctl] 4 OSContPad (unswizzled host decl) view -> {'OPEN' if c else 'MISSED'}")
    tr = dict(TYPE_ROWS); tr.pop(("OSTimer", "interval")); r = run(type_rows=tr)
    c = any("OSTimer" in o[2] and "interval" in o[2] for o in r["open"]); ok += c
    print(f"[s7602-ctl] 5 drop OSTimer.interval type row -> {'OPEN' if c else 'MISSED'}")
    return ok

if __name__ == "__main__":
    r = run(); report(r)
    good = not r["open"] and not r["stale"] and not r["sbad"]
    if "--controls" in sys.argv:
        n = controls(); print(f"[s7602-ctl] {n}/5"); good = good and n == 5
    sys.exit(0 if good else 1)
