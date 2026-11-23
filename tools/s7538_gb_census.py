#!/usr/bin/env python3
"""s7538 class GB census: every COMPLETION SIGNAL the runtime raises to the guest (a message posted to a guest event /
I/O queue that tells the game "device X is done"), and for each one, whether that device still READS or WRITES guest
RDRAM after the signal while the guest runs.  Class GA (s7535) was one such site: the gfx sp_complete is sent before
the F5 LLE fetched its inputs.  GB asks whether a sibling exists.

Signal idioms (comments stripped): enqueue_external_message_src(.., EventMessageSource::X), enqueue_external_message(..),
sp_complete(), dp_complete(), send_si_message(), dispatch_displaylist_events(..).  Definitions are skipped.
Each site is looked up by (file suffix, enclosing function, line range|None) in RULES -> one or more MODE rows
(a site whose post-signal behaviour depends on an env mode, e.g. dp_complete under RDP_ASYNC / NODRAIN, gets one row per
mode).  Classes:
  H-ordered      every device access to guest RAM for this completion finishes before the signal (synchronous copy /
                 drain / run on the same thread before the post)
  H-copy         the device copied the guest bytes into host memory before the signal; later guest stores are harmless
  H-canon        device access continues after the signal, but hardware does the same (e.g. VI scans the displayed
                 framebuffer through the whole field after the retrace interrupt)
  H-dead         the guest never reaches this signal (libRecompiledFuncs.a does not import the entry point)
  H-nomem        the signal is not tied to any guest-RAM transfer (timer)
  not-device     a guest-originated osSendMesg / osJamMesg (the guest's own store order)
  H-instrument-only  env-gated self-test, default off
  H-latent-FIXED(opt-in)  an H-latent-fix whose fix exists behind an owner opt-in (class GA)
  H-latent-fix   device RAM access after the signal with the guest running -> OPEN (needs a same-run A/B)
  UNCLASSIFIED   -> FAIL
Checks per mode row (all must pass, or the row FAILs): ("before", rx) rx occurs in the enclosing function body before the
site; ("body", rx) anywhere in the body; ("file", path, rx) in another file; ("fnbody", path, fn, rx) in a named function of
another file; ("nm_absent", sym) / ("nm_present", sym) against `nm -u build/libRecompiledFuncs.a`.

  python3 tools/s7538_gb_census.py              # rows + summary; exit 1 on FAIL / UNCLASSIFIED / open H-latent-fix
  python3 tools/s7538_gb_census.py --controls   # planted fixture, mutation controls, nm control, coverage control
"""
import os, re, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s7530_fw_census as fw
import s7533_fz_census as fz

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOTS = ["lib/N64ModernRuntime/librecomp/src", "lib/N64ModernRuntime/ultramodern/src", "src/main", "src/rsp"]
LIB = "build/libRecompiledFuncs.a"
SIG = re.compile(r'\b(enqueue_external_message_src|enqueue_external_message|sp_complete|dp_complete|send_si_message|'
                 r'dispatch_displaylist_events)\s*\(')
EV, PI, FL, EXT, INP, MQ, TM = ("ultramodern/src/events.cpp", "librecomp/src/pi.cpp", "librecomp/src/flash.cpp",
                                "ultramodern/src/extensions.cpp", "ultramodern/src/input.cpp", "ultramodern/src/mesgqueue.cpp",
                                "ultramodern/src/timer.cpp")
RC, MN, AI, AU, UC = ("src/main/rt64_render_context.cpp", "src/main/main.cpp", "lib/N64ModernRuntime/librecomp/src/ai.cpp",
                      "lib/N64ModernRuntime/ultramodern/src/audio.cpp", "src/main/upstream_compat.cpp")
RT64ST = "lib/rt64/src/hle/rt64_state.cpp"

AI_COPY = ("AI completion: the guest's osAiSetNextBuffer_recomp (guest thread) calls queue_audio_buffer -> queue_samples, "
           "which byte-swaps every sample into a host std::vector before SDL_QueueAudio; the AI event thread only posts "
           "when the host queue drains, so no guest PCM byte is read after any AI message")
AI_CHECKS = [("fnbody", AI, "osAiSetNextBuffer_recomp", r"ultramodern::queue_audio_buffer\(rdram"),
             ("fnbody", AU, "queue_audio_buffer", r"audio_callbacks\.queue_samples\("),
             ("fnbody", MN, "queue_samples", r"std::vector<int16_t> native_samples\(num_samples\)"),
             ("nm_present", "osAiSetNextBuffer_recomp")]

# (file suffix, function, (lo, hi) | None, [(mode, class, why, checks)])
RULES = [
    # --- SP ------------------------------------------------------------------------------------------------------------------
    (EV, "sp_complete", None, [("def", "H-ordered", "the sp_complete() body: ordering is decided at its call sites", [])]),
    (EV, "task_thread_func", None, [("audio", "H-ordered",
     "audio / non-gfx RSP task: run_task runs the whole ucode (every DMA in and out) synchronously on the SP task thread, "
     "then sp_complete", [("before", r"ultramodern::rsp::run_task\(PASS_RDRAM task\)")])]),
    (EV, "gfx_thread_func", r"if \(!s7535_late\)\s*$", [("early", "H-latent-FIXED(opt-in)",
     "class GA (s7535-s7537): default early sp_complete before send_dl lets the guest overwrite the in-flight F5 inputs; "
     "fix = ROGUESQ_SP_LATE=1 (owner opt-in, docs/OWNER-OPT-INS.md)",
     [("before", r"rs64_sp_late_task\(\)"), ("file", "docs/OWNER-OPT-INS.md", r"ROGUESQ_SP_LATE=1")])]),
    (EV, "gfx_thread_func", r"\bif \(s7535_late\)\s*$", [("late", "H-ordered",
     "ROGUESQ_SP_LATE=1: sp_complete after send_dl returned; the F5 LLE (every RSP DMA) ran inside send_dl",
     [("before", r"renderer_context->send_dl\(&task_action->task\)")])]),
    (EXT, "dispatch_displaylist_events", None, [("dl-event", "H-dead",
     "osExQueueDisplaylistEvent (recomp extension) is not imported by the game: no event is ever pending",
     [("nm_absent", "osExQueueDisplaylistEvent_recomp")])]),
    (EXT, "on_displaylist_submitted", None, [("dl-event", "H-dead", "see dispatch_displaylist_events",
     [("nm_absent", "osExQueueDisplaylistEvent_recomp")])]),
    (EXT, "on_displaylist_parsed", None, [("dl-event", "H-dead", "see dispatch_displaylist_events",
     [("nm_absent", "osExQueueDisplaylistEvent_recomp")])]),
    (EXT, "on_displaylist_completed", None, [("dl-event", "H-dead", "see dispatch_displaylist_events",
     [("nm_absent", "osExQueueDisplaylistEvent_recomp")])]),
    # --- DP ------------------------------------------------------------------------------------------------------------------
    (EV, "dp_complete", None, [("def", "H-ordered", "the dp_complete() body: ordering is decided at its call site", [])]),
    (EV, "gfx_thread_func", r"renderer_end = std::chrono", [
        ("sync", "H-ordered",
         "default (RDP_ASYNC off): RT64 interprets every RDP range inside send_dl on the Gfx thread (texture loads read "
         "core.RDRAM there, fb copies to RDRAM happen there), dp_complete follows send_dl",
         [("before", r"renderer_context->send_dl\(&task_action->task\)"),
          ("file", RC, r"rs64_rdp_async_on = \[\] \{ const char \*e = std::getenv\(\"ROGUESQ_RDP_ASYNC\"\)")]),
        ("async-drain", "H-ordered",
         "ROGUESQ_RDP_ASYNC=1 (NODRAIN off): RdpqScope's destructor (rs64_rdpq_task_exit) drains the worker before send_dl "
         "returns, so every RT64 RDRAM read/write of the task precedes dp_complete",
         [("file", RC, r"struct RdpqScope \{ RdpqScope\(\) \{ ultramodern::rs64_rdpq_task_enter\(\); \} ~RdpqScope\(\) "
                       r"\{ ultramodern::rs64_rdpq_task_exit\(\); \} \} rdpq_scope;"),
          ("fnbody", RC, "rs64_rdpq_task_exit", r"rdpq::drain\(\);")]),
        ("async-nodrain", "H-latent-FIXED(opt-in)",
         "FIXED(opt-in) s7540 by ROGUESQ_RDP_NODRAIN=3 (row async-rwait). MEASURED s7539 = TORN (tools/s7539_gb_score.py: L1/L4/L12 167/297/354 post-signal texture loads read bytes the guest rewrote after dp_complete, 2 KB 4-bit texture re-decoded every frame by swizzleTextureRowsToTmem 0x800249B4/E4 via parseImageFile; controls planted==caught, older-snapshot diffs, witness ~0.7 MB/window). ROGUESQ_RDP_ASYNC=1 ROGUESQ_RDP_NODRAIN=1 (listed in docs/OWNER-OPT-INS.md): rs64_rdpq_task_exit only "
         "flush_pend()s, so send_dl returns and dp_complete is posted while the worker still has the task's tail job(s) "
         "queued. Those jobs read texture bytes from core.RDRAM (only the command words are copied) and RT64 writes "
         "framebuffer copies back to RDRAM, after the guest was told the RDP is done. Hardware posts DP full-sync only "
         "after the last RDP memory access. Lever for the same-run A/B: ROGUESQ_RDP_NODRAIN=2 (alternates per async window)",
         [("fnbody", RC, "rs64_rdpq_task_exit", r"if \(in_task == 0 && task_nodrain\) \{ if \(task_rwait\) reads_wait\(\); else flush_pend\(\);(?: if \(gb::on\) \{[^}]*\})? return; \}"),
          ("file", "docs/OWNER-OPT-INS.md", r"ROGUESQ_RDP_NODRAIN=3")]),
        ("async-rwait", "H-ordered",
         "s7540 ROGUESQ_RDP_NODRAIN=3: task exit waits (reads_wait) until every job of the task is popped and the running one has "
         "called rs64_s7540_reads_done() after State::fullSync's last fullSyncFramebufferPairTiles, so every texture-source RDRAM read "
         "precedes dp_complete (measured s7540 NODRAIN=4 same-run: as=4 post-signal loads 0). Still after the post: the final "
         "renderAndSynchronize (fb read-in via fbStorage.store, writebacks) and hashTracking: s7541 measured them (rs64_s7541_span, "
         "tools/s7541_gb_score.py, NODRAIN=4 + S7541_HOLD=1, L4/L12/L1): 0 read-in / clobber / hash spans differ from the guest's view at "
         "the post, controls planted==caught; writebacks themselves land late (~84% change bytes after the post), no guest reader "
         "(s6938 WBW, s7391; NODRAIN=3 WBW rerun queued s7541_wbw_rwait)",
         [("fnbody", RC, "reads_wait", r"cv_idle\.wait\(lk, \[\] \{ return q\.empty\(\) && \(!busy \|\| cur_rd\); \}\);"),
          ("file", "lib/rt64/src/hle/rt64_state.cpp", r"fullSyncFramebufferPairTiles\(workload, fbPair, loadOpCursor, rdpTileCursor\);\s*\}\s*\}\s*rs64_s7540_reads_done\(\);"),
          ("file", "lib/rt64/src/hle/rt64_framebuffer_manager.cpp", r"rs64_s7541_span\(4, RDRAM"),
          ("file", "docs/OWNER-OPT-INS.md", r"ROGUESQ_RDP_NODRAIN=3")])]),
    # --- VI / AI -------------------------------------------------------------------------------------------------------------
    (EV, "vi_thread_func", r"\[vi-enq\]", [("vi", "H-canon",
     "VI retrace message: the device reads the displayed framebuffer after it, as hardware VI scans the origin through the "
     "whole field; RT64's RDRAM-sourced present copies it into present.storage on the Gfx thread (H-copy of a scan-out the "
     "hardware also performs after the interrupt); origin/registers are host copies made in osViSwapBuffer",
     [("file", RT64ST, r"memcpy\(present\.storage\.data\(\), &RDRAM\[screenFbAddress\], screenFbBytes\)"),
      ("nm_present", "osViSwapBuffer_recomp")])]),
    # s7864: ROGUESQ_AI_VI_CLOCK=1/2 (det harness, default off) posts AI completions from the VI thread on a fixed clock;
    # the PCM bytes were already copied at osAiSetNextBuffer (AI_COPY), so the post order vs guest memory is the same H-copy.
    (EV, "vi_thread_func", r"s7864_ai_vi_clock\(\)\) \{", [("ai-vi-clock", "H-copy", AI_COPY + " (s7864 opt-in VI-clocked post)",
     AI_CHECKS + [("file", "lib/N64ModernRuntime/ultramodern/src/events.cpp", r"getenv\(\"ROGUESQ_AI_VI_CLOCK\"\); bool v = e && \*e && \*e != '0'")])]),
    (EV, "vi_thread_func", r"!ai_event_external\(\)\) \{\s*(?:ultramodern::)?$", [("ai-vi", "H-copy", AI_COPY, AI_CHECKS)]),
    (EV, "init_events", r"\[s7197-ai-stall\]", [("ai-drain", "H-copy", AI_COPY, AI_CHECKS)]),
    (EV, "init_events", r"set_native_thread_name\(\"AI Hz\"\)", [("ai-hz", "H-copy", AI_COPY, AI_CHECKS)]),
    # --- SI ------------------------------------------------------------------------------------------------------------------
    (EV, "send_si_message", None, [("def", "H-ordered", "send_si_message body: ordering at its callers", [])]),
    (INP, "osContStartQuery", None, [("si", "H-ordered",
     "SI query done: no guest RAM transfer at all; the status block is written later by the guest-thread osContGetQuery",
     [("nm_present", "osContStartQuery_recomp")])]),
    (INP, "osContStartReadData", None, [("si", "H-ordered",
     "SI read done: the host pad state is polled BEFORE the message; the guest pad block is written only by the "
     "guest-thread osContGetReadData, so no device store lands after the signal",
     [("before", r"input_callbacks\.poll_input\(\)"), ("nm_present", "osContGetReadData_recomp")])]),
    # --- PI ------------------------------------------------------------------------------------------------------------------
    (PI, "s7196_unknown_region_complete", None, [("pi-unk", "H-ordered",
     "unknown-region PI completion: no transfer is performed", [])]),
    (PI, "do_dma", r"\[s5061-pi-dma-guard\]", [("pi-guard", "H-ordered", "s5061 guard skip: completion without any transfer", [])]),
    (PI, "do_dma", r"recomp::do_rom_read\(", [("pi-rom", "H-ordered",
     "ROM->RDRAM PI DMA: do_rom_read copies synchronously on the guest thread (osPiStartDma_recomp -> do_dma) before "
     "the completion message", [("before", r"recomp::do_rom_read\(rdram, rdram_address, physical_addr, size\)"),
                                 ("nm_present", "osPiStartDma_recomp")])]),
    (PI, "do_dma", r"\bsave_read\(", [("pi-sram-rd", "H-ordered",
     "SRAM read: save_read synchronous before the message (unreachable: save type Eep4k -> message_box exit)",
     [("before", r"save_read\(rdram, rdram_address")])]),
    (PI, "do_dma", r"\bsave_write\(", [("pi-sram-wr", "H-copy",
     "SRAM write: save_write memcpy's the guest bytes into save_context.save_buffer under its mutex before the message; "
     "the file writer thread reads only that host buffer",
     [("before", r"save_write\(rdram, rdram_address"), ("fnbody", "lib/N64ModernRuntime/" + PI, "save_write_ptr", r"memcpy\(&save_context\.save_buffer")])]),
    (FL, "osFlashWriteBuffer_recomp", None, [("flash", "H-dead", "flash not imported (save type Eep4k)",
     [("nm_absent", "osFlashWriteBuffer_recomp")])]),
    (FL, "osFlashReadArray_recomp", None, [("flash", "H-dead", "flash not imported (save type Eep4k)",
     [("nm_absent", "osFlashReadArray_recomp")])]),
    # --- non-device ----------------------------------------------------------------------------------------------------------
    (TM, "timer_thread", None, [("timer", "H-nomem", "osSetTimer expiry message: no guest-RAM transfer", [])]),
    (MQ, "osSendMesg", None, [("guest", "not-device", "guest-originated message", [])]),
    (MQ, "osJamMesg", None, [("guest", "not-device", "guest-originated message", [])]),
    (UC, "control", r"getenv\(\"ROGUESQ_S7392_CTL\"\)", [("ctl", "H-instrument-only", "s7392 message-queue self-test (ROGUESQ_S7392_CTL, default off)",
     [("body", r"ROGUESQ_S7392_CTL")])]),
    (UC, "control", r"getenv\(\"ROGUESQ_S7399_CTL\"\)", [("ctl", "H-instrument-only", "s7399 event-post self-test (ROGUESQ_S7399_CTL, default off)",
     [("body", r"ROGUESQ_S7399_CTL")])]),
]
OK = {"H-ordered", "H-copy", "H-canon", "H-dead", "H-nomem", "not-device", "H-instrument-only", "H-latent-FIXED(opt-in)"}
_nm = {}


def nm_imports(lib=LIB):
    if lib not in _nm:
        try:
            out = subprocess.run(["nm", "-u", os.path.join(REPO, lib)], capture_output=True, text=True).stdout
        except OSError:
            out = ""
        _nm[lib] = {l.strip().lstrip("_") for l in out.splitlines() if l.strip()}
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


def sites(path, over=None):
    over = over or {}
    t = read(path, over)
    spans = fz.func_spans(t)
    out = []
    last_end = {}   # s7653: per enclosing function, end of the previous signal -> the anchor segment of the next one
    for m in SIG.finditer(t):
        close = fz.split_args(t, m.end())[1] if hasattr(fz, "split_args") else m.end()
        if re.match(r'\s*(?:const\s*)?\{', t[close + 1:close + 20]) or re.match(r'\s*\{', t[close:close + 5]):
            continue                                   # a definition, not a call
        if re.search(r'\bvoid\s+(?:[\w:]+::)?$', t[max(0, m.start() - 40):m.start()]):
            continue
        ln = t.count("\n", 0, m.start()) + 1
        enc = [s for s in spans if s[0] <= m.start() <= s[1]]
        fn = enc[-1] if enc else (0, len(t), "<file>")
        src = re.search(r'EventMessageSource::(\w+)', t[m.start():m.start() + 200])
        seg = t[max(fn[0], last_end.get(fn[0], fn[0])):m.start()]
        last_end[fn[0]] = m.end()
        out.append(dict(path=path, line=ln, kind=m.group(1), fn=fn[2], body=t[fn[0]:fn[1] + 1], off=m.start() - fn[0], seg=seg,
                        src=src.group(1) if src and m.group(1).endswith("_src") else ""))
    return out


def run_checks(site, checks, over, lib):
    fails = []
    for c in checks:
        k = c[0]
        if k == "before":
            ok = re.search(c[1], site["body"][:site["off"]]) is not None
        elif k == "body":
            ok = re.search(c[1], site["body"]) is not None
        elif k == "file":
            ok = re.search(c[2], read(c[1], over)) is not None
        elif k == "fnbody":
            b = fn_body(read(c[1], over), c[2])
            ok = b is not None and re.search(c[3], b) is not None
        elif k == "nm_absent":
            ok = bool(nm_imports(lib)) and c[1] not in nm_imports(lib)
        elif k == "nm_present":
            ok = c[1] in nm_imports(lib)
        else:
            ok = False
        if not ok:
            fails.append(":".join(str(x) for x in c)[:90])
    return fails


def rule_hits(site, rule):
    # s7653: rng is None (whole function) or a TEXT ANCHOR regex searched in the site's segment (enclosing-function text since the
    # previous signal in that function, comments stripped). Absolute line ranges drifted silently (s7538 pi.cpp rows, +20 lines).
    f, fn, rng, _ = rule
    if not (site["path"].endswith(f) and site["fn"] == fn):
        return False
    if rng is None:
        return True
    if isinstance(rng, tuple) and rng and rng[0] == "near":   # ("near", rx, n): rx in the n body chars before the site
        return re.search(rng[1], site["body"][max(0, site["off"] - rng[2]):site["off"]]) is not None
    if isinstance(rng, tuple) and rng and rng[0] == "line":   # ("line", rx): rx on the site's own source line
        b, o = site["body"], site["off"]
        a = b.rfind("\n", 0, o) + 1; e = b.find("\n", o)
        return re.search(rng[1], b[a:e if e >= 0 else len(b)]) is not None
    if isinstance(rng, tuple):   # legacy line range: drifts silently; s7653 removed all of them from s7538/s7542
        return rng[0] <= site["line"] <= rng[1]
    return re.search(rng, site.get("seg", site["body"]), re.M) is not None


def classify(site, rules):
    for r in rules:
        if rule_hits(site, r):
            return r[3]
    return None


def files_under(roots):
    out = []
    for r in roots:
        for dp, _, fs in os.walk(os.path.join(REPO, r)):
            for f in sorted(fs):
                if f.endswith((".cpp", ".c", ".hpp", ".h")):
                    out.append(os.path.relpath(os.path.join(dp, f), REPO))
    return sorted(out)


def census(files, rules=RULES, over=None, lib=LIB, quiet=False):
    over = over or {}
    rows, stat = [], {"sites": 0, "unclassified": 0, "fail": 0, "open": 0}
    for p in files:
        for s in sites(p, over):
            stat["sites"] += 1
            modes = classify(s, rules)
            if modes is None:
                stat["unclassified"] += 1
                rows.append((s, "-", "UNCLASSIFIED", "no rule", []))
                continue
            for mode, cls, why, checks in modes:
                fails = run_checks(s, checks, over, lib)
                if fails:
                    stat["fail"] += 1
                if cls == "H-latent-fix":
                    stat["open"] += 1
                rows.append((s, mode, cls if not fails else "FAIL-check", why, fails))
    # s7653: an anchored rule whose file was scanned but which matched no site is STALE -> FAIL (never re-scope silently)
    scanned = {p for p in files}
    allsites = [x for x in (r[0] for r in rows) if x.get("path")]
    for r in rules:
        anchored = isinstance(r[2], str) or (isinstance(r[2], tuple) and r[2] and r[2][0] in ("near", "line"))
        if not anchored or not any(p.endswith(r[0]) for p in scanned):
            continue
        if not any(rule_hits(x, r) for x in allsites):
            stat["fail"] += 1
            rows.append((dict(path=r[0], line=0, kind="-", src="", fn=r[1]), r[3][0][0], "FAIL-check", "STALE anchor " + str(r[2]), ["stale anchor"]))
    if not quiet:
        for s, mode, cls, why, fails in rows:
            print("%s:%d %s %s [%s] %s -> %s%s" % (s["path"], s["line"], s["kind"], s["src"], s["fn"], mode, cls,
                  ("  FAILED " + "; ".join(fails)) if fails else ""))
            if cls in ("H-latent-fix", "FAIL-check", "UNCLASSIFIED"):
                print("      " + why[:400])
        from collections import Counter
        print("summary: sites=%d rows=%d unclassified=%d fail=%d open_latent=%d  %s" % (
            stat["sites"], len(rows), stat["unclassified"], stat["fail"], stat["open"],
            dict(Counter(r[2] for r in rows))))
    return rows, stat


def controls():
    files = files_under(ROOTS)
    ok = 0
    tests = []
    # 1 planted fixture: an unknown device completion -> UNCLASSIFIED; a planted definition is skipped
    with tempfile.TemporaryDirectory() as d:
        fx = os.path.join(d, "fixture.cpp")
        open(fx, "w").write("void ultramodern::send_si_message() {\n x();\n}\n"
                            "void fake_dev_thread() {\n  // enqueue_external_message_src(mq, 0, false, X) in a comment\n"
                            "  ultramodern::enqueue_external_message_src(mq, m, false, ultramodern::EventMessageSource::Pi);\n}\n")
        rel = os.path.relpath(fx, REPO)
        _, st = census([rel], quiet=True)
        tests.append(("planted unknown signal -> 1 site, UNCLASSIFIED (definition + comment skipped)",
                      st["sites"] == 1 and st["unclassified"] == 1))
        # 2 mutation: the NODRAIN drain restored in a copy -> the open row's check FAILs (instrument reads the code)
        src = open(os.path.join(REPO, RC), errors="replace").read()
        m2 = os.path.join(d, "rc_drain.cpp")
        open(m2, "w").write(re.sub(r"if \(in_task == 0 && task_nodrain\) \{ if \(task_rwait\) reads_wait\(\); else flush_pend\(\);(?: if \(gb::on\) \{[^}]*\})? return; \}", "/* drained */", src))
        rows, _ = census(files, over={RC: m2}, quiet=True)
        tests.append(("mutation: NODRAIN early-return removed -> async-nodrain row FAIL-check",
                      any(r[1] == "async-nodrain" and r[2] == "FAIL-check" for r in rows)))
        # 3 mutation: drain() removed from task_exit -> async-drain H-ordered FAILs
        m3 = os.path.join(d, "rc_nodrainall.cpp")
        open(m3, "w").write(src.replace("rdpq::drain(); if (rdpq::task_async)", "if (rdpq::task_async)"))
        rows, _ = census(files, over={RC: m3}, quiet=True)
        tests.append(("mutation: drain() removed -> async-drain row FAIL-check",
                      any(r[1] == "async-drain" and r[2] == "FAIL-check" for r in rows)))
        # 3b mutation (s7540): reads_wait without the reads-done predicate -> async-rwait H-ordered FAILs
        m3b = os.path.join(d, "rc_norwait.cpp")
        open(m3b, "w").write(src.replace("return q.empty() && (!busy || cur_rd); });", "return true; });"))
        rows, _ = census(files, over={RC: m3b}, quiet=True)
        tests.append(("mutation: reads-done predicate removed -> async-rwait row FAIL-check",
                      any(r[1] == "async-rwait" and r[2] == "FAIL-check" for r in rows)))
        # 4 mutation: dp_complete moved before send_dl in a copy of events.cpp -> the dp rows' 'before' check FAILs
        evp = "lib/N64ModernRuntime/" + EV
        ev = open(os.path.join(REPO, evp), errors="replace").read()
        m4 = os.path.join(d, "ev_dpfirst.cpp")
        ev2 = ev.replace("renderer_context->send_dl(&task_action->task); g1e::tasks++;", "RENDER_LATER(); g1e::tasks++;")
        open(m4, "w").write(ev2)
        rows, _ = census([evp], over={evp: m4}, quiet=True)
        tests.append(("mutation: send_dl call removed before dp/late-sp sites -> sync + late rows FAIL-check",
                      sum(1 for r in rows if r[1] in ("sync", "late") and r[2] == "FAIL-check") == 2))
    # 5 nm control: a lib that imports the DL-event extension -> H-dead rows FAIL
    imp = nm_imports(LIB)
    _nm["fake"] = imp | {"osExQueueDisplaylistEvent_recomp"}
    rows, _ = census(files, lib="fake", quiet=True)
    tests.append(("nm control: DL-event extension imported -> 4 dl-event rows FAIL-check",
                  sum(1 for r in rows if r[1] == "dl-event" and r[2] == "FAIL-check") == 4 and len(imp) > 100))
    # 6 coverage: no rules -> every site UNCLASSIFIED; live census has >= 25 sites
    _, st0 = census(files, rules=[], quiet=True)
    _, st1 = census(files, quiet=True)
    tests.append(("coverage: rule-less census -> all %d sites UNCLASSIFIED" % st0["sites"],
                  st0["unclassified"] == st0["sites"] >= 25 and st1["sites"] == st0["sites"]))
    # 6b stale-anchor control (s7653): a rule whose anchor matches no site in a scanned file must FAIL
    _, st2 = census(files, rules=RULES + [(PI, "do_dma", r"NO_SUCH_ANCHOR_s7653", [("x", "H-ordered", "planted", [])])], quiet=True)
    tests.append(("stale anchor control: planted unmatched anchor -> exactly 1 extra FAIL", st2["fail"] == st1["fail"] + 1))
    # 7 live census: 0 unclassified, 0 failed checks
    tests.append(("live census: 0 unclassified, 0 FAIL-check", st1["unclassified"] == 0 and st1["fail"] == 0))
    for name, passed in tests:
        ok += passed
        print("%s  %s" % ("PASS" if passed else "FAIL", name))
    print("controls %d/%d" % (ok, len(tests)))
    return 0 if ok == len(tests) else 1


def main():
    if "--controls" in sys.argv:
        sys.exit(controls())
    _, st = census(files_under(ROOTS))
    sys.exit(1 if (st["unclassified"] or st["fail"] or st["open"]) else 0)


if __name__ == "__main__":
    main()
