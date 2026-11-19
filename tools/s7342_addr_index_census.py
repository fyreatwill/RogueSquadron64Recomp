#!/usr/bin/env python3
"""s7342 class S census: host tables indexed by an address-derived value vs dd>1 spill addresses.
A table sized for 8/16 MB of RDRAM (per-word writer rows, per-page tags, coverage bitsets) and indexed by
`(addr & mask) >> k`, `(addr - 0x80000000) >> k` or `phys >> k` silently reads/writes past its end when the address is a
spill address (0x81000000-0x81800000, phys 0x01000000-0x017FFFFF, s7326/s7336). That is not a reject but an OOB access.
Part 1 SUBSCRIPTS: every `T[ ... >> k ... ]` (k 2..23), every `T[v]` where `v = ... >> k ...;` sits within 8 lines above,
  and every `.set(/.test(/.reset(` with a shifted argument, in the s7338 HOST scope. Classed with the s7338 C/P/G/D
  framework, then:
    H hash slot (index multiplied by a 64-bit mix constant)  K index is not an address (pixel/word ordinal, map key; hand)
    M masked: `& MASK` inside the subscript and (MASK >> k) < table entries
    N bounded: the enclosing function rejects addresses past the table span before the subscript (hand-verified s7342)
    B default-on, address index, no bound <= table size (defect)   ? unclassified
Part 2 TABLES: every host array / resize / new[] / vector ctor with >= 0x8000 entries, joined to the Part 1 rows that index
  it; a big table with an unclassified address subscript is reported.
'?' or B => exit 1. --controls plants a default-on `tag[(a - 0x80000000u) >> 12]` ('?'), the same via a local ('?'), and a
log-gated one ('G')."""
import re, sys, pathlib, importlib.util
import importlib.util as _ilu_cr, sys as _sys_cr
if "census_rules" not in _sys_cr.modules:  # s7654 shared text-anchored rules (one instance per process)
    _crs = _ilu_cr.spec_from_file_location("census_rules", __import__("pathlib").Path(__file__).resolve().parent / "census_rules.py")
    _sys_cr.modules["census_rules"] = _ilu_cr.module_from_spec(_crs); _crs.loader.exec_module(_sys_cr.modules["census_rules"])
census_rules = _sys_cr.modules["census_rules"]
from collections import Counter, defaultdict
ROOT = pathlib.Path(__file__).resolve().parents[1]
_s = importlib.util.spec_from_file_location("s7338", ROOT / "tools/s7338_mask_census.py")
m = importlib.util.module_from_spec(_s); _s.loader.exec_module(m)
SUB = re.compile(r"\b(\w+)\s*(?:\[[^\[\]]*\]\s*)?\[([^\[\]]*?>>\s*(\d+)u?[^\[\]]*)\]")
BITOP = re.compile(r"\b(\w+)\s*\.\s*(?:set|test|reset)\s*\(([^()]*>>\s*(\d+)u?[^()]*)\)")
VAR = re.compile(r"\b(?:const\s+)?(?:u?int\d+_t|unsigned|int|size_t|auto)\s+(\w+)\s*=\s*([^;]*>>\s*(\d+)u?[^;]*);")
HASHMIX = re.compile(r"\*\s*0x[0-9A-Fa-f]{12,}")
MASKRE = re.compile(r"&\s*(0x[0-9A-Fa-f]+)u?")
# Hand classes (s7342 review). Key (function, table) -> (class, reason).
HAND = {
    ("rs64_cov_bit", "bits"): ("K", "pixel x >> 5 into a 71x32-word coverage row (s_cov_*), x is a screen column"),
    ("?", "bits"): ("K", "Rs64CovAcc pixel coverage bitset: x >> 5 screen column"),
    ("rs64_bl_eq", "pm"): ("K", "blender mux field (blend >> k) & 3u into a 4-name string table"),
    ("rs64_bl_eq", "a"): ("K", "blender mux field (blend >> k) & 3u"), ("rs64_bl_eq", "b"): ("K", "blender mux field & 3u"),
    ("rs64_f5_dump_join", "g_f5_last_writer"): ("N", "returns unless source < 0x800000 && bytes <= 0x800000 - source; table 0x200000 rows"),
}
# Tables whose every use is classed by line text (members of huge functions; checked s7342).
LINE = {
    "m.full[wd >> 6]": ("K", "TMEM word ordinal wd < RDP_TMEM_WORDS_RS64 (512) into full[8]"),
    "m.part[wd >> 6]": ("K", "TMEM word ordinal wd < RDP_TMEM_WORDS_RS64 (512) into part[8]"),
    "VCOL.set(n, result >> 16)": ("K", "RSP VU carry flag: set(lane n, carry bit); the shifted term is the value, n < 8"),
    "hist[((uint64_t)cls << 40)": ("K", "std::map key composed from (cls, off, pc); not a sized table"),
}
DECL = [re.compile(r"\b(\w+)\s*\[\s*([^\[\];]+?)\s*\]\s*(?:\[[^\]]*\]\s*)*(?:=|;|\{)"),
        re.compile(r"\b(\w+)\s*(?:\.|->)\s*(?:resize|assign|reserve)\s*\(\s*([^,);]+)"),
        re.compile(r"\b(\w+)\s*=\s*(?:new\s+[\w:<>]+|static_cast<[^>]+>\s*\(\s*(?:std::)?calloc)\s*[\[(]\s*([^\]),;]+)"),
        re.compile(r"std::vector<[^;]*>\s+(\w+)\s*\(\s*([^,);]+)"),
        re.compile(r"\b(\w+)\s*=\s*\([^()]*\*\s*\)\s*(?:std::)?(?:calloc|malloc)\s*\(\s*([^,);]+)")]

CONST = re.compile(r"^\s*(?:static\s+)?(?:constexpr|const)\s+[\w:]+\s+(\w+)\s*=\s*([^;,]+);")

def ev(expr, names=None):
    for nm, v in (names or {}).items(): expr = re.sub(r"\b%s\b" % re.escape(nm), str(v), expr)
    e = re.sub(r"(0x[0-9A-Fa-f]+|\d+)[uUlL]+\b", r"\1", expr.strip())
    if not re.fullmatch(r"[0-9a-fA-Fx\s()+\-*/<>|&]+", e): return None
    try: return int(eval(e, {"__builtins__": {}}))
    except Exception: return None

DECLLINE = re.compile(r"^\s*(?:static\s+|constexpr\s+|const\s+|thread_local\s+)*[\w:<>]+\s*\**\s+\w+\s*\[[^\]]*\]\s*(?:\[[^\]]*\]\s*)*(?:=[^=]|;|\{)")

def names_of(src):
    names = {}
    for l in src:                                        # named sizes: `constexpr uint32_t N = 1u << 18;`, `#define N 0x...`
        mm = CONST.match(l) or re.match(r"^\s*#define\s+(\w+)\s+(\(?[0-9xXa-fA-FuU<>\s()]+\)?)\s*$", l)
        if mm and ev(mm.group(2)) is not None: names[mm.group(1)] = ev(mm.group(2))
    return names

# Hash functions whose result is provably < the table size (s7342 read): name -> (bits of the result, reason)
HASHFN = {"s7239_hash": (17, "((e >> 2) * 2654435761u) >> 15: uint32 product >> 15 = 17 bits = S7239_HN (1u << 17)")}
HASHBODY = {"s7239_hash": "inline uint32_t s7239_hash(uint32_t e) { return ((e >> 2) * 2654435761u) >> 15; }"}  # proof pinned to text

def tables(path, floor=0x8000):
    out = {}
    src = path.read_text(errors="replace").splitlines()
    names = names_of(src)
    for i, l in enumerate(src):
        if l.strip().startswith("//") or "return" in l and "[" in l.split("return", 1)[1][:3]: continue
        for di, r in enumerate(DECL):
            if di == 0 and not DECLLINE.match(l): continue
            for mm in r.finditer(l):
                n = ev(mm.group(2), names)
                if n and n >= floor and (mm.group(1) not in out or out[mm.group(1)][0] < n):
                    out[mm.group(1)] = (n, i + 1, l.strip()[:120])
    return out

def classify(path, pgf, sizes):
    lines = path.read_text(errors="replace").splitlines()
    rows = []
    def add(regex, extra_filter):
        m.MASK = regex
        for (ln, fn, mk, c, text) in m.sites(path, pgf):
            mm = regex.search(lines[ln - 1][lines[ln - 1].find(mk):]) or regex.search(mk)
            if not mm or not extra_filter(mm): continue
            rows.append([ln, fn, mm.group(1), mm.group(2).strip(), int(mm.group(3)), c, text])
    add(SUB, lambda mm: 2 <= int(mm.group(3)) <= 23)
    add(BITOP, lambda mm: 2 <= int(mm.group(3)) <= 23)
    for i, l in enumerate(lines):                       # `v = ... >> k;` then `T[v]` within 8 lines
        mv = VAR.search(l)
        if not mv or not 2 <= int(mv.group(3)) <= 23: continue
        v = mv.group(1)
        cre = re.compile(r"\b(\w+)\s*\[\s*(%s)\s*\]()" % re.escape(v))
        for j in range(i + 1, min(i + 9, len(lines))):
            if re.search(r"\b%s\s*=[^=]" % re.escape(v), lines[j]): break
            if cre.search(lines[j]):
                m.MASK = cre
                for (ln, fn, mk, c, text) in m.sites(path, pgf):
                    if ln == j + 1:
                        rows.append([ln, fn, cre.search(lines[j]).group(1), mv.group(2).strip(), int(mv.group(3)), c, text])
    seen, out = set(), []
    for r in rows:
        ln, fn, tab, idx, k, c, text = r
        if (ln, tab) in seen or DECLLINE.match(lines[ln - 1]): continue
        seen.add((ln, tab))
        why = ""
        if c == "?":
            hl = next((v for key, v in LINE.items() if key in text), None)
            if HASHMIX.search(idx): c, why = "H", "hash slot"
            elif (fn, tab) in HAND: c, why = HAND[(fn, tab)]
            elif ("?", tab) in HAND and fn not in [f for (f, t) in HAND if t == tab]: c, why = HAND[("?", tab)]
            elif hl: c, why = hl
            elif census_rules.lookup(str(path), fn, text): c, why = census_rules.lookup(str(path), fn, text)
            else:
                mk = MASKRE.search(idx); n = sizes.get(tab, (None,))[0]
                if mk and n and (int(mk.group(1), 16) >> k) < n:
                    c, why = "M", f"(0x{int(mk.group(1), 16):X} >> {k}) < {n:#x} entries"
        out.append((ln, fn, tab, idx, k, c, why, text))
    return out

RING = re.compile(r"&\s*\(\s*\(?\s*1u?\s*<<\s*\d+\s*\)?\s*-\s*1\s*\)|%\s*\w+|&\s*0x[0-9A-Fa-f]+u?\s*$")

def big_uses(path, pgf, big):
    """Part 2b: EVERY subscript of a >= 0x8000-entry table (shifted or not), classed C/P/G/D, then M (index masked to
    fewer than the table's entries: byte table & 0x7FFFFF, ring & (N-1)), L (loop ordinal bounded by the table size in the
    same `for`), or '?'."""
    lines = path.read_text(errors="replace").splitlines()
    names, out = names_of(lines), []
    for tab, (n, dln, _) in big.items():
        cre = re.compile(r"\b%s\s*\[([^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*)\]" % re.escape(tab))
        m.MASK = cre
        for (ln, fn, mk, c, text) in m.sites(path, pgf):
            if DECLLINE.match(lines[ln - 1]) or ln == dln: continue
            idx = cre.search(mk).group(1).strip()
            why = ""
            if c == "?":
                mm = [int(x, 16) for x in re.findall(r"&\s*\(?\s*(0x[0-9A-Fa-f]+)", idx)]
                sh = re.search(r">>\s*(\d+)", idx); k = int(sh.group(1)) if sh else 0
                rg = re.search(r"&\s*\(\s*\(?\s*1u?\s*<<\s*(\d+)", idx)
                if mm and (max(mm) >> k) < n: c, why = "M", f"(0x{max(mm):X} >> {k}) < {n:#x}"
                elif rg and (1 << int(rg.group(1))) <= n: c, why = "M", f"ring & ((1 << {rg.group(1)}) - 1)"
                elif (rn := re.search(r"&\s*\(\s*(\w+)\s*-\s*1\s*\)", idx)) and names.get(rn.group(1), 1 << 40) <= n \
                        and names[rn.group(1)] & (names[rn.group(1)] - 1) == 0:
                    c, why = "M", f"ring & ({rn.group(1)} - 1), {rn.group(1)} = {names[rn.group(1)]:#x}"
                elif re.fullmatch(r"\w+", idx) and (hf := re.search(r"\b%s\s*=\s*(\w+)\s*\(" % idx, "\n".join(lines[max(0, ln - 6):ln]))) \
                        and hf.group(1) in HASHFN and (1 << HASHFN[hf.group(1)][0]) <= n \
                        and HASHBODY[hf.group(1)] in "\n".join(lines) \
                        and re.search(r"%s\s*=\s*\(%s\s*\+\s*1\)\s*&\s*\(\s*(\w+)\s*-\s*1\s*\)" % (idx, idx), "\n".join(lines[max(0, ln - 6):ln])):
                    c, why = "H", HASHFN[hf.group(1)][1] + "; probe h = (h + 1) & (N - 1)"
                elif re.fullmatch(r"\w+", idx):
                    loop = "\n".join(lines[max(0, ln - 12):ln])
                    b = re.findall(r"for\s*\([^;]*;[^;]*\b%s\s*<=?\s*([^;)]*?)\s*(?:&&\s*%s\s*<\s*(\w+))?\s*;" % (idx, idx), loop)
                    lim = [ev(x[1]) for x in b if x[1]] + [ev(x[0]) for x in b]
                    if any(v is not None and v <= n for v in lim): c, why = "L", f"for-loop bound <= {n:#x}"
            if c == "?" and census_rules.lookup(str(path), fn, text): c, why = census_rules.lookup(str(path), fn, text)
            out.append((ln, fn, tab, idx, c, why, text))
    return out

def run(files, pgf):
    rows, big, uses = [], {}, []
    for p in files:
        rel = str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else p.name
        uses += [(rel,) + u for u in big_uses(p, pgf, tables(p))]
        sizes = tables(p, 1)
        for t, v in tables(p).items(): big[(str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else p.name, t)] = v
        for r in classify(p, pgf, sizes):
            rows.append((str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else p.name,) + r)
    return rows, big, uses

# s7342 widening beyond the s7338 scope: the remaining host sources and headers (tables declared in headers / small TUs).
EXTRA = ["src/main/*.cpp", "src/main/*.h", "src/rsp/*.h", "lib/N64ModernRuntime/librecomp/include/librecomp/*.hpp",
         "lib/N64ModernRuntime/ultramodern/include/ultramodern/*.hpp", "lib/rt64/src/hle/*.hpp"]

def main():
    pgf = m.probe_gate_fns()
    if "--controls" in sys.argv:
        import tempfile
        t = pathlib.Path(tempfile.mkdtemp()) / "planted.cpp"
        t.write_text("static uint8_t tag[0x800000 >> 12];\n"
                     "static void mark(uint32_t a) {\n    tag[(a - 0x80000000u) >> 12] = 1;\n}\n"
                     "static void mark2(uint32_t a) {\n    const uint32_t idx = (a & 0x1FFFFFFFu) >> 12;\n    tag[idx] = 1;\n}\n"
                     "static void logged(uint32_t a) {\n    if (!log_e9_provenance()) return;\n    tag[(a - 0x80000000u) >> 12] = 2;\n}\n"
                     "static void masked(uint32_t a) {\n    tag[(a & 0x7FFFFFu) >> 12] = 3;\n}\n")
        t.write_text(t.read_text() + "static uint32_t pcs[0x800000];\n"
                     "static void pcw(uint32_t a) {\n    pcs[a & 0x1FFFFFFu] = 1;\n}\n"
                     "static void pcm(uint32_t a) {\n    pcs[a & 0x7FFFFFu] = 1;\n}\n")
        rows, big, uses = run([t], pgf)
        gu = {(u[2], u[5]) for u in uses}
        assert gu == {("pcw", "?"), ("pcm", "M")}, f"big-table control failed: {gu}"
        got = {(r[2], r[6]) for r in rows}
        assert got == {("mark", "?"), ("mark2", "?"), ("logged", "G"), ("masked", "M")}, f"control failed: {got}"
        sz = tables(t, 1)
        assert sz.get("tag", (0,))[0] == 0x800, f"table size control failed: {sz}"
        print("[s7342] controls: planted default-on subscript '?' (direct + via local), gated 'G', masked 'M', table 0x800 sized; big table byte subscript unmasked '?', masked 'M'")
    files, seen = [], set()
    for pat in m.HOST + EXTRA:
        for p in sorted(ROOT.glob(pat)):
            if p not in seen: seen.add(p); files.append(p)
    rows, big, uses = run(files, pgf)
    cc = Counter(r[6] for r in rows)
    print(f"[s7342] class S subscripts={len(rows)} files={len(files)} " + " ".join(f"{k}={v}" for k, v in sorted(cc.items())))
    for r in rows:
        if r[6] not in "CPGD" or "-v" in sys.argv:
            print(f"  {r[6]} {r[0]}:{r[1]} {r[2]} {r[3]}[{r[4][:50]}] {r[7] or ''}")
    by = defaultdict(list)
    for r in rows: by[(r[0], r[3])].append(r[6])
    print(f"[s7342] tables >= 0x8000 entries: {len(big)}")
    joined = 0
    for (f, t), (n, ln, text) in sorted(big.items()):
        cls = by.get((f, t))
        if cls: joined += 1
        if cls or "-v" in sys.argv:
            print(f"  {f}:{ln} {t}[{n:#x}] address-shift subscripts: {dict(Counter(cls)) if cls else 'none'}")
    print(f"[s7342] big tables with an address-shift subscript: {joined}")
    uc = Counter(u[5] for u in uses)
    print(f"[s7342] part 2b every subscript of the {len(big)} big tables: uses={len(uses)} " +
          " ".join(f"{k}={v}" for k, v in sorted(uc.items())))
    for u in uses:
        if u[5] not in "CPGD" or "-v" in sys.argv: print(f"  {u[5]} {u[0]}:{u[1]} {u[2]} {u[3]}[{u[4][:50]}] {u[6]}")
    bad = [r for r in rows if r[6] in "?B"]
    for u in uses:
        if u[5] in "?B": print(f"  DEFECT/UNCLASSIFIED big-table {u[0]}:{u[1]} {u[2]} {u[3]}[{u[4]}] :: {u[7][:120]}"); bad.append(u)
    for r in [r for r in rows if r[6] in "?B"]: print(f"  DEFECT/UNCLASSIFIED {r[0]}:{r[1]} {r[2]} {r[3]}[{r[4]}] :: {r[8][:120]}")
    bad = list(bad) + census_rules.report("s7342")  # s7654: a stale shared rule fails the gate (after the row printers)
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
