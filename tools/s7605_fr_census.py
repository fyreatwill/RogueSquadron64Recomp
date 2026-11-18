#!/usr/bin/env python3
"""s7605 class FR: host code reading or writing a GUEST floating-point register (ctx->fN.view, f_odd).

Contract (N64Recomp cgenerator.cpp fpr_*_to_string + librecomp cop0_status_write, s7409): a single lives in ctx->fN.fl, a
double in the WHOLE 64-bit even register ctx->fN.d in both FR modes; only mtc1/mfc1/lwc1/swc1 of an odd register go through
f_odd (FR=0 -> f(N-1).u32h, FR=1 -> fN.u32l). Host-called code always runs FR=0 (thread entry and reset init FR=0; the 7
hand-asm FR=1 routines restore FR=0 before returning, s7409/s7410). o32: float arg0 f12, float arg1 after a float f14,
float arg1 after an int a1 (GPR bits), double arg0 f12.d, float return f0.fl, double return f0.d.
Each access token is matched against a SITE_ROWS entry that names the expected view and the retail prototype; the token's
register+view must equal the row's (so a changed view is OPEN even when the line still matches). Additional rules:
  - any odd FPR (.fl/.d/.u32*) in host code is OPEN unless its row says FR=1 (host code is FR=0);
  - an FPR value cast through an integer type ((uint8_t)/(gpr)/(int) ... ctx->fN.fl) on the right of an FPR store is OPEN;
  - helpers.hpp: _arg<.,float> must return f12.fl, _arg_float_a1 must take _arg<1, u32>, _arg_float_f14 must return
    f14.fl, _return<float> must write f0.fl;
  - every host *_recomp function whose retail prototype carries a float/double (FLOATPROTO) must have a row; a host stub
    of a known float-bearing libultra/libm name with no FLOATPROTO entry is OPEN.
--controls: (1) plant `ctx->f0.d = 1.0;` in a float-returning stub copy -> OPEN; (2) plant a read of ctx->f13.fl -> OPEN;
(3) drop every row -> OPEN; (4) make _arg_float_a1 read _arg<2, u32> -> OPEN; (5) plant a host sinf_recomp -> OPEN;
(6) revert the s7605 recomphook_get_return_double fix -> OPEN.  Exit 0 only if 0 open, 0 stale rows, 6/6 controls.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = "lib/N64ModernRuntime"
DIRS = ["src", L + "/librecomp/src", L + "/librecomp/include", L + "/ultramodern/src", L + "/ultramodern/include"]
HELPERS = L + "/librecomp/include/librecomp/helpers.hpp"
UC = "src/main/upstream_compat.cpp"
MH = L + "/librecomp/src/mod_hooks.cpp"
GEN = "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs"
SKIP = re.compile(r"/(tests?|third_party|thirdparty)/")
TOK = re.compile(r"(?:\b\w+(?:\.back\(\))?)(?:->|\.)f(\d+)\.(fl|fh|d|u32l|u32h|u64)\b|\bf_odd\b")

# (file suffix, line substring, expected tokens "fN.view" joined by ',', reason)
SITE_ROWS = [
    (UC, "ctx->f4.fl = (float)(0.5 / (f4 - f6)", "f4.fl,f0.fl", "s6904 fog hook before 0x8001726C trunc.w.s $f2,$f4 / "
     "0x80017274 trunc.w.s $f2,$f0: the game's own fm/fo are singles in f4/f0, the hook overwrites them as .fl"),
    (UC, "fprintf(stderr, \"[fogp] n=%u", "f4.fl,f0.fl", "ok-diag: ROGUESQ_G5E_FOGP log of the same two singles"),
    (UC, "[osViSetXScale #%d] scale=%f", "f12.fl", "ok-diag: env log; void osViSetXScale(f32) arg0 = f12"),
    (UC, "osViSetXScale(ctx->f12.fl);", "f12.fl", "void osViSetXScale(f32 value): float arg0 in f12"),
    (UC, "[osViSetYScale #%d] scale=%f", "f12.fl", "ok-diag: env log; void osViSetYScale(f32) arg0 = f12"),
    (UC, "osViSetYScale(ctx->f12.fl);", "f12.fl", "void osViSetYScale(f32 value): float arg0 in f12"),
    (L + "/librecomp/src/vi.cpp", "osViSetYScale(ctx->f12.fl);", "f12.fl", "weak default, overridden by upstream_compat"),
    (L + "/librecomp/src/vi.cpp", "osViSetXScale(ctx->f12.fl);", "f12.fl", "weak default, overridden by upstream_compat"),
    (HELPERS, "return ctx->f12.fl;", "f12.fl", "_arg<0,float>: o32 float arg0"),
    (HELPERS, "return ctx->f14.fl;", "f14.fl", "_arg_float_f14: second float after a float arg0"),
    (HELPERS, "ctx->f0.fl = val;", "f0.fl", "_return<float>: float return in f0"),
    (L + "/librecomp/src/math_routines.cpp", "ctx->f0.d = ret;", "f0.d", "double __ull_to_d(u64): double return f0.d"),
    (L + "/librecomp/src/math_routines.cpp", "ctx->f0.fl = ret;", "f0.fl", "float __ull_to_f(u64) / __ll_to_f(s64): f0.fl"),
    (L + "/librecomp/src/math_routines.cpp", "int64_t ret = (int64_t)ctx->f12.fl;", "f12.fl", "s64 __f_to_ll(f32): arg0 f12"),
    (L + "/librecomp/src/mod_config_api.cpp", "ctx->f0.d = double(*as_u32);", "f0.d", "double recomp_get_config_double"),
    (L + "/librecomp/src/mod_config_api.cpp", "ctx->f0.d = *as_double;", "f0.d", "double recomp_get_config_double"),
    (L + "/librecomp/src/mod_config_api.cpp", "ctx->f0.d = 0.0;", "f0.d", "double recomp_get_config_double"),
    (MH, "ctx->f0.fl = hook_contexts.back().f0.fl;", "f0.fl,f0.fl", "recomphook_get_return_float: float return copy"),
    (MH, "ctx->f0.d = hook_contexts.back().f0.d;", "f0.d,f0.d", "recomphook_get_return_double (s7605 fix): whole f0.d"),
    (L + "/librecomp/src/recomp.cpp", "ctx->f_odd = &ctx->f1.u32l;", "f_odd,f1.u32l", "FR=1 mapping (s7409): address only"),
    (L + "/librecomp/src/recomp.cpp", "ctx->f_odd = &ctx->f0.u32h;", "f_odd,f0.u32h", "FR=0 mapping (s7409): address only"),
    (L + "/librecomp/src/recomp.cpp", "ctx.f_odd = &ctx.f0.u32h;", "f_odd,f0.u32h", "thread entry FR=0 init"),
    (L + "/librecomp/src/recomp.cpp", "ctx->mips3_float_mode = true;", "", "context line (no token)"),
]
# host *_recomp functions whose retail prototype carries a float/double
FLOATPROTO = {"osViSetXScale": "void(f32)", "osViSetYScale": "void(f32)", "__ull_to_d": "f64(u64)", "__ull_to_f": "f32(u64)",
              "__ll_to_f": "f32(s64)", "__f_to_ll": "s64(f32)"}
FLOATY = re.compile(r"^(sinf?|cosf?|tanf?|sqrtf?|atan2?f?|powf?|expf?|logf?|fabsf?|fmodf?|floorf?|ceilf?|gu[A-Z]\w*|"
                    r"__(?:d|f|ll|ull)_to_(?:d|f|ll|ull)|osViSet[XY]Scale|__osSetFpcCsr)$")
NOFLOAT = {"__osSetFpcCsr": "u32 __osSetFpcCsr(u32): FCR31 value in a0/v0, no FPR; 0 game call sites"}


def strip_comments(t):
    t = re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), t, flags=re.S)
    return re.sub(r"//[^\n]*", lambda m: " " * len(m.group(0)), t)


def load(over=None):
    out = {}
    for d in DIRS:
        for dp, _, fs in os.walk(os.path.join(ROOT, d)):
            if SKIP.search(dp): continue
            for f in fs:
                if f.endswith((".cpp", ".hpp", ".h", ".c", ".mm", ".cc")):
                    p = os.path.join(dp, f); rel = os.path.relpath(p, ROOT)
                    out[rel] = open(p, errors="surrogateescape").read()
    for k, v in (over or {}).items(): out[k] = v
    return out


def run(over=None, rows=None, verbose=False):
    raw = load(over); rows = SITE_ROWS if rows is None else rows
    stats, open_, used = {}, [], set()
    for rel, txt in raw.items():
        t = strip_comments(txt); lines = txt.split("\n"); tl = t.split("\n")
        for ln, code in enumerate(tl, 1):
            toks = [("f_odd" if m.group(0) == "f_odd" else f"f{m.group(1)}.{m.group(2)}") for m in TOK.finditer(code)]
            if not toks: continue
            line = lines[ln - 1].strip(); v = None; why = ""
            for i, (suf, sub, exp, why_) in enumerate(rows):
                if rel.endswith(suf) and sub in line:
                    used.add(i); why = why_
                    v = "row" if toks == exp.split(",") else "view-mismatch"
                    break
            odd = [x for x in toks if x != "f_odd" and int(x[1:].split(".")[0]) & 1]
            if odd and "FR=1" not in why: v = "odd-fr0"
            if re.search(r"f\d+\.(?:fl|fh|d|u32l|u32h|u64)\s*=\s*\((?:gpr|u?int(?:8|16|32|64)_t|int|unsigned|u8|s8|u16|s16|u32|s32)\)\s*(?:\(\s*\w+\s*\)\s*)?[\w.()>-]*f\d+\.(?:fl|d)", code):
                v = "int-cast"
            k = v if v == "row" else "OPEN"
            stats[k] = stats.get(k, 0) + 1
            if k == "OPEN": open_.append((rel, ln, f"{v or 'no-row'} {toks} {line[:120]}"))
            elif verbose: print(f"  row  {rel}:{ln} {toks} {line[:100]}")
    h = strip_comments(raw.get(HELPERS, ""))
    for pat, what in [(r"is_same_v<T, float>\)\s*\{\s*if constexpr \(index < 2\)\s*\{[^}]*return ctx->f12\.fl;", "_arg<.,float> -> f12.fl"),
                      (r"_arg_float_a1\(uint8_t\* rdram, recomp_context\* ctx\) \{(?:(?!\ninline)[\s\S])*?ret\.as_u32 = _arg<1, u32>\(rdram, ctx\);", "_arg_float_a1 reads a1 bits"),
                      (r"_arg_float_f14[^{]*\{[^}]*return ctx->f14\.fl;", "_arg_float_f14 -> f14.fl"),
                      (r"_return\(recomp_context\* ctx, T val\)[\s\S]*?is_same_v<T, float>\)\s*\{\s*ctx->f0\.fl = val;", "_return<float> -> f0.fl")]:
        if not re.search(pat, h): open_.append((HELPERS, 0, "helper contract broken: " + what))
    fns = set()
    for rel, txt in raw.items():
        for m in re.finditer(r"\bvoid\s+(\w+)_recomp\s*\(\s*uint8_t\s*\*", strip_comments(txt)): fns.add(m.group(1))
    for f in sorted(fns):
        if FLOATY.match(f) and f not in FLOATPROTO and f not in NOFLOAT:
            open_.append(("<host fns>", 0, f"float-prototype host stub {f}_recomp has no FLOATPROTO row"))
    stats["host_fns"] = len(fns); stats["floatproto"] = len([f for f in fns if f in FLOATPROTO])
    stale = [rows[i] for i in range(len(rows)) if i not in used and rows[i][2]]
    return stats, open_, stale


def game_calls():
    if not os.path.isdir(GEN): return "gen dir missing"
    n = {}
    for f in os.listdir(GEN):
        if not f.endswith(".c"): continue
        t = open(os.path.join(GEN, f), errors="surrogateescape").read()
        for name in list(FLOATPROTO) + list(NOFLOAT):
            n[name] = n.get(name, 0) + len(re.findall(r"\b" + re.escape(name) + r"_recomp\s*\(rdram", t))
    return " ".join(f"{k}={v}" for k, v in sorted(n.items()))


def report(r, tag="real"):
    stats, op, stale = r
    print(f"[{tag}] " + " ".join(f"{k}={v}" for k, v in sorted(stats.items())) + f" open={len(op)} stale_rows={len(stale)}")
    for o in op: print("   OPEN", o)
    for s in stale: print("   STALE", s[:2])


def controls():
    ok = 0
    src = open(os.path.join(ROOT, UC)).read()
    plant = lambda body, name="rs64_fr_ctl": src + f'\nextern "C" void {name}_recomp(uint8_t* rdram, recomp_context* ctx) {{\n' + body + '\n}\n'
    r = run({UC: plant("    ctx->f0.d = 1.0; /* float-returning stub writing the double view */")})
    c = any("ctx->f0.d = 1.0" in o[2] for o in r[1]); ok += c; print("control 1 (f0.d write, no row):", "OPEN" if c else "MISSED")
    r = run({UC: plant("    float b = ctx->f13.fl; (void)b;")})
    c = any("f13.fl" in o[2] for o in r[1]); ok += c; print("control 2 (odd f13 read in FR=0 host code):", "OPEN" if c else "MISSED")
    r = run(rows=[])
    c = any("osViSetXScale(ctx->f12.fl)" in o[2] for o in r[1]); ok += c; print("control 3 (rows dropped):", "OPEN" if c else "MISSED")
    h = open(os.path.join(ROOT, HELPERS)).read()
    r = run({HELPERS: h.replace("ret.as_u32 = _arg<1, u32>(rdram, ctx);", "ret.as_u32 = _arg<2, u32>(rdram, ctx);")})
    c = any("_arg_float_a1" in o[2] for o in r[1]); ok += c; print("control 4 (_arg_float_a1 reads a2):", "OPEN" if c else "MISSED")
    r = run({UC: plant("    ctx->r2 = 0;", "sinf")})
    c = any("sinf_recomp" in o[2] for o in r[1]); ok += c; print("control 5 (host sinf stub, no FLOATPROTO):", "OPEN" if c else "MISSED")
    m = open(os.path.join(ROOT, MH)).read()
    old = ("    ctx->f0.fl = (gpr)(uint8_t)hook_contexts.back().f0.fl;\n"
           "    ctx->f1.fl = (gpr)(uint8_t)hook_contexts.back().f1.fl;")
    r = run({MH: m.replace("    ctx->f0.d = hook_contexts.back().f0.d;", old)})
    c = any("uint8_t" in o[2] for o in r[1]) and any("f1.fl" in o[2] for o in r[1]); ok += c
    print("control 6 (pre-s7605 recomphook_get_return_double):", "OPEN" if c else "MISSED")
    print(f"controls {ok}/6"); return ok


if __name__ == "__main__":
    r = run(verbose="-v" in sys.argv); report(r)
    print("game call sites:", game_calls())
    good = not r[1] and not r[2]
    if "--controls" in sys.argv: good = controls() == 6 and good
    sys.exit(0 if good else 1)
