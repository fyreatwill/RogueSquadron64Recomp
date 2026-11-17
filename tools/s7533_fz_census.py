#!/usr/bin/env python3
"""s7533 class FZ census: host code that WRITES guest RDRAM, the reverse direction of class FY
(tools/s7532_fy_census.py: host copies OF guest bytes).  A host write races the guest when it runs on a thread
other than the guest CPU thread while the guest is not blocked on the completion the write precedes
(lost guest store, or a half-done write observed).

Write idioms scanned (comments stripped), DESTINATION names guest memory or a local alias of it
(`T* p = rdram + x;` / `= &rdram[..]` / `= TO_PTR(..)` in the same function):
  memcpy/memmove/memset(dst, ..)      std::copy/copy_n(.., dst) std::fill/fill_n(dst, ..)
  guest[..] = / op=                   MEM_W/H/B/D(..) =          *(T*)(guest + ..) = / *reinterpret_cast<T*>(guest..) =
Per site the enclosing named function is resolved (lambda bodies are attributed to their outer function) and looked up
in RULES (file suffix, function) -> class, thread, timing reason, checks (s7530 run_checks: verify=<regex in file>,
envoff=<VAR absent from owner/loop config>, nocaller=<symbol absent from the linked binary>).
Classes: H-guest-thread (runs on the guest CPU thread: a guest syscall / recompiled-func helper; ordered with guest stores)
         H-canon (non-guest thread, but the guest is blocked on / has not yet been told of the completion this write precedes,
                  or the write IS the hardware semantics, e.g. RSP DMA / PI DMA before the completion interrupt)
         H-instrument-only (env-gated diagnostic, default off)   H-dead (unreachable in the linked binary)
         H-latent-fix (non-guest thread, guest running, range the guest also writes) -> must be instrumented
         UNCLASSIFIED (no rule) -> FAIL

  python3 tools/s7533_fz_census.py              # every row + summary, exit 1 on any FAIL
  python3 tools/s7533_fz_census.py --controls   # planted fixture, mutation control, coverage control
"""
import bisect, os, re, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s7530_fw_census as fw

ROOTS = ["lib/N64ModernRuntime/librecomp/src", "lib/N64ModernRuntime/librecomp/include", "lib/N64ModernRuntime/ultramodern/src", "src/main", "src/rsp",
         "lib/rt64/src/hle", "lib/rt64/src/gbi", "lib/rt64/src/render"]
G = r'(?:rdram|RDRAM|g_rdram_for_submit|g_recomp_rdram\w*|fromRDRAM|rdram_ptr|rdram_base)'
GUEST = re.compile(r'\b' + G + r'\b')
ALIAS = re.compile(r'([A-Za-z_]\w*)\s*=\s*(?:\([^;=]*\)\s*|reinterpret_cast<[^>]*>\s*\(\s*)?\(?\s*&?\s*(?:[\w.\->]*' + G +
                   r'\b|TO_PTR\s*\()[^;]*;')
FN = re.compile(r'\b(?:std::)?(memcpy|memmove|memset|copy|copy_n|fill|fill_n|__atomic_store_n|__atomic_compare_exchange_n|'
                r'__atomic_exchange_n|__atomic_fetch_\w+|copyNativeToRAM)\s*\(')
WRAP_ARG = {"copyNativeToRAM": 0}   # host helpers that write guest memory through a pointer argument
IDX = re.compile(r'([A-Za-z_][\w.\->]*)\s*\[([^;\]]*(?:\][^;=\[]*\[[^;\]]*)*)\]\s*(?:[+\-|&^]?=)(?!=)')
MEMM = re.compile(r'\bMEM_([WHBD])U?\s*\(([^;]*?)\)\s*(?:[+\-|&^]?=)(?!=)')
CAST = re.compile(r'\*\s*(?:reinterpret_cast<[^>]*\*\s*>|\(\s*(?:volatile\s+)?[\w:]+\s*\*\s*\))\s*\(\s*([^;]*?)\)\s*(?:[+\-|&^]?=)(?!=)')


def split_args(t, i):
    depth, cur, args, j = 0, i, [], i
    while j < len(t):
        c = t[j]
        if c in "([{":
            depth += 1
        elif c in ")]}":
            if depth == 0:
                args.append(t[cur:j]); return args, j
            depth -= 1
        elif c == "," and depth == 0:
            args.append(t[cur:j]); cur = j + 1
        j += 1
    return args, j


def func_spans(t):
    """List of (open, close, name) for outermost code braces whose head looks like a function definition."""
    t2 = re.sub(r'"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])\'', lambda m: ' ' * len(m.group(0)), t)
    t2 = re.sub(r'(?m)^[ \t]*#(?:[^\n]*\\\n)*[^\n]*', lambda m: re.sub(r'[^\n]', ' ', m.group(0)), t2)  # preprocessor lines
    out, stack = [], []
    for i, c in enumerate(t2):
        if c == '{':
            head = t2[max(t2.rfind(';', 0, i), t2.rfind('}', 0, i), t2.rfind('{', 0, i)) + 1:i]
            ns = bool(re.search(r'\bnamespace\b[^()]*$|extern\s+"C"\s*$|\b(struct|class|enum|union)\b[^()]*$|=\s*$', head))
            code_depth = sum(1 for s in stack if s[0] == 'code')
            name = None
            if not ns and code_depth == 0:
                m = re.findall(r'([A-Za-z_][\w:~]*)\s*\([^{}]*\)\s*(?:const\s*)?(?:noexcept\s*)?(?:->\s*[\w:<>*& ]+)?\s*(?::[^{]*)?$', head, re.S)
                name = m[-1].split("::")[-1] if m else "?"
            stack.append(('ns' if ns else 'code', i, name))
        elif c == '}' and stack:
            kind, o, name = stack.pop()
            if kind == 'code' and name is not None:
                out.append((o, i, name))
    return sorted(out)


def sites(path):
    try:
        raw = open(path, errors="replace").read()
    except OSError:
        return
    t = fw.strip_comments(raw)
    starts = [0]
    for ln in t.split("\n")[:-1]:
        starts.append(starts[-1] + len(ln) + 1)
    lno = lambda pos: bisect.bisect_right(starts, pos)
    spans = func_spans(t)
    opens = [s[0] for s in spans]

    def enclosing(pos):
        k = bisect.bisect_right(opens, pos) - 1
        while k >= 0:
            if spans[k][0] <= pos <= spans[k][1]:
                return spans[k]
            k -= 1
        return (0, len(t), "<file>")

    alias_cache = {}

    def aliases(span):
        if span not in alias_cache:
            body = t[span[0]:span[1]]
            alias_cache[span] = {m.group(1) for m in ALIAS.finditer(body) if m.group(1) not in ("rdram", "RDRAM")}
        return alias_cache[span]

    def is_guest(expr, pos):
        e = expr.strip()
        e = re.sub(r'^\s*(?:\(\s*[\w:\s\*]+\)\s*|reinterpret_cast<[^>]*>\s*\(|static_cast<[^>]*>\s*\()+', '', e).lstrip("&*( ")
        if re.match(r'(?:[\w]+(?:\.|->))*' + G + r'\b', e) or re.match(r'TO_PTR\s*\(', e):
            return True
        b = re.match(r'([A-Za-z_]\w*)', e)
        return bool(b) and b.group(1) in aliases(enclosing(pos))

    out = []
    for m in FN.finditer(t):
        args, end = split_args(t, m.end())
        f = m.group(1)
        if f in ("memcpy", "memmove", "memset", "fill", "fill_n") or f.startswith("__atomic") or f in WRAP_ARG:
            dst = args[0] if args else ""
        elif f == "copy" and len(args) == 3:
            dst = args[2]
        elif f == "copy_n" and len(args) == 3:
            dst = args[2]
        else:
            continue
        if is_guest(dst, m.start()):
            out.append((lno(m.start()), f, dst.strip()[:50], enclosing(m.start())[2], raw))
    for rx, kind in ((IDX, "index"), (MEMM, "MEM"), (CAST, "cast")):
        for m in rx.finditer(t):
            if kind == "index":
                base = m.group(1)
                if base.endswith(("rdram", "RDRAM")) is False and not is_guest(base, m.start()):
                    continue
                dst = base + "[..]"
            elif kind == "MEM":
                dst = "MEM_" + m.group(1)
            else:
                if not is_guest(m.group(1), m.start()):
                    continue
                dst = "*(" + m.group(1).strip()[:40] + ")"
            out.append((lno(m.start()), kind, dst[:50], enclosing(m.start())[2], raw))
    return sorted(set((a, b, c, d) for a, b, c, d, _ in out)), raw


# (file suffix, function, line regex|None, class, thread, reason, checks)
GT, PRE, GFX, TASK, POLL = "guest", "pre-guest", "gfx", "task", "poller"
L, O, UC, MN, RC, B, ST = ("librecomp/src/", "overlays.cpp", "src/main/upstream_compat.cpp", "src/main/main.cpp",
                           "src/main/rt64_render_context.cpp", "src/rsp/dpc_bridge.cpp", "hle/rt64_state.cpp")
EV = "ultramodern/src/events.cpp"
RING = ("RDP command bytes in the RSP-output ring, rewritten on the Gfx thread after the early sp_complete. The guest CPU never "
        "stores into the ring (RSP DMA output only): s7532 ROGUESQ_S7532_UNDO_CHK measured 0 foreign bytes in 3.1 GB of ring "
        "ranges across the same restore..undo window (L4 dd1 / L15 dd8 21:9, control 1/1); s7489 host DMA write watch host_wF=0")
RULES = [
    # --- guest CPU thread: OS syscall replacements / recompiled-function helpers, ordered with the guest's own stores ----------
    (L + "cont.cpp", "osContInit_recomp", None, "H-guest-thread", GT, "libultra osContInit replacement (guest syscall)", {}),
    (L + "cont.cpp", "osContGetReadData_recomp", None, "H-guest-thread", GT, "osContGetReadData replacement (guest syscall)", {}),
    (L + "flash.cpp", "osFlashReadStatus_recomp", None, "H-guest-thread", GT, "flash syscall replacement", {}),
    (L + "flash.cpp", "osFlashReadId_recomp", None, "H-guest-thread", GT, "flash syscall replacement", {}),
    (L + "mod_config_api.cpp", "return_string", None, "H-guest-thread", GT, "mod API export, called from recompiled code", {}),
    (L + "ultra_translation.cpp", "osInitialize_recomp", None, "H-guest-thread", GT, "osInitialize replacement", {}),
    (L + "pi.cpp", "osPiStartDma_recomp", None, "H-guest-thread", GT,
     "PI DMA replacement: the copy completes inside the syscall, before the completion message is sent", {}),
    (L + "pi.cpp", "do_rom_read", None, "H-guest-thread", GT, "called from osPiStartDma_recomp/osEPiStartDma (synchronous)",
     {"verify": r"recomp::do_rom_read\(rdram, rdram_address, physical_addr, size\);"}),
    (L + "pi.cpp", "do_rom_pio", None, "H-guest-thread", GT, "osPiReadIo replacement path (synchronous)", {}),
    (L + "pi.cpp", "save_read", None, "H-guest-thread", GT,
     "EEPROM/SRAM/flash read into guest memory inside the read syscall, under save_buffer_mutex (the saving thread only reads "
     "save_buffer, never rdram)", {"verify": r"std::lock_guard lock \{ save_context\.save_buffer_mutex \};"}),
    (UC, "osDpGetCounters_recomp", None, "H-guest-thread", GT, "syscall replacement", {}),
    (UC, "osViSwapBuffer_recomp", None, "H-guest-thread", GT, "syscall replacement", {}),
    (UC, "osViSetMode_recomp", None, "H-guest-thread", GT, "syscall replacement", {}),
    (UC, "zmemcpy", None, "H-guest-thread", GT, "zlib zmemcpy replacement called from recompiled inflate", {}),
    (UC, "rs64_s6883_tables", None, "H-guest-thread", GT,
     "spliced into a recompiled function (tools/apply_s6883_spancell.py); the memset needs ROGUESQ_G1D_SPANCELL bit 2, default 3",
     {"verify": r'm = e \? atoi\(e\) : 3;'}),
    (UC, "rs64_s5042_poison", None, "H-instrument-only", GT, "free-path poison, ROGUESQ_FREE_POISON only (guest thread)",
     {"envoff": "ROGUESQ_FREE_POISON"}),
    (L + O, "rs64_s7520_swap", None, "H-instrument-only", GT, "s7520 code-watch control flip (ROGUESQ_S7520_CTL), osViSwapBuffer",
     {"envoff": "ROGUESQ_S7520_CTL"}),
    (L + O, "rs64_s7520_gf", None, "H-instrument-only", GT, "s7520 overlay control flip (ROGUESQ_S7520_CTL)", {"envoff": "ROGUESQ_S7520_CTL"}),
    # --- before the guest thread starts ----------------------------------------------------------------------------------------
    (L + "recomp.cpp", "init", None, "H-pre-guest", PRE, "osMemSize/boot words written before game_thread runs the entrypoint", {}),
    (L + "mods.cpp", "init_mod_code", None, "H-pre-guest", PRE, "mod section load + relocation at startup", {}),
    (L + O, "read_patch_data", None, "H-pre-guest", PRE, "patch section load at startup", {}),
    # --- RSP / RDP device semantics on host threads ----------------------------------------------------------------------------
    ("librecomp/rsp.hpp", "dma_dmem_to_rdram", None, "H-canon", TASK + "/" + GFX,
     "RSP SP_WR DMA: the device writing RDRAM is the hardware semantics. Audio tasks run before their sp_complete; gfx "
     "(LLE inside send_dl, after the early sp_complete) writes the RDP ring / F5 output, see RING", {}),
    ("librecomp/rsp.hpp", "+", None, "H-canon", TASK + "/" + GFX, "s6713 fast-DMA word path of dma_dmem_to_rdram", {}),
    (ST, "fullSync", r"copyNativeToRAM", "H-canon", GFX,
     "RT64 colour/depth framebuffer write-back = the RDP's own framebuffer stores; runs inside send_dl before dp_complete "
     "(events.cpp: send_dl then dp_complete), i.e. before the guest is told the RDP finished", {"verify": r"rs64_wbw_pre\(RDRAM"}),
    (ST, "fullSync", r"ROGUESQ_RI_CLEAR|s_riclr|storageAddress\], 0", "H-instrument-only", GFX, "s6249 ROGUESQ_RI_CLEAR discriminator",
     {"envoff": "ROGUESQ_RI_CLEAR"}),
    (ST, "fullSync", r"colorFb->addressStart\], 0", "H-instrument-only", GFX, "s6246 ROGUESQ_WB_CLEAR discriminator",
     {"envoff": "ROGUESQ_WB_CLEAR"}),
    (B, "rsp_dpc_submit_impl", r"g_s4272_shadow|wm_live", "H-canon", GFX, "s4286 wrap restore / undo. " + RING,
     {"verify": r"ROGUESQ_S7532_UNDO_CHK"}),
    (B, "rsp_dpc_submit_impl", r"MEM_B\(\d, sm\)", "H-instrument-only", GFX,
     "synth FULL_SYNC scratch at 0x7FFF80 (top of RDRAM), ROGUESQ_FS_PIPE_INJECT only", {"envoff": "ROGUESQ_FS_PIPE_INJECT"}),
    (B, "rsp_dpc_submit_impl", r"\(off \+ 7\) \^ 3", "H-instrument-only", GFX, "ROGUESQ_PRIM_ALPHA_FF poke", {"envoff": "ROGUESQ_PRIM_ALPHA_FF"}),
    (B, "rsp_dpc_submit_impl", r"submit_lo \+ [456]", "H-instrument-only", GFX, "ROGUESQ_PRIM_FF poke", {"envoff": "ROGUESQ_PRIM_FF"}),
    (B, "rs64_spike_scan", None, "H-canon", GFX, "CULL_SPIKE (default on) / DD_MELT / G5B kill-sheet rewrite ring commands. " + RING, {}),
    (B, "rs64_region_scan", None, "H-canon", GFX, "ASPECT region shift rewrites ring commands. " + RING, {}),
    (B, "rs64_rw_cmd", None, "H-canon", GFX, "ASPECT rect-wrap rewrites ring commands. " + RING, {}),
    (B, "rs64_g1d_pause_dim", None, "H-canon", GFX, "ASPECT pause-dim widening rewrites ring commands. " + RING, {}),
    (B, "rs64_g1d_title_clear", r"memcpy", "H-canon", GFX, "ASPECT scissor widening in the ring. " + RING, {}),
    (B, "rs64_g1d_title_clear", r"memset", "H-canon", GFX,
     "clears a wide (>512) 16-bit colour image the DL is about to draw (once per cimg, <=4): an RDP-owned framebuffer written "
     "before the RDP fills it, inside send_dl before dp_complete", {"verify": r"if \(seen \|\| s_n >= 4\) continue;"}),
    (B, "rs64_m4_dma_probe", None, "not-guest", GFX, "b[] is a local 16-byte array (alias false positive)", {"verify": r"uint8_t b\[16\];"}),
    (B, "<file>", r"struct Rs64BfGuard|uint8_t b\[8\]", "not-guest", "-", "struct member initialisers (alias false positive)", {}),
    (MN, "factor5_gfx_runner", None, "not-guest", "-", "b[] is a local 16-byte array (alias false positive)", {"verify": r"uint8_t b\[16\];"}),
    ("src/rsp/s7521_ucode_watch.cpp", "rs64_s7521_task", None, "H-instrument-only", TASK, "s7521 IMEM/ucode control flip (restored)",
     {"envoff": "ROGUESQ_S7521_UCODEWATCH"}),
    ("src/rsp/s7521_ucode_watch.cpp", "rs64_s7521_imem", None, "H-instrument-only", TASK, "s7521 IMEM DMA control flip (restored)",
     {"envoff": "ROGUESQ_S7521_UCODEWATCH"}),
    # --- host-thread levers / diagnostics while the guest runs -----------------------------------------------------------------
    (EV, "apply", r"__atomic_(compare_exchange|store)_n\(lb", "H-latent-FIXED", GFX,
     "s7533 FPS60 clamp: was `if (b == 2) b = 1;` on the Gfx thread while the guest runs (RMW lost-store race); now a byte CAS, "
     "plant control ROGUESQ_S7533_FZ_CHK", {"verify": r"__atomic_compare_exchange_n\(lb, &expect, \(uint8_t\)1"}),
    (EV, "apply", r"rdram\[LIM \^ 3\]", "H-instrument-only", GFX, "s6255 ROGUESQ_G1E_LIMIT window lever", {"envoff": "ROGUESQ_G1E_LIMIT"}),
    (EV, "apply", r"orig_r|orig_l|io\[i\]", "H-instrument-only", GFX,
     "s6018 G1c ROGUESQ_DD_RADIUS/LOD/IMUL levers (unconditional per-VI override, not RMW); ROGUESQ_DRAW_DISTANCE does not set them",
     {"envoff": "ROGUESQ_DD_RADIUS"}),
    (MN, "rs64_s6848_force_ovl", None, "H-instrument-only", GT, "ROGUESQ_S6848_FORCE_OVL", {"envoff": "ROGUESQ_S6848_FORCE_OVL"}),
    (MN, "start_level_poller", None, "H-harness-lever", POLL,
     "ROGUESQ_FORCE_SEL / FORCE_MISSION poller thread: unconditional override toward a forced value (a lost guest store is the "
     "lever's purpose); soak routing only, never in the owner recipe", {"envoff": "ROGUESQ_FORCE_SEL"}),
    (MN, "start_state_poller", None, "H-instrument-only", POLL, "ROGUESQ_FORCE_EMPTY_POOL_SENTINEL experiment",
     {"envoff": "ROGUESQ_FORCE_EMPTY_POOL_SENTINEL"}),
    (MN, "get_n64_input", None, "H-instrument-only", "input", "ROGUESQ_POSE_REF pose lock", {"envoff": "ROGUESQ_POSE_REF"}),
    (RC, "?", r"RDRAM\[addr \^ 3\] = [05]", "H-instrument-only", GFX, "ROGUESQ_FORCE_BUFFER_PROGRESS slot driver (RMW, diag)",
     {"envoff": "ROGUESQ_FORCE_BUFFER_PROGRESS"}),
    (RC, "?", r"a - 0x80000000u\)\) = v", "H-instrument-only", GFX, "s6750 ROGUESQ_DEBUG_WRITE one-shot", {"envoff": "ROGUESQ_DEBUG_WRITE"}),
]


def classify(path, fn, raw, rules, ln):
    line = raw.split("\n")[ln - 1]
    rule = next((r for r in rules if path.endswith(r[0]) and r[1] == fn and (r[2] is None or re.search(r[2], line))), None)
    if not rule:
        return "UNCLASSIFIED", "?", "no rule for %s" % fn
    err = fw.run_checks(path, raw, rule[6], fw.BINARY)
    return ("FAIL-check", rule[4], err) if err else (rule[3], rule[4], rule[5])


def census(files, rules=None):
    rules = RULES if rules is None else rules
    rows, fails = [], 0
    for p in files:
        r = sites(p)
        if not r:
            continue
        ss, raw = r
        for ln, kind, dst, fn in ss:
            cls, thr, why = classify(p, fn, raw, rules, ln)
            fails += cls in ("UNCLASSIFIED", "FAIL-check", "H-latent-fix")
            rows.append((p, ln, kind, dst, fn, cls, thr, why))
    return rows, fails


def main():
    if "--controls" in sys.argv:
        sys.exit(controls())
    rows, fails = census(fw.files_under(ROOTS))
    from collections import Counter
    for r in rows:
        print("%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s" % (r[0].replace("lib/N64ModernRuntime/", "").replace("lib/rt64/src/", "rt64/"),
              r[1], r[2], r[3][:28], r[4][:30], r[5], r[6], r[7][:90] if "--why" in sys.argv else ""))
    print("summary: sites=%d %s fails=%d" % (len(rows), dict(sorted(Counter(r[5] for r in rows).items())), fails))
    sys.exit(1 if fails else 0)


def controls():
    res = []
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "fixture_fz.cpp")
        open(p, "w").write("static void gfx_hook(uint8_t* rdram) { rdram[0x1234 ^ 3] = 7; }\n"
                           "static void alias(uint8_t* rdram) { uint32_t* w = (uint32_t*)(rdram + 0x40); w[2] = 9; }\n"
                           "static void local(uint8_t* rdram) { uint8_t b[4]; b[0] = rdram[3]; }\n"
                           "static void ms(uint8_t* rdram) { memset(rdram + 0x100, 0, 16); }\n")
        rows, fails = census([p])
        by = {}
        for r in rows: by.setdefault(r[4], []).append(r[5])
        res.append(("planted gfx-thread index store -> UNCLASSIFIED", by.get("gfx_hook") == ["UNCLASSIFIED"], rows))
        res.append(("alias store through local pointer -> caught", by.get("alias") == ["UNCLASSIFIED"], rows))
        res.append(("memset into guest -> caught", by.get("ms") == ["UNCLASSIFIED"], rows))
        res.append(("store into host local array -> not a site", "local" not in by, rows))
        # mutation: put the pre-s7533 RMW clamp back into a copy of events.cpp -> the FPS60 row must lose its FIXED rule
        src = "lib/N64ModernRuntime/ultramodern/src/events.cpp"
        mut = os.path.join(d, "ultramodern", "src", "events.cpp"); os.makedirs(os.path.dirname(mut))
        txt = open(src, errors="replace").read()
        a = txt.index("    if (fps60) {\n        static const bool chk"); b = txt.index("    static const char* le = std::getenv(\"ROGUESQ_G1E_LIMIT\")")
        txt2 = txt[:a] + "    if (fps60 && rdram[0x128EAF ^ 3] == 2) rdram[0x128EAF ^ 3] = 1;\n" + txt[b:]
        open(mut, "w").write(txt2)
        rows, fails = census([mut])
        bad = [r for r in rows if r[4] == "apply" and "128EAF" in open(mut).read().split("\n")[r[1] - 1]]
        res.append(("mutation: RMW clamp restored -> UNCLASSIFIED", bool(bad) and all(r[5] == "UNCLASSIFIED" for r in bad), bad[:2]))
    rows, fails = census(fw.files_under(ROOTS), rules=[])
    res.append(("coverage: rule-less census sees >=100 UNCLASSIFIED", fails >= 100, "fails=%d" % fails))
    rows, fails = census(fw.files_under(ROOTS))
    res.append(("live census 0 fails", fails == 0, [r for r in rows if r[5] in ("UNCLASSIFIED", "FAIL-check")][:4]))
    ok = True
    for name, good, detail in res:
        print("control %-52s %s %s" % (name, "PASS" if good else "FAIL", "" if good else str(detail)[:300]))
        ok &= bool(good)
    print("controls: %d/%d PASS" % (sum(1 for r in res if r[1]), len(res)))
    return 0 if ok else 1


if __name__ == "__main__":
    main()
