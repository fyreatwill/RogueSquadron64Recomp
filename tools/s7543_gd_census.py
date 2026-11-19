#!/usr/bin/env python3
"""s7543 class GD census: can another guest thread observe a half-updated guest struct because the port YIELDS somewhere
hardware cannot?

Guest threads run one at a time (one run token, handed over by resume_thread_tagged -> running.signal()), so a guest thread
only loses the CPU at an explicit yield.  Class GC (s7542) showed every host write into guest RAM is ordered vs its signal;
GD asks whether any yield splits two dependent guest-struct stores.  On hardware a thread loses the CPU (a) inside an OS
call that blocks or wakes a higher-priority thread, or (b) at an interrupt, which cannot land inside __osDisableInt ..
__osRestoreInt.  In this port __osDisableInt/__osRestoreInt are no-ops (ultra_translation.cpp), so the census has three
sections:

  A  runtime replacements (every GC H-guest-thread function + every runtime function that calls a yield primitive):
     guest-struct stores (S) and yields (Y, one level of callee followed) in body order.
       H-atomic      no yield, or every yield after the last store (tail yield: the struct is complete when it yields)
       H-yield-safe  a non-tail yield inside a span a rule names, with the invariant that makes the struct consistent there
                     (e.g. do_send blocks inside `while (MQ_IS_FULL(mq))`: nothing of the queue is written yet and the
                     condition is re-read after every resume)
       H-def         a yield primitive itself; checked: nothing touches guest memory between the run-token hand-off
                     (running.signal) and the caller's park (running.wait), so the outgoing host thread cannot overlap
       H-torn-OPEN   a non-tail yield no rule covers
  B  guest critical sections in generated code: every __osDisableInt_recomp .. __osRestoreInt_recomp region must contain
     no call (H-no-call), and every cop0_status_write must be the FR-bit (0x04000000) FPU-mode toggle (not-int), not an
     IE/EXL change.  Otherwise OPEN.
  C  yields the port injected into guest code (yield_self*, rs64_preempt_point, check_running_queue, ... in
     RecompiledFuncs/funcs_*.c): each must lie outside every B region (H-int-enabled: hardware could take an interrupt
     and switch threads at that instruction too).  Inside a region -> OPEN.

  python3 tools/s7543_gd_census.py             # rows + summary; exit 1 on OPEN / FAIL / empty section
  python3 tools/s7543_gd_census.py --controls  # planted mutations (see controls())
"""
import os, re, sys, glob, tempfile
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s7538_gb_census as gb
import s7533_fz_census as fz
import s7542_gc_census as gc

REPO = gb.REPO
GEN = os.environ.get("RS64_RECOMP_FUNCS", os.path.join(os.path.dirname(REPO), "N64Recomp", "RecompiledFuncs"))
U = "lib/N64ModernRuntime/ultramodern/src/"
RT_FILES = [U + f for f in ("mesgqueue.cpp", "threads.cpp", "scheduling.cpp", "threadqueue.cpp", "timer.cpp", "events.cpp",
                            "input.cpp")] + ["lib/N64ModernRuntime/librecomp/src/" + f for f in ("pi.cpp", "cont.cpp", "sp.cpp",
                            "ultra_translation.cpp")] + ["src/main/upstream_compat.cpp"]
PRIM = ("run_next_thread_and_wait", "resume_thread_and_wait", "wait_for_resumed", "swap_to_thread", "check_running_queue",
        "yield_self", "yield_self_1ms", "pause_self", "rs64_preempt_point", "wait_for_external_message",
        "wait_for_external_message_timed", "s7195_refused_block_recv")
YRE = re.compile(r'(?<![\w.>:])(?:ultramodern::)?(%s)\s*\(' % "|".join(PRIM))
SRE = re.compile(r'->\s*\w+(?:\[[^]]*\])?\s*(?:[-+|&^]?=(?!=)|\+\+|--)|\bMEM_[WHBD]\s*\((?:[^()]|\([^()]*\))*\)\s*[-+|&^]?=(?!=)'
                 r'|\bTO_PTR\([^()]*\)\s*\[[^]]*\]\s*=(?!=)|\*TO_PTR\([^()]*\)\s*=(?!=)'
                 r'|\bthread_queue_(?:insert|pop|remove)\s*\(|\bschedule_running_thread\s*\(')
CALLRE = re.compile(r'(?<![\w.>])(?:ultramodern::)?([A-Za-z_]\w*)\s*\(')

# A rules: (file suffix, function) -> (class, invariant, [span regexes that cover a non-tail yield], [must-match checks])
RULES = {
    ("mesgqueue.cpp", "do_send"): ("H-yield-safe",
        "blocks inside while(MQ_IS_FULL): only the sender is queued on blocked_on_send, msg slot/first/validCount untouched; "
        "the full test is re-read after every resume, then slot store + validCount++ (+first for jam) run with no yield",
        [r'while\s*\(\s*MQ_IS_FULL\(mq\)\s*\)\s*\{[^{}]*\}'], [r'while\s*\(\s*MQ_IS_FULL\(mq\)\s*\)']),
    ("mesgqueue.cpp", "do_recv"): ("H-yield-safe",
        "blocks inside while(MQ_IS_EMPTY) before any queue store, empty test re-read after resume; the refused-msg park "
        "(s7195_refused_block_recv) never returns, so no store follows it",
        [r'while\s*\(\s*MQ_IS_EMPTY\(mq\)\s*\)\s*\{[^{}]*\}', r'if\s*\(block\)\s*s7195_refused_block_recv\([^;]*;'],
        [r'while\s*\(\s*MQ_IS_EMPTY\(mq\)\s*\)']),
    ("threads.cpp", "_thread_func"): ("H-yield-safe",
        "the initial park precedes the thread's first guest work; the exit store self->context=nullptr runs only when "
        "self->context == thread_context, i.e. this thread still owns the OSThread and holds the run token (a destroyed "
        "thread's context was cleared before its wake signal, so a dying host thread only reads)",
        [r'try\s*\{\s*wait_for_resumed\([^;]*;\s*\}'], [r'if\s*\(\s*self->context\s*==\s*thread_context\s*\)\s*\{\s*self->context\s*=\s*nullptr']),
    ("upstream_compat.cpp", "osStopThread_recomp"): ("H-yield-safe",
        "the yield is the osStopThread(NULL) self-stop branch, which returns at once; stores belong to the other-thread branch",
        [r'if\s*\(\s*t_\s*==\s*NULLPTR\s*\)\s*\{\s*ultramodern::run_next_thread_and_wait\([^;]*;\s*return;\s*\}'], []),
    ("mesgqueue.cpp", "osSendMesg"): ("H-yield-safe",
        "the cf0 dup-ack drop yields (check_running_queue) and returns -1 without touching the queue; do_send's own order is "
        "its own row; the only later store is s4260::on_result, a host-side diag table (Ent, not guest RAM)",
        [r'(?:ultramodern::)?check_running_queue\(PASS_RDRAM1\);\s*return -1;', r'bool sent = do_send\([^;]*;'],
        [r's4260::on_result\(']),
    ("threads.cpp", "osStartThread"): ("H-yield-safe",
        "branch split: a guest caller (thread_self set) schedules then yields at the tail; the state store is the else "
        "branch (runtime init, no guest thread running), which hands over without yielding",
        [r'if\s*\(\s*thread_self\s*\)\s*\{[^{}]*\}'], [r'else\s*\{\s*t->state = OSThreadState::QUEUED;\s*resume_thread_tagged']),
}
DEFS = {  # yield primitives: (file suffix, fn) -> [checks that the hand-off cannot overlap guest accesses]
    ("threads.cpp", "run_next_thread_and_wait"): [r'run_next_thread\(PASS_RDRAM1\);\s*wait_for_resumed\('],
    ("threads.cpp", "resume_thread_and_wait"): [r'resume_thread_tagged\(t, "swap"\);\s*wait_for_resumed\('],
    ("threads.cpp", "run_next_thread"): [r'resume_thread_tagged\(to_run, "run_next"\);\s*\}\s*$'],
    ("threads.cpp", "resume_thread_tagged"): [r'running\.signal\(\);\s*return;', r'running\.signal\(\);\s*\}\s*$'],
    ("threads.cpp", "wait_for_resumed"): ["PREWAIT"],
    ("scheduling.cpp", "swap_to_thread"): [r'state = OSThreadState::QUEUED;\s*ultramodern::resume_thread_and_wait\('],
    ("scheduling.cpp", "check_running_queue"): [r'thread_queue_pop\([^;]*;\s*swap_to_thread\('],
}
GUEST_ACCESS = re.compile(r'\bTO_PTR\(|\bMEM_[WHBDU]|\brdram\s*\[|->\s*(?:queue|state|priority|next|validCount|first|msg)\b')


def rt_funcs(over):
    """(path, fn, body) for every function in RT_FILES."""
    out = []
    for p in RT_FILES:
        t = gb.read(p, over)
        for o, c, name in fz.func_spans(t):
            out.append((p, name, t[o:c + 1]))
    return out


def events(body, yfns, sfns):
    ev = [(m.start(), "Y", m.group(1)) for m in YRE.finditer(body)]
    ev += [(m.start(), "S", body[m.start():m.start() + 40].split("\n")[0]) for m in SRE.finditer(body)]
    have = {e[0] for e in ev}
    for m in CALLRE.finditer(body):                       # one level of callee
        f = m.group(1)
        if m.start() in have or f in PRIM:
            continue
        if f in yfns:
            ev.append((m.start(), "Y", f + "()"))
        elif f in sfns:
            ev.append((m.start(), "S", f + "()"))
    return sorted(ev)


_GC = {}


def section_a(over=None, rules=None, lib=gb.LIB):
    over = over or {}
    rules = RULES if rules is None else rules
    funcs = rt_funcs(over)
    direct_y = {n for p, n, b in funcs if YRE.search(b)} | set(PRIM)
    direct_s = {n for p, n, b in funcs if SRE.search(b)}
    if lib not in _GC:                                     # the GC guest-thread set (live tree; mutations here are A-local)
        gcrows, _ = gc.census(gc.files(), lib=lib, quiet=True)
        _GC[lib] = {(r[0]["path"], r[0]["fn"]) for r in gcrows if r[2] == "H-guest-thread"}
    want = set(_GC[lib])
    want |= {(p, n) for p, n, b in funcs if YRE.search(b) or (os.path.basename(p), n) in DEFS}
    rows = []
    for p, n, b in funcs:
        if (p, n) not in want:
            continue
        key = (os.path.basename(p), n)
        ev = events(b, direct_y - {n}, direct_s - {n})
        ys = [e for e in ev if e[1] == "Y"]
        last_s = max([e[0] for e in ev if e[1] == "S"], default=-1)
        nontail = [e for e in ys if e[0] < last_s]
        seq = " ".join("%s:%s" % (e[1], e[2].strip()[:24]) for e in ev)
        if key in DEFS:
            fails = []
            for c in DEFS[key]:
                if c == "PREWAIT":
                    pre = b.split("running.wait()")[0]
                    if "running.wait()" not in b or GUEST_ACCESS.search(pre):
                        fails.append("guest access before running.wait()")
                elif not re.search(c, b, re.S | re.M):
                    fails.append("missing " + c)
            rows.append((p, n, "FAIL-check" if fails else "H-def", "; ".join(fails) or "hand-off: nothing after signal / before wait", seq))
            continue
        if not nontail:
            rows.append((p, n, "H-atomic", "no yield" if not ys else "tail yield(s) only", seq))
            continue
        r = rules.get(key)
        if not r:
            rows.append((p, n, "H-torn-OPEN", "non-tail yield(s) %s, no rule" % [e[2] for e in nontail], seq))
            continue
        cls, inv, spans, checks = r
        covered = [(m.start(), m.end()) for s in spans for m in re.finditer(s, b, re.S)]
        unc = [e for e in nontail if not any(a <= e[0] < z for a, z in covered)]
        miss = [c for c in checks if not re.search(c, b, re.S)]
        if unc:
            rows.append((p, n, "H-torn-OPEN", "uncovered yield(s) %s" % [e[2] for e in unc], seq))
        elif miss:
            rows.append((p, n, "FAIL-check", "missing " + "; ".join(miss), seq))
        else:
            rows.append((p, n, cls, inv, seq))
    return rows


def gen_files(gen):
    return sorted(glob.glob(os.path.join(gen, "funcs_*.c")))


def fn_index(lines):
    names, cur = [], "<file>"
    for ln in lines:
        m = re.match(r'RECOMP_FUNC void (\w+)\(', ln)
        if m:
            cur = m.group(1)
        names.append(cur)
    return names


FR = 0x04000000
ASG = re.compile(r'^\s*ctx->r(\d+)\s*=\s*(.*?);\s*(?://.*)?$')


def reg_val(lines, names, i, r, depth=0):
    """Backward straight-line resolver within one generated function: int constant, ('SR', set_bits, clear_bits) for a
    value derived from cop0_status_read by |const / &const, or None."""
    fn = names[i]
    for j in range(i - 1, max(-1, i - 800), -1):
        if names[j] != fn:
            return None
        m = ASG.match(lines[j])
        if not m or int(m.group(1)) != r:
            continue
        e = m.group(2).strip()
        if depth > 8:
            return None
        if re.fullmatch(r'cop0_status_read\(ctx\)', e):
            return ("SR", 0, 0)
        k = re.fullmatch(r'S32\(0X([0-9A-F]+)u? << 16\)', e, re.I)
        if k:
            return (int(k.group(1), 16) << 16) & 0xFFFFFFFF
        k = re.fullmatch(r'~\(ctx->r(\d+) \| ctx->r(\d+)\)', e)
        if k and k.group(1) == k.group(2):
            v = reg_val(lines, names, j, int(k.group(1)), depth + 1)
            return ~v & 0xFFFFFFFF if isinstance(v, int) else None
        k = re.fullmatch(r'ctx->r(\d+) ([|&]) (?:ctx->r(\d+)|0X([0-9A-F]+))', e, re.I)
        if not k:
            return None
        x = reg_val(lines, names, j, int(k.group(1)), depth + 1)
        y = int(k.group(4), 16) if k.group(4) else reg_val(lines, names, j, int(k.group(3)), depth + 1)
        if isinstance(y, tuple) and isinstance(x, int):
            x, y = y, x
        if isinstance(x, int) and isinstance(y, int):
            return (x | y) if k.group(2) == "|" else (x & y)
        if isinstance(x, tuple) and isinstance(y, int):
            _, st, cl = x
            if k.group(2) == "|":
                return ("SR", st | y, cl & ~y)
            return ("SR", st & y, cl | (~y & 0xFFFFFFFF))
        return None
    return None


def sr_value(lines, names, i, r):
    """('SR', set, clear) for the value a cop0_status_write stores, else None."""
    return reg_val(lines, names, i + 1, r)


def section_bc(gen=GEN, extra=None):
    """B: critical regions + cop0 status writes; C: injected yields.  extra = list of (name, text) fixture files."""
    files = [(f, open(f, errors="replace").read()) for f in gen_files(gen)] + (extra or [])
    brows, crows, regions = [], [], []
    yc = re.compile(r'(?<![\w.>])(?:ultramodern::)?(%s|osYieldThread_recomp)\s*\(' % "|".join(PRIM))
    for f, txt in files:
        lines = txt.split("\n")
        names = fn_index(lines)
        base = os.path.basename(f)
        open_at = None
        for i, ln in enumerate(lines):
            code = ln.split("//")[0]
            if re.search(r'\b__osDisableInt_recomp\s*\(\s*rdram', code):
                open_at = i
            elif re.search(r'\b__osRestoreInt_recomp\s*\(\s*rdram', code) and open_at is not None:
                body = "\n".join(l.split("//")[0] for l in lines[open_at + 1:i])
                calls = [c for c in re.findall(r'\b(\w+)\s*\(\s*rdram\s*,\s*ctx\s*\)', body)]
                regions.append((base, open_at, i))
                brows.append(("%s:%d-%d" % (base, open_at + 1, i + 1), names[i], "OPEN" if calls else "H-no-call",
                              ("calls " + ",".join(calls)) if calls else "no call between DisableInt and RestoreInt"))
                open_at = None
            m = re.search(r'\bcop0_status_write\s*\(\s*ctx\s*,\s*ctx->r(\d+)\s*\)', code)
            if m:
                v = sr_value(lines, names, i, int(m.group(1)))
                fr = isinstance(v, tuple) and ((v[1] | v[2]) & ~FR & 0xFFFFFFFF) == 0 and (v[1] | v[2]) == FR
                brows.append(("%s:%d" % (base, i + 1), names[i], "not-int" if fr else "OPEN",
                              ("FR (0x04000000) FPU-mode %s" % ("set" if v[1] else "clear")) if fr else
                              "Status write not resolved to SR|FR or SR&~FR (%r)" % (v,)))
        for i, ln in enumerate(lines):
            code = ln.split("//")[0]
            m = yc.search(code)
            if not m or re.match(r'\s*(?:extern\s|void\s|static\s)', code):
                continue
            inside = [r for r in regions if r[0] == base and r[1] < i < r[2]]
            crows.append(("%s:%d" % (base, i + 1), names[i], "OPEN" if inside else "H-int-enabled",
                          m.group(1) + (" inside DisableInt region" if inside else " outside every DisableInt region")))
    return brows, crows


def census(over=None, rules=None, gen=GEN, extra=None, lib=gb.LIB, quiet=False):
    a = section_a(over, rules, lib)
    b, c = section_bc(gen, extra)
    st = Counter()
    for r in a:
        st["A:" + r[2]] += 1
    for r in b:
        st["B:" + r[2]] += 1
    for r in c:
        st["C:" + r[2]] += 1
    bad = sum(v for k, v in st.items() if k.endswith(("OPEN", "FAIL-check")))
    if not quiet:
        for p, n, cls, why, seq in a:
            print("A %s [%s] -> %s | %s\n      %s" % (p, n, cls, why[:200], seq[:220]))
        for loc, fn, cls, why in b:
            print("B %s [%s] -> %s | %s" % (loc, fn, cls, why))
        for loc, fn, cls, why in c:
            print("C %s [%s] -> %s | %s" % (loc, fn, cls, why))
        print("summary: A=%d B=%d C=%d open/fail=%d %s" % (len(a), len(b), len(c), bad, dict(sorted(st.items()))))
    return a, b, c, bad


def controls():
    tests = []
    mq = U + "mesgqueue.cpp"
    src = open(os.path.join(REPO, mq), errors="replace").read()
    with tempfile.TemporaryDirectory() as d:
        # 1 planted yield between do_send's slot store and validCount++ -> do_send H-torn-OPEN
        a = "        TO_PTR(OSMesg, mq->msg)[last] = msg;\n        mq->validCount++;\n"
        mut = src.replace(a, "        TO_PTR(OSMesg, mq->msg)[last] = msg;\n        rs64_preempt_point(rdram);\n        mq->validCount++;\n")
        m1 = os.path.join(d, "mq1.cpp"); open(m1, "w").write(mut)
        rows = section_a({mq: m1})
        tests.append(("planted rs64_preempt_point between do_send slot store and validCount++ -> do_send H-torn-OPEN",
                      mut != src and any(r[1] == "do_send" and r[2] == "H-torn-OPEN" for r in rows)))
        # 2 planted yield via a one-level callee (osSetThreadPri: check_running_queue moved before the queue re-insert)
        th = U + "threads.cpp"
        tsrc = open(os.path.join(REPO, th), errors="replace").read()
        k = tsrc.rfind("t->priority = pri;")                  # the osSetThreadPri store (the first one is osCreateThread)
        mt = tsrc[:k + 18] + " swap_to_thread(PASS_RDRAM t);" + tsrc[k + 18:] if k > 0 else tsrc
        m2 = os.path.join(d, "th2.cpp"); open(m2, "w").write(mt)
        rows = section_a({th: m2})
        tests.append(("planted swap_to_thread after osSetThreadPri's priority store -> osSetThreadPri H-torn-OPEN",
                      mt != tsrc and any(r[1] == "osSetThreadPri" and r[2] == "H-torn-OPEN" for r in rows)))
        # 3 rule deleted -> do_send OPEN
        r3 = {k: v for k, v in RULES.items() if k[1] != "do_send"}
        rows = section_a(rules=r3)
        tests.append(("rule deleted (do_send) -> do_send H-torn-OPEN", any(r[1] == "do_send" and r[2] == "H-torn-OPEN" for r in rows)))
        # 4 hand-off overlap: a guest read planted before running.wait() -> wait_for_resumed FAIL-check
        mw = tsrc.replace("    thread_context->running.wait();", "    (void)TO_PTR(OSThread, thread_self)->state;\n    thread_context->running.wait();", 1)
        m4 = os.path.join(d, "th4.cpp"); open(m4, "w").write(mw)
        rows = section_a({th: m4})
        tests.append(("guest read planted before wait_for_resumed's running.wait() -> FAIL-check",
                      mw != tsrc and any(r[1] == "wait_for_resumed" and r[2] == "FAIL-check" for r in rows)))
    # 5-7 generated-code fixtures
    fx = ("fx_gd.c",
          "RECOMP_FUNC void gd_fake_a(uint8_t* rdram, recomp_context* ctx) {\n"
          "    __osDisableInt_recomp(rdram, ctx);\n    yield_self_1ms(rdram);\n    gd_fake_b(rdram, ctx);\n"
          "    __osRestoreInt_recomp(rdram, ctx);\n"
          "    ctx->r1 = cop0_status_read(ctx);\n    ctx->r2 = S32(0X0 << 16);\n    ctx->r2 = ctx->r2 | 0X1;\n    ctx->r1 = ctx->r1 | ctx->r2;\n"
          "    cop0_status_write(ctx, ctx->r1);\n    rs64_preempt_point(rdram);\n}\n")
    b, c = section_bc(extra=[fx])
    tests.append(("fixture: call inside a DisableInt region -> B OPEN", any(r[0].startswith("fx_gd.c:2") and r[2] == "OPEN" for r in b)))
    tests.append(("fixture: IE-bit Status write -> B OPEN", any(r[0] == "fx_gd.c:10" and "('SR', 1, 0)" in r[3] and r[2] == "OPEN" for r in b)))
    tests.append(("fixture: yield inside region -> C OPEN, yield after region -> C H-int-enabled",
                  any(r[0] == "fx_gd.c:3" and r[2] == "OPEN" for r in c) and any(r[0] == "fx_gd.c:11" and r[2] == "H-int-enabled" for r in c)))
    # 8 coverage + live
    a0 = section_a(rules={})
    a1, b1, c1, bad = census(quiet=True)
    n_rules = sum(1 for r in a1 if r[2] == "H-yield-safe")
    tests.append(("coverage: rule-less A -> every H-yield-safe row (%d) becomes H-torn-OPEN" % n_rules,
                  n_rules >= 4 and sum(1 for r in a0 if r[2] == "H-torn-OPEN") == n_rules))
    tests.append(("live: A>=40 rows, B has the musyxSynthFrame region, C>=20 injected yields, 0 OPEN/FAIL (%d/%d/%d)" % (len(a1), len(b1), len(c1)),
                  len(a1) >= 40 and sum(1 for r in a1 if r[2] == "H-def") == len(DEFS) and any("musyxSynthFrame" in r[1] and r[2] == "H-no-call" for r in b1) and len(c1) >= 20 and bad == 0))
    ok = 0
    for name, passed in tests:
        ok += passed
        print("%s  %s" % ("PASS" if passed else "FAIL", name))
    print("controls %d/%d" % (ok, len(tests)))
    return 0 if ok == len(tests) else 1


def main():
    if "--controls" in sys.argv:
        sys.exit(controls())
    a, b, c, bad = census()
    sys.exit(1 if (bad or not a or not b or not c) else 0)


if __name__ == "__main__":
    main()
