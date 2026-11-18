#!/usr/bin/env python3
"""s7604 class RA: host code READING a guest register (ctx->rN) or a gpr alias of one.

MIPS64 contract: a 32-bit value in a gpr is sign-extended, so a KSEG0 pointer in a0 is 0xFFFFFFFF80114388.  Host code that
uses the raw 64-bit value in a compare with a u32 constant (`ctx->r4 == 0x80114388u` is always false), as a host index /
offset (`rdram + ctx->r4`), in a 64-bit divide / right shift / size_t length, or passes it to a 64-bit parameter without
truncating is wrong.  Every read is classified:
  ok-cast   operand of a cast / U32() / S32() / static_cast to a <=32-bit type, or initialiser of a <=32-bit local
  ok-macro  address operand of MEM_*/LD/SD/TO_PTR/ADD32/SUB32 (they subtract 0xFFFFFFFF80000000 or mask; recomp.h, ultra64.h)
  ok-zero   == 0 / != 0 / ! / bare truth test (sign fill cannot change a zero test)
  ok-hilo   `<< 32` (sign fill shifted out) or `& 0xFFFFFFFF` (masked), the u64 pair idiom of math_routines/osSetTime
  ok-copy   stored back into another ctx->rM unchanged
  ok-param  argument of a function whose declared parameter at that index is <=32-bit (signature map built from the tree)
  ok-alias  initialises a gpr/uint64_t/auto local whose every later read classifies ok by these same rules
  row       SITE_ROWS entry naming why the 64-bit use is right (e.g. a gpr-typed sink that masks)
  OPEN      anything else.
_arg<N,T> (helpers.hpp) is checked separately: the integral branch must static_cast<T> with sizeof(T)<=4 and the pointer
branch must go through TO_PTR.
--controls: (1) plant `if (ctx->r4 == 0x80114388u)` in a copy of upstream_compat.cpp -> OPEN; (2) plant `rdram[ctx->r5]`
-> OPEN; (3) drop a SITE_ROW -> OPEN (stale row reported too); (4) make _arg drop its sizeof<=4 truncation -> OPEN;
(5) plant a gpr alias compared with a u32 constant -> OPEN (alias follow-through); (6) plant
`(uint32_t)(ctx->r4 >> 16)` -> OPEN (truncation after a 64-bit shift).
Exit 0 only if 0 open, 0 stale rows and 6/6 controls.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = "lib/N64ModernRuntime"
DIRS = ["src", L + "/librecomp/src", L + "/librecomp/include", L + "/ultramodern/src", L + "/ultramodern/include"]
HELPERS = L + "/librecomp/include/librecomp/helpers.hpp"
UC = "src/main/upstream_compat.cpp"
SKIP = re.compile(r"/(tests?|third_party|thirdparty)/")

T32 = r"(?:const\s+)?(?:uint32_t|int32_t|u32|s32|unsigned(?:\s+int)?|int|uint16_t|int16_t|uint8_t|int8_t|u16|s16|u8|s8|bool|" \
      r"OSMesg|OSPri|OSId|OSIntMask|OSEvent|PTR\(\s*\w+\s*\))"
CAST = re.compile(r"(?:\(\s*" + T32 + r"\s*\)\s*\(?\s*|\b(?:U32|S32)\s*\(\s*|static_cast\s*<\s*" + T32 + r"\s*>\s*\(\s*)$")
IMPL = re.compile(r"\b" + T32 + r"\s+\w+\s*=\s*$")
MACROS = {"MEM_W", "MEM_H", "MEM_B", "MEM_HU", "MEM_BU", "MEM_WU", "MEM_D", "LD", "SD", "LWL", "LWR", "TO_PTR", "ADD32", "SUB32"}
REG = re.compile(r"\bctx->r(\d+)\b")

# (file suffix, line substring) -> reason
SITE_ROWS = [
    ("src/main/upstream_compat.cpp", "gpr buf_ptr = ctx->r4;", "row: osDpGetCounters alias read only by the canonical-sext "
     "check (int64_t)buf_ptr == (int32_t)lo, a %llX log of the full value, MEM_W and (uint32_t) - all 64-bit-correct"),
    ("src/main/upstream_compat.cpp", "uint64_t dest_full = (uint64_t)ctx->r4;", "row: zmemcpy in_range() accepts sign-"
     "extended (>= 0xFFFFFFFF80000000) or zero-extended KSEG0, full-width log only"),
    ("src/main/upstream_compat.cpp", "uint64_t src_full  = (uint64_t)ctx->r5;", "row: as dest_full"),
    ("src/main/upstream_compat.cpp", "uint64_t len_full  = (uint64_t)ctx->r6;", "row: zmemcpy length: a sign-filled "
     "(>= 2 GB) length fails in_range and is skipped; used length is (uint32_t)len_full"),
    ("src/main/upstream_compat.cpp", "rs64_guest_range_valid(static_cast<uint64_t>(ctx->r4)", "row: "
     "rs64_guest_range_valid_top accepts addr >= 0xFFFFFFFF80000000 (sext) or (addr>>32)==0 (zext), rejects others"),
    (L + "/librecomp/src/sp.cpp", "rs64_sp_task_range_valid(static_cast<uint64_t>(ctx->r4)", "row: sp.cpp range check takes "
     "both sext (addr >= kseg0_base) and zext ((addr>>32)==0) forms"),
    (L + "/librecomp/src/sp.cpp", "rs64_spai_guard_bad(\"osSpTaskStartGo\", static_cast<uint64_t>(ctx->r4)", "row: "
     "rs64_spai_guard_bad -> rs64_sp_task_range_valid, both forms"),
    (L + "/librecomp/src/ultra_translation.cpp", "load_doubleword(rdram, ctx->r29, 0x10)", "row: recomp.h load_doubleword"
     "(rdram, gpr reg, gpr offset) only feeds reg to MEM_W (two (uint32_t) word loads)"),
    (L + "/librecomp/src/heap.cpp", "old_form ? (size_t)ctx->r4 :", "row: ROGUESQ_S7604_ALLOC=0 restore arm of the s7604 "
     "recomp_alloc fix (default path is (size_t)(uint32_t)ctx->r4); mod export, 0 game calls"),
    (L + "/librecomp/src/pak.cpp", "RS64_PAK(", "row: RS64_PAK macro casts its pfs operand (uint32_t)(pfs), pak.cpp:11"),
    (L + "/librecomp/src/print.cpp", "gpr buf = ctx->r4;", "row: __osRdbSend buf alias: canonical-sext check "
     "(int64_t)buf == (int32_t)b32 then MEM_B; 0 callers in the game"),
    (L + "/librecomp/src/print.cpp", "size_t size = ctx->r5;", "row: __osRdbSend size: size > 0x800000 rejected first, so a "
     "sign-filled length is refused; 0 callers in the game"),
    (L + "/librecomp/src/print.cpp", "size_t size = ctx->r6;", "row: is_proutSyncPrintf size is never read (body commented out)"),
    (L + "/librecomp/src/pi.cpp", "uint32_t devAddr = handle->baseAddress | ctx->r5;", "row: OR then narrowing to uint32_t "
     "== OR of the low words; the sign fill is discarded by the uint32_t init"),
    (L + "/librecomp/src/pi.cpp", "gpr dramAddr = ctx->r6;", "row: passed to do_rom_pio(gpr) whose guard reads "
     "(uint32_t)ram_address and copies via MEM_W (pi.cpp:181-200)"),
    (L + "/librecomp/src/eep.cpp", "gpr buffer = ctx->r6;", "row: buffer -> rs64_spai_guard_bad (both forms), save_read/"
     "save_write PTR(void) (int32_t, truncates), rs64_eep_row(gpr) which only does MEM_BU(i, buffer)"),
    (L + "/librecomp/src/ai.cpp", "rs64_spai_guard_bad(\"osAiSetNextBuffer\", static_cast<uint64_t>(ctx->r4)",
     "row: guard checks the full 64-bit gpr for canonical sign extension (rejects non-canonical), length masked & 0xFFFFFFFF"),
]


def strip_comments(s):
    s = re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), s, flags=re.S)
    s = re.sub(r'"(?:\\.|[^"\\\n])*"', lambda m: '"' + "_" * (len(m.group(0)) - 2) + '"', s)
    return re.sub(r"//[^\n]*", "", s)


def load(over=None):
    files = {}
    for d in DIRS:
        for r, _, fs in os.walk(os.path.join(ROOT, d)):
            for f in fs:
                p = os.path.join(r, f); rel = os.path.relpath(p, ROOT)
                if SKIP.search("/" + rel) or not f.endswith((".cpp", ".c", ".h", ".hpp", ".mm")): continue
                src = (over or {}).get(rel)
                files[rel] = src if src is not None else open(p, errors="ignore").read()
    return files


def signatures(files):
    """name -> list of param-type lists (all overloads/lambdas seen)."""
    sig = {}
    fn = re.compile(r"\b(\w+)\s*\(((?:[^()]|\([^()]*\))*)\)\s*(?:const\s*)?(?:noexcept\s*)?(?:->\s*[\w:<>* ]+)?\s*[{;]")
    lam = re.compile(r"\b(?:auto|const\s+auto)\s+(\w+)\s*=\s*\[[^\]]*\]\s*\(((?:[^()]|\([^()]*\))*)\)")
    for t in files.values():
        t = re.sub(r"\bRDRAM_ARG\b", "uint8_t* rdram,", t)
        for rx in (fn, lam):
            for m in rx.finditer(t):
                ps = [p.strip() for p in split_args(m.group(2))]
                if not ps or not all(DECL.fullmatch(p) or p in ("", "void") for p in ps): continue
                types = [DECL.fullmatch(p).group(1).strip() if DECL.fullmatch(p) else p for p in ps]
                sig.setdefault(m.group(1), []).append(types)
    return sig


DECL = re.compile(r"((?:const\s+|unsigned\s+|struct\s+)*[A-Za-z_][\w:]*(?:\s*<[^<>]*>)?(?:\s*\(\s*\w+\s*\))?(?:\s*[*&]+\s*|\s+)(?:const\s*)?)"
                  r"[A-Za-z_]\w*\s*(?:=[^,]*)?", re.S)


def split_args(s):
    out, d, cur = [], 0, ""
    for ch in s:
        if ch in "([<{": d += 1
        elif ch in ")]>}": d -= 1
        if ch == "," and d == 0: out.append(cur); cur = ""
        else: cur += ch
    out.append(cur); return out


def enclosing_call(t, pos):
    """innermost unclosed '(' before pos: (name, arg index) or (None, None)."""
    d, i, idx = 0, pos - 1, 0
    while i >= 0 and pos - i < 3000:
        ch = t[i]
        if ch in ")]}": d += 1
        elif ch in "([{":
            if d == 0:
                if ch != "(": return None, None
                m = re.search(r"([\w:]+)\s*(?:<[^<>]*>)?\s*$", t[max(0, i - 80):i])
                if re.match(r"\s*PASS_RDRAM\b", t[i + 1:i + 40]): idx += 1
                return (m.group(1).split("::")[-1] if m else None), idx
            d -= 1
        elif ch == "," and d == 0: idx += 1
        elif ch == ";" and d == 0: return None, None
        i -= 1
    return None, None


def is32(ty):
    return bool(re.fullmatch(T32 + r"(?:\s*&)?", ty.strip())) or ty.strip() in ("uint32_t", "int32_t")


def classify(t, s, e, sig, depth=0):
    """classify the read t[s:e] (ctx->rN or alias identifier)."""
    before = t[max(0, s - 160):s]; after = t[e:e + 120]
    if re.match(r"\s*(=(?!=)|\+=|-=|\|=|&=|\^=|<<=|>>=)", after): return "write"
    cm = CAST.search(before)
    if cm and cm.group(0).rstrip().endswith("("):
        # cast applied to a parenthesised expression: truncation comes AFTER the expression, so a >>, / or % on the raw
        # 64-bit value would pull sign fill into the low word.
        d, j = 1, e
        while j < len(t) and d:
            d += {"(": 1, ")": -1}.get(t[j], 0); j += 1
        if re.search(r">>|/|%", t[e:j - 1]): return None
    if cm or IMPL.search(before): return "ok-cast"
    if re.search(r"\bMEM_(?:W|H|B|HU|BU|WU)\s*\([^;]*\)\s*=\s*$", before) and re.match(r"\s*;", after): return "ok-cast"  # sw/sh/sb store truncates
    if re.search(r"\(\s*\(?\s*(?:uint64_t|int64_t|gpr)\s*\)\s*\(?\s*$", before) and re.match(r"\s*\)?\s*<<\s*32\b", after): return "ok-hilo"
    if re.match(r"\s*\)?\s*<<\s*32\b", after): return "ok-hilo"
    if re.match(r"\s*(?:<<\s*0\s*\)\s*)?&\s*0[xX][fF]{1,8}[uU]?\b", after) or re.match(r"\s*\)\s*&\s*0[xX][fF]{1,8}[uU]?\b", after): return "ok-hilo"
    if re.match(r"\s*[!=]=\s*0[uUlL]*\b(?![xX])", after) or re.search(r"(?:!|\b0\s*[!=]=)\s*$", before): return "ok-zero"
    if re.search(r"\b(?:if|while)\s*\(\s*$", before) and re.match(r"\s*\)", after): return "ok-zero"
    if re.search(r"(?:&&|\|\|)\s*$", before) and re.match(r"\s*(?:&&|\|\||\))", after): return "ok-zero"
    if re.search(r"(?:&&|\|\||\(|\?)\s*$", before) and re.match(r"\s*(?:&&|\|\|)", after): return "ok-zero"
    if re.search(r"\bctx->r\d+\s*=\s*$", before) and re.match(r"\s*;", after): return "ok-copy"
    name, idx = enclosing_call(t, s)
    if name in MACROS:
        return "ok-macro" if (idx == 1 or name in ("ADD32", "SUB32")) and re.match(r"\s*[,)]", after) else None
    m = re.search(r"\b(?:const\s+)?(gpr|uint64_t|auto|int64_t)\s+(\w+)\s*=\s*$", before)
    if m and re.match(r"\s*;", after):
        if depth: return None
        # follow the alias to the end of its enclosing block
        end = block_end(t, e); bad = []
        for mm in re.finditer(r"\b" + re.escape(m.group(2)) + r"\b", t[e:end]):
            p = e + mm.start()
            if t[p - 1] in ".>" : continue
            v = classify(t, p, p + len(m.group(2)), sig, 1)
            if v is None: bad.append(t.count("\n", 0, p) + 1)
        return "ok-alias" if not bad else ("alias-open@" + ",".join(map(str, bad)))
    if name and re.match(r"\s*[,)]", after) and name not in ("if", "while", "for", "switch", "return", "sizeof"):
        cands = sig.get(name, [])
        tys = [c[idx] for c in cands if idx < len(c)]
        if tys and all(is32(ty) for ty in tys): return "ok-param"
    return None


def block_end(t, i):
    d = 0
    for mm in re.compile(r"[{}]").finditer(t, i):
        if mm.group(0) == "{": d += 1
        else:
            d -= 1
            if d < 0: return mm.start()
    return len(t)


def run(over=None, rows=None, verbose=False):
    raw = load(over); files = {k: strip_comments(v) for k, v in raw.items()}
    rows = SITE_ROWS if rows is None else rows
    sig = signatures(files)
    stats, open_, used = {}, [], set()
    h = files.get(HELPERS, "")
    if not (re.search(r"sizeof\s*\(\s*T\s*\)\s*<=\s*4", h) and re.search(r"return\s+static_cast<T>\(raw_arg\)", h)
            and re.search(r"return\s+TO_PTR\(", h)):
        open_.append((HELPERS, 0, "_arg<N,T> integral/pointer branch no longer truncates"))
    for rel, t in files.items():
        if rel == HELPERS: continue
        lines = raw[rel].split("\n")
        for m in REG.finditer(t):
            if t[m.end():m.end() + 1] == "[" or re.match(r"\s*\)\s*\[", t[m.end():m.end() + 4]) and t[m.start() - 2:m.start()] == "(&":
                v = None
            else:
                v = classify(t, m.start(), m.end(), sig)
            if v == "write": continue
            ln = t.count("\n", 0, m.start()) + 1; line = lines[ln - 1].strip()
            if v is None or v.startswith("alias-open"):
                for i, (suf, sub, why) in enumerate(rows):
                    if rel.endswith(suf) and sub in line: v = "row"; used.add(i); break
            k = v if v and not v.startswith("alias-open") else "OPEN"
            stats[k] = stats.get(k, 0) + 1
            if k == "OPEN": open_.append((rel, ln, (v or "") + " " + line[:130]))
            elif verbose: print(f"  {k:9} {rel}:{ln} {line[:110]}")
    stale = [rows[i] for i in range(len(rows)) if i not in used]
    return stats, open_, stale


def report(r, tag="real"):
    stats, op, stale = r
    print(f"[{tag}] " + " ".join(f"{k}={v}" for k, v in sorted(stats.items())) + f" open={len(op)} stale_rows={len(stale)}")
    for o in op: print("   OPEN", o)
    for s in stale: print("   STALE", s[:2])


def controls():
    ok = 0
    src = open(os.path.join(ROOT, UC)).read()
    plant = lambda body: src + '\nextern "C" void rs64_ra_ctl_recomp(uint8_t* rdram, recomp_context* ctx) {\n' + body + '\n}\n'
    r = run({UC: plant("    if (ctx->r4 == 0x80114388u) ctx->r2 = 1;")})
    c = any("0x80114388u" in o[2] for o in r[1]); ok += c; print("control 1 (raw gpr == u32 constant):", "OPEN" if c else "MISSED")
    r = run({UC: plant("    ctx->r2 = rdram[ctx->r5];")})
    c = any("rdram[ctx->r5]" in o[2] for o in r[1]); ok += c; print("control 2 (raw gpr as host index):", "OPEN" if c else "MISSED")
    r = run(rows=[])
    c = any("osAiSetNextBuffer" in o[2] for o in r[1]); ok += c; print("control 3 (row dropped):", "OPEN" if c else "MISSED")
    h = open(os.path.join(ROOT, HELPERS)).read()
    r = run({HELPERS: h.replace("sizeof(T) <= 4", "sizeof(T) <= 8")})
    c = any(o[0] == HELPERS for o in r[1]); ok += c; print("control 4 (_arg admits 64-bit T):", "OPEN" if c else "MISSED")
    r = run({UC: plant("    gpr q = ctx->r6;\n    if (q == 0x8010FEE0u) ctx->r2 = 1;")})
    c = any("gpr q = ctx->r6" in o[2] for o in r[1]); ok += c; print("control 5 (gpr alias == u32 constant):", "OPEN" if c else "MISSED")
    r = run({UC: plant("    ctx->r2 = (uint32_t)(ctx->r4 >> 16);")})
    c = any(">> 16" in o[2] for o in r[1]); ok += c; print("control 6 (cast after a 64-bit right shift):", "OPEN" if c else "MISSED")
    print(f"controls {ok}/6"); return ok


if __name__ == "__main__":
    r = run(verbose="-v" in sys.argv); report(r)
    good = not r[1] and not r[2]
    if "--controls" in sys.argv: good = controls() == 6 and good
    sys.exit(0 if good else 1)
