#!/usr/bin/env python3
"""s7607 class UW: C++ exceptions that unwind THROUGH generated C frames.

ultramodern::thread_terminated is thrown by osDestroyThread when a guest thread destroys itself. The exception unwinds
through osDestroyThread_recomp, every generated guest frame on the thread's stack, and run_thread_function /
rs64_entrypoint_with_rdram_capture, and is caught at the thread roots (_thread_func, the Game Start entrypoint try).
Retail semantics: osDestroyThread(self) never returns, so skipping the guest epilogues is retail-equivalent. Only HOST
state is at risk: a non-RAII lock, a static flag or depth counter set before a guest call and restored after it, or an
object built without unwind tables (std::terminate on the first self-destroy).

Checks (each failing one is OPEN):
  T  every C++ `throw` in src/ + librecomp + ultramodern matches THROW_ROWS: `caught` (thread_terminated, needs roots)
     or `fatal` (std::runtime_error, no catch can swallow it: no catch(...) / catch(std::exception) on these paths);
  R  every catch(thread_terminated) matches ROOT_ROWS, and every host->guest entry (run_thread_function call sites,
     game_entry.entrypoint) sits inside a `try {` whose handler catches thread_terminated;
  C  host osDestroyThread( callers are only osDestroyThread_recomp; guest callers of osDestroyThread_recomp match
     GUEST_CALLER_ROWS;
  H  every host frame on the unwind path (HOST_FRAMES) holds no non-RAII lock / static-flag set before its guest call
     or throw, and runs no restore code after the guest call;
  F  no -fno-exceptions / -fno-unwind-tables / -fno-asynchronous-unwind-tables / -fno-cxx-exceptions in the flags of
     RecompiledFuncs, PatchesLib, RogueSquadron64Recomp, librecomp, ultramodern;
  U  every text symbol of every RecompiledFuncs / PatchesLib object, and every C object of the executable, has a
     compact-unwind entry at its address (objdump --unwind-info vs nm);
  P  no generated/patch function that can be on a self-destroying stack (static ancestors of osDestroyThread_recomp,
     plus everything reachable from an unresolved indirect call: conservative) sets a static / _Thread_local / g_ flag
     or counter before a guest call and restores it after (paired state). Off-path paired sites are listed, not OPEN.
--controls: (1) unrowed thread_terminated throw; (2) non-RAII lock before the throw; (3) -fno-exceptions on
RecompiledFuncs; (4) THROW_ROWS row dropped; (5) `try {` removed before run_thread_function; (6) paired flag planted
across a call in unregisterServiceWorker; (7) object built without unwind tables. --witness: compile
tools/s7607_uw_witness.{c,cpp} with the real RecompiledFuncs C flags (must catch) and with unwind tables off (must
terminate). Exit 0 only if 0 open, 0 stale rows, 7/7 controls, 2/2 witness arms.
"""
import collections, glob, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = "lib/N64ModernRuntime"
DIRS = ["src", L + "/librecomp/src", L + "/librecomp/include", L + "/ultramodern/src", L + "/ultramodern/include"]
GEN = "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs"
PATCHES = "RecompiledPatches/patches.c"
SKIP = re.compile(r"/(tests?|third_party|thirdparty)/")
THR = L + "/ultramodern/src/threads.cpp"
REC = L + "/librecomp/src/recomp.cpp"
UT = L + "/librecomp/src/ultra_translation.cpp"
MAIN = "src/main/main.cpp"
FLAGS = ["build/CMakeFiles/RecompiledFuncs.dir/flags.make", "build/CMakeFiles/PatchesLib.dir/flags.make",
         "build/CMakeFiles/RogueSquadron64Recomp.dir/flags.make",
         "build/N64ModernRuntime/librecomp/CMakeFiles/librecomp.dir/flags.make",
         "build/N64ModernRuntime/ultramodern/CMakeFiles/ultramodern.dir/flags.make"]
BADFLAG = re.compile(r"(?<![\w-])-f(no-exceptions|no-unwind-tables|no-asynchronous-unwind-tables|no-cxx-exceptions)\b")

THROW_ROWS = [  # (file, line substring, kind, reason)
    (THR, "throw ultramodern::thread_terminated{};", "caught",
     "osDestroyThread(self): t_ == thread_self; roots _thread_func x2 + Game Start entrypoint try; live (runtime "
     "'[thr-destroy] self id=6/9 ... (throw terminated)' and the process continues)"),
    (L + "/librecomp/src/pi.cpp", 'throw std::runtime_error("ROM DMA write unimplemented");', "fatal",
     "cart write DMA: unsupported, fatal by design (no catch -> std::terminate)"),
    (L + "/ultramodern/src/events.cpp", 'throw std::runtime_error("Failed to initialize the renderer");', "fatal",
     "renderer init failure at boot: fatal by design"),
    (THR, 'throw std::runtime_error("Invalid thread priority!");', "fatal",
     "set_native_thread_priority bad enum: fatal by design (unreachable: all callers pass enum constants)"),
    (THR, 'throw std::runtime_error("No threads left to run!\\n");', "fatal",
     "scheduler run queue empty: fatal by design (libultra would hang)"),
]
ROOT_ROWS = [  # (file, try-body substring that must precede the catch, reason)
    (THR, "wait_for_resumed(PASS_RDRAM thread_context);",
     "_thread_func pre-start wait: wait_for_resumed itself never throws (no throw in its body); harmless root"),
    (THR, "run_thread_function(PASS_RDRAM entrypoint, self->sp, arg);",
     "_thread_func: catches a self-destroy, then marks context null + run_next_thread + cleanup_thread (RAII-free, "
     "runs after the catch so nothing is skipped)"),
    (REC, "game_entry.entrypoint(rdram, context);",
     "Game Start thread: boot entry (rs64_entrypoint_with_rdram_capture -> recomp_entrypoint)"),
]
ENTRY_CALLS = [(THR, "run_thread_function(PASS_RDRAM entrypoint, self->sp, arg);"),
               (REC, "game_entry.entrypoint(rdram, context);")]
GUEST_CALLER_ROWS = {
    "unregisterServiceWorker": "0x800070BC: libultra-style worker teardown, osDestroyThread(t) of a worker or of self; "
                               "the only generated caller; nothing host-side after it in the frame (retail never returns)",
}
# host frames between the throw and the root: (file, function signature substring, call/throw substring, reason)
HOST_FRAMES = [
    (THR, 'extern "C" void osDestroyThread(', "throw ultramodern::thread_terminated{};",
     "before the throw: RS64_S7491 watch (s7545_host lock_guard, returns before the throw) + an fprintf"),
    (UT, 'extern "C" void osDestroyThread_recomp(', "osDestroyThread(rdram, (int32_t)ctx->r4);", "one-line forwarder"),
    (REC, "void run_thread_function(", "func(rdram, &ctx);",
     "ctx is a stack local; only a getenv log before; nothing after the call (#endif })"),
    (MAIN, 'extern "C" void rs64_entrypoint_with_rdram_capture(', "recomp_entrypoint(rdram, ctx);",
     "tail call; g_recomp_rdram_for_wp_raw set before is a plain pointer publish, not a paired flag"),
]
LOCKY = re.compile(r"\.lock\s*\(\s*\)|pthread_mutex_lock|os_unfair_lock_lock|\bmalloc\s*\(|\bnew\s+\w|"
                   r"\bstatic\s+[\w:<> ]+\s+\w+\s*;[^\n]*\n[^\n]*\b\w+\s*=\s*(true|1)\b")
FLAGSET = re.compile(r"(?<![\w.>])(s_\w+|g_\w+|\w*_active|\w*_busy|\w*_depth)\s*(=\s*(true|1)\b|\+\+)|\+\+\s*(s_\w+|g_\w+)")


def rd(p, over):
    if over and p in over: return over[p]
    with open(p if os.path.isabs(p) else os.path.join(ROOT, p), errors="replace") as f: return f.read()


def strip_comments(t):
    t = re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), t, flags=re.S)
    return re.sub(r"//[^\n]*", "", t)


def strip_all(t):
    t = strip_comments(t)
    t = re.sub(r'"(?:\\.|[^"\\\n])*"', '""', t)
    return re.sub(r"'(?:\\.|[^'\\\n])'", "''", t)


def src_files():
    out = []
    for d in DIRS:
        for dp, _, fs in os.walk(os.path.join(ROOT, d)):
            if SKIP.search(dp + "/"): continue
            for f in fs:
                if f.endswith((".cpp", ".hpp", ".h", ".c", ".cc", ".inl")):
                    out.append(os.path.relpath(os.path.join(dp, f), ROOT))
    return sorted(out)


def func_body(text, sig):
    i = text.find(sig)
    if i < 0: return None
    j = text.find("{", i); depth = 0
    for k in range(j, len(text)):
        if text[k] == "{": depth += 1
        elif text[k] == "}":
            depth -= 1
            if depth == 0: return text[j:k + 1]
    return None


def guest_bodies(over):
    """name -> (body, file); splits generated files and the patch file at every top-level function definition."""
    body = {}
    files = sorted(glob.glob(GEN + "/funcs_*.c")) + [os.path.join(ROOT, PATCHES)]
    defre = re.compile(r"^(?:RECOMP_FUNC|static|extern|inline|__attribute__|void|int|uint\w*|unsigned|bool)[^;=\n]*?"
                       r"\b(\w+)\s*\([^;{}]*\)\s*\{?\s*$", re.M)
    for f in files:
        s = rd(f, over)
        ms = list(defre.finditer(s))
        for a, b in zip(ms, ms[1:] + [None]):
            body[a.group(1)] = (s[a.start():b.start() if b else len(s)], f)
    return body


def static_names(text):
    out = set()
    for m in re.finditer(r"\bstatic\s+(?:_Thread_local\s+|volatile\s+|const\s+)*[A-Za-z_][\w ]*?\**\s*\b([A-Za-z_]\w*)"
                         r"\s*(?:=|;|\[|,)", text):
        out.add(m.group(1))
    out |= set(re.findall(r"\b_Thread_local\s+[\w ]+?\**\s*\b([A-Za-z_]\w*)\s*[;=]", text))
    out |= set(re.findall(r"\bextern\s+[\w ]+?\**\s*\b(g_\w+)\s*;", text))
    return out


CALLRE = re.compile(r"\b(\w+)\(rdram, ctx\)")
LOOKRE = re.compile(r"LOOKUP_FUNC\(([^()]*(?:\([^()]*\))?[^()]*)\)\(rdram, ctx\)")
DECL = re.compile(r"\bstatic\b|^\s*\{?\s*(?:const\s+)?(?:int|unsigned|uint\d+_t|int\d+_t|size_t|long|short|char|float|double|bool)\b")
P_ROWS = {  # (guest function, host variable) on a conservative self-destroy stack -> reason
    ("clampGridCellLookup", "g_s7025_in"): "s7025 clampsplit timing window flag, set only when ROGUESQ_S7022_ST=1 "
        "(g_rs64_s7022); a skipped reset only miscounts g_s7025[22]/[25] diagnostics (ok-gated)",
}


def paired_sites(name, text, statics):
    lines = [l for l in strip_comments(text).splitlines()]
    out = []
    for x in statics:
        if x not in text: continue
        up = re.compile(r"(?<![\w.>])" + re.escape(x) + r"\s*(\+\+|\+=|=(?!=)\s*(?!0\b|0u\b|false\b|NULL\b)[^;]+;)|\+\+\s*" + re.escape(x) + r"\b")
        dn = re.compile(r"(?<![\w.>])" + re.escape(x) + r"\s*(--|-=|=\s*(0|0u|false|NULL)\s*;)|--\s*" + re.escape(x) + r"\b")
        ups = [i for i, l in enumerate(lines) if up.search(l) and not DECL.search(l)]
        for i0 in ups:
            for i1 in range(i0 + 1, len(lines)):
                if dn.search(lines[i1]) and not DECL.search(lines[i1]):
                    seg = lines[i0:i1 + 1]
                    if any((CALLRE.search(l) and "rdram, ctx" in l) or "LOOKUP_FUNC" in l for l in seg):
                        out.append((name, x, i0, i1))
                    break
    return out


# ---- B/D: the second throw path. osDestroyThread(other) clears t->context and signals the target; the target wakes in
# wait_for_resumed, sees the context replaced and calls osDestroyThread(NULL) -> throw. So EVERY host frame that can
# reach wait_for_resumed (every blocking stub) is a possible unwind frame. Name-level host call graph over DIRS.
BLOCK_ROWS = {  # host ancestor of wait_for_resumed/osDestroyThread -> (verdict, reason)
    "_thread_func": ("root", "catch roots; the post-catch cleanup runs after the handler, nothing skipped"),
    "wait_for_resumed": ("ok", "throw site 2 is its last statement"),
    "run_next_thread_and_wait": ("ok", "wait is the last statement"),
    "resume_thread_and_wait": ("ok", "wait is the last statement"),
    "swap_to_thread": ("ok", "resume_thread_and_wait is the last statement"),
    "check_running_queue": ("ok", "swap_to_thread is the last statement of its branch"),
    "pause_self": ("ok", "infinite wait loop"), "yield_self": ("ok", "check_running_queue last"),
    "yield_self_1ms": ("ok", "check_running_queue last"),
    "rs64_preempt_point": ("ok", "check_running_queue last (fixup_preempt_point.py call from glyph-mesh guest code)"),
    "do_recv": ("ok", "skipped: the post-wake retry loop; osDestroyThread(other) already removed the thread from "
                "blocked_on_recv (thread_queue_remove t->queue)"),
    "do_send": ("ok", "same as do_recv for blocked_on_send"),
    "dequeue_external_messages": ("ok", "name-graph edge only: do_send(..., block=false) never waits"),
    "wait_for_external_message": ("ok", "name-graph edge only: do_send(..., false) never waits"),
    "wait_for_external_message_timed": ("ok", "name-graph edge only: do_send(..., false) never waits"),
    "osRecvMesg": ("ok-gated", "after do_recv skipped: g_s4259 blocked_mq=0 (ROGUESQ s4259), g1b blk_since exchange(0) "
                   "(g1b_blk_on), rs64_tl, s4908/s4911 logs, check_running_queue (thread is dead), s7399 recv hook"),
    "osSendMesg": ("ok-gated", "after do_send skipped: s4259 counters + logs only"),
    "osJamMesg": ("ok-gated", "after do_send skipped: logs only"),
    "osRecvMesg_recomp": ("ok", "RAII locals run (DTOR_ROWS); skipped: s7394::post_recv (gated), s7394fix::holder.store "
                          "(only after a SUCCESSFUL recv: a thread that dies blocked never became holder), m5 join logs"),
    "osSendMesg_recomp": ("ok", "skipped: s7392/s7399/s7394 hooks (gated) and s7394fix::holder.store(-1): only skipped "
                          "when the sender dies blocked in its own send, i.e. the token was never posted -> the guest "
                          "mutex is lost in retail too; the stale holder mirror matches that state"),
    "osJamMesg_recomp": ("ok-gated", "s7392 hook after (gated)"),
    "osStartThread_recomp": ("ok", "forwarder"), "osSetThreadPri_recomp": ("ok", "forwarder"),
    "osDestroyThread_recomp": ("ok", "forwarder"), "osStopThread_recomp": ("ok", "self path: wait then return"),
    "osStartThread": ("ok", "check_running_queue last"), "osSetThreadPri": ("ok", "check_running_queue last"),
    "osStopThread": ("ok", "wait last"),
    "s7195_refused_block_recv": ("ok", "parks forever (for(;;) wait); counters only"),
    "pre": ("ok-gated", "s7394::pre (ROGUESQ_S7394*): lock_guard block closed before take_return; also s7551::pre "
            "(memcpy, name collision)"),
    "post_send": ("ok-gated", "s7394 window close, lock_guard block closed before the nested send"),
    "take_return": ("ok-gated", "s7394 control: NOBLOCK recv+send"),
    "control": ("ok-gated", "s7392/s7399 one-shot controls (ROGUESQ_S7392_CTL / ROGUESQ_S7399_CTL), NOBLOCK only"),
    "rs64_wbw_pre": ("ok", "name collision: calls s7551::pre (memcpy), not s7394::pre"),
    "main": ("dead", "threads.cpp #if 0 example main"),
    "bootproc": ("dead", "port_main.c: upstream example, not in any CMake target (no object)"),
    "idle_thread_func": ("dead", "port_main.c example"), "main_thread_func": ("dead", "port_main.c example"),
    "thread3_func": ("dead", "port_main.c example"), "thread4_func": ("dead", "port_main.c example"),
}
DTOR_ROWS = {  # RAII local constructed in a BLOCK_ROWS frame -> destructor runs DURING the unwind
    "Rs64WaitScope": "clears the wait-table pending bit: correct on unwind (the wait ended)",
    "S4913RecvScope": "diagnostic mark recv-*-ret (ROGUESQ s4913 tag queues only); harmless",
    "Rs64Cf0Delay": "test arm ROGUESQ_CF0_DELAY_TEST: dtor BLOCKS (nested osRecvMesg) -> must return when "
                    "std::uncaught_exceptions() > 0 (s7607 fix; before it a throw inside the dtor -> std::terminate)",
    "S7590PortRel": "_thread_func: releases the g1b mach-port slot (correct; runs after the catch anyway)",
    "lock_guard": "scoped; checked below: never alive across a blocking call",
    "unique_lock": "scoped; checked below: never alive across a blocking call",
}
KW = {"if", "for", "while", "switch", "return", "sizeof", "catch", "defined", "decltype", "alignof", "static_assert",
      "__attribute__"}


def host_funcs(texts):
    F = {}
    for f, t0 in texts.items():
        t = strip_all(t0); n = len(t); i = 0; last = 0; stack = []
        while i < n:
            ch = t[i]
            if ch == "{":
                hdr = t[last:i]
                if not stack or stack[-1] is None:
                    h = hdr.strip()
                    if re.search(r"\bnamespace\b[^;()]*$", h) or h.endswith('extern ""'):
                        stack.append(None); last = i + 1; i += 1; continue
                    m = re.search(r"\b([A-Za-z_]\w*(?:::~?\w+)*)\s*\([^{};]*\)\s*(?:const\s*)?(?:noexcept\s*)?(?:->[^{]*)?$", hdr)
                    if m and m.group(1).split("::")[-1] not in KW and not re.search(r"\b(struct|class|enum|union)\b", hdr.split("(")[0]):
                        d = 0
                        for k in range(i, n):
                            if t[k] == "{": d += 1
                            elif t[k] == "}":
                                d -= 1
                                if d == 0: break
                        F.setdefault(m.group(1).split("::")[-1], []).append((f, t.count("\n", 0, i) + 1, t[i:k + 1]))
                        i = k + 1; last = i; continue
                stack.append("x")
            elif ch == "}":
                if stack: stack.pop()
                last = i + 1
            elif ch == ";" and (not stack or stack[-1] is None): last = i + 1
            i += 1
    return F


def host_path(texts, over):
    opens, stale, info = [], [], collections.Counter()
    F = host_funcs(texts)
    callers = collections.defaultdict(set)
    for name, defs in F.items():
        for _, _, b in defs:
            for c in set(re.findall(r"\b([A-Za-z_]\w*)\s*\(", b)):
                if c in F and c != name: callers[c].add(name)
    seen, st = set(), ["wait_for_resumed", "osDestroyThread"]
    while st:
        for p in callers[st.pop()]:
            if p not in seen: seen.add(p); st.append(p)
    blk = seen | {"wait_for_resumed", "osDestroyThread"}
    info["host_blocking_frames"] = len(seen)
    for name in sorted(seen):
        if name not in BLOCK_ROWS: opens.append(f"B unrowed host frame on the blocking unwind path: {name} ({F[name][0][0]}:{F[name][0][1]})")
        else: info["b_" + BLOCK_ROWS[name][0]] += 1
    stale += [f"B stale row {n}" for n in BLOCK_ROWS if n not in seen]
    for name in sorted(seen):
        for f, ln, b in F[name]:
            lines = b.splitlines()
            bl = [i for i, l in enumerate(lines) if any(re.search(r"(?<![\w.])" + re.escape(x) + r"\s*\(", l) for x in blk if x != name)]
            if not bl: continue
            for i, l in enumerate(lines[:bl[-1]]):
                m = re.search(r"\.lock\s*\(\s*\)|pthread_mutex_lock|os_unfair_lock_lock", l)
                if m: opens.append(f"B non-RAII lock before a blocking call in {name} ({f}:{ln + i}): {l.strip()[:90]}")
                for m in re.finditer(r"\b(?:std::)?(lock_guard|unique_lock|scoped_lock)\s*<[^>]*>\s*\w+\s*[({]|\b([A-Z]\w*(?:Scope|Delay|Rel|Hold|Guard))\s+\w+\s*[({]", l):
                    cls = m.group(1) or m.group(2)
                    if cls not in DTOR_ROWS: opens.append(f"D unrowed RAII local {cls} in blocking frame {name} ({f}:{ln + i})")
                    else: info["dtor_locals"] += 1
                    if m.group(1):  # lock alive until its block closes: must close before every later blocking call
                        d = 0; end = len(lines)
                        for k in range(i, len(lines)):
                            d += lines[k][(m.start() if k == i else 0):].count("{") - lines[k][(m.start() if k == i else 0):].count("}")
                            if d < 0: end = k; break
                        if any(i < j <= end for j in bl) or (any(j == i for j in bl) and lines[i].find("{", m.end()) < 0):
                            opens.append(f"B {cls} alive across a blocking call in {name} ({f}:{ln + i})")
    # every destructor of a rowed RAII class that itself blocks must bail out while unwinding
    for cls in DTOR_ROWS:
        for f, t in texts.items():
            s = strip_all(t)
            m = re.search(r"~" + cls + r"\s*\(\s*\)\s*\{", s)
            if not m: continue
            d = 0
            for k in range(m.end() - 1, len(s)):
                d += (s[k] == "{") - (s[k] == "}")
                if d == 0: break
            body = s[m.end():k]
            if any(re.search(r"(?<![\w.])" + re.escape(x) + r"\s*\(", body) for x in blk | {"osRecvMesg", "osSendMesg", "osJamMesg"}):
                info["blocking_dtors"] += 1
                if "uncaught_exceptions" not in body:
                    opens.append(f"D destructor ~{cls} blocks without an uncaught_exceptions() bail-out ({f}): throw-in-dtor -> std::terminate")
    return opens, stale, info, blk


def run(over=None, rows=None, flags_over=None, extra_objs=None, verbose=False):
    over = over or {}; rows = rows if rows is not None else THROW_ROWS
    opens, stale, info = [], [], collections.Counter()
    files = src_files(); texts = {f: rd(f, over) for f in files}
    # T: throws
    used = set()
    for f, t in texts.items():
        raw = strip_comments(t).splitlines()
        for n, l in enumerate(strip_all(t).splitlines(), 1):
            if not re.search(r"\bthrow\b\s*[\w:]", l): continue
            l = raw[n - 1]
            hit = [r for r in rows if f == r[0] and r[1] in l]
            if hit and hit[0][:2] in used: opens.append(f"T row matched twice (a second throw shares its text): {f}:{n}")
            elif hit: used.add(hit[0][:2]); info["throw_" + hit[0][2]] += 1
            else: opens.append(f"T unrowed throw {f}:{n}: {l.strip()[:120]}")
    stale += [f"T stale row {r[0]}: {r[1]}" for r in rows if r[:2] not in used]
    for f, t in texts.items():
        for n, l in enumerate(strip_comments(t).splitlines(), 1):
            if re.search(r"catch\s*\(\s*(\.\.\.|const\s+std::exception|std::exception)", l):
                opens.append(f"T catch-all could swallow a fatal/terminated: {f}:{n}: {l.strip()[:100]}")
    # R: roots
    used = set()
    for f, t in texts.items():
        s = strip_comments(t)
        for m in re.finditer(r"catch\s*\(\s*ultramodern::thread_terminated", s):
            pre = s[max(0, m.start() - 400):m.start()]
            tm = list(re.finditer(r"\btry\s*\{", pre)); tb = pre[tm[-1].start():] if tm else ""
            hit = [r for r in ROOT_ROWS if r[0] == f and r[1] in tb]
            if hit: used.add(hit[0][:2]); info["roots"] += 1
            else: opens.append(f"R unrowed catch {f}:{s.count(chr(10), 0, m.start()) + 1}")
    stale += [f"R stale root {r[0]}: {r[1]}" for r in ROOT_ROWS if r[:2] not in used]
    for f, sub in ENTRY_CALLS:
        s = strip_comments(texts[f]); i = s.find(sub)
        pre = s[max(0, i - 200):i]; post = s[i:i + 300]
        if i < 0: stale.append(f"R entry call gone {f}: {sub}"); continue
        if not re.search(r"try\s*\{\s*(//[^\n]*\s*)*$", pre.rstrip() + " ") and not re.search(r"try\s*\{[^{}]*$", pre):
            opens.append(f"R host->guest entry not inside try: {f}: {sub}")
        elif not re.search(r"\}\s*catch\s*\(\s*ultramodern::thread_terminated", post):
            opens.append(f"R entry try lacks a thread_terminated handler: {f}: {sub}")
        else: info["entries_rooted"] += 1
    for f, t in texts.items():
        s = strip_comments(t)
        for m in re.finditer(r"(?<![\w.])run_thread_function\s*\(", s):
            line = s[s.rfind("\n", 0, m.start()) + 1:s.find("\n", m.start())]
            if re.search(r"\bvoid\s+run_thread_function", line) or line.lstrip().startswith("#define"): continue
            if "PASS_RDRAM entrypoint" not in line: opens.append(f"R extra run_thread_function caller {f}: {line.strip()[:100]}")
    # C: callers
    for f, t in texts.items():
        s = strip_comments(t)
        for m in re.finditer(r"(?<![\w.])osDestroyThread\s*\(", s):
            line = s[s.rfind("\n", 0, m.start()) + 1:s.find("\n", m.start())]
            if re.search(r"\bvoid\s+osDestroyThread\s*\(", line): continue
            if f == UT and "(int32_t)ctx->r4" in line: info["host_destroy_callers"] += 1; continue
            if f == THR and "osDestroyThread(PASS_RDRAM NULLPTR);" in line and "wait_for_resumed" in s[:m.start()][-1500:]:
                info["host_destroy_callers"] += 1; continue  # throw path 2: a destroyed thread wakes in wait_for_resumed
            opens.append(f"C host osDestroyThread caller outside the stub: {f}: {line.strip()[:100]}")
    gb = guest_bodies(over)
    names = set(gb)
    gcall = sorted(n for n, (b, _) in gb.items() if re.search(r"\bosDestroyThread_recomp\(rdram, ctx\)", b))
    for n in gcall:
        if n not in GUEST_CALLER_ROWS: opens.append(f"C unrowed guest caller of osDestroyThread_recomp: {n}")
    stale += [f"C stale guest caller row {n}" for n in GUEST_CALLER_ROWS if n not in gcall]
    info["guest_destroy_callers"] = len(gcall)
    # H: host frames
    for f, sig, call, why in HOST_FRAMES:
        b = func_body(strip_comments(texts[f]), sig)
        if b is None or call not in b: stale.append(f"H frame gone {f}: {sig}"); continue
        before, after = b.rsplit(call, 1)[0], (b.rsplit(call, 1)[1] if not call.startswith("throw") else "")
        if "#else" in before and "#endif" in after: before = before.rsplit("#else", 1)[1]
        if LOCKY.search(before): opens.append(f"H non-RAII resource before the call in {sig.strip()}: {LOCKY.search(before).group(0)}")
        if FLAGSET.search(before): opens.append(f"H flag set before the call in {sig.strip()}: {FLAGSET.search(before).group(0)}")
        rest = re.sub(r"#\s*endif|[\s}]", "", after) if after else ""
        if rest and not call.startswith("throw"): opens.append(f"H code after the guest call in {sig.strip()}: {rest[:80]}")
        info["host_frames_ok"] += 1
    # F: flags
    fl = dict(flags_over or {})
    for p in FLAGS:
        t = fl.get(p) or (rd(p, over) if os.path.exists(os.path.join(ROOT, p)) else None)
        if t is None: opens.append(f"F flags.make missing: {p}"); continue
        for l in t.splitlines():
            if l.startswith(("C_FLAGS", "CXX_FLAGS")) and BADFLAG.search(l):
                opens.append(f"F {p}: {BADFLAG.search(l).group(0)} in {l.split('=')[0].strip()}")
        info["flag_files"] += 1
    # U: compact unwind per object
    objs = sorted(glob.glob(ROOT + "/build/CMakeFiles/RecompiledFuncs.dir/**/*.o", recursive=True) +
                  glob.glob(ROOT + "/build/CMakeFiles/PatchesLib.dir/**/*.o", recursive=True) +
                  glob.glob(ROOT + "/build/CMakeFiles/RogueSquadron64Recomp.dir/**/*.c.o", recursive=True)) + list(extra_objs or [])
    nsym = 0
    for o in objs:
        syms = set()
        for l in subprocess.run(["nm", "-m", o], capture_output=True, text=True).stdout.splitlines():
            m = re.match(r"([0-9a-f]+) \(__TEXT,__text\) (?:non-)?external (?:\(was a private external\) )?(_\w+)", l)
            if m: syms.add((int(m.group(1), 16), m.group(2)))
        starts = {int(x, 16) for x in re.findall(r"start:\s+0x([0-9a-f]+)", subprocess.run(
            ["objdump", "--unwind-info", o], capture_output=True, text=True).stdout)}
        miss = sorted(s for a, s in syms if a not in starts)
        nsym += len(syms)
        if miss: opens.append(f"U {os.path.relpath(o, ROOT)}: {len(miss)}/{len(syms)} text symbols lack compact unwind (e.g. {miss[0]})")
    info["objects"] = len(objs); info["text_symbols"] = nsym
    # P: paired host state on self-destroy stacks
    addr = {}
    for n, (b, _) in gb.items():
        m = re.search(r"// 0x([0-9A-F]{8}):", b)
        if m and n not in addr.values(): addr.setdefault(int(m.group(1), 16), n)
    edges = collections.defaultdict(set); unk = set()
    for n, (b, _) in gb.items():
        for m in CALLRE.finditer(b):
            if m.group(1) in names or m.group(1).endswith("_recomp"): edges[m.group(1)].add(n)
        for m in LOOKRE.finditer(b):
            a = m.group(1).strip()
            if re.fullmatch(r"0x[0-9A-Fa-f]+", a) and int(a, 16) in addr: edges[addr[int(a, 16)]].add(n)
            else: unk.add(n)

    def anc(seeds):
        seen, st = set(), list(seeds)
        while st:
            for p in edges.get(st.pop(), ()):
                if p not in seen: seen.add(p); st.append(p)
        return seen
    hp_open, hp_stale, hp_info, blockers = host_path(texts, over)
    opens += hp_open; stale += hp_stale; info.update(hp_info)
    seeds = sorted(x for x in blockers if any(re.search(r"\b" + re.escape(x) + r"\(rdram(, ctx)?\)", b) for b, _ in gb.values()))
    info["guest_seeds"] = len(seeds)
    for x in seeds:
        for n, (b, _) in gb.items():
            if re.search(r"\b" + re.escape(x) + r"\(rdram(, ctx)?\)", b): edges[x].add(n)
    A = anc(seeds); onpath = A | unk | anc(unk)
    info["ancestors_direct"] = len(A); info["indirect_callers"] = len(unk); info["onpath_conservative"] = len(onpath)
    stat_by_file = {}
    offp = []; used_p = set()
    for n, (b, f) in gb.items():
        if f not in stat_by_file: stat_by_file[f] = static_names(rd(f, over))
        for site in paired_sites(n, b, stat_by_file[f]):
            if n in onpath and (n, site[1]) in P_ROWS: info["p_ok_gated"] += 1; used_p.add((n, site[1]))
            elif n in onpath: opens.append(f"P paired host state across a guest call on a self-destroy stack: {site[0]} {site[1]}")
            else: offp.append(site)
    info["paired_offpath"] = len(offp)
    stale += [f"P stale row {k}" for k in P_ROWS if k not in used_p]
    if verbose:
        for s in offp: print("  P off-path", s[0], s[1])
    return opens, stale, info


def report(tag, r):
    o, s, i = r
    print(f"[{tag}] open={len(o)} stale={len(s)} " + " ".join(f"{k}={v}" for k, v in sorted(i.items())))
    for x in o + s: print("   ", x)


def controls():
    ok = 0
    thr = rd(THR, None)
    def opened(r, pat): return any(pat in x for x in r[0] + r[1])
    a = "void ultramodern::run_next_thread_and_wait("
    t1 = thr.replace(a, "void s7607_ctl() { throw ultramodern::thread_terminated{}; }\n" + a, 1); assert t1 != thr
    r = run(over={THR: t1})
    ok += c("1 unrowed throw", opened(r, "T unrowed throw") or opened(r, "T row matched twice"))
    t2 = thr.replace("        throw ultramodern::thread_terminated{};", "        s_mu.lock();\n        throw ultramodern::thread_terminated{};", 1); assert t2 != thr
    r = run(over={THR: t2})
    ok += c("2 non-RAII lock before throw", opened(r, "H non-RAII"))
    fm = rd(FLAGS[0], None).replace("C_FLAGS = -g", "C_FLAGS = -fno-exceptions -g", 1)
    r = run(flags_over={FLAGS[0]: fm}); ok += c("3 -fno-exceptions on RecompiledFuncs", opened(r, "F build/CMakeFiles/RecompiledFuncs"))
    r = run(rows=THROW_ROWS[1:]); ok += c("4 row dropped", opened(r, "T unrowed throw"))
    t5 = re.sub(r"try \{(\s*// Run the thread's function)", r"{\1", thr, count=1); assert t5 != thr
    r = run(over={THR: t5})
    ok += c("5 try removed before run_thread_function", opened(r, "not inside try") or opened(r, "stale root"))
    gf = sorted(glob.glob(GEN + "/funcs_*.c"))
    tgt = next(f for f in gf if "RECOMP_FUNC void unregisterServiceWorker(" in rd(f, None))
    t = rd(tgt, None)
    t0 = t; t = t.replace("osDestroyThread_recomp(rdram, ctx);", "s_s7607_ctl_busy = 1;\n    osDestroyThread_recomp(rdram, ctx);\n    s_s7607_ctl_busy = 0;", 1); assert t != t0
    t = "static int s_s7607_ctl_busy;\n" + t
    r = run(over={tgt: t}); ok += c("6 paired flag across destroy call", opened(r, "P paired host state"))
    d = tempfile.mkdtemp(prefix="s7607_"); src = os.path.join(d, "x.c")
    open(src, "w").write("void s7607_a(void(*f)(void)){f();f();}\nvoid s7607_b(void(*f)(void)){s7607_a(f);f();}\n")
    bad = os.path.join(d, "bad.o")
    subprocess.run(["clang", "-O2", "-arch", "arm64", "-fno-asynchronous-unwind-tables", "-fno-unwind-tables", "-c", src, "-o", bad], check=True)
    r = run(extra_objs=[bad]); ok += c("7 object without unwind tables", opened(r, "U " + os.path.relpath(bad, ROOT)))
    return ok


def c(name, fired):
    print(f"  control {name}: {'FIRED' if fired else 'MISSED'}"); return 1 if fired else 0


def witness():
    fm = rd(FLAGS[0], None)
    get = lambda k: next(l.split("=", 1)[1].split() for l in fm.splitlines() if l.startswith(k + " ="))
    cf, ci = get("C_FLAGS"), get("C_INCLUDES")
    inc = [x for x in ci] + ["-I" + os.path.join(ROOT, "lib/N64ModernRuntime/librecomp/include")]
    d = tempfile.mkdtemp(prefix="s7607w_"); arms = 0
    cxx = os.path.join(d, "h.o")
    subprocess.run(["clang++", "-std=c++20", "-O2", "-arch", "arm64", "-mmacosx-version-min=11.0"] + inc +
                   ["-c", os.path.join(ROOT, "tools/s7607_uw_witness.cpp"), "-o", cxx], check=True)
    for arm, extra, want in (("real-flags", [], 0), ("no-unwind-control", ["-fno-asynchronous-unwind-tables", "-fno-unwind-tables"], "nonzero")):
        o = os.path.join(d, arm + ".o"); exe = os.path.join(d, arm)
        subprocess.run(["clang"] + cf + extra + inc + ["-c", os.path.join(ROOT, "tools/s7607_uw_witness.c"), "-o", o], check=True)
        subprocess.run(["clang++", "-arch", "arm64", cxx, o, "-o", exe], check=True)
        p = subprocess.run([exe], capture_output=True, text=True)
        good = (p.returncode == 0) if want == 0 else (p.returncode != 0)
        print(f"  witness {arm}: rc={p.returncode} out={p.stdout.strip()} err={p.stderr.strip()[:80]} -> {'PASS' if good else 'FAIL'}")
        arms += good
    return arms


if __name__ == "__main__":
    r = run(verbose="-v" in sys.argv); report("s7607 UW", r)
    good = not r[0] and not r[1]
    if "--controls" in sys.argv:
        n = controls(); print(f"  controls {n}/7"); good = good and n == 7
    if "--witness" in sys.argv:
        n = witness(); print(f"  witness {n}/2"); good = good and n == 2
    sys.exit(0 if good else 1)
