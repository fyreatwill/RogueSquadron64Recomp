#!/usr/bin/env python3
"""s7555 class GO census: every device STATUS / progress value the runtime RETURNS to the guest (the polled twin of class GB's
completion signals, tools/s7538_gb_census.py), and whether each is consistent with hardware ordering (busy until the matching
signal, then idle) in every mode: default, ROGUESQ_RDP_ASYNC=1 NODRAIN=3, ROGUESQ_SP_LATE=1, ROGUESQ_FPS60=1.

Three parts, all must pass for exit 0:
 (A) RETURN rows: every `X_recomp` definition under ROOTS whose body assigns ctx->r2 (a value returned to the guest), plus the
     out-parameter getters in OUTPARAM (status written into a guest buffer).  Each row: imported by the game?
     (`nm -u build/libRecompiledFuncs.a`), weak (shadowed by a strong definition elsewhere), and a RULE.
     Non-imported rows are H-unused automatically (proved by nm, not assumed).  Imported rows need a rule whose checks pass;
     an H-consistent rule whose code check FAILS turns the row into H-stale (OPEN) - the claim is read from the code.
 (B) CALL SITES: every guest call of an imported row in the generated code (GEN), with whether the caller READS $v0 after the
     call (first later mention of ctx->r2 is a read) or kills it (first mention is a plain write).  An unknown use counts as read.
     A row whose every call site kills $v0 is H-ret-unused (its value cannot reach game logic, whatever it is).
 (C) MMIO: the generated code never forms a device-register base (lui 0xA3F0-0xA4FF / 0x03F0-0x04FF, KSEG1 or physical), so no
     game code polls a device register past the replaced libultra layer.  Any such constant is listed and FAILs.
Getters in DEVICE_GETTERS with no definition at all must also be nm-absent (else the game would link to nothing - FAIL).

Classes: H-unused (not imported), H-shadowed (weak def, a strong one wins), H-ret-unused, H-consistent (value ordered with its
signal in every mode, reason + code checks), H-nostatus (returned value is not device progress: constant success, arithmetic,
time), H-signal (the returned value IS the message-queue signal, taken under the queue's own lock), H-nopak (no Controller Pak:
retail with an empty slot gets the same error), H-instrument-only, H-stale (OPEN), UNCLASSIFIED / FAIL.

  python3 tools/s7555_go_census.py              # rows + summary; exit 1 on FAIL / UNCLASSIFIED / H-stale / MMIO site
  python3 tools/s7555_go_census.py --controls   # planted fixtures + mutation controls
"""
import os, re, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s7530_fw_census as fw
import s7533_fz_census as fz

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOTS = ["lib/N64ModernRuntime/librecomp/src", "lib/N64ModernRuntime/ultramodern/src", "src/main", "src/rsp"]
LIB = "build/libRecompiledFuncs.a"
GEN = os.environ.get("RS64_RECOMP_FUNCS", os.path.join(os.path.dirname(REPO), "N64Recomp", "RecompiledFuncs"))
SP, UC, AI, PI, EEP = ("lib/N64ModernRuntime/librecomp/src/sp.cpp", "src/main/upstream_compat.cpp",
                       "lib/N64ModernRuntime/librecomp/src/ai.cpp", "lib/N64ModernRuntime/librecomp/src/pi.cpp",
                       "lib/N64ModernRuntime/librecomp/src/eep.cpp")
# libultra device status/progress getters (hardware register readers). A row is emitted for each even with no host definition.
DEVICE_GETTERS = ["osAiGetLength", "osAiGetStatus", "__osAiDeviceBusy", "osDpGetStatus", "osDpGetCounters", "osSpTaskYielded",
                  "__osSpGetStatus", "__osSpDeviceBusy", "osPiGetStatus", "__osPiDeviceBusy", "osEPiReadIo", "__osSiDeviceBusy",
                  "osViGetCurrentFramebuffer", "osViGetNextFramebuffer", "osViGetCurrentLine", "osViGetCurrentMode",
                  "osViGetStatus", "osViGetCurrentField", "osGetCount", "osGetTime", "osEepromProbe", "osContGetQuery",
                  "osContGetReadData", "osFlashCheckEraseEnd", "osPfsFileState", "osPfsFreeBlocks"]
OUTPARAM = {"osContGetQuery", "osContGetReadData", "osDpGetCounters"}   # status returned through a guest buffer, not $v0

NOPAK = ("H-nopak", "no Controller Pak: host returns PFS_ERR_NOPACK / -1 every call; retail with an empty slot fails the same "
         "call the same way (s7527 FU NOPAK), so there is no busy/idle progress to order", [])
# name -> (class, why, checks).  checks: ("body", rx) in this definition's body; ("fnbody", path, fn, rx); ("nm_present", sym)
RULES = {
    "osSpTaskYielded": ("H-consistent",
        "spTaskSchedulerThread 0x80019E14 calls it on the SP-done message for a task it asked to yield (pending 0x80128D40) and "
        "stores the result to 0x8011A89F = 'resume the yielded gfx task'.  The port never yields a running task (the F5 LLE runs "
        "every gfx task to completion inside send_dl; the yield request only latches g_sp_yield_requested, reset by every "
        "osSpTaskStartGo), so the hardware-consistent answer is always 0 = 'it completed'.  Default returns 0; mode-independent "
        "(SP_LATE moves only when sp_complete is posted, RDP_ASYNC/NODRAIN only the DP side, FPS60 only the frame pacing).  "
        "ROGUESQ_SP_YIELDED_REQUEST_ONLY=1 (legacy diag, default off) would answer 1 for a completed task",
        [("body", r"const uint32_t returned = request_only && requested \? 1u : 0u;\s*ctx->r2 = returned;"),
         ("body", r"std::getenv\(\"ROGUESQ_SP_YIELDED_REQUEST_ONLY\"\)"),
         ("fnbody", UC, "osSpTaskStartGo_recomp", r"rs64_sp_reset_yield_request\(\);")]),
    "osViGetCurrentField": ("H-consistent",
        "returns 0 = the field bit of a non-interlaced mode; retail oracle s2199/s2211: 415/415 watched returns = 0.  "
        "viRetraceHandlerThread stores it to 0x80128D2C, read by getInactiveBufferIndex (^1) and postSwapRdpReset; a constant "
        "in every mode, as on hardware for this game's modes",
        [("body", r"ctx->r2 = 0;")]),
    "osAiSetNextBuffer": ("H-consistent",
        "retail returns -1 while the AI DMA FIFO is full (__osAiDeviceBusy); the host queue is unbounded so it always accepts "
        "(0).  Ordering-consistent only if no caller acts on it: see the call-site column (both sites must kill $v0, else this "
        "row is promoted to H-stale by the ret-use rule)",
        [("body", r"ultramodern::queue_audio_buffer\(rdram, ctx->r4, ctx->r5\);\s*ctx->r2 = 0;")]),
    "osPiStartDma": ("H-consistent",
        "returns 0 after do_dma copied ROM->RDRAM synchronously on the guest thread (class GB pi-rom row), so 'accepted' and "
        "'done' are both true when the guest sees the value", [("body", r"do_dma\(")]),
    "osEepromProbe": ("H-nostatus", "save-type constant (EEPROM 16K = retail cart), no progress", [("body", r"ctx->r2 = 0x02;")]),
    "osEepromLongRead": ("H-consistent", "returns after the synchronous host save_read of the whole block; 0 = done",
                         [("body", r"save_read\(")]),
    "osEepromLongWrite": ("H-consistent", "returns after the synchronous host save_write copy into the save buffer; 0 = done",
                          [("body", r"save_write\(")]),
    "osGetTime": ("H-nostatus", "monotone host clock in CPU-count ticks (s7514 FK); no device progress", []),
    "osSetTimer": ("H-nostatus", "constant 0 (success)", []),
    "osAiSetFrequency": ("H-nostatus", "returns the rate actually programmed (arithmetic on the request), no progress", []),
    "osVirtualToPhysical": ("H-nostatus", "pure address arithmetic", []),
    "osSpTaskLoad": ("H-nostatus", "void in libultra; any $v0 is scratch", []),
    "osSpTaskStartGo": ("H-nostatus", "void in libultra; the guard return value is scratch", []),
    "osSendMesg": ("H-signal", "0 / -1 (queue full, NOBLOCK) is the message queue itself: computed by ultramodern osSendMesg "
                   "under the queue lock that posts the signal", [("body", r"osSendMesg\(rdram, ")]),
    "osJamMesg": ("H-signal", "same as osSendMesg", [("body", r"osJamMesg\(rdram, ")]),
    "osRecvMesg": ("H-signal", "0 / -1 (queue empty, NOBLOCK) is the message queue itself: a polled device queue reports "
                   "empty exactly until the device's enqueue, the GB signal", [("body", r"osRecvMesg\(rdram, ")]),
    "osContGetQuery": ("H-consistent", "copies the host status block that osContStartQuery's SI message already describes "
                       "(GB si row: no SI transfer outstanding after the message)", []),
    "osContGetReadData": ("H-consistent", "copies the pad state polled BEFORE osContStartReadData posted its SI message "
                          "(GB si row: input_callbacks.poll_input before the post)",
                          [("fnbody", "lib/N64ModernRuntime/ultramodern/src/input.cpp", "osContStartReadData",
                            r"input_callbacks\.poll_input\(\)")]),
    "osDpGetCounters": ("H-nostatus", "zeroes the 8 DP counters; only caller is the submitGfxFrame profiler path, profiler "
                        "gate 0 (s7514 FK, single-source); never device progress",
                        [("body", r"MEM_W\(i \* 4, buf_ptr\) = 0;")]),
    "__ll_div": ("H-nostatus", "pure 64-bit arithmetic (math_routines.cpp)", []),
    "__ll_mul": ("H-nostatus", "pure 64-bit arithmetic", []), "__ull_div": ("H-nostatus", "pure 64-bit arithmetic", []),
    "__ull_rem": ("H-nostatus", "pure 64-bit arithmetic", []),
    "__osDisableInt": ("H-nostatus", "returns the (no-op) interrupt mask; host guest threads hold one run token (class GD)", []),
    "osPfsInitPak": NOPAK, "osPfsAllocateFile": NOPAK, "osPfsDeleteFile": NOPAK, "osPfsFindFile": NOPAK,
    "osPfsReadWriteFile": NOPAK,
}
OK = {"H-unused", "H-shadowed", "H-ret-unused", "H-consistent", "H-nostatus", "H-signal", "H-nopak", "H-instrument-only"}
# lui of a device register page: RCP registers 0x03F0-0x04FF (+KSEG1 0xA3F0-0xA4FF) and physical PIF 0x1FC0.  ROM KSEG1
# 0xB0xx is not a register; KSEG1 PIF 0xBFC0 is not matched because it collides with float immediates (0x8006D168
# lui a2,0xBFC0 = -1.5f to scaleVec3ByRandomRange) - PIF RAM is reached only by SI (osCont*/osEeprom*, all replaced).
MMIO = re.compile(r'S32\(0X(?:A3F|A4[0-9A-F]|03F|04[0-9A-F])[0-9A-F] << 16\)|S32\(0X1FC0 << 16\)')
# replacements too instrumented for always_sets_r2's textual test: every arm of the dispatch assigns ctx->r2 and the body
# has no early return (checked here, so a code change that breaks it drops the row from the killer set)
KILLER_RULES = {"osRecvMesg": r"ctx->r2 = result;[\s\S]*\} else if \(mq_addr == 0x8010FEE0u\) \{[\s\S]*ctx->r2 = result;"
                              r"[\s\S]*\} else \{\s*ctx->r2 = osRecvMesg\(rdram, "}
_nm = {}


def nm_imports(lib=LIB):
    if lib not in _nm:
        try:
            out = subprocess.run(["nm", "-u", os.path.join(REPO, lib)], capture_output=True, text=True).stdout
        except OSError:
            out = ""
        s = set()
        for l in out.splitlines():
            if l.strip():
                n = l.split()[-1]
                n = n[1:] if n.startswith("_") else n          # strip exactly the Mach-O prefix underscore
                if n.endswith("_recomp"):
                    s.add(n[:-len("_recomp")])
        _nm[lib] = s
    return _nm[lib]


def read(path, over):
    p = over.get(path, os.path.join(REPO, path))
    try:
        return fw.strip_comments(open(p, errors="replace").read())
    except OSError:
        return ""


def fn_body(t, fn):
    for o, c, name in fz.func_spans(t):
        if name == fn:
            return t[o:c + 1]
    return None


def files_under(roots):
    out = []
    for r in roots:
        for dp, _, fs in os.walk(os.path.join(REPO, r)):
            for f in sorted(fs):
                if f.endswith((".cpp", ".c")):
                    out.append(os.path.relpath(os.path.join(dp, f), REPO))
    return sorted(out)


def definitions(files, over):
    """every X_recomp definition: (name, path, line, body, weak, returns)"""
    out = []
    for p in files:
        t = read(p, over)
        for o, c, n in fz.func_spans(t):
            # fz names `__attribute__((weak)) void f(..)` spans "__attribute__": resolve the name from the header text
            hdr = re.search(r'(\w+)\s*\([^;{}()]*\)\s*(?:const\s*)?$', t[max(0, o - 400):o])
            n = hdr.group(1) if hdr and n == "__attribute__" else n
            if not n.endswith("_recomp"):
                continue
            base = n[:-len("_recomp")]
            body = t[o:c + 1]
            line0 = t.rfind("\n", 0, max(0, t.rfind(n, 0, o)))
            weak = re.search(r'__attribute__\s*\(\(\s*weak\s*\)\)', t[line0 + 1:o]) is not None
            ret = re.search(r'ctx->r2(?!\d)\s*=[^=]', body) is not None
            if ret or base in OUTPARAM or base in DEVICE_GETTERS:
                out.append(dict(name=base, path=p, line=t.count("\n", 0, o) + 1, body=body, weak=weak, ret=ret))
    return out


CALL = re.compile(r'\b(\w+)_recomp\(rdram, ctx\);')


def call_sites(gen, names, killers=()):
    """name -> list of (file, line, use) where use in read|kill|unknown.  killers: replacements whose host body ends with
    an unconditional ctx->r2 assignment, so a call to one before any $v0 read kills the value"""
    res = {n: [] for n in names}
    try:
        fs = sorted(f for f in os.listdir(gen) if f.endswith(".c"))
    except OSError:
        return res
    for f in fs:
        lines = open(os.path.join(gen, f), errors="replace").read().split("\n")
        for i, l in enumerate(lines):
            m = CALL.search(l)
            if not m or m.group(1) not in res or "RECOMP_FUNC" in l:
                continue
            res[m.group(1)].append((f, i + 1, ret_use(lines, i + 1, killers)))
    return res


R2 = re.compile(r'ctx->r2(?!\d)')


def ret_use(lines, i, killers=()):
    for l in lines[i:i + 80]:
        s = l.strip()
        if not s or s.startswith("//") or re.match(r'(goto after_\d+;|after_\d+:|L_[0-9A-F]+:)$', s):
            continue
        c = CALL.search(s)
        if c and c.group(1) in killers:
            return "kill"
        if "RECOMP_FUNC" in s or s == "return;" or c or re.search(r'\bgoto L_', s):
            return "unknown"
        if s.startswith("if (__builtin_expect(g_rs64_store_diag"):
            continue                                        # diag-only statement
        if not R2.search(s):
            continue
        w = re.search(r'ctx->r2(?!\d)\s*=(?!=)\s*(.*)', s)
        before = s[:w.start()] if w else s
        if w and not R2.search(before) and not R2.search(w.group(1)):
            return "kill"
        return "read"
    return "unknown"


def always_sets_r2(body):
    """the body's last statement before the closing brace (after trailing diag calls) and every `return;` are preceded by
    a ctx->r2 assignment in the same block: conservative textual test"""
    b = body.rstrip()[:-1]
    for m in re.finditer(r'return\s*;', b):
        if not re.search(r'ctx->r2(?!\d)\s*=[^=][^;]*;\s*(?:\w+\([^;]*\);\s*)*$', b[:m.start()]):
            return False
    tail = re.sub(r'(?:\s*(?:if \([^;{}]*\) )?[\w:]+(?:\.\w+)*\([^;{}]*\);)*\s*$', '', b)
    return re.search(r'ctx->r2(?!\d)\s*=[^=][^;]*;\s*$', tail) is not None


def mmio_sites(gen, over_files=None):
    out = []
    fs = over_files if over_files is not None else [os.path.join(gen, f) for f in sorted(os.listdir(gen))
                                                    if f.endswith(".c")] if os.path.isdir(gen) else []
    for p in fs:
        for i, l in enumerate(open(p, errors="replace").read().split("\n")):
            if MMIO.search(l):
                out.append((os.path.basename(p), i + 1, l.strip()[:80]))
    return out


def run_checks(d, checks, over, lib):
    fails = []
    for c in checks:
        if c[0] == "body":
            ok = re.search(c[1], d["body"]) is not None
        elif c[0] == "fnbody":
            b = fn_body(read(c[1], over), c[2])
            ok = b is not None and re.search(c[3], b) is not None
        elif c[0] == "nm_present":
            ok = c[1] in nm_imports(lib)
        else:
            ok = False
        if not ok:
            fails.append(":".join(str(x) for x in c)[:90])
    return fails


def census(files=None, rules=RULES, over=None, lib=LIB, gen=GEN, mmio_files=None, quiet=False):
    over = over or {}
    files = files if files is not None else files_under(ROOTS)
    imp = nm_imports(lib)
    defs = definitions(files, over)
    strong = {d["name"] for d in defs if not d["weak"]}
    names = sorted({d["name"] for d in defs if d["name"] in imp})
    killers = {d["name"] for d in defs if d["name"] in imp and not d["weak"] and (always_sets_r2(d["body"]) or (
        d["name"] in KILLER_RULES and re.search(KILLER_RULES[d["name"]], d["body"]) and not re.search(r'\breturn\s*;', d["body"])))}
    calls = call_sites(gen, names, killers)
    rows = []
    stat = {"defs": len(defs), "imported": 0, "unclassified": 0, "fail": 0, "stale": 0, "calls": 0, "mmio": 0}
    for d in defs:
        n, cs = d["name"], calls.get(d["name"], [])
        used = sum(1 for c in cs if c[2] != "kill")
        if n not in imp:
            cls, why, fails = "H-unused", "not imported by libRecompiledFuncs.a (nm -u)", []
        elif d["weak"] and n in strong:
            cls, why, fails = "H-shadowed", "weak definition; the strong one in another file is the row that runs", []
        else:
            stat["imported"] += 1
            stat["calls"] += len(cs)
            rule = rules.get(n)
            if rule is None:
                cls, why, fails = "UNCLASSIFIED", "imported value-returning replacement with no rule", []
            else:
                cls, why, checks = rule
                fails = run_checks(d, checks, over, lib)
                if n not in OUTPARAM and cs and used == 0 and cls in ("H-consistent", "H-nostatus"):
                    cls, why = "H-ret-unused", "every guest call site kills $v0 before reading it; " + why
                elif n == "osAiSetNextBuffer" and used:
                    cls = "H-stale"                         # the H-consistent claim depends on nobody reading it
                if fails and cls in ("H-consistent", "H-ret-unused", "H-signal"):
                    cls = "H-stale"
                elif fails:
                    cls = "FAIL-check"
        if cls == "UNCLASSIFIED":
            stat["unclassified"] += 1
        elif cls == "H-stale":
            stat["stale"] += 1
        elif cls == "FAIL-check":
            stat["fail"] += 1
        rows.append((d, cls, why, fails, cs))
    # getters with no host definition must not be imported
    defined = {d["name"] for d in defs}
    for g in DEVICE_GETTERS:
        if g not in defined:
            ok = g not in imp
            rows.append((dict(name=g, path="<none>", line=0, weak=False, ret=False), "H-unused" if ok else "FAIL-check",
                         "no host definition and not imported" if ok else "imported but no host definition", [] if ok else ["nm"], []))
            if not ok:
                stat["fail"] += 1
    mm = mmio_sites(gen, mmio_files)
    stat["mmio"] = len(mm)
    if not quiet:
        for d, cls, why, fails, cs in rows:
            if cls in ("H-unused",) and d["path"] != "<none>" and d["name"] not in DEVICE_GETTERS:
                continue                                    # unimported non-device helpers: counted, not printed
            u = "calls=%d read=%d kill=%d unk=%d" % (len(cs), sum(c[2] == "read" for c in cs), sum(c[2] == "kill" for c in cs),
                                                     sum(c[2] == "unknown" for c in cs)) if cs else "calls=0"
            print("%-26s %-15s %s:%d %s%s" % (d["name"], cls, d["path"].split("/")[-1], d["line"], u,
                  ("  FAILED " + "; ".join(fails)) if fails else ""))
            if cls in ("H-stale", "FAIL-check", "UNCLASSIFIED"):
                print("      " + why[:400])
        for s in mm:
            print("MMIO %s:%d %s" % s)
        from collections import Counter
        print("summary: defs=%d imported_rows=%d guest_calls=%d unclassified=%d fail=%d stale=%d mmio=%d  %s" % (
            stat["defs"], stat["imported"], stat["calls"], stat["unclassified"], stat["fail"], stat["stale"], stat["mmio"],
            dict(Counter(r[1] for r in rows))))
    return rows, stat


def bad(st):
    return st["unclassified"] or st["fail"] or st["stale"] or st["mmio"]


def controls():
    files = files_under(ROOTS)
    tests = []
    base_rows, base = census(files, quiet=True)
    tests.append(("baseline: >=20 imported rows, >=100 guest call sites, 0 open", base["imported"] >= 20 and base["calls"] >= 100
                  and not bad(base)))
    with tempfile.TemporaryDirectory() as d:
        # 1 planted fixture: an imported getter with no rule -> UNCLASSIFIED; a weak twin of a strong def -> H-shadowed
        fx = os.path.join(d, "fixture.cpp")
        open(fx, "w").write('extern "C" void osSpTaskYielded_recomp(uint8_t* rdram, recomp_context* ctx) { ctx->r2 = 1; }\n'
                            'extern "C" __attribute__((weak)) void osGetTime_recomp(uint8_t* rdram, recomp_context* ctx) '
                            '{ ctx->r2 = 0; }\n')
        rel = os.path.relpath(fx, REPO)
        rows, st = census(files + [rel], rules={k: v for k, v in RULES.items() if k != "osSpTaskYielded"}, quiet=True)
        fxr = [r for r in rows if r[0]["path"] == rel]
        tests.append(("planted: rule-less imported getter UNCLASSIFIED, weak twin H-shadowed",
                      any(r[1] == "UNCLASSIFIED" and r[0]["name"] == "osSpTaskYielded" for r in fxr)
                      and any(r[1] == "H-shadowed" and r[0]["name"] == "osGetTime" for r in fxr)))
        # 2 mis-ordered site: osSpTaskYielded made to answer 'yielded' by default -> H-stale
        src = open(os.path.join(REPO, SP), errors="replace").read()
        m2 = os.path.join(d, "sp_bad.cpp")
        open(m2, "w").write(src.replace("request_only && requested ? 1u : 0u;", "requested ? 1u : 0u;"))
        rows, st = census(files, over={SP: m2}, quiet=True)
        tests.append(("mutation: osSpTaskYielded reports yielded for a completed task -> H-stale, exit 1",
                      any(r[0]["name"] == "osSpTaskYielded" and r[1] == "H-stale" for r in rows) and bad(st)))
        # 3 nm control: pretend the game imports osDpGetStatus -> it needs a rule -> UNCLASSIFIED
        _nm["fake"] = nm_imports() | {"osDpGetStatus", "osViGetCurrentLine"}
        rows, st = census(files, lib="fake", quiet=True)
        tests.append(("nm control: osDpGetStatus imported -> UNCLASSIFIED; osViGetCurrentLine imported w/o def -> FAIL",
                      any(r[0]["name"] == "osDpGetStatus" and r[1] == "UNCLASSIFIED" for r in rows)
                      and any(r[0]["name"] == "osViGetCurrentLine" and r[1] == "FAIL-check" for r in rows)))
        # 4 ret-use classifier on planted generated code
        g = os.path.join(d, "gen"); os.mkdir(g)
        open(os.path.join(g, "funcs_x.c"), "w").write(
            "RECOMP_FUNC void a(uint8_t* rdram, recomp_context* ctx) {\n    osAiSetNextBuffer_recomp(rdram, ctx);\n"
            "        goto after_1;\n    after_1:\n    // 0x0: addu $s0, $v0, $zero\n    ctx->r16 = ADD32(ctx->r2, 0);\n}\n"
            "RECOMP_FUNC void b(uint8_t* rdram, recomp_context* ctx) {\n    osAiSetNextBuffer_recomp(rdram, ctx);\n"
            "    ctx->r2 = S32(0XA440 << 16);\n}\n")
        cs = call_sites(g, ["osAiSetNextBuffer"])["osAiSetNextBuffer"]
        rows, st = census(files, gen=g, quiet=True)
        ai = [r for r in rows if r[0]["name"] == "osAiSetNextBuffer"]
        tests.append(("ret-use: read site + kill site classified; osAiSetNextBuffer read -> H-stale; planted lui 0xA440 -> mmio",
                      sorted(c[2] for c in cs) == ["kill", "read"] and ai and ai[0][1] == "H-stale" and st["mmio"] == 1))
        # 5 MMIO regex does not fire on ROM (0xB0xx) or float (0xBF80) immediates
        f5 = os.path.join(d, "m.c")
        open(f5, "w").write("ctx->r2 = S32(0XB00A << 16);\nctx->r3 = S32(0XBF80 << 16);\nctx->r4 = S32(0X0440 << 16);\n")
        tests.append(("mmio: ROM/float immediates ignored, physical 0x0440 caught", len(mmio_sites(g, [f5])) == 1))
        # 6 code-check control: osPiStartDma's do_dma removed -> H-stale
        src = open(os.path.join(REPO, PI), errors="replace").read()
        m6 = os.path.join(d, "pi_bad.cpp")
        b6 = fn_body(fw.strip_comments(src), "osPiStartDma_recomp")
        open(m6, "w").write(fw.strip_comments(src).replace(b6, b6.replace("do_dma(", "skip_dma(")))
        rows, st = census(files, over={PI: m6}, quiet=True)
        tests.append(("mutation: osPiStartDma without do_dma -> H-stale",
                      any(r[0]["name"] == "osPiStartDma" and r[1] == "H-stale" for r in rows)))
    ok = 0
    for name, r in tests:
        print("%s  %s" % ("PASS" if r else "FAIL", name))
        ok += bool(r)
    print("controls %d/%d" % (ok, len(tests)))
    return ok == len(tests)


def main():
    if "--controls" in sys.argv:
        sys.exit(0 if controls() else 1)
    _, st = census()
    sys.exit(1 if bad(st) else 0)


if __name__ == "__main__":
    main()
