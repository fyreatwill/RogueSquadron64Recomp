#!/usr/bin/env python3
"""s7546 class GF census: host-side reads of OSThread fields through a pointer to a thread the guest may have destroyed.

s7545 v1 showed the guest frees a destroyed thread's OSThread (registerServiceWorker node, rs_malloc'd, OSThread at node+0x20;
unregisterServiceWorker unlinks + rs_free's it) and the heap reuses it within ~2 s, so any host read of that struct after
osDestroyThread sees guest data.  This tool enumerates every host read of an OSThread field (next/priority/queue/state/flags/id/
context/sp) in the port's host code and classifies it:

  H-live        the struct is the caller itself while running (thread_self, this_thread()), a thread popped/peeked from a queue
                (a destroyed thread is dequeued by osDestroyThread before its context is cleared), or a struct being created.
  H-cmp         reachable AFTER osDestroyThread(other) for that struct (the woken host thread: wait_for_resumed after
                running.wait(), _thread_func after its first wait) -- allowed only as an equality compare against the host
                context the thread captured itself; junk != mine -> self-destroy, which is the correct outcome for any value.
  H-guarded     after-destroy region, but on the true side of an `self->context == thread_context` compare (struct is live).
  H-diag        only inside an env-gated diagnostic/print (value printed or compared, never dereferenced as a host pointer).
  H-dead        unreachable in this game.
  OPEN          an after-destroy read that is not a compare (e.g. `->context->`), or a rule that says so.
  UNCLASSIFIED  no rule matches.

Guest side (B): every guest osDestroyThread/osSetThreadPri targets a node found by key in the live service-worker list
(0x801128D0, keys from the monotonic counter 0x801128D4; unregister unlinks BEFORE rs_free), so the guest never names a freed
struct; a missed key degenerates to node 0 -> r4=0x20 (retail-identical path), not to a stale struct.  Checked by regex on the
generated code when RS64_RECOMP_FUNCS is present.

Exit 0 iff 0 OPEN and 0 UNCLASSIFIED.  --controls: (1) planted `->context->` deref after the wait in wait_for_resumed -> OPEN;
(2) planted non-compare read of ->sp there -> OPEN; (3) a deleted rule -> UNCLASSIFIED; (4) the real tree -> rc 0;
(5) guest unregister with the unlink moved after rs_free -> B fails.
"""
import os, re, sys, glob

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(REPO, "lib", "N64ModernRuntime")
GEN = os.environ.get("RS64_RECOMP_FUNCS", os.path.join(os.path.dirname(REPO), "N64Recomp", "RecompiledFuncs"))
FIELDS = "next|priority|queue|state|flags|id|context|sp"
SRC_GLOBS = [os.path.join(LIB, "ultramodern", "src", "*.cpp"), os.path.join(LIB, "librecomp", "src", "*.cpp"),
             os.path.join(REPO, "src", "main", "*.cpp")]

# Functions whose code runs on a host thread that may have been woken by osDestroyThread(other): the region after the marker.
POST_DESTROY = {  # (file, func): regex of the line that starts the after-destroy region
    ("threads.cpp", "wait_for_resumed"): r"thread_context->running\.wait\(\)",
    ("threads.cpp", "_thread_func"): r"wait_for_resumed\(PASS_RDRAM thread_context\)",
}

# (file, func) -> (class, why); optional third element: regex the line must match (first matching rule wins).
RULES = [
    ("threads.cpp", "_thread_func", "H-guarded", "run_thread_function(self->sp) only on the true side of self->context == thread_context",
     r"self->sp"),
    ("threads.cpp", "_thread_func", "H-live", "before the first wait: struct was just created by osCreateThread (caller blocks on initialized)"),
    ("threads.cpp", "wait_for_resumed", "H-cmp", "this_thread()->context != thread_context -> osDestroyThread(NULL) self-terminate"),
    ("threads.cpp", "osDestroyThread", "H-live", "caller names a live list node (guest B); self path (incl. after-wake re-call) only prints under ROGUESQ_LOG_THREAD_RESUME and throws"),
    ("threads.cpp", "osCreateThread", "H-live", "struct being created"),
    ("threads.cpp", "osStartThread", "H-live", "fresh/stopped thread (s7544 C rows)"),
    ("threads.cpp", "osSetThreadPri", "H-live", "guest target is a live list node or self (guest B)"),
    ("threads.cpp", "osGetThreadPri", "H-live", "self or caller-named live thread"),
    ("threads.cpp", "osGetThreadId", "H-live", "self or caller-named live thread"),
    ("threads.cpp", "resume_thread_tagged", "H-live", "target popped from a queue / started; destroyed threads are dequeued before context=nullptr; context also checked against g_live_ctx"),
    ("threads.cpp", "run_next_thread", "H-live", "popped from running_queue / self"),
    ("threads.cpp", "run_next_thread_and_wait", "H-live", "thread_self while running"),
    ("threads.cpp", "resume_thread_and_wait", "H-live", "thread_self while running"),
    ("threads.cpp", "get_game_thread_name", "H-live", "called by _thread_func before the first wait"),
    ("threads.cpp", "sampler_loop", "H-diag", "ROGUESQ_LOG_S4586 sampler; context checked against g_live_ctx before use"),
    ("threads.cpp", "on_handoff", "H-diag", "ROGUESQ_LOG_S4586"),
    ("threads.cpp", "s4581_log_switch", "H-diag", "print only"),
    ("threads.cpp", "s4584_note", "H-diag", "print only"),
    ("threads.cpp", "s6983_guest_qos", "H-live", "self"),
    ("threads.cpp", "rogue_current_thread_id", "H-live", "thread_self id (guest-callable probe)"),
    ("scheduling.cpp", "s4583_dump", "H-diag", "ROGUESQ_LOG_S4583 print; cached t3 pointer is a guest address (rdram stays mapped), printed only"),
    ("scheduling.cpp", "schedule_running_thread", "H-live", "thread being readied (popped from a blocked list or started)"),
    ("scheduling.cpp", "swap_to_thread", "H-live", "self / running-queue head"),
    ("scheduling.cpp", "check_running_queue", "H-live", "self / running-queue head"),
    ("threadqueue.cpp", "thread_queue_insert", "H-live", "queue members + thread being inserted"),
    ("threadqueue.cpp", "thread_queue_pop", "H-live", "queue head"),
    ("threadqueue.cpp", "s7396_remove_fixed", "H-live", "queue members (destroyed thread removed here, before context cleared)"),
    ("threadqueue.cpp", "s7396_remove_old", "H-dead", "ROGUESQ_S7396_TQFIX=0 only"),
    ("threadqueue.cpp", "s7396_census", "H-diag", "ROGUESQ_S7396_TQ"),
    ("threadqueue.cpp", "s7396_control", "H-diag", "fake queue at 0x9FFE0000 control"),
    ("threadqueue.cpp", "thread_queue_remove", "H-diag", "debug_printf / ROGUESQ_S7396_TQ print"),
    ("mesgqueue.cpp", "*", "H-live", "this_thread() id in debug_printf"),
    ("pi.cpp", "*", "H-live", "this_thread() diagnostics"),
    ("main.cpp", "get_game_thread_name", "H-live", "called by _thread_func before the first wait"),
    ("upstream_compat.cpp", "osStopThread_recomp", "H-live", "guest stops a live thread (s7544 C rows)"),
    ("upstream_compat.cpp", "note", "H-diag", "ROGUESQ_S7393 print; blocked-list member compare"),
    ("upstream_compat.cpp", "control", "H-diag", "ROGUESQ_S7393_CTL fake waiter"),
    ("upstream_compat.cpp", "*", "H-live", "this_thread() id probes"),
    ("s7391_spwm.cpp", "*", "H-live", "this_thread() probes"),
]

FUNC_RE = re.compile(r"^(?![\s#}])(?!.*\b(?:if|while|for|switch)\s*\().*?\b([A-Za-z_]\w*(?:::\w+)*)\s*\((?:[^()]|\([^()]*\))*\)\s*(?:const\s*)?\{")
DECL_RE = re.compile(r"\bOSThread\s*\*\s*(?:const\s+)?(\w+)")
ACC_RE = re.compile(r"(TO_PTR\(OSThread,[^)]*\)\)?|\b\w+)\s*->\s*(" + FIELDS + r")\b")


def scan(path, text):
    """Rows: (file, func, lineno, var, field, line, post_destroy)."""
    base = os.path.basename(path)
    rows, depth, func, osvars, post_re, post = [], 0, None, set(), None, False
    for i, ln in enumerate(text.split("\n"), 1):
        code = ln.split("//")[0]
        if depth == 0:
            m = FUNC_RE.search(code)
            if m and "OSThread" not in m.group(1):
                func = m.group(1).split("::")[-1]
                osvars = set(DECL_RE.findall(code))
                pr = None
                for (f, fn), rx in POST_DESTROY.items():
                    if f == base and fn == func:
                        pr = rx
                post_re, post = pr, False
        if func:
            osvars |= set(DECL_RE.findall(code))
            for m in ACC_RE.finditer(code):
                var, field = m.group(1), m.group(2)
                if var.startswith("TO_PTR(OSThread") or var in osvars:
                    rows.append((base, func, i, var, field, ln.strip(), post))
            if post_re and re.search(post_re, code):
                post = True
        depth += code.count("{") - code.count("}")
        if depth <= 0:
            depth, func = 0, (None if depth == 0 and "}" in code else func)
    return rows


def classify(row, rules):
    base, func, i, var, field, line, post = row
    if "debug_printf(" in line:
        return "H-diag", "debug_printf compiles to nothing (ultramodern.hpp:186)"
    if post:
        # The after-destroy invariant is semantic, checked independently of the rule table.
        guarded = bool(re.search(r"self->context\s*==\s*thread_context", line))
        if field == "context" and re.search(r"->context\s*(?:!=|==)\s*thread_context", line) and "->context->" not in line:
            return ("H-cmp" if not guarded else "H-cmp"), "equality compare vs the thread's own captured context"
        if field == "context" and re.search(r"->context\s*=\s*nullptr", line):
            return "H-guarded", "store on the true side of the compare"
    for r in rules:
        f, fn, cls, why = r[:4]
        if f == base and (fn == func or fn == "*") and (len(r) < 5 or re.search(r[4], line)):
            if post and cls not in ("H-cmp", "H-guarded", "H-diag"):
                return "OPEN", "after-destroy read not a compare (%s rule %s)" % (fn, cls)
            if post and cls == "H-cmp":
                return "OPEN", "after-destroy read classed H-cmp but not an equality compare"
            if post and cls == "H-guarded" and not guarded_by_compare(row):
                return "OPEN", "after-destroy read outside the compare guard"
            return cls, why
    return "UNCLASSIFIED", "no rule"


_GUARD_LINES = {}


def guarded_by_compare(row):
    return _GUARD_LINES.get((row[0], row[1], row[2]), False)


def mark_guards(path, text):
    """Lines inside `if (self->context == thread_context) {` blocks."""
    base, depth_at, depth, func = os.path.basename(path), None, 0, None
    for i, ln in enumerate(text.split("\n"), 1):
        code = ln.split("//")[0]
        if depth == 0:
            m = FUNC_RE.search(code)
            if m:
                func = m.group(1).split("::")[-1]
        if depth_at is not None and depth > depth_at:
            _GUARD_LINES[(base, func, i)] = True
        if re.search(r"if\s*\(\s*self->context\s*==\s*thread_context\s*\)\s*\{", code):
            depth_at = depth
        depth += code.count("{") - code.count("}")
        if depth_at is not None and depth <= depth_at:
            depth_at = None if not re.search(r"if\s*\(\s*self->context", code) else depth_at
        if depth <= 0:
            depth = 0


def guest_check(gen):
    """B: unregisterServiceWorker unlinks the node before rs_free; set-pri/destroy walk the live list by key."""
    out = []
    files = glob.glob(os.path.join(gen, "funcs_*.c"))
    if not files:
        return [("guest", "SKIP", "no generated code at %s" % gen)]
    want = {"unregisterServiceWorker", "setServiceWorkerPriority", "registerServiceWorker"}
    bodies = {}
    for f in files:
        s = open(f, errors="replace").read()
        for m in re.finditer(r"RECOMP_FUNC void (\w+)\(uint8_t\* rdram, recomp_context\* ctx\) \{\n(.*?)\n;?\}\n", s, re.S):
            if m.group(1) in want:
                bodies[m.group(1)] = m.group(2)
    return guest_rules(bodies)


def guest_rules(bodies):
    out = []
    u = bodies.get("unregisterServiceWorker", "")
    asm = [l.strip()[3:] for l in u.split("\n") if l.strip().startswith("// 0x")]
    asm = list(dict.fromkeys(asm))
    def idx(p):
        for k, a in enumerate(asm):
            if re.search(p, a):
                return k
        return -1
    walk, dst, unl1, unl2, free = (idx(r"lw\s+\$v0, 0x0\(\$s0\)"), idx(r"jal\s+0x8002B480"), idx(r"sw\s+\$v0, 0x28D0\(\$v1\)"),
                                   idx(r"sw\s+\$v0, 0x18\(\$s1\)"), idx(r"jal\s+0x80001C98"))
    ok = min(walk, dst, unl1, unl2, free) >= 0 and walk < dst < unl1 < free and unl2 < free
    out.append(("unregisterServiceWorker", "H-live" if ok else "OPEN",
                "key walk %d < destroy %d < unlink %d/%d < rs_free %d" % (walk, dst, unl1, unl2, free)))
    p = bodies.get("setServiceWorkerPriority", "")
    ok = "lw          $a0, 0x28D0($v0)" in p and "lw          $v0, 0x0($a0)" in p and "osSetThreadPri_recomp" in p
    out.append(("setServiceWorkerPriority", "H-live" if ok else "OPEN", "walks live list 0x801128D0 by key"))
    r = bodies.get("registerServiceWorker", "")
    ok = "lw          $v0, 0x28D4($a0)" in r and "addiu       $v0, $v0, 0x1" in r and "sw          $v0, 0x0($s5)" in r
    out.append(("registerServiceWorker", "H-live" if ok else "OPEN", "key = ++counter 0x801128D4 (monotonic, never reused)"))
    return out


def census(overrides=None, rules=RULES, gen=GEN, quiet=False, guest_bodies=None):
    rows = []
    _GUARD_LINES.clear()
    for g in SRC_GLOBS:
        for p in sorted(glob.glob(g)):
            text = open(p, errors="replace").read()
            if overrides and os.path.basename(p) in overrides:
                text = overrides[os.path.basename(p)](text)
            if "OSThread" not in text:
                continue
            mark_guards(p, text)
            rows += scan(p, text)
    res = [(r, *classify(r, rules)) for r in rows]
    g = guest_rules(guest_bodies) if guest_bodies is not None else guest_check(gen)
    counts = {}
    for r, cls, why in res:
        counts[cls] = counts.get(cls, 0) + 1
    if not quiet:
        seen = set()
        for r, cls, why in res:
            k = (r[0], r[1], r[4], cls)
            if k in seen and cls not in ("OPEN", "UNCLASSIFIED"):
                continue
            seen.add(k)
            print("  %-20s %-26s L%-5d %-8s %-12s %s%s" % (r[0], r[1], r[2], r[4], cls, "[post] " if r[6] else "", why[:90]))
        for name, cls, why in g:
            print("  guest %-34s %-12s %s" % (name, cls, why))
    bad = counts.get("OPEN", 0) + counts.get("UNCLASSIFIED", 0) + sum(1 for x in g if x[1] == "OPEN")
    post = sum(1 for r, c, w in res if r[6])
    summ = "SUMMARY: rows=%d post_destroy=%d %s guest=%s bad=%d" % (
        len(res), post, " ".join("%s=%d" % kv for kv in sorted(counts.items())), ",".join(x[1] for x in g), bad)
    if not quiet:
        print(summ)
    return bad, counts, g, post


def controls():
    ok = 0
    tests = []
    # 1 planted ->context-> deref after the wait
    plant1 = {"threads.cpp": lambda t: t.replace("    thread_context->running.wait();\n",
              "    thread_context->running.wait();\n    TO_PTR(OSThread, ultramodern::this_thread())->context->running.signal();\n", 1)}
    b, c, g, _ = census(plant1, quiet=True)
    tests.append(("plant ->context-> deref after wake", c.get("OPEN", 0) >= 1))
    # 2 planted non-compare ->sp read after the wake
    plant2 = {"threads.cpp": lambda t: t.replace("    thread_context->running.wait();\n",
              "    thread_context->running.wait();\n    int32_t s7546_sp = TO_PTR(OSThread, ultramodern::this_thread())->sp;\n", 1)}
    b, c, g, _ = census(plant2, quiet=True)
    tests.append(("plant ->sp read after wake", c.get("OPEN", 0) >= 1))
    # 3 deleted rule
    rules = [r for r in RULES if r[1] != "resume_thread_tagged"]
    b, c, g, _ = census(rules=rules, quiet=True)
    tests.append(("deleted resume_thread_tagged rule -> UNCLASSIFIED", c.get("UNCLASSIFIED", 0) >= 1))
    # 4 real tree clean and the after-destroy region non-empty
    b, c, g, post = census(quiet=True)
    tests.append(("real tree rc 0 with post-destroy rows > 0", b == 0 and post >= 2))
    # 5 guest unlink after rs_free -> OPEN
    gb = {}
    files = glob.glob(os.path.join(GEN, "funcs_*.c"))
    if files:
        for f in files:
            s = open(f, errors="replace").read()
            for m in re.finditer(r"RECOMP_FUNC void (\w+)\(uint8_t\* rdram, recomp_context\* ctx\) \{\n(.*?)\n;?\}\n", s, re.S):
                if m.group(1) in ("unregisterServiceWorker", "setServiceWorkerPriority", "registerServiceWorker"):
                    gb[m.group(1)] = m.group(2)
        u = gb["unregisterServiceWorker"]
        # move every rs_free comment line to just after the destroy comment
        free_ln = "// 0x80007128: jal         0x80001C98"
        u2 = u.replace(free_ln, "", 1).replace("// 0x800070FC: jal         0x8002B480",
                                                 "// 0x800070FC: jal         0x8002B480\n    " + free_ln, 1)
        gb2 = dict(gb, unregisterServiceWorker=u2)
        b, c, g, _ = census(quiet=True, guest_bodies=gb2)
        tests.append(("guest rs_free before unlink -> OPEN", any(x[1] == "OPEN" for x in g)))
    else:
        tests.append(("guest control (no generated code)", False))
    for name, passed in tests:
        print("  control %-52s %s" % (name, "PASS" if passed else "FAIL"))
        ok += passed
    print("CONTROLS: %d/%d" % (ok, len(tests)))
    return ok == len(tests)


if __name__ == "__main__":
    if "--controls" in sys.argv:
        sys.exit(0 if controls() else 1)
    bad, *_ = census()
    sys.exit(1 if bad else 0)
