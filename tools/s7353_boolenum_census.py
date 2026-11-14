#!/usr/bin/env python3
"""s7353 class AD census: invalid bool / enum values loaded from guest-derived bytes in host code.
C++ facts the classes rest on (checked against [dcl.enum]/[expr.static.cast], C++17):
  * a scoped enum (`enum class` / `enum struct`) ALWAYS has a fixed underlying type (int when none is written), and an unscoped
    enum with `: T` has T. Converting any value that fits the underlying type is defined, so casts to these are FIXED (not UB).
  * only an unscoped enum WITHOUT a fixed type has the narrow "bitmask range" (smallest bit-field holding every enumerator);
    a value outside it is UB. clang exploits that only under -fstrict-enums (not in this build: no CMakeLists sets it), and
    UBSan -fsanitize=enum checks exactly these loads.
  * a `bool` object whose byte is not 0/1 is UB on ANY load: clang emits !range [0,2) metadata for every bool load, so a guest
    byte copied into a bool by memcpy / a bool* cast / a struct overlay can break `if (b)` / `!b` / `b ? :` folding.
  * `bool b = intval;` (implicit or static_cast<bool>, (bool)x) is a conversion (`!= 0`), never a load: SAFE, not a site.
Scope = s7343 files_in_scope(). Sites:
  E   `static_cast<E>(x)` / `(E)x` / `E(x)` where E names an enum declared in the scope or its headers
  BP  a cast to `bool*` / `const bool*` (load through a reinterpreted pointer)
  BS  memcpy / memmove / fread / reinterpret_cast / C cast whose destination is a bool, or a struct type that has a bool member
Classes: C/P/G/D from tools/s7338_mask_census.py sites() (rt64 G/D re-checked with s7343 body_gated(); CORE demotion as s7344)
  FIXED cast to a scoped enum or an unscoped enum with a fixed underlying type (defined for every value of that type)
  RC    unscoped-unfixed cast whose operand is masked / range-checked into the enum's bitmask range
  HOST  the source is host data (host struct of the same type, host config, a host-built table), not guest bytes
  H     hand-verified (reason in HAND)   FIX fixed this session   B default-on guest byte -> bool / out-of-range enum (defect)
  ?     unclassified
'?' or B => exit 1. --controls plants `Mode m = static_cast<Mode>(task->a);` with an unscoped unfixed `enum Mode { A, B }` ('?'),
an `enum class` twin (FIXED), a `: uint32_t` unscoped twin (FIXED), a masked twin `& 1` (RC), a gated twin (G), a
`bool b = task->a;` twin (SAFE: not a site), and `memcpy(&flag, rdram + task->a, 1)` into a bool ('?')."""
import re, sys, pathlib, importlib.util
from collections import Counter
ROOT = pathlib.Path(__file__).resolve().parents[1]
def _load(name, f):
    s = importlib.util.spec_from_file_location(name, ROOT / f); mod = importlib.util.module_from_spec(s); s.loader.exec_module(mod); return mod
s44 = _load("s7344", "tools/s7344_wrap_census.py")
s43, m = s44.s43, s44.s43.m

HDR_PATS = ["src/**/*.h", "src/**/*.hpp", "lib/rt64/src/**/*.h", "lib/N64ModernRuntime/**/*.h", "lib/N64ModernRuntime/**/*.hpp",
            "include/**/*.h"]
ENUM = re.compile(r"\benum\s+(class\s+|struct\s+)?(\w+)\s*(?::\s*([\w:\s]+?))?\s*\{([^}]*)\}")
STRUCT = re.compile(r"\b(?:struct|class)\s+(\w+)\s*(?:final\s*)?(?::[^{;]*)?\{")
MASK_RC = re.compile(r"&\s*(0x[0-9A-Fa-f]+|0b[01]+|\d+)[uUlL]*\s*\)*\s*$")

HAND = [  # (file suffix, needle in line, class, reason) -- s7353 review
    ("patcher.cpp", "cur_action_number & 0b11", "FIXED", "PatchActionType is `enum class` (int): any value is defined; also masked to 2 bits"),
    ("rt64_application_window.cpp", "reinterpret_cast<ApplicationWindow *>(userdata)", "HOST", "SDL event-watch userdata = the host ApplicationWindow `this` it registered"),
    ("mods.cpp", "static_cast<N64Recomp::RelocType>", "FIXED", "RelocType : uint8_t (mod file reloc, host-loaded mod binary)"),
]

def scope_headers():
    seen, out = set(), []
    for pat in HDR_PATS:
        for f in ROOT.glob(pat):
            s = str(f)
            if any(k in s for k in ("/test", "/googletest", "/gtest", "/contrib/", "/third_party/", "/thirdparty/", "/rabbitizer", "/examples/")):
                continue
            if f not in seen: seen.add(f); out.append(f)
    return out

ALIAS = {}
# s7353 blind-spot fix: RT64's shared/ headers (combiner / blender / other-mode decoders, compiled into the host under HLSL_CPU)
# hold the guest-field -> enum decoders but are not in s7343 files_in_scope().
EXTRA_SCOPE = ["lib/rt64/src/shared/*.h"]
NOTSITE = [  # (file suffix, needle) -- the functional-cast regex matched a non-cast
    ("rt64_rdp.cpp", "RDP::RDP(State *state) : state(state)"),     # member-init of `state`; an enum named `state` exists elsewhere
    ("rsp.hpp", "using RspUcodeFunc = RspExitReason("),            # function type, not a cast
]

def _rel(p):
    return str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else p.name

def collect(files):
    """enum name -> list of (kind, fixed_type, nbits_range, rel) ; struct names that carry a bool member."""
    enums, boolstructs = {}, {}
    for p in files:
        t = p.read_text(errors="replace")
        t = re.sub(r"//[^\n]*", "", t)
        for e in ENUM.finditer(t):
            scoped, name, ut, body = bool(e.group(1)), e.group(2), (e.group(3) or "").strip(), e.group(4)
            if scoped: kind = "SCOPED"
            elif ut: kind = "UFIXED"
            else: kind = "UNFIXED"
            enums.setdefault(name, []).append((kind, ut, body, _rel(p)))
        for a in re.finditer(r"\busing\s+(\w+)\s*=\s*(?:typename\s+)?(?:[\w]+::)*(\w+)\s*;|\btypedef\s+(?:enum\s+)?(?:[\w]+::)*(\w+)\s+(\w+)\s*;", t):
            al, tgt = (a.group(1), a.group(2)) if a.group(1) else (a.group(4), a.group(3))
            ALIAS.setdefault(al, set()).add(tgt)
        for s in STRUCT.finditer(t):
            depth, k = 1, s.end()
            while k < len(t) and depth:
                if t[k] == "{": depth += 1
                elif t[k] == "}": depth -= 1
                k += 1
            body = t[s.end():k]
            # direct members only (depth-0 lines): `bool x;` / `bool x = ...;` / `bool a : 1;`
            flat, d = [], 0
            for ch in body:
                if ch == "{": d += 1
                elif ch == "}": d -= 1
                elif d == 0: flat.append(ch)
            if re.search(r"(?:^|[;\n])\s*(?:const\s+)?bool\s+\w+\s*(?:=[^;]*|:\s*\d+)?;", "".join(flat)):
                boolstructs.setdefault(s.group(1), _rel(p))
    for al, tg in ALIAS.items():
        for t in tg:
            if t in enums and al not in enums: enums[al] = list(enums[t])
    return enums, boolstructs

def enum_bits(body):
    """bits needed for the bitmask range of an unscoped unfixed enum from its literal enumerators (None if unknown)."""
    mx, val = 0, -1
    for item in body.split(","):
        item = item.strip()
        if not item: continue
        mm = re.match(r"(\w+)\s*(?:=\s*(.+))?$", item, re.S)
        if not mm: return None
        if mm.group(2):
            try: val = int(mm.group(2).strip().rstrip("uUlL"), 0)
            except ValueError: return None
        else: val += 1
        if val < 0: return None
        mx = max(mx, val)
    return max(1, mx.bit_length())

st = Counter()
BLIND = []   # memcpy/fread with a guest-derived source whose destination type the census cannot resolve (printed with --blind)
GUESTSRC = re.compile(r"\brdram\b|\bRDRAM\b|\bram\b|\bTMEM\b|\bdmem\b|\bDMEM\b|RS64_DMEM_BASE|\btask->|\bg_rdram\w*|\brom\b|\bdl\b|\bsrc\b")
BLIND_HAND = [  # (file suffix, needle in line, type) -- s7353 review: every guest-source copy with an unresolved destination
    ("dpc_bridge.cpp", "q.ram.data(), g_rdram_for_submit", "std::vector<uint8_t> (Slot::ram, :3620)"),
    ("dpc_bridge.cpp", "std::memcpy(&q.rng[o]", "std::vector<uint8_t> (Slot::rng, :3620)"),
    ("dpc_bridge.cpp", "memcpy(&nw0, g_rdram_for_submit", "uint32_t nw0/nw1 (:8118)"),
    ("rt64_interpreter.cpp", "pendingCommandBuffer.data()", "std::array<uint8_t, 256> (rt64_rdp.h:133)"),
    ("rt64_state.cpp", "memcpy(ctx_out, RDRAM", "uint64_t* (ost_wb_read_fields :400)"),
    ("rt64_state.cpp", "memcpy(pri_out, RDRAM", "int32_t* (ost_wb_read_fields :400)"),
    ("rt64_state.cpp", "present.storage.data()", "std::vector<uint8_t> (rt64_present.h:20)"),
    ("rt64_texture_cache.cpp", "memcpy(", "uint8_t* (memcpyRows :549)"),
]
def blind_resolved(rel, raw):
    return next((t for f, n, t in BLIND_HAND if rel.endswith(f) and n in raw), None)
def cc_guest(args):
    return len(args) > 1 and bool(GUESTSRC.search(args[1]))
def census(files, pgf, enums, boolstructs):
    rows = []
    en = "|".join(sorted((re.escape(k) for k in enums), key=len, reverse=True)) or "NOENUM_"
    bs = "|".join(sorted((re.escape(k) for k in boolstructs), key=len, reverse=True)) or "NOSTRUCT_"
    ECAST = re.compile(r"static_cast\s*<\s*(?:[\w]+::)*(%s)\s*>\s*\(|\(\s*(?:[\w]+::)*(%s)\s*\)\s*(?=[\w(])|(?<![\w:.>])(?:[\w]+::)*(%s)\s*\((?!\s*\))" % (en, en, en))
    BPTR = re.compile(r"reinterpret_cast\s*<\s*(?:const\s+)?bool\s*(?:const\s*)?\*\s*>|\(\s*(?:const\s+)?bool\s*(?:const\s*)?\*\s*\)")
    SCAST = re.compile(r"reinterpret_cast\s*<\s*(?:const\s+)?(?:[\w]+::)*(%s)\s*(?:const\s*)?\*\s*>|\(\s*(?:const\s+)?(?:struct\s+)?(?:[\w]+::)*(%s)\s*(?:const\s*)?\*\s*\)" % (bs, bs))
    COPY = re.compile(r"\b(?:std::)?(memcpy|memmove|fread)\s*\(")
    m.MASK = re.compile(r"%s|%s|%s|%s" % (ECAST.pattern, BPTR.pattern, SCAST.pattern, COPY.pattern))
    for p in files:
        rel = str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else p.name
        lines, fns = s43.ln_fn(p); ftext = "\n".join(lines)
        done = set()
        for (ln, fn, mk, c, text) in m.sites(p, pgf):
            if ln in done: continue
            done.add(ln)
            raw = lines[ln - 1]
            l = re.sub(r'"(?:\\.|[^"\\])*"', '""', raw)
            ci = l.find("//")
            if ci >= 0: l = l[:ci]
            if l.lstrip().startswith(("#", "*")) or not l.strip(): continue
            start = fns[ln - 1][1]; body = "\n".join(lines[start:ln])
            if any(rel.endswith(f) and n in raw for f, n in NOTSITE): st["notsite"] += 1; continue
            hits, seen_at = [], set()
            for e in ECAST.finditer(l):
                if e.start() in seen_at: continue
                seen_at.add(e.start())
                name = e.group(1) or e.group(2) or e.group(3)
                # functional-cast form `E(` must not be a declaration `E name(` or a member/function of the same name
                if e.group(3) and (re.search(r"\b(?:enum|struct|class|case)\s*$", l[:e.start()]) or
                                   re.match(r"\s*%s\s*\([^)]*\)\s*(?:const\s*)?[{;]?\s*$" % re.escape(name), l[e.start():]) and fn == name):
                    continue
                if e.group(2) and re.search(r"\b(?:sizeof|alignof)\s*$", l[:e.start()]): continue
                if e.group(1) or e.group(3): arg = s43.args_of(l, e.end())[0]
                elif l[e.end():].startswith("("): arg = s43.args_of(l, e.end() + 1)[0]
                else:
                    mm2 = re.match(r"[\w.\->\[\]]+(?:\([^()]*\))?", l[e.end():]); arg = mm2.group(0) if mm2 else ""
                if not arg: continue
                hits.append(("E", name, arg))
            if BPTR.search(l): hits.append(("BP", "bool*", l.strip()))
            for s in SCAST.finditer(l): hits.append(("BS", s.group(1) or s.group(2), l.strip()))
            for cp in COPY.finditer(l):
                args = s43.args_of(l, cp.end())
                dst = args[0] if cp.group(1) != "fread" else args[0]
                d = re.sub(r"^\(?\s*(?:\(\s*\w+\s*\*\s*\)|reinterpret_cast<[^>]*>\s*\()?\s*&?\s*", "", dst).rstrip(") ")
                v = re.match(r"([A-Za-z_]\w*)", d)
                if not v or "->" in d or "." in d or "[" in d:
                    # member / element destination: resolve the member's declared type
                    mem = re.search(r"(?:->|\.)(\w+)\s*\)*$", d)
                    t = (s44.decl(mem.group(1), ftext) or "") if mem else ""
                else:
                    t = s44.decl(v.group(1), body) or s44.decl(v.group(1), ftext) or ""
                tb = re.sub(r"^(?:const\s+|struct\s+)", "", t.strip()).split("::")[-1]
                if tb == "bool" or tb in boolstructs: hits.append(("BS", tb, l.strip()))
                else:
                    st["copy-nonbool"] += 1
                    if not tb and cc_guest(args):
                        BLIND.append((rel, ln, fn, c, dst[:60], l.strip()[:110], blind_resolved(rel, raw) or "?"))
            for (kind, name, arg) in hits:
                cc, why = c, ""
                if cc in "GD" and rel.startswith("lib/rt64/") and not s43.body_gated(lines, ln): cc = "?"
                if cc == "D" and fn in s44.CORE: cc = "?"
                if kind == "E":
                    kinds = {k for (k, _, _, _) in enums[name]}
                    if cc == "?" and kinds <= {"SCOPED", "UFIXED"}:
                        cc, why = "FIXED", "enum " + name + ": " + "/".join(sorted(kinds)).lower() + " (" + \
                            ",".join(sorted({u or "int" for (_, u, _, _) in enums[name]})) + ")"
                    elif cc == "?":
                        bits = [enum_bits(b) for (k, _, b, _) in enums[name] if k == "UNFIXED"]
                        mk2 = MASK_RC.search(arg)
                        if mk2 and None not in bits and int(mk2.group(1), 0).bit_length() <= min(bits):
                            cc, why = "RC", f"masked to {int(mk2.group(1), 0).bit_length()} bits <= enum range {min(bits)} bits"
                hh = s43.hand(rel, fn, raw.strip(), HAND) if cc == "?" else None
                if hh: cc, why = hh
                rows.append((rel, ln, fn, cc, why, kind, name, arg[:80], raw.strip()[:120]))
    return rows

PLANT = ("enum Mode { MODE_A, MODE_B };\nenum class ModeC { A, B };\nenum ModeF : uint32_t { F_A, F_B };\n"
         "static int planted(OSTask* task) {\n    Mode md = static_cast<Mode>(task->a);\n    return md;\n}\n"
         "static int scoped_twin(OSTask* task) {\n    ModeC md = static_cast<ModeC>(task->a);\n    return (int)md;\n}\n"
         "static int fixed_twin(OSTask* task) {\n    ModeF md = static_cast<ModeF>(task->a);\n    return md;\n}\n"
         "static int rc_twin(OSTask* task) {\n    Mode md = static_cast<Mode>(task->a & 1);\n    return md;\n}\n"
         "static int gated_twin(OSTask* task) {\n    if (!rs64_dlwalk_on()) return 0;\n    Mode md = static_cast<Mode>(task->a);\n    return md;\n}\n"
         "static int safe_twin(OSTask* task) {\n    bool b = task->a;\n    return b;\n}\n"
         "static int bool_copy(uint8_t* rdram, OSTask* task) {\n    bool flag;\n    memcpy(&flag, rdram + task->a, 1);\n    return flag;\n}\n")

def main():
    pgf = m.probe_gate_fns()
    files = s43.files_in_scope()
    fs = set(files)
    for pat in EXTRA_SCOPE:
        for f in sorted(ROOT.glob(pat)):
            if f not in fs: fs.add(f); files.append(f)
    hdrs = scope_headers()
    if "--controls" in sys.argv:
        import tempfile
        t = pathlib.Path(tempfile.mkdtemp()) / "planted.cpp"
        t.write_text(PLANT)
        en, bs = collect([t]); ALIAS.clear()
        got = {(r[2], r[3], r[5]) for r in census([t], pgf, en, bs)}
        want = {("planted", "?", "E"), ("scoped_twin", "FIXED", "E"), ("fixed_twin", "FIXED", "E"), ("rc_twin", "RC", "E"),
                ("gated_twin", "G", "E"), ("bool_copy", "?", "BS")}
        assert got == want, f"control failed: got {sorted(got)} want {sorted(want)}"
        print("[s7353] controls: unscoped-unfixed cast '?', enum class FIXED, `: uint32_t` FIXED, `& 1` RC, gated G, "
              "bool b = task->a not a site, memcpy into bool '?'")
        st.clear()
    seen = set(files); allf = files + [h for h in hdrs if h not in seen]
    enums, boolstructs = collect(allf)
    kc = Counter(k for v in enums.values() for (k, _, _, _) in v)
    print(f"[s7353] enums declared in scope+headers: {len(enums)} names ({dict(kc)}); structs with a bool member: {len(boolstructs)}")
    rows = census(files, pgf, enums, boolstructs)
    cc = Counter(r[3] for r in rows); kk = Counter(r[5] for r in rows)
    print(f"[s7353] class AD sites={len(rows)} files={len(files)} by kind " + " ".join(f"{k}={v}" for k, v in sorted(kk.items())) +
          " | by class " + " ".join(f"{k}={v}" for k, v in sorted(cc.items())) + f" | non-bool copies={st['copy-nonbool']}")
    for r in rows:
        if r[3] in ("?", "B") or "-v" in sys.argv or ("-h" in sys.argv and r[3] in ("H", "FIX", "HOST")):
            print(f"  {r[3]} {r[5]} {r[0]}:{r[1]} {r[2]} [{r[6]}] {r[4]} :: {r[8]}")
    bc = Counter(b[3] for b in BLIND); unres = [b for b in BLIND if b[6] == "?"]
    print(f"[s7353] blind spot (guest-source copy, destination type unresolved): {len(BLIND)} by gate " + " ".join(f"{k}={v}" for k, v in sorted(bc.items())) +
          f"; hand-resolved to a non-bool type {len(BLIND) - len(unres)}, open {len(unres)}")
    for b in BLIND:
        if "--blind" in sys.argv or b[6] == "?": print(f"  blind {b[3]} {b[0]}:{b[1]} {b[2]} dst={b[4]} -> {b[6]} :: {b[5]}")
    bad = [r for r in rows if r[3] in ("?", "B")] + unres
    print(f"[s7353] unclassified/defect: {len(bad)}")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
