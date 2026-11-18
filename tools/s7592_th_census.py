#!/usr/bin/env python3
"""s7592 class TH census: every thread / timer / queue creation site in OUR code, classified by lifetime.

Scope: src/, lib/N64ModernRuntime, lib/rt64/src incl. contrib/plume. Excluded: vendored SDL, contrib trees that are not linked
into the game (mupen64plus-core, imgui/im3d examples, zstd examples/contrib, allocator Tests, texture_packer tool), tests.

Site kinds: std::thread temporaries and named/static/assigned/new/make_unique handles, pthread_create, SDL_CreateThread,
dispatch_source_create / dispatch_queue_create, CFRunLoopTimerCreate, NSTimer scheduledTimer*, std::async.
Verdict per site:
  joined     handle stored (member / assigned / new / make_unique / local) and joined somewhere in the same file
  once       started at most once per process (static handle, call_once, atomic exchange/CAS guard, `if(!x){x=true` guard,
             static-initialiser lambda, or an ANNOT entry naming the once-only caller)
  transient  detached, body has no unbounded loop: the thread ends by itself (sleep + log / one system() call / finite loop)
  per-event  detached unbounded thread started from a path that can run many times  <- the leak shape
  unjoined   stored handle never joined/detached in its file (std::terminate at destruction, or leaks)
  unknown    the heuristics could not decide and no ANNOT entry covers it
gate = env-gated if the enclosing function reads getenv / an *_on() helper guards the start, else default.
--controls: classifies a planted file (joined, once x3, transient, per-event, unjoined, gated per-event) and exits nonzero on a
misclassification. Exit nonzero on any unknown row, or any per-event / unjoined row whose gate is default.
"""
import os, re, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s7591_mr_census import strip, enclosing  # same comment/string stripper and outermost-block finder

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRS = ["src", "lib/N64ModernRuntime", "lib/rt64/src"]
SKIP = re.compile(r"(/N64Recomp/lib/|/test/|/tests/|gtest|gmock|/SDL|/mupen64plus-core/|/examples/|/zstd/(contrib|examples|programs|tests)/|"
                  r"Tests\.cpp$|/tools/texture_packer/|/im3d/|/imgui/|/unit_tests/|/boost-[\d.]+/|/xxHash/tests/)")
EXTS = (".c", ".cc", ".cpp", ".h", ".hpp", ".m", ".mm")
SITE = re.compile(r"(?P<new>\bnew\s+std::thread\s*\()|(?P<mk>make_unique\s*<\s*std::thread\s*>\s*\()|"
                  r"(?P<st>\bstd::thread\b(?!\s*::)(?!\s*>)(?:\s+(?P<name>\w+))?\s*(?P<br>[({]))|"
                  r"(?P<api>\b(?:pthread_create|SDL_CreateThread|dispatch_source_create|dispatch_queue_create|CFRunLoopTimerCreate|"
                  r"scheduledTimerWithTimeInterval|std::async)\s*[(:])")
# Sites the heuristics cannot decide, verified by reading the code (file suffix, text on the site line, verdict, gate, why).
ANNOT = [
    ("ultramodern/src/threads.cpp", "thread_cleaner_thread = std::thread", "once", "default",
     "init_thread_cleanup() is called once from recomp start; the cleaner loops until `exited`"),
    ("ultramodern/src/threads.cpp", "context->host_thread = std::thread", "joined", "default",
     "one host thread per guest OSThread; thread_cleaner_func joins host_thread before deleting the context"),
    ("src/main/main.cpp", "std::thread(reader).detach(); std::thread(writer)", "once", "env-gated",
     "stderr-async switch_on(): reached once from the static init / the single delayed-switch thread"),
    ("src/main/rt64_render_context.cpp", "std::thread(worker).detach()", "once", "default",
     "flush_pend: `if (!started) { started = true; ...}` under the queue mutex"),
    ("upstream_compat.cpp", "if (first) std::thread", "once", "env-gated",
     "s7545 thread watch: `first` is the first-arm latch of the ROGUESQ_S7545 watch"),
    ("ultramodern/src/events.cpp", "std::thread{ [] {", "once", "env-gated",
     "AI Drain / AI Hz threads in init_events(), called once from ultrainit (s4450 / s4440 env knobs)"),
    ("src/main/main.cpp", "if (c && *c == '1') std::thread([] {", "once", "env-gated",
     "s7382_qos_start(): ROGUESQ_S7382_QOS_CTL control spinner, called once from main()"),
    ("ultramodern/src/timer.cpp", "timer_context.thread = std::thread", "once", "default",
     "init_timers() is called once from ultramodern::preinit/ultrainit; timer_thread loops for the process lifetime"),
    ("zstd/lib/common/threading.h", "pthread_create", "joined", "default",
     "ZSTD_pthread_create wrapper macro; its only user pool.c joins every worker in POOL_join (POOL_free)"),
    ("src/main/upstream_compat.cpp", "std::thread([rdram] {", "once", "env-gated",
     "rs64_s4230_poll_start: static atomic `started.exchange(true)` + rs64_s4222_on() at function entry"),
]

def lambda_body(s, i):
    """i at the '(' / '{' that opens the std::thread argument list -> text of the argument list"""
    op = s[i]; cl = ")" if op == "(" else "}"; d = 0
    for j in range(i, len(s)):
        if s[j] in "({": d += 1
        elif s[j] in ")}":
            d -= 1
            if d == 0: return s[i:j + 1], j + 1
    return s[i:], len(s)

def innermost_fn_start(s, pos, lo):
    """start of the innermost '{' block between lo and pos whose header looks like a function (has ')' before '{')"""
    stack = []
    for m in re.finditer(r"[{}]", s[lo:pos]):
        p = lo + m.start()
        if m.group() == "{": stack.append(p)
        elif stack: stack.pop()
    for p in reversed(stack):
        head = s[max(lo, p - 200):p].rstrip()
        if re.search(r"\)\s*(const\s*)?(noexcept\s*)?(->\s*[\w:<>*&\s]+)?$", head) and not re.search(r"\b(if|for|while|switch)\s*\([^;{}]*\)$", head) \
                and not re.search(r"\]\s*\([^;{}]*\)\s*(mutable\s*)?$", head):
            return p
    return lo

GUARD = re.compile(r"call_once\s*\(|\.exchange\s*\(\s*true|compare_exchange_(strong|weak)\s*\(|!\s*(?P<g>\w+)\s*\)\s*\{\s*(?P=g)\s*=\s*true|"
                   r"(\w+)\.exchange\s*\(\s*true")
INF = re.compile(r"for\s*\(\s*;\s*;\s*\)|while\s*\(\s*(true|1)\s*\)|while\s*\(\s*!|while\s*\(\s*[\w.:>-]+\s*(\.load\s*\(\s*\))?\s*\)|"
                 r"while\s*\(\s*[\w.:>-]+\s*\.load\(")

def classify(path, raw):
    s = strip(raw); rows = []
    for m in SITE.finditer(s):
        line = raw.count("\n", 0, m.start()) + 1  # raw: strip() can blank a newline inside a stray quote
        lo, hi = enclosing(s, m.start()); body = s[lo:hi]
        rawline = raw.splitlines()[line - 1] if line - 1 < len(raw.splitlines()) else ""
        stmt_lo = max(s.rfind(";", 0, m.start()), s.rfind("{", 0, m.start()), s.rfind("}", 0, m.start())) + 1
        stmt = s[stmt_lo:m.start()]
        fn_lo = innermost_fn_start(s, m.start(), lo); before = s[fn_lo:m.start()]
        if lo == 0 and hi == len(s): body = s[max(0, stmt_lo - 300):m.start() + 300]  # file scope: local window only
        gate = "env-gated" if ("getenv" in body or re.search(r"\b\w*_on\s*\(\s*\)", before)) else "default"
        kind = "api" if m.group("api") else "handle"
        v = "unknown"; why = ""
        if m.group("api"):
            api = re.match(r"[\w:]+", m.group("api")).group()
            if api == "std::async": v = "joined"; why = "std::async future joins at destruction"
            else: v = "unknown"; why = api
        else:
            br = m.end() - 1
            args, after = lambda_body(s, br)
            tail = s[after:after + 40]
            st2 = re.sub(r"std::\s*$", "", stmt.rstrip()).rstrip() if (m.group("mk") or m.group("new")) else stmt
            assigned = re.search(r"([\w\]\[]+)\s*(\.|->)?\s*$", st2.rstrip().rstrip("=").rstrip()) if re.search(r"=\s*$", st2) else None
            name = m.group("name") if m.group("st") else None
            if m.group("st") and name and re.search(r"\bstatic\b", stmt):
                v, why = "once", "static handle"
            elif assigned or name or m.group("new") or m.group("mk"):
                h = name or (assigned.group(1) if assigned else None)
                if h is None:
                    am = re.search(r"([\w]+)\s*(\.|->)?\s*=\s*(std::)?$", stmt.rstrip()) or re.search(r"([\w]+)\s*\.\s*push_back\s*\(\s*$", stmt)
                    h = am.group(1) if am else None
                if h:
                    h = re.sub(r"\[.*?\]", "", re.split(r"\.|->", h)[-1])
                    if re.search(rf"\b{re.escape(h)}\s*(\.|->)\s*join\s*\(", s) or re.search(rf"\b{re.escape(h)}\s*\)\s*\{{[^}}]*join", s) \
                            or re.search(rf"&\s*\w+\s*:\s*{re.escape(h)}\s*\)\s*\{{\s*\w+\s*(\.|->)\s*join", s):
                        v, why = "joined", f"{h}.join()"
                    elif re.search(rf"\b{re.escape(h)}\s*(\.|->)\s*detach\s*\(", s):
                        lam = re.search(r"\[[^\]]*\]\s*(\([^)]*\))?\s*(mutable\s*)?\{", args)
                        v = "transient" if (lam and not INF.search(args)) else ("once" if GUARD.search(before) else "per-event")
                        why = f"{h}.detach()" + ("" if lam else " named entry")
                    else:
                        v, why = "unjoined", f"no {h}.join()"
            elif re.match(r"\s*\.\s*detach\s*\(", tail):
                sinit = r"\bstatic\s+(const\s+)?(bool|int|std::atomic<\w+>)\s+\w+\s*=\s*\[[^\]]*\]\s*(\(\s*\))?\s*$"
                if GUARD.search(before) or re.search(r"\bstatic\s+(const\s+)?(bool|int|std::atomic<\w+>)\s+\w+\s*=\s*\[", before) \
                        or re.search(sinit, s[max(0, lo - 200):lo]):
                    v, why = "once", "guarded start"
                elif not INF.search(args) and re.search(r"\[[^\]]*\]\s*(\([^)]*\))?\s*(mutable\s*)?\{", args):
                    v, why = "transient", "detached, no unbounded loop"
                else:
                    v, why = "per-event", "detached unbounded or named entry, no once-guard"
        for suf, needle, av, ag, w in ANNOT:
            if path.endswith(suf) and needle in rawline:
                v, gate, why = av, ag, "ANNOT: " + w
        rows.append((path, line, v, gate, why))
    return rows

def walk():
    for d in DIRS:
        for r, _, fs in os.walk(os.path.join(ROOT, d)):
            for f in fs:
                p = os.path.join(r, f)
                if f.endswith(EXTS) and not SKIP.search(p): yield p

CTRL = r'''
#include <thread>
#include <cstdlib>
struct Joined { std::thread *t = nullptr; Joined(){ t = new std::thread([]{ for(;;){} }); } ~Joined(){ t->join(); delete t; } };
static std::thread s_once{[]{ for(;;){} }};
void once_call(){ static std::once_flag f; std::call_once(f, []{ std::thread([]{ for(;;){} }).detach(); }); }
void once_xchg(){ static std::atomic<bool> st{false}; if (st.exchange(true)) return; std::thread([]{ for(;;){} }).detach(); }
void transient(){ std::thread([]{ std::this_thread::sleep_for(std::chrono::seconds(1)); /* while(1) in a comment */ }).detach(); }
void per_event_leak(){ std::thread([]{ for(;;){ std::this_thread::sleep_for(std::chrono::seconds(1)); } }).detach(); }
struct Unj { std::thread w; Unj(){ w = std::thread{[]{}}; } };
void gated_leak(){ const char* e = std::getenv("X"); if (e) std::thread([]{ while (true) {} }).detach(); }
'''
CTRL_EXPECT = [("joined", "default"), ("once", "default"), ("once", "default"), ("once", "default"), ("transient", "default"),
               ("per-event", "default"), ("unjoined", "default"), ("per-event", "env-gated")]

def controls():
    d = tempfile.mkdtemp(prefix="s7592ctl"); p = os.path.join(d, "plant.cpp"); open(p, "w").write(CTRL)
    got = [(r[2], r[3]) for r in classify(p, CTRL)]
    ok = got == CTRL_EXPECT
    print(f"controls: {sum(g == e for g, e in zip(got, CTRL_EXPECT))}/{len(CTRL_EXPECT)} {'PASS' if ok else 'FAIL'}")
    if not ok:
        for g, e in zip(got, CTRL_EXPECT): print("  ", g, "expect", e)
        if len(got) != len(CTRL_EXPECT): print("   count", len(got), "expect", len(CTRL_EXPECT))
    return ok

def main():
    ok = controls() if "--controls" in sys.argv else True
    rows = []
    for p in sorted(walk()):
        try: raw = open(p, encoding="utf-8", errors="replace").read()
        except OSError: continue
        if SITE.search(strip(raw)): rows += classify(os.path.relpath(p, ROOT), raw)
    bad = 0
    for path, line, v, gate, why in rows:
        flag = "" if v in ("joined", "once", "transient") else (" <-- OPEN" if gate == "default" or v == "unknown" else " (gated)")
        bad += flag == " <-- OPEN"
        print(f"{path}:{line} {v} {gate}{(' [' + why + ']') if why else ''}{flag}")
    from collections import Counter
    c = Counter(r[2] for r in rows)
    print(f"rows={len(rows)} " + " ".join(f"{k}={c[k]}" for k in sorted(c)) +
          f" gated_per_event={sum(1 for r in rows if r[2] in ('per-event', 'unjoined') and r[3] == 'env-gated')} open={bad}")
    sys.exit(0 if ok and bad == 0 else 1)

if __name__ == "__main__":
    main()
