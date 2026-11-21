#!/usr/bin/env python3
"""s7615 class DQ: deferred guest reads through host queues and host threads.

A host queue (moodycamel / std::deque / queue / list ...) whose ELEMENT carries a guest address or a host view of guest memory,
or a host thread whose entry captures one, lets the consumer read guest memory LATER than the producer's call. On hardware the
read happens at the producer's call, or the guest protocol forbids touching the object until a completion message. Safe only when
the element carries a value copy (copy), the pointer is only a lookup key (key), the guest protocol keeps the object stable until
the consumer is done (protocol, with the contract and witness named), the queue/thread runs only under an env gate (gated), or it
is host-owned (host) / dead.

Sources (must agree on the queue set (file, name)):
  regex  tools/s7615_dq_scan.py  (queue declarations, producer calls, thread creations with one-hop guest check)
  clang  scratch/s7614/ast.json  (tools/s7614_hm_ast.py: static VarDecls + every repo record's FieldDecls; queue-typed ones,
         moodycamel internals / LightweightSemaphore excluded)
Auto rows: a queue whose element is host-only (std::chrono time point, std::string, arithmetic) -> host; a thread whose entry
body and its one-hop same-file callees carry no guest token and produce into no census queue -> host.
Per queue row: every producer call of that queue must match the row's allowed-argument set (a new producer, or a producer that
now passes a pointer, is OPEN). Per gated/protocol row: proof regexes over the raw file text must all match.
--controls: (1) planted static std::deque<uint32_t> with a MEM_W consumer -> unclassified OPEN; (2) drop a queue row -> OPEN;
 (3) planted std::deque<std::chrono::steady_clock::time_point> -> auto host; (4) drop a queue from the AST census -> disagreement;
 (5) planted `events_context.sp_task_queue.enqueue(TO_PTR(OSTask, t))` -> producer contract OPEN; (6) planted
 std::thread([rdram]{ MEM_W(...) }) -> unclassified thread OPEN; (7) env literal removed from a gated row's file -> proof OPEN;
 (8) witness: a planted stack-like varying VI mq fails W.
--witness LOG (tools/s7615_dq_witness.sh, ROGUESQ_RECV_TRACE=1): [hostpost] rows = distinct (mq, source) external-message
 producers. W: >=1 row (instrument fired) incl. the VI queue 0x80114388; each of Sp/Si/Ai/Vi/Dp carries exactly ONE mq (the
 registered event queue, static lifetime: events_context.X.mq set by osSetEventMesg / osViSetEvent); every mq lies in KSEG0 RAM.
Exit 0 only if 0 open, 0 stale rows, sources agree, controls pass."""
import importlib.util, json, os, re, sys, tempfile, copy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import importlib.util as _ilu
_acs = _ilu.spec_from_file_location("ast_cache", os.path.join(ROOT, "tools/ast_cache.py")); ast_cache = _ilu.module_from_spec(_acs); _acs.loader.exec_module(ast_cache)
_sp = importlib.util.spec_from_file_location("dq_scan", os.path.join(ROOT, "tools/s7615_dq_scan.py"))
dq = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(dq)
AST_JSON = os.path.join(ROOT, "scratch/s7614/ast.json")
U = "lib/N64ModernRuntime/ultramodern/src/"
L = "lib/N64ModernRuntime/librecomp/"

# ---- queue rows: (basename, name) -> (class, allowed producer args (regex fullmatch on normalised arg), proofs [(file, regex)], note)
Q = {}
def qrow(base, name, cls, args, proofs, note):
    Q[(base, name)] = dict(cls=cls, args=args, proofs=proofs, note=note)

qrow("events.cpp", "action_queue", "copy", [r"ScreenUpdateAction\{ events_context\.vi\.regs, events_context\.vi\.get_cur_state\(\)->framebuffer, \}",
     r"UpdateConfigAction\{\}", r"SpTaskAction\{ \*task \}"],
     [(U + "events.cpp", r"struct SpTaskAction \{\s*OSTask task;\s*\};"),
      (U + "events.cpp", r"struct ScreenUpdateAction \{\s*ultramodern::renderer::ViRegs regs;\s*PTR\(void\) framebuffer;\s*\};")],
     "OSTask and VI regs by VALUE; the DL behind task.data_ptr is read later by the gfx path = RSP-input protocol (s7535 GA / "
     "s7536 SP_LATE), ScreenUpdate.framebuffer is read at present = VI scanout (s7542 18(c) late-writeback readers)")
qrow("events.cpp", "sp_task_queue", "protocol", [r"task", r"nullptr"],
     [(U + "events.cpp", r"OSTask\* task = TO_PTR\(OSTask, task_\);")],
     "audio OSTask* submit->consume: s7614 Q1 + witness W 236/236 unchanged, one outstanding")
qrow("events.cpp", "deleted_threads", "dead", [], [], "declared only (s7614 U1)")
qrow("mesgqueue.cpp", "g_audio_sp_deliveries", "key", [r"\{queued\.mq, queued\.mesg, queued\.audio\}"],
     [(U + "mesgqueue.cpp", r"if \(it->mq != mq \|\| it->msg != msg\) continue;"),
      (U + "mesgqueue.cpp", r"if \(!queued\.audio\.active\) return;")],
     "(mq, msg) are lookup keys compared in log_audio_sp_receive; the payload is a host AudioRouteMessage copy; log-route only")
qrow("mesgqueue.cpp", "external_messages", "protocol", [r"queued", r"\{mq, msg, jam, requeue_if_blocked\}", r"cur_mesg", r"to_send"],
     [(U + "mesgqueue.cpp", r"QueuedMessage queued\{mq, msg, jam, requeue_enabled\[static_cast<int>\(src\)\]\};"),
      (U + "mesgqueue.cpp", r"const bool sent = do_send\(PASS_RDRAM to_send\.mq, to_send\.mesg, to_send\.jam, false\);")],
     "msg by VALUE; mq is the guest's registered event queue (osSetEventMesg/osViSetEvent, static) or a PI completion queue the "
     "requester blocks on; delivery at the next game-thread dequeue = an interrupt taken at the next exception point. Witness W")
qrow("main.cpp", "g_rumble_edges", "host", [r"\{rs64_rumble_now_us\(\), on\}"],
     [("src/main/main.cpp", r"static std::deque<std::pair<int64_t, bool>> g_rumble_edges;")],
     "s7655 G6a: (host microseconds, motor on/off) pairs, no guest address; capped 512 in set_rumble, aged out in rs64_rumble_duty")
qrow("threads.cpp", "deleted_threads", "host", [r"cur_context"], [], "UltraThreadContext* host objects")
qrow("timer.cpp", "action_queue", "protocol", [r"CheckTimerAction\{ &pr, lo, hi \}", r"a", r"AddTimerAction\{ t_ \}", r"RemoveTimerAction\{ t_ \}"],
     [(U + "timer.cpp", r"static bool s7397_fix\(\) \{ static const bool f = s7397_env\(\"ROGUESQ_S7397_TIMERFIX\", true\);"),
      (U + "timer.cpp", r"a\.carry = true; a\.timestamp = .*a\.interval = interval; a\.mq = mq; a\.msg = msg;")],
     "AddTimer carries the fields by VALUE (s7397 default on); the OSTimer* key is owned by the timer list until it fires, as in "
     "libultra; osStopTimer (the one deferred removal) is unlinked in the game (contract T1); s7397 found no game timer armed")
qrow("mods.hpp", "mod_configuration_thread_queue", "host", [r"ModConfigQueueEnd\(\)", r"ModConfigQueueSave\(\)",
     r"ModConfigQueueSaveMod\{ mod\.manifest\.mod_id \}"], [], "mod ids / save requests (host strings)")
qrow("rt64_render_context.cpp", "s_menu_fifo", "key", [r"msg, id"],
     [("src/main/rt64_render_context.cpp", r"if \(s_menu_fifo\.empty\(\) \|\| s_menu_fifo\.front\(\)\.first != msg\) return v0;"),
      ("src/main/rt64_render_context.cpp", r"const uint32_t id = \*reinterpret_cast<const uint32_t\*>\(rdram \+ \(msg \+ 0x14 - 0x80000000u\)\);")],
     "message pointer is a lookup key; the request id is copied at SEND time (s6781 menu worker FIFO)")
qrow("rt64_render_context.cpp", "q", "gated", [r"std::move\(pend\)", r"std::move\(j\)"],
     [("src/main/rt64_render_context.cpp", r"int rs64_rdp_async_on = \[\] \{ const char \*e = std::getenv\(\"ROGUESQ_RDP_ASYNC\"\)"),
      ("src/main/rt64_render_context.cpp", r"if \(!rs64_rdp_async_on \|\| !in_task \|\| !app->core\.RDRAM\) \{ drain\(\); return false; \}"),
      ("src/main/rt64_render_context.cpp", r"struct Job \{ uint32_t lo = 0, hi = 0; std::vector<uint8_t> w;")],
     "ROGUESQ_RDP_ASYNC (default off); command words COPIED into Job.w at submit; textures read later = real-RDP timing")
qrow("upstream_compat.cpp", "s_s7325_ord", "host", [r"s_s7325_freed\.emplace\(ptr, f\)", r"s_s7325_freed\.emplace\(it->first, f\)"], [],
     "host multimap iterators (s7325 allocation-history diagnostic)")
qrow("s7523_slow_rdp.cpp", "q", "gated", [r"r"], [("src/rsp/s7523_slow_rdp.cpp", r"ROGUESQ_S7523_SLOWRDP")], "slow-RDP model, log-only, default off")
qrow("s7523_slow_rdp.cpp", "sg", "gated", [r"\{lo, hi, r\.off\}"], [("src/rsp/s7523_slow_rdp.cpp", r"ROGUESQ_S7523_SLOWRDP")], "slow-RDP model, log-only")

# ---- vector-as-queue rows (appended AND erased in one file): (basename, name) -> (class, proofs, note)
V = {}
def vrow(base, name, cls, proofs, note): V[(base, name)] = dict(cls=cls, proofs=proofs, note=note)
vrow("overlays.cpp", "loaded_sections", "copy", [(L + "src/overlays.cpp", r"loaded_sections\.emplace_back\(ram, section_table_index\);")],
     "overlay load records by VALUE (ram addr, section index; s7610 OV census)")
vrow("extensions.cpp", "pending_events", "dead", [], "osExQueueDisplaylistEvent pending list; 0 generated callers (contract X1)")
for n in ("spans", "g_plants"):
    vrow("main.cpp", n, "gated", [("src/main/main.cpp", r"static const bool on = envon\(\"ROGUESQ_S7551_GK\"\);")], "s7551 writeback-span audit")
for n in ("s_s7545_thr", "s_s7545_tc"):
    vrow("upstream_compat.cpp", n, "gated", [("src/main/upstream_compat.cpp", r"getenv\(\"ROGUESQ_S7545_THRWATCH\"\)")], "s7545 thread watch")
for n in ("reset_reuse_last", "reset_route_last", "frame_last"):
    vrow("dpc_bridge.cpp", n, "gated", [("src/rsp/dpc_bridge.cpp", r"getenv\(\"ROGUESQ_LOG_E9_PROVENANCE\"\)"),
                                        ("src/rsp/dpc_bridge.cpp", r"if \(!log_e9_provenance\(\)\) return;")], "e9 provenance ring (log)")
vrow("s7096_fwd_cover.cpp", "pend", "gated", [("src/rsp/s7096_fwd_cover.cpp", r"getenv\(\"ROGUESQ_S7096_FWD\"\)")], "s7096 forward-cover audit")
for n in ("snap", "tch"):
    vrow("s7523_slow_rdp.cpp", n, "gated", [("src/rsp/s7523_slow_rdp.cpp", r"ROGUESQ_S7523_SLOWRDP")], "slow-RDP model bytes")

HOST_ELEM = re.compile(r"^(?:std::chrono::[\w:<>, ]+|clk::time_point|std::string|double|float|int|bool|char)$")
def elem(t):
    i = t.find("<"); return t[i + 1:t.rfind(">")].strip() if i >= 0 else ""

# ---- thread rows: (basename, key, caps, ordinal) -> (class, proofs, note). sys = runtime system thread whose guest traffic is a queue row.
T = {}
def trow(base, key, caps, cls, proofs, note, n=0):
    T[(base, key, caps, n)] = dict(cls=cls, proofs=proofs, note=note)
M = "src/main/main.cpp"; UC = "src/main/upstream_compat.cpp"
def env(f, var, then=None):
    return (f, r"getenv\(\"%s\"\)%s" % (var, (r"[\s\S]{0,1500}?" + then) if then else ""))
trow("main.cpp", "s4578_poll", "(rdram)", "gated", [env(M, "ROGUESQ_LOG_S4578"), (M, r"if \(s4578_on\(\) && rdram && len\) \{\s*rs64_s4578_start\(rdram\);")], "s4578 page watch")
trow("main.cpp", "[=]", "[=]", "gated", [(M, r"if \(!\(lg && lg\[0\] && lg\[0\] != '0'\) && !\(fm && fm\[0\]\) && !\(fs && fs\[0\]\)\) return;")], "ROGUESQ_LOG_LEVEL / FORCE_MISSION / FORCE_SEL harness")
for i, (var, fn) in enumerate([("ROGUESQ_LOG_STATE", "start_state_poller"), ("ROGUESQ_LOG_M5_EXACT_ROUTE", "start_m5_exact_route_poller"),
                               ("ROGUESQ_LOG_B50", "start_b50_poller"), ("ROGUESQ_LOG_PHASE", "start_phase_poller"),
                               ("ROGUESQ_LOG_M5_VOICE_SLOTS", "start_m5_voice_slot_poller"), ("ROGUESQ_LOG_FS_SLOT", "start_fs_slot_poller"),
                               ("ROGUESQ_LOG_M5_HOST_WRITE_FAULT", "start_m5_host_write_fault_watch"),
                               ("ROGUESQ_LOG_M5_TASK_WRITE_FAULT", "start_m5_task_write_fault_watch"),
                               ("ROGUESQ_LOG_VTX_WRITE_FAULT", "start_vtx_write_fault_watch"), ("ROGUESQ_LOG_FL_ZERO_WATCH", "start_fl_zero_poller")]):
    if fn in ("start_state_poller", "start_b50_poller", "start_phase_poller", "start_m5_voice_slot_poller", "start_m5_exact_route_poller"):
        pr = [(M, r"static void %s\(\) \{[\s\S]{0,300}?getenv\(\"%s\"\)" % (fn, var))]
    else:
        pr = [env(M, var, fn + r"\(\);")]
    T[("main.cpp", "[]", "[]", i)] = dict(cls="gated", proofs=pr, note=fn)
T[("main.cpp", "[]", "[]", 10)] = dict(cls="gated", proofs=[env(M, "ROGUESQ_LOG_FL_ZERO_WATCH", r"start_fl_zero_poller\(\);")], note="fl-zero re-arm spinner (inside start_fl_zero_poller)")
T[("main.cpp", "[]", "[]", 11)] = dict(cls="gated", proofs=[(M, r"if \(flag_enabled \|\| addr_enabled\) \{[\s\S]{0,300}?start_memwp_watchdog\(\);")], note="ROGUESQ_HWBP watchdog")
trow("main.cpp", "[rdp,mode]", "[rdp,mode]", "gated", [env(M, "ROGUESQ_GODMODE3", r"if \(s_god3\) \{")], "GODMODE3 cheat (opt-in)")
trow("rt64_render_context.cpp", "worker", "()", "gated", [("src/main/rt64_render_context.cpp", r"if \(!rs64_rdp_async_on \|\| !in_task")], "RDP_ASYNC worker (queue row q)")
trow("upstream_compat.cpp", "[rdram]", "[rdram]", "gated", [env(UC, "ROGUESQ_LOG_S4222", r"\}\(\); return on; \}"), env(UC, "ROGUESQ_LOG_S4299P")], "s4299 poll", 0)
trow("upstream_compat.cpp", "[rdram]", "[rdram]", "gated", [env(UC, "ROGUESQ_LOG_S4526", r"std::thread\(\[rdram\]")], "s4526 poll", 1)
trow("upstream_compat.cpp", "[rdram]", "[rdram]", "gated", [(UC, r"if \(!rdram \|\| !rs64_s4222_on\(\) \|\| started\.exchange\(true\)\) return;")], "s4231 allocator-list poll", 2)
trow("upstream_compat.cpp", "[rdram]", "[rdram]", "gated", [env(UC, "ROGUESQ_S4913", r"if \(!on\) return;")], "s4913 swap poll", 3)
trow("s7331_reset_writer.cpp", "poll", "()", "gated", [("src/rsp/s7331_reset_writer.cpp", r"getenv\(\"ROGUESQ_S7331_RESETW\"\)")], "s7331 audit")
trow("recomp.cpp", "[]", "[]", "sys", [], "game thread (recomp::start)")
trow("pi.cpp", "saving_thread_func", "(PASS_RDRAM)", "sys", [], "save writer: copies the host save buffer (s7595 SV census)")
trow("events.cpp", "gfx_thread_func", "(rdram,&gfx_thread_ready,window_handle)", "sys", [], "consumes action_queue (row)")
trow("events.cpp", "task_thread_func", "(rdram,&task_thread_ready)", "sys", [], "consumes sp_task_queue (row)")
trow("events.cpp", "vi_thread_func", "()", "sys", [], "VI: enqueues ScreenUpdate + external messages (rows)")
trow("events.cpp", "[]", "[]", "gated", [(U + "events.cpp", r"if \(s4450_ai_event_drain\(\) != 0\) \{")], "AI event drain thread -> external_messages", 0)
trow("events.cpp", "[]", "[]", "gated", [(U + "events.cpp", r"\} else if \(s4440_ai_event_hz\(\) != 0\) \{")], "AI event hz thread -> external_messages", 1)
trow("threads.cpp", "_thread_func", "(PASS_RDRAMt_,entrypoint,arg,t->context)", "sys", [], "guest thread itself (osCreateThread; s7606 HC)")
trow("timer.cpp", "timer_thread", "(PASS_RDRAM1)", "sys", [], "consumes timer action_queue (row)")
trow("upstream_compat.cpp", "[]", "[]", "gated", [env(UC, "ROGUESQ_S7545_THRWATCH")], "s7545 thread watch summary (hop rs64_s7475_store)", 0)
trow("upstream_compat.cpp", "[]", "[]", "gated", [env(UC, "ROGUESQ_S7777_DANGLE"), (UC, r"struct S7777Arm \{ S7777Arm\(\) \{\s*if \(!s7777_on\(\)\) return;[\s\S]{0,600}?std::thread\(\[\] \{ for \(;;\) \{ std::this_thread::sleep_for\(std::chrono::milliseconds\(250\)\); s7777_sweep\(\);")], "s7777 dangling-global sweep thread (ctor returns before it unless ROGUESQ_S7777_DANGLE)", 2)

def raw(f, over):
    return over.get(f) if f in over else open(os.path.join(ROOT, f), errors="replace").read()

def ast_queues(ast, drop=()):
    QT = re.compile(r"moodycamel::\w*Queue<|ConcurrentQueue<|std::(?:__1::)?(?:deque|queue|priority_queue|list|stack|forward_list)<")
    out = set()
    for v in ast["vars"]:
        d = v["type"].strip("'").split("':'")[-1]
        if QT.search(d) and "LightweightSemaphore" not in d: out.add((v["file"], v["name"]))
    for r in ast["records"]:
        if "thirdparty" in r["file"]: continue
        for n, t in r["fields"]:
            d = t.strip("'").split("':'")[-1]
            if QT.search(d) and "LightweightSemaphore" not in d: out.add((r["file"], n))
    return out - set(drop)

def ast_vecq(ast, drop=()):
    VTA = re.compile(r"std::(?:__1::)?vector<")
    cache = {}; out = set()
    def txt(f):
        if f not in cache:
            p = os.path.join(ROOT, f)
            cache[f] = dq.hm.clean(open(p, errors="replace").read()) if os.path.exists(p) else ""
        return cache[f]
    cands = [(v["file"], v["name"], v["type"]) for v in ast["vars"]] + \
            [(r["file"], n, t) for r in ast["records"] if "thirdparty" not in r["file"] for n, t in r["fields"]]
    for f, n, t in cands:
        d = t.strip("'").split("':'")[-1]
        if VTA.match(d) and not f.startswith("RF/") and dq.vec_used_as_queue(txt(f), n): out.add((f, n))
    return out - set(drop)

def norm(s): return re.sub(r"\s+", " ", s).strip()

def census(scan, ast, qrows=None, trows=None, over=None, ast_drop=(), vrows=None):
    qrows = Q if qrows is None else qrows; trows = T if trows is None else trows; over = over or {}
    vrows = V if vrows is None else vrows
    opn, rep = [], []
    rv = {(v["file"], v["name"]) for v in scan["vecq"]}; av = ast_vecq(ast, ast_drop)
    for x in sorted(rv ^ av):
        opn.append("DISAGREE vecq %s:%s only in %s" % (x[0], x[1], "regex" if x in rv else "clang"))
    vused = set()
    for v in scan["vecq"]:
        k = (os.path.basename(v["file"]), v["name"])
        if k in vrows:
            c = vrows[k]["cls"]; vused.add(k)
            for f, rx in vrows[k]["proofs"]:
                if not re.search(rx, raw(f, over)): opn.append("PROOF vecq %s:%s /%s/ missing" % (k[0], k[1], rx[:60]))
        elif HOST_ELEM.match(elem(v["type"])):
            c = "host(auto)"
        else:
            c = "OPEN"; opn.append("UNCLASSIFIED vecq %s:%d %s %s" % (v["file"], v["line"], v["name"], v["type"]))
        rep.append("V %-11s %s:%d %s  <%s>" % (c, v["file"], v["line"], v["name"], elem(v["type"])[:60]))
    for k in sorted(set(vrows) - vused): opn.append("STALE vecq row %s:%s" % k)
    rq = {(q["file"], q["name"]) for q in scan["queues"] if q["storage"] != "local"}
    aq = ast_queues(ast, ast_drop)
    for x in sorted(rq ^ aq):
        opn.append("DISAGREE queue %s:%s only in %s" % (x[0], x[1], "regex" if x in rq else "clang"))
    used = set(); cls_n = {}
    for q in scan["queues"]:
        k = (os.path.basename(q["file"]), q["name"])
        if q["storage"] == "local":
            c = "fresh"
        elif k in qrows:
            c = qrows[k]["cls"]; used.add(k)
        elif HOST_ELEM.match(elem(q["type"])):
            c = "host(auto)"
        else:
            c = "OPEN"; opn.append("UNCLASSIFIED queue %s:%d %s %s" % (q["file"], q["line"], q["name"], q["type"]))
        cls_n[c] = cls_n.get(c, 0) + 1
        rep.append("Q %-11s %s:%d %s  <%s>" % (c, q["file"], q["line"], q["name"], elem(q["type"])[:60]))
        if k in qrows:
            for f, rx in qrows[k]["proofs"]:
                if not re.search(rx, raw(f, over)): opn.append("PROOF %s:%s /%s/ missing in %s" % (k[0], k[1], rx[:60], f))
    for k in sorted(set(qrows) - used): opn.append("STALE queue row %s:%s" % k)
    # producers: every call of a rowed queue must match an allowed arg (queue looked up by name; owner file or any file)
    byname = {}
    for k in qrows: byname.setdefault(k[1], []).append(k)
    for p in scan["producers"]:
        ks = [k for k in byname.get(p["queue"], []) if k[0] == os.path.basename(p["file"])]
        if not ks and not any(q["name"] == p["queue"] and q["file"] == p["file"] for q in scan["queues"]):
            ks = byname.get(p["queue"], [])  # producer outside the declaring file (header member / extern)
        if not ks: continue
        if len(ks) > 1:
            same = [k for k in ks if k[0] == os.path.basename(p["file"])]
            ks = same or ks
        ok = any(re.fullmatch(a, norm(p["arg"])) for k in ks for a in qrows[k]["args"])
        if not ok: opn.append("PRODUCER %s:%d %s.%s(%s) not in the row's allowed set" % (p["file"], p["line"], p["queue"], p["op"], p["arg"][:70]))
    # threads
    seen = {}; tused = set(); tcls = {}
    qnames = {q["name"] for q in scan["queues"]}
    for th in scan["threads"]:
        b = os.path.basename(th["file"]); kk = (b, th["key"], th["caps"]); n = seen.get(kk, 0); seen[kk] = n + 1
        k = kk + (n,)
        if k in trows:
            c = trows[k]["cls"]; tused.add(k)
            for f, rx in trows[k]["proofs"]:
                if not re.search(rx, raw(f, over)): opn.append("PROOF thread %s /%s/ missing in %s" % (str(k), rx[:60], f))
        elif not th["guest"] and not th["hop"]:
            c = "host(auto)"
        else:
            c = "OPEN"; opn.append("UNCLASSIFIED thread %s:%d key=%s caps=%s guest=%d hop=%s" % (th["file"], th["line"], th["key"], th["caps"], th["guest"], th["hop"]))
        tcls[c] = tcls.get(c, 0) + 1
        rep.append("T %-11s %s:%d %s %s" % (c, th["file"], th["line"], th["key"], th["caps"]))
    for k in sorted(set(trows) - tused, key=str): opn.append("STALE thread row %s" % (k,))
    # T1: osStopTimer unlinked in the game (the only deferred removal); generated code calls osSetTimer_recomp only
    gen = dq.sn.GEN; stop = 0
    for f in os.listdir(gen):
        if f.endswith(".c") and "osStopTimer_recomp(" in open(os.path.join(gen, f), errors="replace").read(): stop += 1
    if stop: opn.append("T1 osStopTimer_recomp called from %d generated files" % stop)
    # X1: osExQueueDisplaylistEvent (the only producer of extensions pending_events) has no generated caller
    xq = sum(1 for f in os.listdir(gen) if f.endswith(".c") and "osExQueueDisplaylistEvent_recomp(" in open(os.path.join(gen, f), errors="replace").read())
    if xq: opn.append("X1 osExQueueDisplaylistEvent_recomp called from %d generated files" % xq)
    return opn, rep, cls_n, tcls, len(rq), len(aq), len(rv), len(av)

def witness(path_or_lines):
    lines = path_or_lines if isinstance(path_or_lines, list) else open(path_or_lines, errors="replace").read().split("\n")
    rows = [(int(m.group(1), 16), int(m.group(2))) for m in (re.match(r"^\[hostpost\] mq=0x([0-9A-F]+) extra=(-?\d+)", l) for l in lines) if m]
    names = ["Timer", "Sp", "Si", "Ai", "Vi", "Pi", "Dp"]
    by = {}
    for mq, s in rows: by.setdefault(s, set()).add(mq)
    bad = []
    if not rows: bad.append("instrument silent")
    if 0x80114388 not in by.get(4, set()): bad.append("VI queue 0x80114388 absent")
    for s in (1, 2, 3, 4, 6):
        if len(by.get(s, ())) > 1: bad.append("%s carries %d mqs" % (names[s], len(by[s])))
    for mq, s in rows:
        if not (0x80000000 <= mq < 0x80800000): bad.append("mq %08X outside KSEG0 RAM" % mq)
    summ = " ".join("%s=%s" % (names[s] if 0 <= s < 7 else s, ",".join("%08X" % m for m in sorted(v))) for s, v in sorted(by.items()))
    return bad, summ, len(rows)

def controls(scan, ast):
    res = []
    td = tempfile.mkdtemp(prefix="s7615ctl_")
    def scan_with(src):
        p = os.path.join(td, "s7615_ctl_%d.cpp" % len(res)); open(p, "w").write(src)
        r = dq.scan(extra=[p]); return r
    # (1)
    r = scan_with("static std::deque<uint32_t> s_ctl_addrs;\nvoid c1(uint8_t* rdram){ uint32_t a = s_ctl_addrs.front(); MEM_W(0, a) = 1; }\n")
    o = census(r, ast)[0]; res.append(("planted deque<uint32_t> -> OPEN", any("UNCLASSIFIED queue" in x and "s_ctl_addrs" in x for x in o)))
    # (2)
    q2 = dict(Q); q2.pop(("mesgqueue.cpp", "external_messages"))
    o = census(scan, ast, qrows=q2)[0]; res.append(("drop external_messages row -> OPEN", any("external_messages" in x for x in o)))
    # (3)
    r = scan_with("static std::deque<std::chrono::steady_clock::time_point> s_ctl_tp;\n")
    _, rep, *_ = census(r, ast); res.append(("planted time_point deque -> host(auto)", any("host(auto)" in x and "s_ctl_tp" in x for x in rep)))
    # (4)
    o = census(scan, ast, ast_drop=[("lib/N64ModernRuntime/ultramodern/src/mesgqueue.cpp", "external_messages")])[0]
    res.append(("drop a queue from the clang census -> DISAGREE", any(x.startswith("DISAGREE") and "external_messages" in x for x in o)))
    # (5)
    r = scan_with("void c5(uint8_t* rdram, uint32_t t){ events_context.sp_task_queue.enqueue(TO_PTR(OSTask, t)); }\n")
    o = census(r, ast)[0]; res.append(("planted sp_task_queue producer -> PRODUCER OPEN", any(x.startswith("PRODUCER") and "sp_task_queue" in x for x in o)))
    # (6)
    r = scan_with("void c6(uint8_t* rdram){ std::thread([rdram]{ MEM_W(0, 0x80100000) = 1; }).detach(); }\n")
    o = census(r, ast)[0]; res.append(("planted guest thread -> UNCLASSIFIED", any("UNCLASSIFIED thread" in x and "s7615_ctl" in x for x in o)))
    # (7)
    t = open(os.path.join(ROOT, M)).read().replace('getenv("ROGUESQ_LOG_FS_SLOT")', 'getenv("ROGUESQ_X")')
    o = census(scan, ast, over={M: t})[0]; res.append(("gate literal removed -> PROOF OPEN", any(x.startswith("PROOF thread") and "FS_SLOT" in x for x in o)))
    # (9) planted static vector<uint32_t> used as a queue -> unclassified vecq (and clang cannot see it: regex-only DISAGREE too)
    r = scan_with("static std::vector<uint32_t> s_ctl_pend;\nvoid c9(uint32_t a){ s_ctl_pend.push_back(a); }\nvoid c9b(){ s_ctl_pend.erase(s_ctl_pend.begin()); }\n")
    o = census(r, ast)[0]; res.append(("planted vector-as-queue -> UNCLASSIFIED vecq", any("UNCLASSIFIED vecq" in x and "s_ctl_pend" in x for x in o)))
    # (10) drop pending_events from the clang census -> DISAGREE vecq
    o = census(scan, ast, ast_drop=[("lib/N64ModernRuntime/ultramodern/src/extensions.cpp", "pending_events")])[0]
    res.append(("drop a vecq from the clang census -> DISAGREE", any(x.startswith("DISAGREE vecq") and "pending_events" in x for x in o)))
    # (8)
    bad, _, _ = witness(["[hostpost] mq=0x80114388 extra=4 n=1 tid=1", "[hostpost] mq=0x803FFE20 extra=4 n=2 tid=1"])
    res.append(("witness: second VI mq -> W fails", bool(bad)))
    return res

def main():
    a = sys.argv[1:]
    ast_cache.ensure(AST_JSON, "tools/s7614_hm_ast.py")  # s7655
    scan = dq.scan(); ast = json.load(open(AST_JSON))
    opn, rep, qc, tc, nr, na, nvr, nva = census(scan, ast)
    if "-v" in a:
        print("\n".join(rep))
    print("queues regex=%d clang=%d  queue classes %s" % (nr, na, qc))
    print("vector-as-queue regex=%d clang=%d" % (nvr, nva))
    print("threads %d  classes %s  producers %d" % (len(scan["threads"]), tc, len(scan["producers"])))
    ok = not opn
    for x in opn: print("OPEN", x)
    if "--witness" in a:
        bad, summ, n = witness(a[a.index("--witness") + 1])
        print("witness rows=%d %s -> %s" % (n, summ, "PASS" if not bad else "FAIL " + "; ".join(bad)))
        ok = ok and not bad
    if "--controls" in a:
        cs = controls(scan, ast)
        for d, p in cs: print("control %-55s %s" % (d, "PASS" if p else "FAIL"))
        print("controls %d/%d" % (sum(p for _, p in cs), len(cs)))
        ok = ok and all(p for _, p in cs)
    print("open=%d -> %s" % (len(opn), "CLOSED" if ok else "OPEN"))
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
