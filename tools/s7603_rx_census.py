#!/usr/bin/env python3
"""s7603 class RX: host code writing a value into a GUEST REGISTER (ctx->rN / ctx->fN / _return).

MIPS64 contract: a 32-bit result in a gpr must be sign-extended to 64 bits.  gpr is uint64_t (N64Recomp recomp.h), so
`ctx->r2 = (uint32_t)0x80001000` stores 0x0000000080001000, which recompiled `beq`/`slt`/64-bit adds compare against the
sign-extended 0xFFFFFFFF80001000 of `lui` and get wrong.  Two halves:

A) write sites  `ctx->rN = rhs` / `ctx->rN op= rhs` / `_return<T>(ctx, v)` / `_return(ctx, v)` / `ctx->fN.x = v`.
   Auto verdicts:  ok-sext  rhs is (int32_t)/(gpr)(int32_t|int16_t|int8_t)/int32_t(..)/... + 0xFFFFFFFF80000000ULL, a
                            _return (helpers.hpp _return sign-extends: ctx->r2 = int32_t(val), checked below), an int32_t-typed
                            constexpr/local, or a call whose ultra64.h return type is s32/int/OSPri/OSId/PTR(..)
                   ok-small literal < 0x80000000 or negative literal, (uint16_t)/(uint8_t) casts, MEM_BU/MEM_HU, 0/1 ternaries
                   ok-copy  rhs is another ctx->rM (already canonical)
                   fpr      ctx->fN.fl/.d/.u32l write (not a gpr; no sign-extension contract)
   Anything else needs a SITE_ROWS entry (ok-small with the bound named, consumer with the guest reader named) or is OPEN.
B) host stubs `void X_recomp(uint8_t* rdram, recomp_context* ctx)` that never write r2: if the recompiled game calls X
   (count in ../N64Recomp/RecompiledFuncs) its retail prototype must be void (RETAIL_VOID), else r2 is stale -> OPEN.
   Uncalled stubs are dead.  Non-_recomp definitions are hooks/mod-API (observer or gated), listed by name in HOOKS.
C) CONSUMERS: a stub that returns a zero-extended u32 that can exceed 0x7FFFFFFF is ok only if every guest call site's
   first read of ctx->r2 is a 32-bit store (`MEM_W(..) = ctx->r2`).  Checked mechanically in RecompiledFuncs.
--controls: (1) plant `ctx->r2 = (uint32_t)0x80001000u;` into a copy of print.cpp -> OPEN; (2) delete the r2 write from
osSpTaskYielded_recomp (called once by the game, retail OSYieldResult) -> OPEN; (3) drop a SITE_ROW -> OPEN; (4) synthetic call site that
reads osVirtualToPhysical's v0 with a compare -> OPEN; (5) make helpers.hpp _return zero-extend -> OPEN.
Exit 0 only if 0 open, 0 stale rows and 5/5 controls.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = "lib/N64ModernRuntime"
DIRS = ["src", L + "/librecomp/src", L + "/librecomp/include", L + "/ultramodern/src", L + "/ultramodern/include"]
FUNCS = os.path.join(os.path.dirname(ROOT), "N64Recomp", "RecompiledFuncs")
HELPERS = L + "/librecomp/include/librecomp/helpers.hpp"
ULTRA = L + "/ultramodern/include/ultramodern/ultra64.h"
SKIP = re.compile(r"/(tests?|third_party)/")

SEXT_TYPES = {"s32", "int", "int32_t", "OSPri", "OSId", "OSIntMask_s"}
# Retail libultra prototypes (libultra 2.0 headers) of every stub the game calls that does not set v0.
RETAIL_VOID = {"osDpGetCounters", "osDpSetStatus", "osSpTaskYield", "osContGetQuery", "osContGetReadData",
               "osViSetSpecialFeatures", "osStopThread", "__osRestoreInt", "osCreatePiManager", "osCreateViManager",
               "osInvalICache", "osInvalDCache", "osWritebackDCache", "osWritebackDCacheAll", "osCreateThread",
               "osStartThread", "osDestroyThread", "osSetThreadPri", "osCreateMesgQueue", "osSetEventMesg",
               "osViSetEvent", "osSetCount", "osSetTime", "osInitialize", "__osInitialize_common", "osViSwapBuffer",
               "osViSetMode", "osViSetXScale", "osViSetYScale", "osViRepeatLine", "osViBlack", "osSpTaskLoad",
               "osSpTaskStartGo", "osUnmapTLBAll", "__osPiGetAccess", "__osPiRelAccess", "osFlashReadStatus",
               "osFlashReadId", "osFlashClearStatus", "osFlashChange", "__osInitialize_msp", "__osInitialize_kmc",
               "__osInitialize_isv", "isPrintfInit", "osExQueueDisplaylistEvent", "osYieldThread"}
HOOK_PREFIX = re.compile(r"^(rs64_|recomp_|recomphook_|wait_one_frame$|maybe$|control$)")

# (file suffix, line substring) -> verdict
SITE_ROWS = [
    ("librecomp/src/ai.cpp", "ctx->r2 = buffered;", "ok-small: get_remaining_audio_bytes() is the AI queue depth in bytes "
     "(a few frames of 16-bit stereo, << 2^31)"),
    ("librecomp/src/ai.cpp", "ctx->r2 = buffered != 0 ? AI_STATUS_FIFO_FULL : 0;", "ok-small: AI_STATUS_FIFO_FULL is "
     "0x40000000u (bit 30, ai.cpp:13), below the sign bit"),
    ("librecomp/src/sp.cpp", "ctx->r2 = returned;", "ok-small: returned is 0u or 1u (OSYieldResult)"),
    ("librecomp/src/dp.cpp", "ctx->r2 = rdp_state;", "ok-small: rdp_state = 1 << RDPStatusBit::BufferReady, bits < 31"),
    ("librecomp/src/print.cpp", "ctx->r2 = size;", "ok-small: printf byte count of one guest string"),
    ("librecomp/src/mod_config_api.cpp", "ctx->r2 = addr;", "ok-sext: gpr addr = offset + 0xFFFFFFFF80000000ULL (line above)"),
    ("librecomp/src/ultra_translation.cpp", "ctx->r2 = osVirtualToPhysical(", "consumer: u32 zero-extended; KSEG0/1 input "
     "-> & 0x1FFFFFFF (small), other input returned as-is (TODO TLB); every guest call (osSpTaskLoad-class block "
     "0x80033D58..) stores v0 with sw, checked by CONSUMERS"),
    ("src/main/upstream_compat.cpp", "ctx->r2 = (gpr)(s_mb * 1024 * 1024);", "ok-small: s_mb is the ROGUESQ_MEM_MB "
     "override clamped to 4/8 MB class sizes (<= 512 MB = 0x20000000)"),
    ("src/main/upstream_compat.cpp", "ctx->r4 = r; ctx->r5", "ok-small: r = s6963_answer() is a record index (< 0xFFFF, "
     "r*0xB8 stays in the pool); env-gated s6963 walk shortcut"),
]
CONSUMERS = {"osVirtualToPhysical"}

LIT = re.compile(r"^-?\s*(0[xX][0-9a-fA-F]+|\d+)[uUlL]*$")
WRITE = re.compile(r"\bctx->(r\d+|f\d+(?:\.\w+)?)\s*(=|\+=|-=|\|=|&=|\^=|<<=|>>=)(?!=)\s*([^;]*);")
RET = re.compile(r"\b_return\s*(<\s*(\w+)\s*>)?\s*\(\s*ctx\s*,\s*([^;]*)\)\s*;")
DEF = re.compile(r'^\s*(?:extern\s+"C"\s+)?(?:static\s+)?(?:__attribute__\(\(\w+\)\)\s+)?void\s+(\w+)\s*\(\s*uint8_t\s*\*\s*rdram\s*,\s*recomp_context\s*\*\s*ctx\s*\)\s*\{', re.M)


def strip_comments(s):
    s = re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), s, flags=re.S)
    return re.sub(r"//[^\n]*", "", s)


def load(over=None):
    files = {}
    for d in DIRS:
        for r, _, fs in os.walk(os.path.join(ROOT, d)):
            for f in fs:
                p = os.path.join(r, f); rel = os.path.relpath(p, ROOT)
                if SKIP.search("/" + rel) or not f.endswith((".cpp", ".c", ".h", ".hpp")): continue
                src = (over or {}).get(rel)
                files[rel] = strip_comments(src if src is not None else open(p, errors="ignore").read())
    for rel, src in (over or {}).items():
        if rel not in files: files[rel] = strip_comments(src)
    return files


def brace_end(t, i):
    d = 1
    for mm in re.compile(r"[{}]").finditer(t, i):
        d += 1 if mm.group(0) == "{" else -1
        if d == 0: return mm.start()
    return len(t)


def ret_types(ultra):
    out = {}
    for m in re.finditer(r"^\s*(\w+(?:\(\w+\))?)\s+(\w+)\s*\(", ultra, re.M):
        out[m.group(2)] = m.group(1)
    return out


def auto(rhs, text, pos, rtypes):
    r = rhs.strip()
    if re.match(r"^\(\s*gpr\s*\)\s*\(\s*(int32_t|int16_t|int8_t|s32)\s*\)", r) or re.match(r"^\(\s*(int32_t|s32)\s*\)", r) \
            or re.match(r"^int32_t\s*\(", r) or "0xFFFFFFFF80000000ULL" in r:
        return "ok-sext"
    if re.fullmatch(r"[0-9xXa-fA-FuUlL\s*+<()]+", r) and re.search(r"\d", r):
        try:
            if 0 <= eval(re.sub(r"(?<=[0-9a-fA-F])[uUlL]+", "", r), {}) < 0x80000000: return "ok-small"
        except Exception: pass
    if LIT.match(r) or re.match(r"^\(\s*gpr\s*\)\s*\(\s*(uint16_t|uint8_t)\s*\)", r) or re.match(r"^MEM_[BH]U\(", r):
        return "ok-small"
    if re.match(r"^ctx->r\d+$", r): return "ok-copy"
    m = re.match(r"^(?:\(\s*gpr\s*\)\s*)?([\w:]+)\s*(\()?", r)
    if m:
        name = m.group(1).split("::")[-1]
        if m.group(2) and rtypes.get(name) in SEXT_TYPES | {"PTR(void)"}:
            if r.endswith(")") : return "ok-sext"
        if not m.group(2) and re.fullmatch(r"(?:\(\s*gpr\s*\)\s*)?[\w:]+", r):
            # identifier: find its nearest declaration above pos (or a constexpr anywhere)
            dm = list(re.finditer(r"\b(const\s+|constexpr\s+)*(\w+)\s+" + re.escape(name) + r"\s*=", text[max(0, pos - 6000):pos]))
            if CONSTEXPR.get(name) in SEXT_TYPES: return "ok-sext"
            if dm and dm[-1].group(2) in SEXT_TYPES: return "ok-sext"
    return None


ALL = {}
CONSTEXPR = {}


def run(over=None, rows=None, funcs_over=None, verbose=False):
    global ALL
    files = load(over); ALL = files
    CONSTEXPR.clear()
    for t in files.values():
        for c in re.finditer(r"constexpr\s+(\w+)\s+(\w+)\s*=", t): CONSTEXPR.setdefault(c.group(2), c.group(1))
    rows = SITE_ROWS if rows is None else rows
    rtypes = ret_types(files[ULTRA])
    open_, used, stats = [], set(), {}
    # helpers.hpp contract
    h = files[HELPERS]
    if not re.search(r"ctx->r2\s*=\s*int32_t\s*\(\s*val\s*\)", h): open_.append(("A", HELPERS, 0, "_return does not sign-extend"))
    for rel, text in files.items():
        if rel == HELPERS: continue
        lines = text.split("\n")
        for m in list(WRITE.finditer(text)) + list(RET.finditer(text)):
            ln = text.count("\n", 0, m.start()) + 1; line = lines[ln - 1].strip()
            if m.re is RET: v = "ok-sext" if (m.group(2) in (None,) or m.group(2) in SEXT_TYPES | {"u32", "uint32_t", "u16", "u8"}) else None
            elif m.group(1).startswith("f"): v = "fpr"
            else: v = auto(m.group(3), text, m.start(), rtypes)
            if v is None:
                for i, (suf, sub, verdict) in enumerate(rows):
                    if rel.endswith(suf) and sub in line: v = verdict.split(":")[0]; used.add(i); break
            stats[v or "OPEN"] = stats.get(v or "OPEN", 0) + 1
            if v is None: open_.append(("A", rel, ln, line[:140]))
            elif verbose: print(f"  {v:9} {rel}:{ln} {line[:110]}")
    # B: stubs without r2
    calls = funcs_over if funcs_over is not None else load_funcs()
    ncall = {}
    for c in re.finditer(r"\b(\w+_recomp)\(rdram, ctx\)", calls): ncall[c.group(1)] = ncall.get(c.group(1), 0) + 1
    for rel, text in files.items():
        for m in DEF.finditer(text):
            body = text[m.end():brace_end(text, m.end())]; name = m.group(1)
            if re.search(r"ctx->r2\s*=[^=]|_return\s*[<(]|ctx->f0\.\w+\s*=[^=]", body): continue
            ln = text.count("\n", 0, m.start()) + 1
            if not name.endswith("_recomp"):
                k = "hook" if HOOK_PREFIX.match(name) else None
            else:
                base = name[:-7]; n = ncall.get(name, 0)
                k = "dead" if n == 0 else ("void" if base in RETAIL_VOID else None)
            stats["B-" + (k or "OPEN")] = stats.get("B-" + (k or "OPEN"), 0) + 1
            if k is None: open_.append(("B", rel, ln, name + " called, no r2 write, retail prototype not void"))
            elif verbose: print(f"  B-{k:7} {rel}:{ln} {name}")
    # C: consumers
    for name in CONSUMERS:
        sites = [mm.end() for mm in re.finditer(r"\b" + name + r"_recomp\(rdram, ctx\);", calls)]
        if not sites: open_.append(("C", name, 0, "no call sites found (consumer check vacuous)"))
        for p in sites:
            seg = calls[p:p + 4000]
            r = next((x for x in re.finditer(r"[^\n]*\bctx->r2\b[^\n]*", seg)
                      if "__builtin_expect(g_rs64" not in x.group(0)), None)
            ok = r and re.search(r"MEM_W\([^)]*\)\s*=\s*ctx->r2\s*;", r.group(0))
            stats["C-" + ("sw" if ok else "OPEN")] = stats.get("C-" + ("sw" if ok else "OPEN"), 0) + 1
            if not ok: open_.append(("C", name, calls.count("\n", 0, p), (r.group(0).strip() if r else "no r2 read")[:120]))
    stale = [rows[i] for i in range(len(rows)) if i not in used]
    return stats, open_, stale


_FUNCS = None
def load_funcs():
    global _FUNCS
    if _FUNCS is None:
        _FUNCS = "".join(open(os.path.join(FUNCS, f), errors="ignore").read()
                         for f in sorted(os.listdir(FUNCS)) if f.endswith(".c"))
    return _FUNCS


def report(r, tag="real"):
    stats, op, stale = r
    print(f"[{tag}] " + " ".join(f"{k}={v}" for k, v in sorted(stats.items())) + f" open={len(op)} stale_rows={len(stale)}")
    for o in op: print("   OPEN", o)
    for s in stale: print("   STALE", s[:2])


def controls():
    ok = 0
    pr = L + "/librecomp/src/print.cpp"; src = open(os.path.join(ROOT, pr)).read()
    r = run({pr: src + '\nextern "C" void rs64_ctl1_recomp(uint8_t* rdram, recomp_context* ctx) { ctx->r2 = (uint32_t)0x80001000u; }\n'})
    c1 = any(o[1] == pr and "0x80001000" in o[3] for o in r[1]); ok += c1; print("control 1 (zero-extended KSEG0 literal):", "OPEN" if c1 else "MISSED")
    sp = L + "/librecomp/src/sp.cpp"; s = open(os.path.join(ROOT, sp)).read()
    s2 = s.replace("ctx->r2 = returned;", "(void)returned;")
    r = run({sp: s2}); c2 = s2 != s and any(o[0] == "B" and "osSpTaskYielded" in o[3] for o in r[1]); ok += c2
    print("control 2 (called stub loses its r2 write):", "OPEN" if c2 else "MISSED")
    r = run(rows=SITE_ROWS[1:]); c3 = any("buffered;" in o[3] for o in r[1]); ok += c3; print("control 3 (row dropped):", "OPEN" if c3 else "MISSED")
    f = load_funcs().replace("osVirtualToPhysical_recomp(rdram, ctx);\n", "osVirtualToPhysical_recomp(rdram, ctx);\n    if (ctx->r2 == ctx->r4) goto x;\n", 1)
    r = run(funcs_over=f); c4 = any(o[0] == "C" for o in r[1]); ok += c4; print("control 4 (v0 compared, not stored):", "OPEN" if c4 else "MISSED")
    h = open(os.path.join(ROOT, HELPERS)).read()
    r = run({HELPERS: h.replace("ctx->r2 = int32_t(val);", "ctx->r2 = uint32_t(val);")}); c5 = any(o[1] == HELPERS for o in r[1]); ok += c5
    print("control 5 (_return zero-extends):", "OPEN" if c5 else "MISSED")
    print(f"controls {ok}/5"); return ok


if __name__ == "__main__":
    r = run(verbose="-v" in sys.argv); report(r)
    good = not r[1] and not r[2]
    if "--controls" in sys.argv: good = controls() == 5 and good
    sys.exit(0 if good else 1)
