#!/usr/bin/env python3
"""s7606 class HC: host code that CALLS a guest (recompiled) function.

Enumerates every call expression NAME(rdram, X) / NAME(PASS_RDRAM X) in src/ + librecomp + ultramodern whose callee is
(a) a generated guest function (RecompiledFuncs RECOMP_FUNC names), (b) a host variable/parameter/member declared as a
guest-function pointer (recomp_func_t*, (*NAME)(uint8_t* rdram, recomp_context*)), or (c) a GameEntry callback member
(.entrypoint/.thread_create_callback/.on_init_callback). Each call must match a SITE_ROWS entry; per kind:
  fresh   new recomp_context: r29 written before the call (or the callee's first generated statement writes r29), FR=0
          set up (f_odd = &f0.u32h and mips3_float_mode = 0/false, here or in the named init function);
  reused  host stub passes ITS ctx on: after the call, no read of ctx->rN in the rest of the function (the callee
          clobbers every caller-saved register; only r2/r3 results are legitimate, and they need a row flag);
  dead    callee pointer is never assigned on this port (checked: no assignment in src/);
  gated   runs only with mods loaded / an env flag (named in the row).
Global contract checks (each failing one is OPEN):
  - OSThread.sp is int32_t and osCreateThread sets t->sp = sp - 0x10 (libultra's 16-byte o32 arg area);
  - osCreateThread_recomp passes entry/arg/sp as (int32_t) (sign-extended into run_thread_function's uint64 params);
  - run_thread_function sets ctx.r29 = sp, ctx.r4 = arg, FR=0;
  - get_function's miss path is fatal (no silent mid-function / unknown entry) unless ROGUESQ_STUB_MISSING_FUNCS;
  - the generated recomp_entrypoint's first statement writes r29;
  - generated code reads gp (r28) only in data_gap_* bodies or diagnostic fprintf lines (thread ctx leaves gp = 0);
  - runtime thread entries (THREAD_RT, from [m5-runtime-context] logs) are generated function starts with an 8-aligned
    sp inside KSEG0 RAM.
--controls: (1) fresh ctx call without r29; (2) fresh ctx call without f_odd; (3) rows dropped; (4) reused-ctx call then a
ctx->r4 read; (5) t->sp = sp (no arg area); (6) runtime entry 0x8008ED74 (mid-function) + sp 0x80166434 (misaligned);
(7) OSThread.sp as uint32_t. Exit 0 only if 0 open, 0 stale rows, 7/7 controls.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = "lib/N64ModernRuntime"
DIRS = ["src", L + "/librecomp/src", L + "/librecomp/include", L + "/ultramodern/src", L + "/ultramodern/include"]
GEN = "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs"
SKIP = re.compile(r"/(tests?|third_party|thirdparty)/")
REC = L + "/librecomp/src/recomp.cpp"
THR = L + "/ultramodern/src/threads.cpp"
U64 = L + "/ultramodern/include/ultramodern/ultra64.h"
UT = L + "/librecomp/src/ultra_translation.cpp"
OVL = L + "/librecomp/src/overlays.cpp"
UC = "src/main/upstream_compat.cpp"
LOG = "scratch/agent/loop.log.pre-s5016"

# (file suffix, line substring, kind, extra, reason)
SITE_ROWS = [
    (REC, "game_entry.thread_create_callback(rdram, &ctx);", "dead", "thread_create_callback",
     "GameEntry callback, never assigned on this port (main.cpp supported_games omits it) -> nullptr, branch dead"),
    (REC, "func(rdram, &ctx);", "fresh", "",
     "run_thread_function: fresh ctx, r29 = OSThread.sp (= stack top - 0x10), r4 = arg, FR=0; func = get_function(entry); "
     "2 textual sites (Win32 SEH arm + POSIX arm), same ctx setup"),
    (REC, "game_entry.entrypoint(rdram, context);", "fresh", "init:recomp_entrypoint",
     "boot: context zeroed in the Game Start thread, FR=0 set by init(); entrypoint = rs64_entrypoint_with_rdram_capture "
     "-> recomp_entrypoint whose first statement is lui $sp (0x80000400)"),
    (REC, "game_entry.on_init_callback(rdram, context);", "dead", "on_init_callback",
     "GameEntry callback, never assigned on this port -> branch dead"),
    ("src/main/main.cpp", "recomp_entrypoint(rdram, ctx);", "reused", "",
     "rs64_entrypoint_with_rdram_capture forwards its ctx as a tail call; nothing reads ctx after it"),
    (L + "/librecomp/src/mod_hooks.cpp", "native_func(rdram, ctx);", "gated", "mods",
     "mod hook dispatch: only a loaded code mod registers hooks (no mods shipped; s7597)"),
    (L + "/librecomp/src/mod_events.cpp", "native_func(rdram, ctx);", "gated", "mods",
     "mod event dispatch: only a loaded code mod registers event callbacks"),
]


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
                    p = os.path.join(dp, f)
                    out[os.path.relpath(p, ROOT)] = open(p, errors="surrogateescape").read()
    for k, v in (over or {}).items(): out[k] = v
    return out


_GEN = None
def gen():
    """(names, {start_addr: name}, {name: body}) of the generated guest functions."""
    global _GEN
    if _GEN is not None: return _GEN
    names, starts, bodies = set(), {}, {}
    for f in sorted(os.listdir(GEN)):
        if not f.endswith(".c"): continue
        t = open(os.path.join(GEN, f), errors="surrogateescape").read()
        parts = re.split(r"^RECOMP_FUNC void (\w+)\(uint8_t\* rdram, recomp_context\* ctx\) \{", t, flags=re.M)
        for i in range(1, len(parts), 2):
            n, b = parts[i], parts[i + 1]
            names.add(n); bodies[n] = b
            m = re.search(r"// (0x[0-9A-F]{8}):", b)
            if m: starts[int(m.group(1), 16)] = n
    _GEN = (names, starts, bodies); return _GEN


def thread_rt(over=None):
    if over is not None: return over
    p = os.path.join(ROOT, LOG); rt = {}
    if os.path.exists(p):
        for m in re.finditer(r"site=run_thread_function addr=0x([0-9A-F]{8}) sp=0x([0-9A-F]{8}) arg=0x([0-9A-F]{8})",
                             open(p, errors="replace").read()):
            rt[(int(m.group(1), 16), int(m.group(2), 16))] = int(m.group(3), 16)
    return rt


CALL = re.compile(r"(?<![\w>])((?:\w+\.)?[A-Za-z_]\w*)\s*\(\s*(?:PASS_RDRAM\s*|rdram\s*,\s*)(&?\w+)\s*\)")
MEMBERS = {"entrypoint", "thread_create_callback", "on_init_callback"}


def run(over=None, rows=None, rt_over=None, verbose=False):
    raw = load(over); rows = SITE_ROWS if rows is None else rows
    names, starts, bodies = gen()
    ptrs = set()
    for t in raw.values():
        s = strip_comments(t)
        ptrs |= set(re.findall(r"recomp_func_t\s*\*\s*(\w+)\b(?!\s*\()", s))
        ptrs |= set(re.findall(r"\(\s*\*\s*(\w+)\s*\)\s*\(\s*uint8_t\s*\*\s*rdram\s*,\s*recomp_context", s))
    stats, open_, used = {}, [], set()
    for rel, txt in raw.items():
        s = strip_comments(txt); sl = s.split("\n"); lines = txt.split("\n")
        for ln, code in enumerate(sl, 1):
            for m in CALL.finditer(code):
                callee = m.group(1); base = callee.split(".")[-1]
                if "." in callee and base not in MEMBERS: continue
                if not (base in names or base in ptrs or base in MEMBERS): continue
                if re.search(r"\b(?:void|bool|auto)\s+" + re.escape(base) + r"\s*\(", code): continue  # definition
                line = lines[ln - 1].strip(); var = m.group(2).lstrip("&")
                hit = None
                for i, row in enumerate(rows):
                    if rel.endswith(row[0]) and row[1] in line: hit = (i, row); break
                if hit is None:
                    open_.append((rel, ln, f"no-row guest call {callee}({var}) {line[:110]}")); continue
                used.add(hit[0]); kind, extra = hit[1][2], hit[1][3]
                fstart = ln - 1
                while fstart > 0 and not re.match(r"^[A-Za-z].*\)\s*(?:const\s*)?\{\s*$|^[A-Za-z][^;]*\{\s*$", sl[fstart]): fstart -= 1
                pre = "\n".join(sl[fstart:ln - 1]) + "\n" + code[:m.start()]
                bad = None
                if kind == "fresh":
                    if extra.startswith("init:"):
                        tgt = extra.split(":")[1]
                        fb = bodies.get(tgt, "")
                        first = re.search(r"\n\s*(ctx->r\d+)\s*=", fb)
                        if not first or first.group(1) != "ctx->r29": bad = f"callee {tgt} does not set r29 first"
                        ib = re.search(r"\nvoid init\(uint8_t\* rdram, recomp_context\* ctx, gpr entrypoint\) \{(.*?)\n\}", s, re.S)
                        if not ib or not re.search(r"ctx->f_odd = &ctx->f0\.u32h;", ib.group(1)) or \
                                not re.search(r"ctx->mips3_float_mode = (?:false|0);", ib.group(1)):
                            bad = (bad or "") + " init() does not set FR=0"
                        if not re.search(r"init\(rdram, " + var + r", ", pre): bad = (bad or "") + f" {var} not passed to init()"
                    else:
                        acc = r"\b" + re.escape(var) + r"\s*(?:\.|->)"
                        if not re.search(acc + r"r29\s*=", pre): bad = "fresh ctx: r29 not set before the call"
                        if not re.search(acc + r"f_odd\s*=\s*&\s*" + re.escape(var) + r"\s*(?:\.|->)f0\.u32h", pre):
                            bad = (bad or "") + " fresh ctx: f_odd not FR=0"
                        if not re.search(acc + r"mips3_float_mode\s*=\s*(?:0|false)", pre):
                            bad = (bad or "") + " fresh ctx: mips3_float_mode not 0"
                elif kind == "reused":
                    post, depth = [], 0
                    rest = code[m.end():] + "\n" + "\n".join(sl[ln:ln + 80])
                    for ch_i, ch in enumerate(rest):
                        if ch == "{": depth += 1
                        elif ch == "}":
                            depth -= 1
                            if depth < 0: rest = rest[:ch_i]; break
                    r = re.findall(r"\b" + re.escape(var) + r"\s*->\s*(r\d+|f\d+)\b", rest)
                    if r: bad = f"reused ctx read after guest call: {sorted(set(r))}"
                elif kind == "dead":
                    for r2, t2 in raw.items():
                        if r2.startswith("src/") and re.search(r"(?:\.|\b)" + extra + r"\s*=", strip_comments(t2)):
                            bad = f"{extra} assigned in {r2}: not dead"
                k = "OPEN" if bad else kind
                stats[k] = stats.get(k, 0) + 1
                if bad: open_.append((rel, ln, f"{bad} :: {line[:100]}"))
                elif verbose: print(f"  {kind:6} {rel}:{ln} {line[:100]}")
    # global contract checks
    def need(rel, pat, what):
        if not re.search(pat, strip_comments(raw.get(rel, "")), re.S): open_.append((rel, 0, "contract broken: " + what))
    need(U64, r"UltraThreadContext\* context;[^;]*\n\s*int32_t sp;\s*\n\}\s*OSThread;", "OSThread.sp is int32_t (sign-extends)")
    need(THR, r"t->sp = sp - 0x10;", "osCreateThread reserves the 16-byte o32 arg area")
    need(THR, r"static void _thread_func\(RDRAM_ARG PTR\(OSThread\) self_, PTR\(thread_func_t\) entrypoint, PTR\(void\) arg,",
         "_thread_func carries entry/arg as int32 PTR()")
    need(THR, r"run_thread_function\(PASS_RDRAM entrypoint, self->sp, arg\);", "thread start passes OSThread.sp")
    need(UT, r"osCreateThread\(rdram, \(int32_t\)ctx->r4, \(OSId\)ctx->r5, \(int32_t\)ctx->r6, \(int32_t\)ctx->r7,\s*"
             r"\(int32_t\)MEM_W\(0x10, ctx->r29\)", "osCreateThread_recomp sign-extends entry/arg/sp")
    need(REC, r"void run_thread_function\(uint8_t\* rdram, uint64_t addr, uint64_t sp, uint64_t arg\) \{(?:(?!\n\}).)*?"
              r"ctx\.r29 = sp;\s*ctx\.r4 = arg;", "run_thread_function sets r29/r4")
    need(OVL, r"get_function\(int32_t addr\) \{(?:(?!\n\}).)*?func_map\.find\(addr\);(?:(?!\n\}).)*?ROGUESQ_STUB_MISSING_FUNCS"
              r"(?:(?!\n\}).)*?Failed to find function(?:(?!\n\}).)*?std::exit\(EXIT_FAILURE\);",
         "get_function miss path is fatal (entry must be a function start)")
    gp = []
    for n, b in bodies.items():
        if n.startswith("data_gap_"): continue
        for l in b.split("\n"):
            if "ctx->r28" in l and not re.match(r"\s*(?://|f?printf|fprintf|ctx->r28\s*=)", l.strip()) and "fprintf" not in l \
                    and not re.search(r"U32\(ctx->r28\)\);\s*$", l):
                gp.append((n, l.strip()[:80]))
    for g in gp: open_.append(("<gen>", 0, f"live gp read in {g[0]}: {g[1]}"))
    stats["gp_live_reads"] = len(gp)
    rt = thread_rt(rt_over)
    for (a, sp), arg in sorted(rt.items()):
        why = []
        if a not in starts: why.append("entry not a function start")
        if sp & 7: why.append("sp not 8-aligned")
        if not (0x80000000 <= sp < 0x80800000): why.append("sp outside KSEG0 RAM")
        if why: open_.append(("<runtime>", 0, f"thread entry 0x{a:08X} sp=0x{sp:08X}: {', '.join(why)}"))
    stats["rt_entries"] = len(rt); stats["ptr_names"] = len(ptrs)
    stale = [rows[i] for i in range(len(rows)) if i not in used]
    return stats, open_, stale


def report(r, tag="real"):
    stats, op, stale = r
    print(f"[{tag}] " + " ".join(f"{k}={v}" for k, v in sorted(stats.items())) + f" open={len(op)} stale_rows={len(stale)}")
    for o in op: print("   OPEN", o)
    for s in stale: print("   STALE", s[:2])


def controls():
    ok, src = 0, open(os.path.join(ROOT, UC)).read()
    def plant(body):
        return src + '\nextern "C" void rs64_hc_ctl(uint8_t* rdram, recomp_context* ctx) {\n' + body + '\n}\n'
    crow = [(UC, "slotDispatcherIter(rdram, &c); /*hcctl*/", "fresh", "", "control")]
    r = run({UC: plant("    recomp_context c{};\n    c.f_odd = &c.f0.u32h;\n    c.mips3_float_mode = 0;\n    slotDispatcherIter(rdram, &c); /*hcctl*/")},
            rows=SITE_ROWS + crow)
    c = any("r29 not set" in o[2] for o in r[1]); ok += c; print("control 1 (fresh ctx, no r29):", "OPEN" if c else "MISSED")
    r = run({UC: plant("    recomp_context c{};\n    c.r29 = 0xFFFFFFFF803FFFF0ull;\n    c.mips3_float_mode = 0;\n    slotDispatcherIter(rdram, &c); /*hcctl*/")},
            rows=SITE_ROWS + crow)
    c = any("f_odd not FR=0" in o[2] for o in r[1]); ok += c; print("control 2 (fresh ctx, no f_odd):", "OPEN" if c else "MISSED")
    r = run(rows=[])
    c = any("no-row" in o[2] and "func(ctx)" in o[2] for o in r[1]); ok += c; print("control 3 (rows dropped):", "OPEN" if c else "MISSED")
    r = run({UC: plant("    slotDispatcherIter(rdram, ctx); /*hcctl*/\n    int y = (int)ctx->r4; (void)y;")},
            rows=SITE_ROWS + [(UC, "slotDispatcherIter(rdram, ctx); /*hcctl*/", "reused", "", "control")])
    c = any("reused ctx read" in o[2] for o in r[1]); ok += c; print("control 4 (reused ctx, then ctx->r4):", "OPEN" if c else "MISSED")
    t = open(os.path.join(ROOT, THR)).read()
    r = run({THR: t.replace("t->sp = sp - 0x10;", "t->sp = sp;")})
    c = any("arg area" in o[2] for o in r[1]); ok += c; print("control 5 (no o32 arg area):", "OPEN" if c else "MISSED")
    rt = dict(thread_rt()); rt[(0x8008ED74, 0x80166434)] = 0
    r = run(rt_over=rt)
    c = any("not a function start" in o[2] and "not 8-aligned" in o[2] for o in r[1]); ok += c
    print("control 6 (mid-function entry, misaligned sp):", "OPEN" if c else "MISSED")
    h = open(os.path.join(ROOT, U64)).read()
    r = run({U64: h.replace("UltraThreadContext* context; // An actual pointer regardless of platform\n    int32_t sp;",
                            "UltraThreadContext* context; // An actual pointer regardless of platform\n    uint32_t sp;")})
    c = any("OSThread.sp" in o[2] for o in r[1]); ok += c; print("control 7 (OSThread.sp zero-extends):", "OPEN" if c else "MISSED")
    print(f"controls {ok}/7"); return ok


if __name__ == "__main__":
    r = run(verbose="-v" in sys.argv); report(r)
    good = not r[1] and not r[2] and r[0].get("rt_entries", 0) > 0
    if "--controls" in sys.argv: good = controls() == 7 and good
    sys.exit(0 if good else 1)
