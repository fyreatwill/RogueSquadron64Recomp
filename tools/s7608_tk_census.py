#!/usr/bin/env python3
"""s7608 class TK: host state keyed by guest-thread identity that can name the WRONG thread.

Two ways a thread key goes wrong on this port: (a) a destroyed thread's entry is read by the next incarnation that re-uses
its OSId / OSThread struct (s7607: workers are destroyed and re-created with the same id), and (b) OSIds are NOT unique among
live threads (witness below: 8 distinct threads carry id 0, 2 carry id 9), so "entry[my id]" can be another live thread's.
Enumerates every line in src/ + librecomp + ultramodern that derives or stores a thread key (rogue_current_thread_id,
rs64_guest_tid, OSThread->id compares/indices, [..tid..] tables, g1b_slot, g_live_ctx/thr_live_*, pthread_self,
GetCurrentThreadId, this_thread::get_id). printf-only lines are auto 'print'. Every other line must match a SITE_ROWS entry:
  diag:<FLAG>  the code runs only with that env flag (default off) or only feeds a diagnostic dump;
  host         keyed by the HOST thread (pthread_self, thread_local): each guest incarnation is a new std::thread (C1);
  reset        the entry is cleared on exit/unwind (RAII destructor or S7590 slot guard, C3/C5);
  ptrlive      g_live_ctx keyed by UltraThreadContext*: erased after join and BEFORE delete, so no ABA (C4);
  accessor     the id getter / its declaration;
  naming       id used only to name a thread / build a print token;
  incarn       s7394fix incarnation key (the s7608 fix): thread_local token, unique per incarnation (C2).
Contract checks (each failing one is OPEN): C1 osCreateThread spawns `context->host_thread = std::thread{` per call;
C2 every s7394fix::holder store/compare uses s7394fix::me(), me() keeps a thread_local token, release stores -1;
C3 ~Rs64WaitScope clears pending; C4 thread_cleaner_func calls thr_live_remove before `delete to_delete`;
C5 the S7590 guard clears its g1b port slot on exit; C6 thread_self is thread_local.
Any line combining s7394fix::holder with rogue_current_thread_id is BAD (the pre-s7608 OSId key).
--controls: (1) plant a tid-indexed default-path table with no reset -> OPEN; (2) drop a row -> OPEN; (3) remove
thr_live_remove from the cleaner -> OPEN (C4); (4) plant the old OSId compare on s7394fix::holder -> OPEN.
--witness: [thr-create-id] rows in scratch/agent/loop.log.pre-s5016: distinct (entry, OSThread) per OSId (must show a repeated
id, else the collision premise is unproven). Exit 0 only if 0 open, 0 stale rows, 4/4 controls, witness PASS when asked.
"""
import os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = "lib/N64ModernRuntime"
DIRS = ["src", L + "/librecomp/src", L + "/librecomp/include", L + "/ultramodern/src", L + "/ultramodern/include"]
SKIP = re.compile(r"/(tests?|third_party|thirdparty)/")
UC = "src/main/upstream_compat.cpp"
THR = L + "/ultramodern/src/threads.cpp"
MQ = L + "/ultramodern/src/mesgqueue.cpp"
EV = L + "/ultramodern/src/events.cpp"
SCH = L + "/ultramodern/src/scheduling.cpp"
LOG = "scratch/agent/loop.log.pre-s5016"
PAT = re.compile(r"rogue_current_thread_id\(|rs64_guest_tid\(|->id *(==|!=|&|\*|;|\))|\[[a-z0-9_]*tid[a-z0-9_]* *(&|\])|"
                 r"g1b_slot|thr_live_(add|remove|contains)\(|g_live_ctx\b|pthread_self\(\)|GetCurrentThreadId\(|"
                 r"this_thread::get_id\(\)")

# (file suffix, line substring, kind, reason). One row may cover several lines (same idiom in one function).
SITE_ROWS = [
    ("src/rsp/s7535_ga_chk.cpp", "pthread_self()", "host", "s7535 GA checker: gfx host thread identity (not a guest thread)"),
    (UC, "g_cine_tid.store(GetCurrentThreadId()", "diag:_WIN32", "cine watchdog, inside #ifdef _WIN32 (not built on macOS)"),
    (UC, "tid, last_err, GetCurrentThreadId());", "diag:_WIN32", "cine watchdog print, #ifdef _WIN32"),
    (UC, "sendtgt_note(mq_addr, GetCurrentThreadId(),", "diag:ROGUESQ_RECV_TRACE", "sendtgt_note returns unless recv-trace/stack"),
    (UC, "GetCurrentThreadId(),", "diag:_WIN32", "Win32 stack-capture print"),
    (UC, "rogue_current_thread_id(rdram), valid, r, orr ?", "naming", "s7393 print continuation line (multi-line fprintf)"),
    (UC, "static uint32_t rs64_guest_tid(uint8_t* rdram) {", "accessor", "recv-trace guest id getter"),
    (UC, "return (uint32_t)TO_PTR(OSThread, t)->id;", "accessor", "rs64_guest_tid body"),
    (UC, "const uint32_t gid = rs64_guest_tid(rdram);", "diag:ROGUESQ_RECV_TRACE", "recv_trace_enter returns unless enabled"),
    (UC, 'extern "C" int rogue_current_thread_id(uint8_t* rdram);', "accessor", "declaration"),
    (UC, "g_s4264_blk[tid & 63]", "diag:ROGUESQ_S4262", "s4264 registry: enter/exit called only when s4264_on"),
    (UC, "const int tid = rogue_current_thread_id(rdram) & 63;", "diag:ROGUESQ_S4262", "s4262_note_send returns unless on"),
    (UC, "e.htid = (uint64_t)(uintptr_t)pthread_self(); e.gtid = rogue_current_thread_id(rdram)", "diag:ROGUESQ_LOG_S4580",
     "s4580 ring, rec() only under s4580::on()"),
    (UC, "tid = rogue_current_thread_id(r);", "reset", "Rs64WaitScope: [stall-dump] table only; ~Rs64WaitScope clears pending "
     "(runs on thread_terminated unwind too, s7607), so a destroyed waiter leaves pending=0 (C3)"),
    (UC, "Rs64WaitEnt& w = g_rs64_waittab[tid & 63];", "reset", "same: written at wait start, cleared by the destructor; read only "
     "by rs64_waittab_dump (diagnostic print)"),
    (UC, "if (rogue_current_thread_id(rdram) != 0) return;", "diag:ROGUESQ_RETRACE_HOLD_TEST", "Rs64RetraceHold test arm, c[0]>0 only"),
    (UC, "close_locked('N', rogue_current_thread_id(rdram)", "diag:ROGUESQ_S7394_BD", "s7394 window census (s7394::on)"),
    (UC, "owner = rogue_current_thread_id(rdram); s_wtids", "diag:ROGUESQ_S7394_BD", "s7394 window census"),
    (UC, "rogue_current_thread_id(rdram) != owner && now() < shadow_until", "diag:ROGUESQ_S7394_BD", "s7394 window census"),
    (UC, "const int tid = rogue_current_thread_id(rdram);", "diag:ROGUESQ_S7394_BD", "s7394 pre/post_recv/post_send (3 lines)"),
    (UC, "if (!tk()) return rogue_current_thread_id(rdram);", "incarn", "s7608 =0 arm (old OSId key) only"),
    (UC, "g_s4913_last_tid.store((int)rogue_current_thread_id(rdram))", "diag:ROGUESQ_S4913", "s4913 after the !on return"),
    (UC, "(int)rogue_current_thread_id(rdram), tag, a, b, slots);", "diag:ROGUESQ_S4913", "s4913 print"),
    (UC, "const uint64_t tid = GetCurrentThreadId();", "diag:ROGUESQ_RECV_TRACE", "host tid only fed to recv_trace_enter/exit"),
    (UC, "s4264_enter(rogue_current_thread_id(rdram) & 63", "diag:ROGUESQ_S4262", "inside if (s4264_on)"),
    (UC, "s4264_exit(rogue_current_thread_id(rdram) & 63)", "diag:ROGUESQ_S4262", "inside if (s4264_on)"),
    ("src/rsp/dpc_bridge.cpp", "pthread_self()", "host", "s7029 bf2 checker: gfx host thread identity, g_bf_check only"),
    (SCH, "g_s4583_t3", "diag:s4583", "s4583_dump bookkeeping (OSThread* of id 3) only feeds the dump print"),
    (MQ, "return (uint64_t)pthread_self();", "host", "rs64_host_tid non-Apple arm (Apple uses pthread_threadid_np)"),
    (MQ, 'extern "C" int rogue_current_thread_id(uint8_t* rdram);', "accessor", "declaration"),
    (MQ, "extern thread_local int g1b_slot;", "host", "g1b slot is thread_local (fresh -1 in every new host thread)"),
    (MQ, "static thread_local int g1b_slot = -1;", "host", "non-Apple fallback, thread_local"),
    (MQ, "osid = g_g1b_thread_osid[g1b_slot]", "diag:ROGUESQ_G1E_TL", "rs64_tl returns unless rs64_tl_on"),
    (MQ, "e.pad = g1b_slot;", "diag:ROGUESQ_G1E_TL", "rs64_tl"),
    (MQ, "g_s4259[", "diag:ROGUESQ_S4259", "inside if (s4259_on()) / s4259_tid>=0 (only set when on)"),
    (MQ, "rogue_current_thread_id(PASS_RDRAM1) & 63;", "diag:ROGUESQ_S4259", "s4259 key, inside if (s4259_on())"),
    (MQ, "s4260::on_result(", "diag:ROGUESQ_S4259", "inside if (s4259_on())"),
    (MQ, "g1b_blk_on() && g1b_slot >= 0", "diag:ROGUESQ_G1B", "g1b blocked-time accounting, slot = this host thread's"),
    (MQ, "g_g1b_blk_since_us[g1b_slot]", "diag:ROGUESQ_G1B", "same block (continuation line)"),
    (MQ, "g_g1b_blk_us[g1b_slot]", "diag:ROGUESQ_G1B", "same block"),
    (MQ, "g_g1b_blk_cum_us[g1b_slot]", "diag:ROGUESQ_G1B", "same block"),
    (MQ, "s4908_on() && flags == OS_MESG_BLOCK", "diag:ROGUESQ_S4908", "guarded by s4908_on()"),
    (MQ, "if (is_vi_mq) { s4908_event(", "diag:ROGUESQ_S4908", "s4908_event returns unless s4908_on()"),
    ("src/main/main.cpp", 'extern "C" int rogue_current_thread_id(uint8_t* rdram);', "accessor", "declaration"),
    ("src/main/main.cpp", "std::hash<std::thread::id>{}(std::this_thread::get_id())", "naming", "host thread token in a print"),
    ("src/main/main.cpp", "rogue_current_thread_id(rdram), g_rs64_last_guest_pc", "naming", "[m5-status-store] print argument"),
    ("src/main/main.cpp", "std::this_thread::get_id())));", "naming", "host thread token in a print"),
    ("src/main/main.cpp", "GetCurrentThreadId();", "diag:_WIN32", "Win32 crash/minidump paths"),
    ("src/main/main.cpp", "switch (t->id) {", "naming", "get_game_thread_name: native thread name only"),
    ("src/main/main.cpp", 'return "[Game] " + std::to_string(t->id);', "naming", "thread name"),
    ("src/main/main.cpp", "thread == pthread_self()", "host", "s7355 altstack per host thread (start/terminate hook)"),
    ("src/main/main.cpp", "pthread_self());", "host", "own stack bounds of the faulting host thread"),
    (THR, "static std::unordered_set<UltraThreadContext*> g_live_ctx;", "ptrlive", "C4"),
    (THR, "thr_live_", "ptrlive", "add in osCreateThread, remove after join and before delete (C4), contains on own/target ctx"),
    (THR, "g_live_ctx.", "ptrlive", "set ops under g_live_ctx_mu"),
    (THR, 'return "Game Thread " + std::to_string(t->id);', "naming", "thread name"),
    (THR, "s7405_n[", "diag:ROGUESQ_S7405_FPSR", "FPSR witness counters (s7405_on)"),
    (THR, "const int id = (int)t->id * 1000 + (int)t->priority;", "diag:ROGUESQ_LOG_S4586", "s4586::on_handoff (enabled())"),
    (THR, "if (t->id == 3) t3_pops++;", "diag:ROGUESQ_LOG_S4586", "s4586 counter"),
    (THR, "rs64_run_tok_g = (int32_t)", "naming", "s6808 run token, read only by an rt64 print (2 lines)"),
    (THR, "sf->id == 3) s4586::on_t3_block", "diag:ROGUESQ_LOG_S4586", "on_t3_block stores the last queue for the s4586 dump"),
    (THR, "thread_local int g1b_slot = -1;", "host", "thread_local"),
    (THR, "const int k = g_g1b_nslots.fetch_add(1);", "reset", "g1b slot allocated per host thread, never re-used (monotonic); "
     "S7590 guard clears the port at exit (C5). Slots > 64 get none: diagnostic undercount only"),
    (THR, "s7405_plant(self->id);", "diag:ROGUESQ_S7405_FPSR", "plant runs only when s7405_on"),
    (THR, "return TO_PTR(OSThread, t)->id;", "accessor", "osGetThreadId (retail semantics)"),
    (THR, 'extern "C" int rogue_current_thread_id(uint8_t* rdram) {', "accessor", "definition"),
    (EV, "pthread_mach_thread_np(pthread_self())", "host", "QoS / time-constraint policy of the calling host thread"),
    (EV, "extern thread_local int g1b_slot;", "host", "thread_local"),
    (EV, "pthread_get_qos_class_np(pthread_self()", "host", "QoS read of the calling host thread"),
    (EV, "g1eg::g_row(g1b_slot >= 0", "diag:ROGUESQ_G1E_G", "inside if (g1eg::f)"),
]


def strip_comments(t):
    t = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), t, flags=re.S)
    return re.sub(r"//[^\n]*", "", t)


def load(over=None):
    files = {}
    for d in DIRS:
        for dp, _, fs in os.walk(os.path.join(ROOT, d)):
            if SKIP.search(dp + "/"):
                continue
            for f in fs:
                if f.endswith((".c", ".cpp", ".h", ".hpp")):
                    rel = os.path.relpath(os.path.join(dp, f), ROOT)
                    try:
                        files[rel] = open(os.path.join(dp, f), errors="replace").read()
                    except OSError:
                        pass
    if over:
        files.update(over)
    return files


def run(over=None, rows=None, verbose=False):
    rows = SITE_ROWS if rows is None else rows
    files = load(over)
    used, opens, kinds = set(), [], {}
    for rel, txt in sorted(files.items()):
        for i, ln in enumerate(strip_comments(txt).split("\n"), 1):
            if not PAT.search(ln):
                continue
            if "s7394fix::holder" in ln and "rogue_current_thread_id" in ln:
                opens.append(f"BAD {rel}:{i}: s7394fix::holder keyed by OSId (ids repeat; use s7394fix::me)")
                continue
            if "printf" in ln:
                kinds["print"] = kinds.get("print", 0) + 1
                continue
            hit = None
            for k, r in enumerate(rows):
                if rel.endswith(r[0]) and r[1] in ln:
                    hit = k
                    break
            if hit is None:
                opens.append(f"UNROWED {rel}:{i}: {ln.strip()[:120]}")
                continue
            used.add(hit)
            kd = rows[hit][2].split(":")[0]
            kinds[kd] = kinds.get(kd, 0) + 1
    stale = [r for k, r in enumerate(rows) if k not in used]
    # contracts
    def body(rel, start, end_pat=r"\n}\n"):
        t = files.get(rel, "")
        a = t.find(start)
        if a < 0:
            return ""
        m = re.search(end_pat, t[a:])
        return t[a:a + (m.end() if m else 4000)]
    thr, uc = files.get(THR, ""), files.get(UC, "")
    oc = body(THR, 'extern "C" void osCreateThread(')
    if "context->host_thread = std::thread{" not in oc:
        opens.append("C1 osCreateThread no longer spawns a new std::thread per call")
    fx = body(UC, "namespace s7394fix {", r"\n}\n")
    if not re.search(r"static thread_local int64_t g", fx) or "int64_t me(uint8_t* rdram)" not in fx:
        opens.append("C2 s7394fix::me() lost its thread_local incarnation token")
    for m in re.finditer(r"s7394fix::holder\.(store|load)\(([^)]*\))?", uc):
        seg = uc[m.start():m.start() + 90]
        if m.group(1) == "store" and "store(-1)" in seg:
            continue
        if "s7394fix::me(rdram)" not in seg:
            opens.append(f"C2 s7394fix::holder use without me(): {seg[:70]!r}")
    if "s7394fix::holder.store(-1)" not in uc:
        opens.append("C2 heap-mutex release no longer clears s7394fix::holder")
    ws = body(UC, "~Rs64WaitScope() {", r"\n    }\n")
    if "w.pending = 0" not in ws:
        opens.append("C3 ~Rs64WaitScope no longer clears pending")
    cl = body(THR, "void thread_cleaner_func() {")
    a, b = cl.find("thr_live_remove(to_delete)"), cl.find("delete to_delete")
    if a < 0 or b < 0 or a > b:
        opens.append("C4 thread_cleaner_func: thr_live_remove missing or after delete (ABA on a re-used context address)")
    if "g_g1b_thread_port[k].compare_exchange_strong(e, 0u)" not in thr:
        opens.append("C5 S7590 guard no longer clears the g1b port slot at thread exit")
    if not re.search(r"thread_local\s+PTR\(OSThread\)\s+thread_self", thr):
        opens.append("C6 thread_self is not thread_local")
    if verbose:
        for o in opens:
            print("  OPEN", o)
        for r in stale:
            print("  STALE", r[0], r[1])
    return {"open": opens, "stale": stale, "kinds": kinds, "rows": len(rows)}


def report(r, tag="real"):
    ks = " ".join(f"{k}={v}" for k, v in sorted(r["kinds"].items()))
    print(f"[{tag}] lines {sum(r['kinds'].values())} ({ks}) rows {r['rows']} open {len(r['open'])} stale {len(r['stale'])}")


def controls():
    base = load()
    ok = 0
    uc = base[UC]
    # 1 planted tid-indexed default-path table with no reset
    p = uc.replace("namespace s7394fix {", "static int g_s7608_plant[64];\nstatic void s7608_plant(uint8_t* rdram) "
                   "{ g_s7608_plant[rogue_current_thread_id(rdram) & 63] = 1; }\nnamespace s7394fix {", 1)
    r = run({UC: p}); ok += bool(any("UNROWED" in o for o in r["open"])); print("  ctl1 plant table:", len(r["open"]))
    # 2 dropped row
    rows = [x for x in SITE_ROWS if x[1] != "Rs64WaitEnt& w = g_rs64_waittab[tid & 63];"]
    r = run(rows=rows); ok += bool(r["open"]); print("  ctl2 drop row:", len(r["open"]))
    # 3 remove the cleaner's thr_live_remove
    t = base[THR].replace("            thr_live_remove(to_delete);\n", "", 1)
    r = run({THR: t}); ok += bool(any(o.startswith("C4") for o in r["open"])); print("  ctl3 no remove:", len(r["open"]))
    # 4 old OSId key on the holder compare
    q = uc.replace("s7394fix::holder.load() == s7394fix::me(rdram)) {", "s7394fix::holder.load() == rogue_current_thread_id(rdram)) {", 1)
    r = run({UC: q}); ok += bool(any(o.startswith("BAD") for o in r["open"])); print("  ctl4 OSId holder:", len(r["open"]))
    print(f"controls {ok}/4")
    return ok


def witness():
    path = os.path.join(ROOT, LOG)
    if not os.path.exists(path):
        print("witness: log missing -> FAIL"); return False
    out = subprocess.run(["grep", "-a", "-o", r"\[thr-create-id\] id=[0-9-]* thr=0x[0-9a-f]* pri=[0-9]* entry=0x[0-9A-F]* "
                          r"thr_rdram=0x[0-9A-F]*", path], capture_output=True, text=True).stdout.split("\n")
    per = {}
    n = 0
    for ln in out:
        m = re.search(r"id=(-?\d+) .*entry=(0x[0-9A-F]+) thr_rdram=(0x[0-9A-F]+)", ln)
        if not m:
            continue
        n += 1
        per.setdefault(int(m.group(1)), {}).setdefault((m.group(2), m.group(3)), 0)
        per[int(m.group(1))][(m.group(2), m.group(3))] += 1
    rep = {i: len(v) for i, v in per.items() if len(v) > 1}
    recreated = sum(1 for v in per.values() for c in v.values() if c > 1)
    print(f"witness: {n} creates, {len(per)} ids; ids naming >1 distinct thread: "
          + ", ".join(f"id{i}x{k}" for i, k in sorted(rep.items())) + f"; (entry,struct) pairs re-created: {recreated}")
    good = n > 0 and bool(rep) and recreated > 0
    print("witness", "PASS" if good else "FAIL")
    return good


if __name__ == "__main__":
    r = run(verbose=True)
    report(r)
    good = not r["open"] and not r["stale"]
    if "--controls" in sys.argv:
        good = controls() == 4 and good
    if "--witness" in sys.argv:
        good = witness() and good
    sys.exit(0 if good else 1)
