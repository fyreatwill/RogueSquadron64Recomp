#!/usr/bin/env python3
"""s7609 class MK: host state keyed by a GUEST STRUCT ADDRESS (OSMesgQueue*, OSTimer*, OSIoMesg*) that survives the guest
re-creating / re-using that struct (s7393: 6 queues are re-created live on the route; s7397: OSTimer structs are re-armed).

Enumerates every line in src/ + librecomp + ultramodern that stores a guest struct address into host state, compares
host state against one, or keys a host container by one (PAT). printf lines are auto 'print'. Every other line must match
a SITE_ROWS entry:
  diag:<FLAG>  runs only with that env flag (default off) or only feeds a diagnostic dump/print;
  stat         write-only counter keyed by address; read only by a diag dump (no default-path decision);
  value        the address is a constant/argument and the decision reads the CURRENT guest struct at each use;
  retail       stores the pointer exactly as libultra does (__osEventStateTab, __osViNext, OSTimer fields), re-read per delivery;
  fresh        per-call / thread_local state set and cleared inside one OS call (C4);
  extq         pending external delivery tagged by mq address (host-event latency): crosses an incarnation only if an event
               target is re-created while a message is in flight -> covered by --witness (re-created set ^ event targets);
  timer        active_timers keyed by OSTimer address: re-arm carries fields atomically (s7397, C3), fire re-reads t->mq (C2);
  fix          s7394fix heap-mutex re-seed skip (8010FEE0): skip is thread_local, holder released on every 8010FEE0 post (C5).
Contracts (each failing one is OPEN): C1 osCreateMesgQueue resets blocked_on_recv/blocked_on_send/validCount/first (all
incarnation state lives in the guest struct, not the host); C2 timer fire posts cur_timer->mq/msg (no cached copy);
C3 ROGUESQ_S7397_TIMERFIX defaults on; C4 pi.cpp clears s7398_msg (2 sites) and it is thread_local; C5 s7394fix::skip is
thread_local and the 8010FEE0 release stores holder -1; C6 all 3 external requeue sites gate on external_requeue_ok.
Any std::map/set/unordered_* whose key type is PTR(OS...) outside timer.cpp is BAD unless rowed.
--controls: (1) plant a default-path std::map keyed by mq_ in osSendMesg -> OPEN; (2) drop a row -> OPEN; (3) remove the
validCount reset from osCreateMesgQueue -> OPEN (C1); (4) plant a cached mq pointer compared after re-create -> OPEN.
--witness: scratch/s7393q/report_l{5,10,15}.txt (ROGUESQ_S7393_CQ, re-created queues) and scratch/s7392q/report_l*.txt
(ROGUESQ_S7392_MQ, external-delivery targets + requeues), same route + levels, separate runs; both need CONTROL PASS.
PASS = re-created set non-empty (premise) and disjoint from every external target, and 0 requeues on the route.
Exit 0 only if 0 open, 0 stale rows, 4/4 controls, witness PASS when asked.
"""
import os, re, sys, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("tk", os.path.join(ROOT, "tools/s7608_tk_census.py"))
tk = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(tk)
L = "lib/N64ModernRuntime"
UC = "src/main/upstream_compat.cpp"
MQ = L + "/ultramodern/src/mesgqueue.cpp"
EV = L + "/ultramodern/src/events.cpp"
TM = L + "/ultramodern/src/timer.cpp"
PI = L + "/librecomp/src/pi.cpp"
PAT = re.compile(r"(\.|->)\w*mq\w*\s*(=[^=]|\.store\()|\b\w*_mq\w*\s*=[^=]|seen_mq\[|(==|!=)\s*\(?\w*\)?\s*mq_?\b|\bmq_?\)?\s*(==|!=)|"
                 r"\.mq\s*(==|!=)|active_timers\.(insert|erase|find)\(|\*it == \w+->timer|s7398_msg\s*=|requeued_messages\.push_back|"
                 r"external_messages\.enqueue\(|g_audio_sp_deliveries\.push_back|kS4263Q\[|0x80128CF0u|\bctl_q\s*(=|&&)|"
                 r"\[\s*(\{[^}]*)?\(?\w*\)?\s*\w*mq_?\s*\}?\s*\]|"
                 r"(std::map|unordered_map|std::set|unordered_set)<\s*(PTR\(OS\w+\)|uint32_t\s*,?\s*\w*>\s*\w*mq)")
MAPPTR = re.compile(r"(std::map|unordered_map|std::set|unordered_set)<\s*PTR\(OS\w+\)")

SITE_ROWS = [
    (PI, "static thread_local uint32_t s7398_msg = 0;", "fresh", "s7398 completion OSIoMesg: thread_local, per call"),
    (PI, "s7398_msg = mb;", "fresh", "set inside the osEPiStartDma body, cleared before return (C4)"),
    (PI, "if (s7398_fix()) s7398_msg = (uint32_t)ctx->r5;", "fresh", "osPiStartDma path, cleared before return (C4)"),
    (PI, "s7398_msg = 0;", "fresh", "the two clears (C4)"),
    (PI, "(uint32_t)MEM_W(4, (gpr)(int32_t)mb) == (uint32_t)mq", "diag:s7398_ctl", "readback check inside if (s7398_ctl())"),
    (EV, "mq = mq_;", "retail", "osSetEventMesg (sp/dp/ai/si) + osViSetEvent next_state: libultra stores the same pointer in "
     "__osEventStateTab/__osViNext; every delivery sends to whatever struct is at the address now"),
    (EV, "if (cur_state->mq != NULLPTR) {", "retail", "VI delivery reads the registered pointer per retrace"),
    (EV, "events_context.ai.mq != NULLPTR", "retail", "AI delivery reads the registered pointer per event (3 sites)"),
    (MQ, "!= 0x80114388u || !audiotick_trace_enabled()", "diag:ROGUESQ_LOG_AUDIOTICK_TRACE", "log_vi_mq / log_vi_deq"),
    (MQ, "seen_mq[", "diag:ROGUESQ_RECV_TRACE", "log_unique_mq_tag returns unless recv_trace_env (3 lines)"),
    (MQ, "g_audio_sp_deliveries.push_back", "diag:audio-route", "log_audio_sp_delivery returns unless queued.audio.active "
     "(rs64_audio_route_snapshot: g_audio_route_context.active, route logger only); g_current_audio_route only read by the "
     "route snapshot export"),
    (MQ, "if (it->mq != mq || it->msg != msg) continue;", "diag:audio-route", "log_audio_sp_receive, same list"),
    (MQ, "if (cur == mq) return &tab[i];", "stat", "s4260::find: per-mq enq/send counters, read only by the ROGUESQ_S4259 watcher"),
    (MQ, "tab[i].mq.compare_exchange_strong(z, mq) || z == mq", "stat", "s4260::find slot claim"),
    (MQ, "external_messages.enqueue(queued);", "extq", "enqueue_external_message_src (host events: timer/SP/SI/AI/VI/PI/DP)"),
    (MQ, "external_messages.enqueue({mq, msg, jam, requeue_if_blocked});", "extq", "enqueue_external_message (host-thread sends)"),
    (MQ, "if (static_cast<uint32_t>(to_send.mq) == 0x80114388u) {", "stat", "DeqStats.vi counter, only fed to the VI recv log"),
    (MQ, "if (static_cast<uint32_t>(to_send.mq) == 0x80114388u && !mesgqueue_guard_refuse(", "value", "reads validCount of the "
     "current VI queue struct for the delivery log"),
    (MQ, "requeued_messages.push_back(to_send);", "extq", "requeue (Timer/SP/SI/DP sources) only when full + external_requeue_ok"),
    (MQ, "external_messages.enqueue(cur_mesg);", "extq", "batch requeue"),
    (MQ, "external_messages.enqueue(to_send);", "extq", "wait_for_external_message(_timed) requeue (2 sites)"),
    (MQ, "if (static_cast<uint32_t>(mq_) == 0x80149670u) s4585::ai_sends++;", "stat", "s4585 AI send counter, dump only"),
    (MQ, "if ((uint32_t)mq_ != tmq) {", "diag:ROGUESQ_REFUSED_RECV_TEST", "test arm, returns unless set"),
    (MQ, "g_s4259[", "diag:ROGUESQ_S4259", "inside if (s4259_on()) or s4259_tid >= 0 (only set when on) (4 lines)"),
    (MQ, "if (static_cast<uint32_t>(mq_) == 0x80128CF0u && flags == OS_MESG_BLOCK && !jam) {", "value", "s7367 CF0 dup-ack drop "
     "decides on MQ_IS_FULL(cq) of the current struct (CF0 created once per run, s7393 creates=1)"),
    (MQ, "const bool is_a1_queue = static_cast<uint32_t>(mq_) == 0x8010FEE0u;", "diag:ROGUESQ_LOG_A1_QUEUE", "before-copy only"),
    (MQ, "const bool is_vi_mq = (static_cast<uint32_t>(mq_) == 0x80114388u);", "value", "reads current validCount for the VI "
     "recv log + s4908 event (prints)"),
    (MQ, "void s4261_note_timer(uint32_t mq) { s4260::timer_n++; s4260::timer_last_mq = mq; }", "stat", "watcher-only counter"),
    (TM, "std::set<PTR(OSTimer), decltype(timer_sort)> active_timers{timer_sort};", "timer", "the libultra timer list analogue"),
    (TM, "if (*it == add_action->timer) { ++live; if (add_action->carry)", "timer", "s7397 re-arm: pointer scan erases the old "
     "entry before the fields change (C3)"),
    (TM, "t->timestamp = add_action->timestamp; t->interval = add_action->interval; t->mq = add_action->mq;", "timer",
     "s7397 carry: fields written on the timer thread, never under a stale set key"),
    (TM, "active_timers.insert(add_action->timer);", "timer", "insert after the carry"),
    (TM, "if (*it == remove_action->timer) ++live;", "timer", "osStopTimer live scan"),
    (TM, "size_t n = active_timers.erase(remove_action->timer);", "timer", "osStopTimer erase"),
    (TM, "it = (*it == remove_action->timer) ? active_timers.erase(it)", "timer", "s7397 stale-key fallback erase by pointer"),
    (TM, "std::set<PTR(OSTimer)> seen;", "diag:ROGUESQ_S7397_TM_CTL", "CheckTimerAction, enqueued only by the TM_CTL control"),
    (TM, "? active_timers.erase(it) : std::next(it);", "diag:ROGUESQ_S7397_TM_CTL", "CheckTimerAction fake-range purge"),
    (TM, "active_timers.erase(cur_timer_);", "timer", "head pop while waiting"),
    (TM, "active_timers.insert(cur_timer_);", "timer", "head re-insert (interrupted wait / interval reload, 2 sites)"),
    (TM, "a.interval = interval; a.mq = mq; a.msg = msg;", "timer", "osSetTimer s7397 carry action"),
    (TM, "t->mq = mq;", "retail", "ROGUESQ_S7397_TIMERFIX=0 arm: libultra osSetTimer writes the OSTimer directly"),
    ("src/main/rt64_render_context.cpp", "for (uint32_t q : {0x80128CF0u, 0x80128D10u, 0x80114388u})", "diag:stall-dump",
     "stall-dump print loop"),
    (UC, "(mq_addr != 0x80138D10u && mq_addr != 0x80128CF0u)) return;", "diag:ROGUESQ_LOG_M5_FRAME_SYNC", "logger gate"),
    (UC, "const uint32_t obj = mq == 0x8011A408u ? 0x11A408u : 0u;", "diag:ROGUESQ_LOG_SUBMIT_BOUNDARY", "log_submit_boundary"),
    (UC, "if (g_recv_stats[i].mq == mq) return &g_recv_stats[i];", "diag:ROGUESQ_RECV_TRACE", "recv_stat_for: recv_trace_enter/"
     "exit return unless enabled"),
    (UC, "g_recv_stats[n].mq = mq;", "diag:ROGUESQ_RECV_TRACE", "recv_stat_for slot claim"),
    (UC, "if (mq == 0x8011A818u) {", "diag:ROGUESQ_RECV_TRACE", "recv_trace_enter body"),
    (UC, "static const uint32_t kS4263Q[3]", "diag:ROGUESQ_S4262", "s4263 queue list"),
    (UC, "if (kS4263Q[i] == mq) return i;", "diag:ROGUESQ_S4262", "s4263_idx"),
    (UC, "kS4263Q[i]", "diag:ROGUESQ_S4262", "s4263 dump (2 lines)"),
    (UC, "g_s4264_recvs[{tid, mq}]++;", "diag:ROGUESQ_S4262", "s4264_enter, called only when s4264_on"),
    (UC, "g_s4264_sends[{tid, mq}]++;", "diag:ROGUESQ_S4262", "s4262_note_send returns unless on"),
    (MQ, '"[createmq] row=%u mq=0x%08X', "print", "fprintf format continuation line (recv_trace_env only)"),
    (UC, "if (tid != 0 && mq != 0x8011A818u) return;", "diag:ROGUESQ_S4262", "s4264 send note"),
    (UC, "(PTR(OSMesgQueue))0x80128CF0u);", "diag:CF0-ring", "rs64_cf0_ev ring / Cf0Delay + RetraceHold test arms read the "
     "current CF0 struct for prints (3 lines)"),
    (UC, "const bool cf0 = mq == 0x80128CF0u;", "stat", "Rs64WaitScope ([stall-dump] table, dump-only; ROGUESQ_WAITTAB)"),
    (UC, "Rs64WaitEnt& w = g_rs64_waittab[tid & 63]; w.mq = mq;", "stat", "waittab entry, read only by rs64_waittab_dump"),
    (UC, "if (w.mq.load() == mq && w.ra.load() == ra) w.pending = 0;", "stat", "waittab clear"),
    (UC, "if (mq == 0x80128CF0u) rs64_cf0_ev(", "stat", "CF0 event ring (dump-only)"),
    (UC, "cf0(k_arm() > 0 && (uint32_t)c->r4 == 0x80128CF0u", "diag:ROGUESQ_CF0_DELAY_TEST", "test arm"),
    (UC, "tab[i].kind == kind && tab[i].mq == mq", "diag:ROGUESQ_S7392_MQ", "s7392 table"),
    (UC, "static uint32_t ctl_q = 0;", "diag:ROGUESQ_S7399_EVP", "s7399 control queue"),
    (UC, "return mq == 0x80114388u || mq == 0x80110770u", "diag:ROGUESQ_S7399_EVP", "s7399 evq"),
    (UC, "{ std::lock_guard<std::mutex> lk(mu); ctl_q = q; }", "diag:ROGUESQ_S7399_EVP", "s7399 control"),
    (UC, "s7399::ev[i].mq == mq", "diag:ROGUESQ_S7399_EVP", "s7399 ev table"),
    (UC, "s7399::rv[i].mq == mq", "diag:ROGUESQ_S7399_EVP", "s7399 rv table"),
    (UC, "->queue == mq", "diag:ROGUESQ_S7393_CQ", "s7393 orphan check (2 lines)"),
    (UC, "if (seen[k] == mq) { re = true; break; }", "diag:ROGUESQ_S7393_CQ", "s7393 re-create detect"),
    (UC, "if (tab[i].mq == mq && tab[i].key == key) break;", "diag:ROGUESQ_S7393_CQ", "s7393 table"),
    (UC, "if (mq != MQ", "diag:ROGUESQ_S7394_BD", "s7394 census (3 lines)"),
    (UC, "if (mq == 0x8010FEE0u && cnt == 1 && s7394fix::on()", "fix", "s7394fix held re-seed (C5)"),
    (UC, "tag(mq == 0x80128CF0u ? \"recv-ack\"", "diag:ROGUESQ_S4913", "S4913RecvScope -> rs64_s4913_mark returns unless on"),
]


def run(over=None, rows=None, verbose=False):
    rows = SITE_ROWS if rows is None else rows
    files = tk.load(over)
    used, opens, kinds = set(), [], {}
    for rel, txt in sorted(files.items()):
        for i, ln in enumerate(tk.strip_comments(txt).split("\n"), 1):
            if not PAT.search(ln):
                continue
            if "printf" in ln:
                kinds["print"] = kinds.get("print", 0) + 1
                continue
            hit = next((k for k, r in enumerate(rows) if rel.endswith(r[0]) and r[1] in ln), None)
            if hit is None:
                tag = "BAD" if (MAPPTR.search(ln) and not rel.endswith(TM)) else "UNROWED"
                opens.append(f"{tag} {rel}:{i}: {ln.strip()[:120]}")
                continue
            used.add(hit)
            kd = rows[hit][2].split(":")[0]
            kinds[kd] = kinds.get(kd, 0) + 1
    stale = [r for k, r in enumerate(rows) if k not in used]
    mq, tm, pi, uc = (files.get(x, "") for x in (MQ, TM, PI, UC))
    a = mq.find('extern "C" void osCreateMesgQueue(')
    cq = mq[a:a + 900] if a >= 0 else ""
    for f in ("mq->blocked_on_recv = NULLPTR;", "mq->blocked_on_send = NULLPTR;", "mq->validCount = 0;", "mq->first = 0;"):
        if f not in cq:
            opens.append(f"C1 osCreateMesgQueue lost `{f}` (incarnation state would survive a re-create)")
    if "enqueue_external_message_src(cur_timer->mq, cur_timer->msg," not in tm:
        opens.append("C2 timer fire no longer re-reads cur_timer->mq/msg from the guest struct")
    if 's7397_env("ROGUESQ_S7397_TIMERFIX", true)' not in tm:
        opens.append("C3 s7397 timer carry fix is no longer default on")
    if pi.count("s7398_msg = 0;") < 2 or "static thread_local uint32_t s7398_msg" not in pi:
        opens.append("C4 s7398_msg is no longer thread_local + cleared at both call ends")
    if "static thread_local bool skip = false;" not in uc or "s7394fix::holder.store(-1)" not in uc:
        opens.append("C5 s7394fix::skip not thread_local or holder never released")
    if mq.count("to_send.requeue_if_blocked && external_requeue_ok(PASS_RDRAM to_send)") < 3:
        opens.append("C6 an external requeue site lost the external_requeue_ok gate")
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
    base = tk.load(); ok = 0; m = base[MQ]; b0 = len(run()["open"])
    anchor = "    // Try to send the message.\n    bool sent = do_send(PASS_RDRAM mq_, msg, jam, flags == OS_MESG_BLOCK);\n    if (s4259_on())"
    p = m.replace(anchor, "    { static std::map<uint32_t, int> g_s7609_plant; if (g_s7609_plant[(uint32_t)mq_]++ > 3) return -1; }\n" + anchor, 1)
    r = run({MQ: p}); c = p != m and len(r["open"]) > b0 and any("UNROWED" in o or "BAD" in o for o in r["open"]); ok += c
    print("  ctl1 plant mq map:", len(r["open"]), "PASS" if c else "FAIL")
    rows = [x for x in SITE_ROWS if x[1] != "if (*it == remove_action->timer) ++live;"]
    r = run(rows=rows); c = len(r["open"]) > b0; ok += c; print("  ctl2 drop row:", len(r["open"]), "PASS" if c else "FAIL")
    a = m.find('extern "C" void osCreateMesgQueue(')
    q = m[:a] + m[a:].replace("    mq->validCount = 0;\n", "", 1)
    r = run({MQ: q}); c = q != m and len(r["open"]) > b0 and any(o.startswith("C1") for o in r["open"]); ok += c
    print("  ctl3 no validCount reset:", len(r["open"]), "PASS" if c else "FAIL")
    t = m.replace(anchor, "    { static uint32_t s_s7609_cached_mq = static_cast<uint32_t>(mq_); if (s_s7609_cached_mq == (uint32_t)mq_) flags = 0; }\n" + anchor, 1)
    r = run({MQ: t}); c = t != m and len(r["open"]) > b0 and any("UNROWED" in o for o in r["open"]); ok += c
    print("  ctl4 cached mq pointer:", len(r["open"]), "PASS" if c else "FAIL")
    print(f"controls {ok}/4")
    return ok


def witness():
    recre, ext, rq, ctl3, ctl2, files = set(), {}, 0, 0, 0, 0
    for lv in (5, 10, 15):
        for d, kind in (("scratch/s7393q", "cq"), ("scratch/s7392q", "mq")):
            p = os.path.join(ROOT, d, f"report_l{lv}.txt")
            if not os.path.exists(p):
                print("witness: missing", p); return False
            files += 1
            for ln in open(p, errors="replace"):
                if ln.startswith("CONTROL PASS"):
                    ctl2 += kind == "mq"
                m = re.match(r"^(\S+)?\s+mq=([0-9A-F]{8}) \S+\s+cnt=\d+ creates=(\d+) re=(\d+)", ln)
                if kind == "cq" and m:
                    if m.group(1) == "CTRL":
                        ctl3 += int(m.group(4)) > 0
                    elif int(m.group(4)) > 0:
                        recre.add(m.group(2))
                m = re.search(r"\bE mq=([0-9A-F]{8}) ext:(\S+)\s+flags=\d+ calls=(\d+) fails=(\d+) rq=(\d+)", ln)
                if kind == "mq" and m:
                    ext.setdefault(m.group(1), set()).add(m.group(2)); rq += int(m.group(5))
    both = recre & set(ext)
    print(f"witness: {files} reports; controls cq {ctl3}/3 mq {ctl2}/3; re-created queues {len(recre)} ({','.join(sorted(recre))}); "
          f"external targets {len(ext)}; overlap {len(both)} {sorted(both)}; route requeues {rq}")
    good = ctl3 == 3 and ctl2 == 3 and bool(recre) and bool(ext) and not both and rq == 0
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
