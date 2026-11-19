#!/usr/bin/env python3
"""s7544 class GE census: does any runtime replacement leave OSThread state / queue / priority in a form that differs from
libultra 2.0 AND that something reads?

Boring check first: the port's OSThreadState enum (ultramodern/ultra64.h) is STOPPED=0 QUEUED=1 RUNNING=2 BLOCKED=3, not
libultra's STOPPED=1 RUNNABLE=2 RUNNING=4 WAITING=8, and the port never stores RUNNING or BLOCKED at all (a running or
mesg-blocked thread keeps the QUEUED it got when it was last scheduled).  So every row "differs" in the stored value; what
matters is whether anything reads the field.  Sections:

  A  replacement transitions: every store to t->state / t->queue / t->priority and every queue op (thread_queue_insert /
     remove / pop, schedule_running_thread) in the thread replacements, each matched against a RULE that states the
     libultra transition and why the port's is equal or benign.  An op no rule covers -> OPEN; a function with ops and no
     rule -> unclassified.
  B  guest readers: every load/store in generated code (RecompiledFuncs/funcs_*.c) whose address resolves (straight-line
     lui/addiu propagation) into a static OSThread [base, base+0x30) of the 11 static game threads (thr-create log), plus
     every access at +0x20..+0x4F through the service-worker struct pointer in the worker functions (worker+0x20 is its
     OSThread).  Any hit -> OPEN unless a rule names it.  Port-owned fields: next 0, pri 4, queue 8, state 0x10, flags
     0x12, id 0x14, host context pointer 0x20..0x27, sp 0x28.
  C  call sites: every guest call of osStopThread / osDestroyThread / osSetThreadPri / osStartThread / osYieldThread with
     its r4 (target) resolved.  osStopThread is the risky one: the port's non-NULL branch never yields, so a non-NULL
     SELF stop would keep running (libultra parks it); the NULL branch yields without state=STOPPED, which a later
     osSetThreadPri/osDestroyThread would read (state!=STOPPED with queue NULL -> insert into queue 0).  Each site must
     show its target is not the calling thread (caller not reachable from the target thread's entry by direct calls), or
     the caller has no direct caller and no constant reference to its address (dead).

  python3 tools/s7544_ge_census.py             # rows + summary; exit 1 on OPEN / unclassified / empty section
  python3 tools/s7544_ge_census.py --controls  # planted mutations (see controls())
Limits (stated in the output): B resolves only constant addresses and the worker-struct functions; a thread pointer that
travels through the heap to other code is not followed.  C reachability follows direct calls only (LOOKUP_FUNC indirect
calls are not followed), so 'target thread cannot reach caller' is a direct-call-graph claim.
"""
import os, re, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s7538_gb_census as gb
import s7533_fz_census as fz

REPO = gb.REPO
GEN = os.environ.get("RS64_RECOMP_FUNCS", os.path.join(os.path.dirname(REPO), "N64Recomp", "RecompiledFuncs"))
U = "lib/N64ModernRuntime/ultramodern/"
HDR = U + "include/ultramodern/ultra64.h"
SRC = [U + "src/threads.cpp", U + "src/scheduling.cpp", U + "src/mesgqueue.cpp", "src/main/upstream_compat.cpp"]
FUNCS = {"osCreateThread", "osStartThread", "osStopThread", "osStopThread_recomp", "osDestroyThread", "osSetThreadPri",
         "osYieldThread_recomp", "do_send", "do_recv", "swap_to_thread", "schedule_running_thread", "run_next_thread",
         "check_running_queue", "_thread_func"}
OPRE = re.compile(r'\bt(?:->|_)?\w*->(state|queue|priority)\s*=(?!=)|->(state)\s*=(?!=)|\b(thread_queue_insert|thread_queue_remove'
                  r'|thread_queue_pop|schedule_running_thread)\s*\(')

# (fn) -> list of (op regex, libultra transition, verdict, why).  Every op in the body must match one entry.
RULES = {
    "osCreateThread": [
        (r't->queue = NULLPTR', "-> STOPPED, queue NULL", "H-equal", "libultra osCreateThread: next=queue=NULL"),
        (r't->priority = pri', "pri := arg", "H-equal", "same"),
        (r't->state = OSThreadState::STOPPED', "state := OS_STATE_STOPPED", "H-benign",
         "value 0 vs libultra 1, flags not zeroed: no guest reader (section B)")],
    "osStartThread": [
        (r'ultramodern::schedule_running_thread\(PASS_RDRAM t_\)', "STOPPED/WAITING -> RUNNABLE on run queue", "H-benign",
         "libultra re-blocks a STOPPED thread whose t->queue is a mesg queue (WAITING); the port makes it runnable and the "
         "blocked do_recv/do_send resumes inside while(MQ_IS_EMPTY/FULL), re-tests and re-queues itself (GD rows), so "
         "the observable outcome is the same; no state precondition check, but section C shows one start per create"),
        (r't->state = OSThreadState::QUEUED;\s*resume_thread_tagged', "init start -> RUNNABLE", "H-equal",
         "runtime init path (no guest thread running)")],
    "osStopThread": [],  # upstream version: overridden by osStopThread_recomp (no state/queue ops)
    "osStopThread_recomp": [
        (r'ultramodern::thread_queue_remove\(PASS_RDRAM t->queue, t_\)', "RUNNABLE/WAITING -> STOPPED, dequeued", "H-equal",
         "__osDequeueThread(t->queue, t); t->queue left as libultra leaves it"),
        (r't->state = OSThreadState::STOPPED', "state := STOPPED", "H-equal",
         "same transition; the non-NULL SELF case (libultra parks, port returns) is excluded per call site in section C")],
    "osDestroyThread": [
        (r'ultramodern::thread_queue_remove\(PASS_RDRAM t->queue, t_\)', "non-STOPPED -> dequeued, destroyed", "H-equal",
         "libultra __osDequeueThread(t->queue, t) for RUNNABLE/WAITING")],
    "osSetThreadPri": [
        (r't->priority = pri', "pri := arg", "H-equal", "same"),
        (r'ultramodern::thread_queue_remove\(PASS_RDRAM t->queue, t_\);\s*ultramodern::thread_queue_insert\(PASS_RDRAM t->queue, t_\)',
         "RUNNABLE/WAITING other -> re-sorted in t->queue", "H-equal",
         "needs state!=STOPPED => t->queue!=NULL; the only way to break it is osStopThread(NULL) (state left QUEUED, queue "
         "NULL), which section C shows has no caller")],
    "schedule_running_thread": [
        (r'thread_queue_insert\(PASS_RDRAM running_queue, t_\);\s*t->state = OSThreadState::QUEUED', "-> RUNNABLE on run queue",
         "H-benign", "value 1 vs libultra 2: no guest reader")],
    "swap_to_thread": [
        (r'thread_queue_insert\(PASS_RDRAM ultramodern::running_queue, ultramodern::this_thread\(\)\);\s*TO_PTR\(OSThread, '
         r'ultramodern::this_thread\(\)\)->state = OSThreadState::QUEUED', "RUNNING -> RUNNABLE (preempted)", "H-benign",
         "same transition, value 1 vs 2")],
    "check_running_queue": [
        (r'ultramodern::thread_queue_pop\(PASS_RDRAM running_queue\)', "head RUNNABLE -> RUNNING", "H-benign",
         "pop clears queue (libultra __osPopThread does not; nothing reads it, B); state left QUEUED vs RUNNING")],
    "run_next_thread": [
        (r'ultramodern::thread_queue_pop\(PASS_RDRAM ultramodern::running_queue\)', "head RUNNABLE -> RUNNING", "H-benign",
         "as check_running_queue")],
    "do_send": [
        (r'thread_queue_insert\(PASS_RDRAM GET_MEMBER\(OSMesgQueue, mq_, blocked_on_send\)', "RUNNING -> WAITING on mq->fullqueue",
         "H-benign", "state stays QUEUED (vs WAITING 8): no guest reader; t->queue names the mq list as in libultra"),
        (r'schedule_running_thread\(PASS_RDRAM ultramodern::thread_queue_pop\(PASS_RDRAM blocked_queue\)\)',
         "WAITING head -> RUNNABLE", "H-equal", "__osEnqueueThread(&__osRunQueue, __osPopThread(&mq->mtqueue))")],
    "do_recv": [
        (r'thread_queue_insert\(PASS_RDRAM GET_MEMBER\(OSMesgQueue, mq_, blocked_on_recv\)', "RUNNING -> WAITING on mq->mtqueue",
         "H-benign", "as do_send"),
        (r'schedule_running_thread\(PASS_RDRAM ultramodern::thread_queue_pop\(PASS_RDRAM blocked_queue\)\)',
         "WAITING head -> RUNNABLE", "H-equal", "as do_send")],
    "osYieldThread_recomp": [],   # host yield only: no guest state touched (s7381: 0 calls in play)
    "_thread_func": [],
}

# static game threads (struct, entry fn, id/pri) from [thr-create-id] (every soak log agrees)
STATIC_THREADS = {0x80163E20: "mainBootstrapWorker", 0x80154B40: "0x80004360", 0x80154710: "0x80005570",
                  0x8010D3D0: "0x80001088", 0x8010DDA0: "0x800016AC", 0x801494B0: "0x8008ED70", 0x8011CED8: "0x8001C328",
                  0x8011DA98: "0x80019BF4", 0x8010FF70: "siServiceThread", 0x8011CD28: "0x80019868", 0x8010D218: "0x800017A0"}
WORKER_FNS = ("registerServiceWorker", "stopServiceWorker", "unregisterServiceWorker", "setServiceWorkerPriority")
B_RULES = {}   # (fn, addr) -> why ; none needed when B is empty
# C: osStopThread call sites -> how the target is shown not to be self
C_RULES = {
    "mainBootstrapWorker": ("other", 0x8010D3D0, "runs on thread 0x80163E20 (entry 0x80000C68 = mainBootstrapWorker); stops "
                            "the creator thread 0x8010D3D0"),
    "waitForSerialIdle": ("other", 0x8010FF70, "stops siServiceThread (0x8010FF70); siServiceThread cannot reach "
                          "waitForSerialIdle by direct calls"),
    "stopServiceWorker": ("dead", None, "no direct caller and no constant reference to its address"),
}
THREAD_ENTRY = {0x8010FF70: "siServiceThread"}
# C: osStartThread preconditions.  libultra ignores a start on a RUNNABLE/RUNNING thread; the port's schedule_running_thread
# would link it into the run queue a second time.  So every start site must target a fresh (just created) or stopped thread.
START_WRAPPERS = {   # wrapper fn -> (kind, data, why)
    "releaseSerialLock": ("seq", {"initSaveData": "WRWRWRR", "saveLoadDispatcher": "WR", "loadOrSaveEepromRecord": "WR",
                                  "loadOrSaveAllEepromRecords": "WR"},
                          "restarts siServiceThread stopped by waitForSerialIdle; per caller the W/R order is fixed (the RR "
                          "tail of initSaveData is the two branches of the third W's osEepromLongWrite result)"),
    "startServiceWorker": ("after", "registerServiceWorker", "each caller registers (osCreateThread) the worker first"),
    "restartServiceWorker": ("dead", None, "no direct caller and no constant reference to its address"),
}


def hdr_enum(over):
    t = gb.read(HDR, over)
    m = re.search(r'typedef enum \{\s*STOPPED,\s*QUEUED,\s*RUNNING,\s*BLOCKED\s*\}\s*OSThreadState;', t)
    return "STOPPED=0 QUEUED=1 RUNNING=2 BLOCKED=3" if m else None


def section_a(over=None, rules=None):
    over = over or {}
    rules = RULES if rules is None else rules
    rows, seen = [], set()
    for p in SRC:
        t = gb.read(p, over)
        for o, c, name in fz.func_spans(t):
            if name not in FUNCS or (name, p) in seen:
                continue
            seen.add((name, p))
            body = t[o:c + 1]
            ops = [(m.start(), body[m.start():m.start() + 70].split("\n")[0].strip()) for m in OPRE.finditer(body)]
            if name not in rules:
                rows.append((p, name, "-", "unclassified" if ops else "H-none", "no rule" if ops else "no ops"))
                continue
            covered = set()
            for rx, lib, verdict, why in rules[name]:
                ms = list(re.finditer(rx, body))
                if not ms:
                    rows.append((p, name, lib, "FAIL", "rule regex no longer matches: " + rx[:60]))
                    continue
                for m in ms:
                    covered |= {o2 for o2, _ in ops if m.start() <= o2 < m.end()}
                rows.append((p, name, lib, verdict, why))
            for o2, txt in ops:
                if o2 not in covered:
                    rows.append((p, name, "?", "OPEN", "uncovered op: " + txt))
    return rows


ASG = re.compile(r'^\s*ctx->r(\d+)\s*=\s*(.*?);\s*$')
MEMRE = re.compile(r'\bMEM_(W|H|HU|B|BU|D)\((?:(-?0X[0-9A-F]+|-?\d+),\s*ctx->r(\d+)|ctx->r(\d+),\s*(-?0X[0-9A-F]+|-?\d+))\)', re.I)


def ival(s):
    return int(s, 16) if s.upper().lstrip("-").startswith("0X") and not s.startswith("-") else (
        -int(s[1:], 16) if s.startswith("-0X") or s.startswith("-0x") else int(s))


def rval(lines, names, i, r, depth=0):
    """Backward straight-line constant resolver (lui / addiu / ori / move) inside one function, stopping at labels."""
    if r == 0:
        return 0
    fn = names[i]
    for j in range(i - 1, max(-1, i - 60), -1):
        if names[j] != fn or re.match(r'^\s*L_[0-9A-F]+:', lines[j]):
            return None
        m = ASG.match(lines[j])
        if not m or int(m.group(1)) != r:
            if re.search(r'\bctx->r%d\s*=' % r, lines[j]) or re.search(r'^\s*\w+\(rdram, ctx\);', lines[j]):
                return None
            continue
        e = m.group(2).strip()
        if depth > 6:
            return None
        k = re.fullmatch(r'S32\(0X([0-9A-F]+)u? << 16\)', e, re.I)
        if k:
            return (int(k.group(1), 16) << 16) & 0xFFFFFFFF
        k = re.fullmatch(r'ADD32\(ctx->r(\d+), (-?0X[0-9A-F]+|-?\d+)\)', e, re.I) or re.fullmatch(r'ADD32\((0), (-?0X[0-9A-F]+|-?\d+)\)', e, re.I)
        if k:
            base = 0 if k.group(1) == "0" and "ctx->r" not in e else rval(lines, names, j, int(k.group(1)), depth + 1)
            return None if base is None else (base + ival(k.group(2))) & 0xFFFFFFFF
        k = re.fullmatch(r'ctx->r(\d+) \| (0X[0-9A-F]+)', e, re.I)
        if k:
            base = rval(lines, names, j, int(k.group(1)), depth + 1)
            return None if base is None else base | int(k.group(2), 16)
        return None
    return None


def load_gen(gen, extra):
    files = [(f, open(f, errors="replace").read()) for f in sorted(glob.glob(os.path.join(gen, "funcs_*.c")))] + (extra or [])
    lines, names = [], []
    for f, t in files:
        cur = "<file>"
        for ln in t.split("\n"):
            m = re.match(r'RECOMP_FUNC void (\w+)\(', ln)
            if m:
                cur = m.group(1)
            lines.append(ln)
            names.append(cur)
    return lines, names


def section_b(lines, names):
    rows = []
    for i, ln in enumerate(lines):
        if "MEM_" not in ln or "rs64_" in ln.split("MEM_")[0][-30:]:
            continue
        for m in MEMRE.finditer(ln):
            off, reg = (m.group(2), m.group(3)) if m.group(2) else (m.group(5), m.group(4))
            reg = int(reg)
            fn = names[i]
            if fn in WORKER_FNS and reg not in (29,):
                o = ival(off)
                if 0x20 <= o < 0x50:
                    rows.append((fn, i, "worker+0x%X" % o, "OPEN" if (fn, o) not in B_RULES else "H-ruled", ln.strip()[:90]))
                continue
            if reg == 29:
                continue
            base = rval(lines, names, i, reg)
            if base is None:
                continue
            a = (base + ival(off)) & 0xFFFFFFFF
            for t in STATIC_THREADS:
                if t <= a < t + 0x30:
                    rows.append((fn, i, "0x%08X=thr0x%08X+0x%X" % (a, t, a - t), B_RULES.get((fn, a), "OPEN"), ln.strip()[:90]))
    return rows


def callgraph(lines, names):
    g = {}
    for i, ln in enumerate(lines):
        m = re.match(r'^\s*(\w+)\(rdram, ctx\);', ln)
        if m:
            g.setdefault(names[i], set()).add(m.group(1))
    return g


def reach(g, root):
    seen, st = set(), [root]
    while st:
        f = st.pop()
        if f in seen:
            continue
        seen.add(f)
        st.extend(g.get(f, ()))
    return seen


def fn_vram(gen, fn):
    try:
        t = open(os.path.join(gen, "recomp_overlays.inl")).read()
    except OSError:
        return None
    m = re.search(r'\.func = %s, \.offset = 0x([0-9A-F]+)' % re.escape(fn), t)
    return int(m.group(1), 16) + 0x80000440 if m else None


def calls_in(lines, names, fn, wanted):
    return [(i, m.group(1)) for i, ln in enumerate(lines) if names[i] == fn
            for m in [re.match(r'^\s*(%s)(?:_recomp)?\(rdram, ctx\);' % "|".join(wanted), ln)] if m]


def is_dead(lines, gen, fn, callers):
    va = fn_vram(gen, fn)
    refs = va is not None and any(re.search(r'ADD32\(ctx->r\d+, 0X%X\)' % (va & 0xFFFF), ln2) for ln2 in lines)
    return not callers.get(fn) and va is not None and not refs


def start_row(lines, names, i, fn, ts, g, callers, gen):
    api = "osStartThread"
    prior = [k for k, w in calls_in(lines, names, fn, ["osCreateThread"]) if k < i]
    if prior:
        return (api, fn, ts, "H-fresh", "osCreateThread earlier in the same function")
    if fn not in START_WRAPPERS:
        return (api, fn, ts, "unclassified", "start of a thread not created here; no wrapper rule")
    kind, data, why = START_WRAPPERS[fn]
    ok = True
    if kind == "dead":
        ok = is_dead(lines, gen, fn, callers)
    elif kind == "after":
        for c in sorted(callers.get(fn, ())):
            seq = calls_in(lines, names, c, [data, fn])
            first = [w for _, w in seq]
            ok = ok and bool(first) and first[0] == data
        ok = ok and bool(callers.get(fn))
    elif kind == "seq":
        got = {}
        for c in sorted(callers.get(fn, ())):
            got[c] = "".join("W" if w == "waitForSerialIdle" else "R" for _, w in calls_in(lines, names, c, ["waitForSerialIdle", fn]))
        ok = got == data
        if not ok:
            why = "W/R order changed: %s" % got
    return (api, fn, ts, "H-stopped-or-fresh" if ok else "OPEN", why)


def section_c(lines, names, gen):
    g = callgraph(lines, names)
    callers = {}
    for f, cs in g.items():
        for c in cs:
            callers.setdefault(c, set()).add(f)
    rows = []
    for i, ln in enumerate(lines):
        m = re.match(r'^\s*(osStopThread|osDestroyThread|osSetThreadPri|osStartThread|osYieldThread)_recomp\(rdram, ctx\);', ln)
        if not m:
            continue
        api, fn = m.group(1), names[i]
        tgt = rval(lines, names, i, 4)
        ts = "?" if tgt is None else "0x%08X" % tgt
        if api == "osStartThread":
            rows.append(start_row(lines, names, i, fn, ts, g, callers, gen))
            continue
        if api != "osStopThread":
            v = {"osYieldThread": "H-benign (host yield only, guest state untouched)",
                 "osSetThreadPri": "H-equal (self when 0, else worker re-sort: A rule)",
                 "osDestroyThread": "H-equal (A rule; self-destroy throws thread_terminated)",
                 }[api]
            rows.append((api, fn, ts, v.split(" ")[0], v))
            continue
        if tgt == 0:
            rows.append((api, fn, ts, "OPEN", "osStopThread(NULL): port yields without state=STOPPED"))
            continue
        rule = C_RULES.get(fn)
        if rule is None:
            rows.append((api, fn, ts, "unclassified", "no C rule"))
            continue
        kind, want, why = rule
        ok = True
        if kind == "other":
            ok = tgt == want and fn not in reach(g, THREAD_ENTRY.get(want, "<none>")) if want in THREAD_ENTRY else tgt == want
            if want == 0x8010D3D0:   # caller must be the thread entry of a different static thread
                ok = ok and STATIC_THREADS.get(0x80163E20) == fn
        elif kind == "dead":
            ok = is_dead(lines, gen, fn, callers)
        rows.append((api, fn, ts, "H-not-self" if ok else "OPEN", why if ok else "rule check failed: " + why))
    return rows


def census(over=None, rules=None, gen=GEN, extra=None, quiet=False):
    over = over or {}
    enum = hdr_enum(over)
    a = section_a(over, rules)
    lines, names = load_gen(gen, extra)
    b = section_b(lines, names)
    c = section_c(lines, names, gen)
    bad = [r for r in a if r[3] in ("OPEN", "unclassified", "FAIL")] + [r for r in b if r[3] == "OPEN"] + \
          [r for r in c if r[3] in ("OPEN", "unclassified")]
    if not quiet:
        print("enum:", enum or "CHANGED (re-check every H-benign value row)")
        print("== A replacement transitions (%d rows)" % len(a))
        for r in a:
            print("  %-22s %-24s %-14s %-40s %s" % (os.path.basename(r[0]), r[1], r[3], r[2][:40], r[4][:110]))
        print("== B guest accesses into OSThread fields (%d rows; %d static threads, worker fns %s)" %
              (len(b), len(STATIC_THREADS), ",".join(WORKER_FNS)))
        for r in b:
            print("  %-28s %-28s %s  %s" % (r[0], r[2], r[3], r[4]))
        print("== C thread-API call sites (%d rows)" % len(c))
        for r in c:
            print("  %-15s %-26s r4=%-11s %-12s %s" % r)
        print("LIMITS: B follows constant addresses + worker fns only; C reachability is direct calls only.")
        print("SUMMARY: A=%d B=%d C=%d bad=%d enum=%s" % (len(a), len(b), len(c), len(bad), "ok" if enum else "CHANGED"))
    return a, b, c, bad, enum


def controls():
    import copy, tempfile
    res = []
    def run(name, cond):
        res.append((name, bool(cond)))
        print("control %-44s %s" % (name, "PASS" if cond else "FAIL"))
    # 1 planted state store in osSetThreadPri -> OPEN
    p = os.path.join(REPO, U + "src/threads.cpp")
    t = open(p).read()
    t2 = t.replace("        t->priority = pri;\n", "        t->priority = pri;\n        t->state = OSThreadState::RUNNING;\n", 1)
    tmp = tempfile.NamedTemporaryFile("w", suffix=".cpp", delete=False); tmp.write(t2); tmp.close()
    a = section_a({U + "src/threads.cpp": tmp.name})
    run("planted state store -> A OPEN", any(r[3] == "OPEN" and r[1] == "osSetThreadPri" for r in a))
    # 2 deleted rule -> unclassified
    rr = dict(RULES); del rr["osDestroyThread"]
    run("deleted rule -> A unclassified", any(r[3] == "unclassified" and r[1] == "osDestroyThread" for r in section_a({}, rr)))
    # 3 rule regex drift -> FAIL
    rr = dict(RULES); rr["osCreateThread"] = RULES["osCreateThread"] + [(r'never_present_xyz', "-", "H-equal", "-")]
    run("stale rule regex -> A FAIL", any(r[3] == "FAIL" for r in section_a({}, rr)))
    # fixtures for B / C
    fx = ("fixture.c", "RECOMP_FUNC void plantReader(uint8_t* rdram, recomp_context* ctx) {\n"
          "    ctx->r4 = S32(0X8011 << 16);\n    ctx->r4 = ADD32(ctx->r4, -0X90);\n"
          "    ctx->r2 = MEM_HU(ctx->r4, 0X10);\n;}\n"
          "RECOMP_FUNC void plantNullStop(uint8_t* rdram, recomp_context* ctx) {\n    ctx->r4 = ADD32(0, 0);\n"
          "    osStopThread_recomp(rdram, ctx);\n;}\n"
          "RECOMP_FUNC void plantCaller(uint8_t* rdram, recomp_context* ctx) {\n    stopServiceWorker(rdram, ctx);\n"
          "    waitForSerialIdleFake(rdram, ctx);\n;}\n"
          "RECOMP_FUNC void siServiceThread(uint8_t* rdram, recomp_context* ctx) {\n    waitForSerialIdle(rdram, ctx);\n;}\n")
    a, b, c, bad, _ = census(extra=[fx], quiet=True)
    run("planted guest state read -> B OPEN", any(r[0] == "plantReader" and r[3] == "OPEN" for r in b))
    run("planted osStopThread(NULL) -> C OPEN", any(r[1] == "plantNullStop" and r[3] == "OPEN" for r in c))
    run("planted stopServiceWorker caller -> C OPEN", any(r[1] == "stopServiceWorker" and r[3] == "OPEN" for r in c))
    run("si thread reaches waitForSerialIdle -> C OPEN", any(r[1] == "waitForSerialIdle" and r[3] == "OPEN" for r in c))
    fx2 = ("fixture2.c", "RECOMP_FUNC void plantStart(uint8_t* rdram, recomp_context* ctx) {\n    osStartThread_recomp(rdram, ctx);\n;}\n"
           "RECOMP_FUNC void plantRelease(uint8_t* rdram, recomp_context* ctx) {\n    releaseSerialLock(rdram, ctx);\n;}\n"
           "RECOMP_FUNC void plantRestart(uint8_t* rdram, recomp_context* ctx) {\n    restartServiceWorker(rdram, ctx);\n;}\n")
    a, b, c, bad, _ = census(extra=[fx2], quiet=True)
    run("planted bare osStartThread -> C unclassified", any(r[1] == "plantStart" and r[3] == "unclassified" for r in c))
    run("unpaired releaseSerialLock -> C OPEN", any(r[1] == "releaseSerialLock" and r[3] == "OPEN" for r in c))
    run("caller of restartServiceWorker -> C OPEN", any(r[1] == "restartServiceWorker" and r[3] == "OPEN" for r in c))
    # positive control for the B resolver on the real tree: the guest's own stores of the thread pointer argument
    # (osCreateThread a0 = 0x8010FF70 in startSiPollingThread) must resolve
    lines, names = load_gen(GEN, None)
    hit = 0
    for i, ln in enumerate(lines):
        if names[i] == "startSiPollingThread" and "osCreateThread_recomp(rdram" in ln:
            hit = rval(lines, names, i, 4) == 0x8010FF70 or hit
    run("resolver finds si thread arg 0x8010FF70", hit)
    hit2 = False
    for i, ln in enumerate(lines):
        if names[i] == "waitForSerialIdle" and "MEM_BU(ctx->r3, 0X741)" in ln:
            hit2 = rval(lines, names, i, 3) == 0x80110000 or hit2
    run("resolver resolves real load 0x80110741", hit2)
    # enum drift detection
    h = open(os.path.join(REPO, HDR)).read().replace("    STOPPED,\n    QUEUED,", "    STOPPED = 1,\n    QUEUED,", 1)
    tmp2 = tempfile.NamedTemporaryFile("w", suffix=".h", delete=False); tmp2.write(h); tmp2.close()
    run("enum change detected", hdr_enum({HDR: tmp2.name}) is None)
    os.unlink(tmp.name); os.unlink(tmp2.name)
    n = sum(1 for _, ok in res if ok)
    print("controls %d/%d" % (n, len(res)))
    return n == len(res)


def main():
    if "--controls" in sys.argv:
        sys.exit(0 if controls() else 1)
    a, b, c, bad, enum = census()
    sys.exit(0 if (not bad and a and c and enum) else 1)


if __name__ == "__main__":
    main()
