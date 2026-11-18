#!/usr/bin/env python3
"""s7600 class GX: fixed-size host arrays subscripted by a guest-derived value with no mask/clamp/range check -> host OOB.

Scope: src/, librecomp/src, ultramodern/src, lib/rt64/src (skips tests/tools/contrib/examples/demos/gui), // comments stripped.
Array set: names declared as `T name[N]` (N non-empty) or `std::array<T, N> name` anywhere in scope (global name set, so
members declared in headers count where the .cpp subscripts them).  Site: `name[expr]` (not a declaration line) whose expr is
not a literal / ALL_CAPS constant.
Auto verdicts per site (printed as counts):
  loop      every identifier in expr is a for-loop variable opened within 60 lines above
  mask      expr ends in `& M` (M numeric) and M < declared size (size resolved from a literal / #define / constexpr), or `% N`
  checked   expr's base identifier appears in a < <= > >= compare within 12 lines above (the range check)
  stacktop  `[xStackSize - 1]` / `[xStackSize]` and the file's push guards `< SIZE` and pop guards `> 1` (named per stack)
Every non-auto site's (file, array) unit needs a ROW (or a FILES rule), else OPEN.  Row verdict prefixes:
  masked   index masked/derived to the field width <= table size (the mask named)
  bounded  index bounded by a check/clamp elsewhere or by construction (named)
  host     index is host-derived (cursor, config, ring counter mod N, enum)
  gated    env-gated diagnostic or path off in the owner recipe (gate named)
  oob      guest-derived and unbounded -> defect row (must be 0)
--controls: (1) plant `s_gx_plant[rdram[a]]` (uint32_t s_gx_plant[8]) in a copy of rt64_rdp.cpp -> OPEN; (2) drop the ROW
rt64_rdp.cpp tiles -> OPEN; (3) plant a too-wide mask `s_gx_plant2[w & 0xFF]` on an 8-entry table -> OPEN (mask auto rule
compares against the declared size).  Exit 0 only if 0 open + 0 oob + 0 stale + 3/3 controls.
"""
import os, re, sys, copy
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRS = ["src", "lib/N64ModernRuntime/librecomp/src", "lib/N64ModernRuntime/ultramodern/src", "lib/rt64/src"]
SKIP = re.compile(r"/(tests?|tools|contrib|examples?|demos?|gui|imgui)/")
EXT = (".cpp", ".cc", ".c", ".h", ".hpp", ".mm")
DECL = re.compile(r"^\s*(?:(?:static|const|constexpr|thread_local|inline|volatile|extern|alignas\([^)]*\)|std::atomic<[^>]*>|unsigned|signed|struct)\s+)*"
                  r"[A-Za-z_][\w:<>,\s\*]*?\s\**([A-Za-z_]\w*)\s*\[\s*([^\]\[]+?)\s*\](?:\s*\[[^\]]*\])*\s*(?:=|;|\{|,)")
ARR = re.compile(r"std::array<[^;]*?,\s*([^>;]+)>\s+([A-Za-z_]\w*)")
SUB = re.compile(r"(?<![\w])([A-Za-z_]\w*)\s*\[((?:[^\[\]]|\[(?:[^\[\]]|\[[^\[\]]*\])*\])+)\]")  # 2 nested levels
CONST = re.compile(r"[0-9xXa-fA-FuUlL]+|[A-Z_][A-Z0-9_]*|[A-Z_][A-Z0-9_]*\s*[-+]\s*\d+")
DEFN = re.compile(r"(?:#define\s+([A-Za-z_]\w*)\s+\(?\s*(0x[0-9a-fA-F]+|\d+)[uUlL]*\s*\)?\s*$)|"
                  r"(?:(?:static\s+)?(?:constexpr|const)\s+[\w:]+\s+([A-Za-z_]\w*)\s*=\s*(0x[0-9a-fA-F]+|\d+)[uUlL]*\s*;)")

def load(files_override=None):
    files = {}
    for d in DIRS:
        for r, _, fs in os.walk(os.path.join(ROOT, d)):
            for f in fs:
                p = os.path.join(r, f); rel = os.path.relpath(p, ROOT)
                if SKIP.search("/" + rel) or not f.endswith(EXT): continue
                src = open(p, errors="ignore").read()
                if files_override and rel in files_override: src = files_override[rel]
                files[rel] = [l.split("//")[0] for l in src.split("\n")]
    return files

def ival(s, defs):
    s = s.strip().strip("()")
    m = re.fullmatch(r"(0x[0-9a-fA-F]+|\d+)[uUlL]*", s)
    if m: return int(m.group(1), 0)
    if s in defs: return defs[s]
    m = re.fullmatch(r"([A-Za-z_]\w*|\d+)\s*([*/+\-])\s*([A-Za-z_]\w*|\d+)", s)
    if m:
        a, b = ival(m.group(1), defs), ival(m.group(3), defs)
        if a is not None and b is not None:
            return {"*": a * b, "/": a // b if b else None, "+": a + b, "-": a - b}[m.group(2)]
    return None

def arrays(files):
    defs = {}
    for L in files.values():
        for l in L:
            m = DEFN.search(l)
            if m:
                n, v = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), m.group(4))
                defs.setdefault(n, int(v, 0))
    sizes = defaultdict(set)  # name -> {size or None}
    for L in files.values():
        for l in L:
            head = l.split("[")[0]
            if "(" in head and "alignas" not in head: continue
            m = DECL.match(l)
            if m and m.group(2).strip(): sizes[m.group(1)].add(ival(m.group(2), defs))
            for m in ARR.finditer(l): sizes[m.group(2)].add(ival(m.group(1), defs))
    return sizes, defs

def loopvars(L, i):
    vs = set()
    for j in range(max(0, i - 60), i + 1):
        for m in re.finditer(r"for\s*\(\s*(?:[\w:<>]+\s+)?([A-Za-z_]\w*)\s*(?:=|:)", L[j]): vs.add(m.group(1))
        for m in re.finditer(r"for\s*\(\s*(?:const\s+)?auto\s*&?\s*\[?\s*([A-Za-z_]\w*)", L[j]): vs.add(m.group(1))
    return vs

KW = {"size", "sizeof", "int", "uint32_t", "uint64_t", "uint16_t", "uint8_t", "size_t", "static_cast", "unsigned", "int32_t", "u", "ull"}

def auto(L, i, n, e, sizes, defs, stackok):
    ids = set(re.findall(r"[A-Za-z_]\w*", e)) - KW
    sz = sizes.get(n, set()); size = min(sz) if sz and None not in sz else None
    m = re.search(r"&\s*\(?\s*(0x[0-9a-fA-F]+|\d+|[A-Za-z_]\w*)[uUlL]*\s*\)?\s*\)?$", e)
    if m and size is not None:
        mv = ival(m.group(1), defs)
        if mv is not None and mv < size: return "mask"
    if re.search(r"%\s*\(?\s*[A-Za-z_0-9]", e): return "mask"
    sm = re.fullmatch(r"(?:[\w\.\->]*?)(\w+StackSize)(\s*-\s*1)?", e.replace(" ", "") if "StackSize" in e else "")
    if sm and sm.group(1) in stackok: return "stacktop"
    lv = loopvars(L, i)
    if ids and ids <= lv: return "loop"
    if re.fullmatch(r"[\w\s\.\->=!<>&|()']*\?\s*\d+\s*:\s*[\w\s\.\->=!<>&|()?:']*", e) and \
       all(re.fullmatch(r"\d+", x.strip()) for x in re.findall(r"[?:]\s*([^?:]+?)(?=\s*(?::|$))", e)): return "ternary"
    vm = re.fullmatch(r"([A-Za-z_]\w*)", e)
    if vm and size is not None:  # maskvar: `v = ... & M;` / `% N` / clamp ternary within 15 lines above, M < size
        for j in range(i, max(-1, i - 16), -1):
            am = re.search(r"\b%s\s*=\s*([^;=][^;]*);" % re.escape(e), L[j])
            if am:
                rhs = am.group(1).strip()
                mm = re.search(r"&\s*\(?\s*(0x[0-9a-fA-F]+|\d+|[A-Za-z_]\w*)[uUlL]*\s*\)?\s*\)?$", rhs)
                if mm and ival(mm.group(1), defs) is not None and ival(mm.group(1), defs) < size: return "maskvar"
                if re.search(r"%\s*\(?\s*[A-Za-z_0-9]", rhs): return "maskvar"
                nums = [int(x, 0) for x in re.findall(r"[?:]\s*(0x[0-9a-fA-F]+|\d+)\b", rhs)]
                if "?" in rhs and nums and max(nums) < size and re.search(r"[<>]", rhs): return "maskvar"
                break
    base = re.match(r"[A-Za-z_][\w\.\->]*", e)
    if base:
        b = re.escape(base.group(0))
        for j in range(max(0, i - 12), i + 1):
            if re.search(r"\b" + b + r"\s*(<|>=|<=|>)[^<>]", L[j]) or re.search(r"[^<>](<|>=|<=|>)\s*" + b + r"\b", L[j]): return "checked"
    return None

def stackguards(files):
    ok = set()
    for L in files.values():
        txt = "\n".join(L)
        for m in set(re.findall(r"(\w+StackSize)\+\+", txt)):
            if re.search(r"\b%s\s*<\s*\w+" % m, txt) and re.search(r"\b%s\s*>\s*1\b" % m, txt): ok.add(m)
    return ok

LIST = sys.argv[sys.argv.index("--list") + 1] if "--list" in sys.argv else None

def scan(files_override=None):
    files = load(files_override); sizes, defs = arrays(files); stackok = stackguards(files)
    units = {}; kinds = Counter()
    for rel, L in files.items():
        for i, l in enumerate(L):
            m0 = DECL.match(l)
            for m in (mm for st in range(len(l)) for mm in [SUB.match(l, st)] if mm and (st == 0 or not (l[st - 1].isalnum() or l[st - 1] == "_"))):
                n, e = m.group(1), m.group(2).strip()
                if n not in sizes or CONST.fullmatch(e): continue
                if m0 and m0.group(1) == n: continue
                k = auto(L, i, n, e, sizes, defs, stackok)
                if k:
                    kinds[k] += 1
                    if LIST and k == LIST: print("  %s %s:%d %s[%s]" % (k, rel, i + 1, n, e[:60]))
                    continue
                u = units.setdefault((rel, n), [i + 1, []])
                if e not in u[1]: u[1].append(e)
    return units, kinds

def suffix(rel, table):
    for k in table:
        if rel.endswith(k): return k
    return None

from s7600_gx_rows import FILES, ROWS

def classify(units, rows):
    out, used = [], set()
    for (rel, n), (ln, ex) in sorted(units.items()):
        fk = suffix(rel, rows); v = None
        if fk and n in rows[fk]: v = rows[fk][n]; used.add((fk, n))
        else:
            ff = suffix(rel, FILES)
            if ff: v = FILES[ff]
        out.append((rel, n, ln, ex, v))
    stale = [(f, n) for f in rows for n in rows[f] if (f, n) not in used]
    return out, stale

def report(out, stale, kinds):
    op = [o for o in out if o[4] is None]; oob = [o for o in out if o[4] and o[4].startswith("oob")]
    c = Counter((o[4] or "OPEN").split(":")[0] for o in out)
    print("s7600 GX census: auto sites %s; units=%d %s" % (" ".join("%s=%d" % kv for kv in sorted(kinds.items())), len(out),
          " ".join("%s=%d" % kv for kv in sorted(c.items()))))
    for o in op: print("  OPEN %s:%d %s[%s]" % (o[0], o[2], o[1], " | ".join(x[:40] for x in o[3][:4])))
    for o in oob: print("  OOB %s:%d %s -> %s" % (o[0], o[2], o[1], o[4]))
    for s in stale: print("  STALE row %s %s" % s)
    return len(op), len(oob), len(stale)

def controls():
    ok = 0; f = "lib/rt64/src/hle/rt64_rdp.cpp"; base = open(os.path.join(ROOT, f)).read()
    p1 = "\nstatic uint32_t s_gx_plant[8];\nvoid s_gx_plant_fn(const uint8_t *rdram, uint32_t a) { s_gx_plant[rdram[a]] = 1; }\n"
    out, _ = classify(scan({f: base + p1})[0], ROWS)
    h = any(o[0] == f and o[1] == "s_gx_plant" and o[4] is None for o in out)
    print("  control 1 plant s_gx_plant[rdram[a]] -> %s" % ("OPEN (caught)" if h else "MISSED")); ok += h
    rows = copy.deepcopy(ROWS); del rows["rt64/src/hle/rt64_rdp.cpp"]["tiles"]
    out, _ = classify(scan()[0], rows)
    h = any(o[0] == f and o[1] == "tiles" and o[4] is None for o in out)
    print("  control 2 drop row rt64_rdp.cpp tiles -> %s" % ("OPEN (caught)" if h else "MISSED")); ok += h
    p3 = "\nstatic uint32_t s_gx_plant2[8];\nvoid s_gx_plant2_fn(uint32_t w) { s_gx_plant2[w & 0xFF] = 1; }\n"
    out, _ = classify(scan({f: base + p3})[0], ROWS)
    h = any(o[0] == f and o[1] == "s_gx_plant2" and o[4] is None for o in out)
    print("  control 3 plant too-wide mask s_gx_plant2[w & 0xFF] (8 entries) -> %s" % ("OPEN (caught)" if h else "MISSED")); ok += h
    return ok

if __name__ == "__main__":
    units, kinds = scan()
    out, stale = classify(units, ROWS)
    n_open, n_oob, n_stale = report(out, stale, kinds)
    rc = 0 if (n_open == 0 and n_oob == 0 and n_stale == 0) else 1
    if "--controls" in sys.argv:
        k = controls(); print("controls %d/3" % k)
        if k != 3: rc = 1
    print("verdict: open=%d oob=%d stale=%d -> %s" % (n_open, n_oob, n_stale, "CLOSED" if rc == 0 else "NOT CLOSED"))
    sys.exit(rc)
