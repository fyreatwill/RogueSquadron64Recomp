#!/usr/bin/env python3
"""s7616 class RQ census: deferred reads of guest RDRAM inside lib/rt64 (+ our rt64_render_context.cpp).
Sources: regex scan (tools/s7616_rq_scan.py, re-run live) and clang AST (tools/s7616_rq_ast.py -> scratch/s7616/ast.json).
Every reference to the RDRAM base (->RDRAM/.RDRAM/implicit this->RDRAM/fromRDRAM) is a row; rows are classified:
  init    base handed over / copied at setup (State::State, Application::setup, implicit Core copy)
  gated   only on the RS64 RDP async worker (ROGUESQ_RDP_ASYNC, default 0; its late reads were measured s7539-s7554)
  copy    bytes memcpy'd at command time (rdpq::submit -> Job.w)
  dead    #ifdef _WIN32 (regex-only, the macOS AST never sees it)
  sync    enclosing function reachable from a Gfx-thread entry and NOT from any RT64 worker-thread entry
  OPEN    anything else (incl. any row reachable from a worker-thread entry)
Call graph = short-name over-approximation with two documented refinements: internal linkage (a non-member function of
render_context.cpp is only callable from that TU) and EXCL edges proved by reading the call site.
--controls runs 9 planted-defect controls. --witness-sample <sample.txt> checks a macOS `sample` of the default recipe."""
import json, os, re, sys, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s7616_rq_scan as S
from rs64_zopen import zopen, resolve  # s7804: retained samples are zstd'd

ROOT = S.ROOT
import importlib.util as _ilu
_acs = _ilu.spec_from_file_location("ast_cache", os.path.join(ROOT, "tools/ast_cache.py")); ast_cache = _ilu.module_from_spec(_acs); _acs.loader.exec_module(ast_cache)
RC = "src/main/rt64_render_context.cpp"
GFX_ROOTS = ["RT64Context::send_dl", "RT64Context::update_screen", "submit_rdp_range", "run_rdp_submission",
             "rs64_rdpq_task_exit"]
NONGFX_ROOTS = [r for r in S.ROOTS_NONGFX if r != "worker"]
EXCL = {("RenderFramebufferManager::get", "Application::setup"): "rt64_render_target_manager.cpp:125 storage.setup() = RenderFramebufferStorage::setup"}
SOLE = {}
INIT = {"State::State", "Application::setup", "RT64Context::RT64Context", "operator="}

def graph():
    ps = S.files()
    g, where = {}, {}
    for p in ps:
        sub = S.callgraph([p])
        for k, v in sub.items():
            g.setdefault(k, set()).update(v); where.setdefault(k, os.path.relpath(p, ROOT))
    # Indirect dispatch: GBI/RDP command tables store handler addresses (&F3D::runDl, &GBI_RDP::setColorImage, ...) and
    # the Interpreter's list walkers call through them. Model: every address-taken function is a callee of the synthetic
    # node "<dispatch>", which every Interpreter::process* calls.
    shorts = {k.split("::")[-1] for k in g}
    disp = set()
    for p in ps:
        t = S.strip(open(p, errors="replace").read())
        for m in re.finditer(r"&\s*((?:\w+::)*(\w+))\b(?!\s*\()", t):
            if m.group(2) in shorts and m.group(2)[0].isalpha(): disp.add(m.group(2))
    g["<dispatch>"] = disp; where["<dispatch>"] = "lib/rt64/src/hle/rt64_interpreter.cpp"
    for k in list(g):
        if k.startswith("Interpreter::process"): g[k].add("<dispatch>")
    return ps, g, where

def sole_callers():
    """Application::setup: the only call site in scope is RT64Context's `app->setup(` (checked live)."""
    n = 0
    for p in S.files():
        n += len(re.findall(r"\bapp(?:lication)?\s*->\s*setup\s*\(", S.strip(open(p, errors="replace").read())))
    return {"Application::setup": {"RT64Context::RT64Context"}} if n == 1 else {}

def reach(g, where, roots, internal=True, excl=EXCL, sole=None):
    sole = SOLE if sole is None else sole
    by = {}
    for k in g: by.setdefault(k.split("::")[-1], set()).add(k)
    seen, path, todo = set(), {}, []
    for r in roots:
        for k in g:
            if k == r or k.endswith("::" + r):
                if k not in seen: seen.add(k); path[k] = [k]; todo.append(k)
    while todo:
        f = todo.pop()
        for cs in g.get(f, ()):
            for k in by.get(cs, ()):
                if internal and where.get(k) == RC and "::" not in k and where.get(f) != RC:
                    continue
                if (f, k) in excl: continue
                if k in sole and f not in sole[k]: continue
                if k not in seen: seen.add(k); path[k] = path[f] + [k]; todo.append(k)
    return seen, path

def win32_lines(path):
    out, st = set(), []
    for i, l in enumerate(open(os.path.join(ROOT, path), errors="replace").read().split("\n"), 1):
        s = l.strip()
        if s.startswith("#if"): st.append("_WIN32" in s and "!" not in s)
        elif s.startswith("#else") and st: st[-1] = False
        elif s.startswith("#endif") and st: st.pop()
        elif any(st): out.add(i)
    return out

def gate_default_off():
    t = open(os.path.join(ROOT, RC)).read()
    return bool(re.search(r'int rs64_rdp_async_on = \[\] \{ const char \*e = std::getenv\("ROGUESQ_RDP_ASYNC"\); return \(e && \*e && \*e != \'0\'\) \? 1 : 0; \}\(\);', t))

def classify(rx, ast, g, where, internal=True, excl=EXCL, gate=None, sole=None):
    gate = gate_default_off() if gate is None else gate
    gs, _ = reach(g, where, GFX_ROOTS, internal, excl, sole)
    called = set().union(*g.values())
    ns, npath = reach(g, where, NONGFX_ROOTS, internal, excl, sole)
    A = {(r["file"], r["line"], r["member"]) for r in ast}
    X = {(r["file"], r["line"], r["member"]) for r in rx}
    win = {f: win32_lines(f) for f in {k[0] for k in X - A}}
    rows, dis = [], []
    for k in sorted(X - A):
        if k[2] and k[1] in win.get(k[0], ()): continue
        dis.append(("regex-only", k))
    for k in sorted(A - X):
        fn = [r["fn"] for r in ast if (r["file"], r["line"], r["member"]) == k]
        if k[0].endswith(".h") and all(f == "operator=" for f in fn): continue  # implicit Core copy-assign
        dis.append(("ast-only", k))
    seen = set()
    for r in rx:
        k = (r["file"], r["line"], r["member"], r["fn"])
        if k in seen: continue
        seen.add(k)
        top = r["fn"].split(">")[0]
        if r["file"] == RC and r["line"] in win32_lines(RC) and (r["file"], r["line"], r["member"]) not in A:
            c = "dead"
        elif top in ns:
            c = "OPEN"; r = dict(r, why="worker-thread path: " + " -> ".join(npath[top]))
        elif top in INIT:
            c = "init"
        elif r["file"] == RC and top == "worker":
            c = "gated" if gate else "OPEN"
        elif r["file"] == RC and top == "submit":
            c = "copy"
        elif top in gs:
            c = "sync"
        elif top.split("::")[-1] not in called:
            c = "dead"; r = dict(r, why="no caller and not address-taken")
        else:
            c = "OPEN"; r = dict(r, why="not reachable from a Gfx entry")
        rows.append(dict(r, cls=c))
    return rows, dis

def witness(path, readers):
    th, bad, seen_gfx, ctl = None, [], 0, set()
    pat = re.compile("|".join(re.escape(x) + r"\(" for x in readers))
    # s7804: the retained witness sample is zstd'd (scratch/s7616/sample.txt.zst)
    for l in zopen(resolve(path) or path):
        if l.startswith("Total number in stack") or l.startswith("Sort by top of stack") or l.startswith("Binary Images"):
            break  # summary sections carry no thread attribution
        m = re.match(r"^\s+\d+ Thread_\d+(?::\s*(.*))?$", l.rstrip("\n"))
        if m:
            th = (m.group(1) or "").strip(); continue
        if th is None: continue
        if pat.search(l):
            if th in ("Gfx Thread", "RS64 RDP async"): seen_gfx += 1
            else: bad.append((th, l.strip()[:120]))
        if "WorkloadQueue::threadRenderFrame(" in l and th == "RT64 Workload": ctl.add("workload")
        if "PresentQueue::threadPresent(" in l and th == "RT64 Present": ctl.add("present")
    return dict(gfx_reader_frames=seen_gfx, bad=bad, controls=sorted(ctl),
                ok=(not bad and seen_gfx > 0 and ctl == {"workload", "present"}))

def reader_syms(rows):
    out = set()
    for r in rows:
        top = r["fn"].split(">")[0]
        if r["cls"] in ("sync", "OPEN") and r["file"] != RC and "::" in top:
            out.add("RT64::" + top)
    return sorted(out)

def summary(rows, dis):
    c = {}
    for r in rows: c[r["cls"]] = c.get(r["cls"], 0) + 1
    return c, len([r for r in rows if r["cls"] == "OPEN"]), len(dis)

def main():
    a = sys.argv[1:]
    ast_cache.ensure(os.path.join(ROOT, "scratch/s7616/ast.json"), "tools/s7616_rq_ast.py")  # s7655
    ast = json.load(open(os.path.join(ROOT, "scratch/s7616/ast.json")))
    assert not ast["failed"], ast["failed"]
    ast = ast["rows"]
    global SOLE
    SOLE = sole_callers()
    print("sole-caller rules:", SOLE)
    ps, g, where = graph()
    rx = []
    for p in ps: rx += S.scan(p)
    rows, dis = classify(rx, ast, g, where)
    c, nopen, ndis = summary(rows, dis)
    print("rows=%d classes=%s open=%d disagree=%d ast_rows=%d tu=%d" % (len(rows), c, nopen, ndis, len(ast), 92))
    for r in rows:
        if r["cls"] == "OPEN": print("  OPEN", r["file"], r["line"], r["fn"], r.get("why", ""))
    for d in dis: print("  DISAGREE", d)
    ok = nopen == 0 and ndis == 0
    syms = reader_syms(rows)
    if "--witness-sample" in a:
        w = witness(a[a.index("--witness-sample") + 1], syms)
        print("witness readers=%d gfx_reader_frames=%d bad=%d controls=%s ok=%s" % (len(syms), w["gfx_reader_frames"], len(w["bad"]), w["controls"], w["ok"]))
        for b in w["bad"][:10]: print("  BAD", b)
        ok = ok and w["ok"]
    if "--controls" in a:
        res = []
        def run(name, rx2=rx, ast2=ast, g2=g, **kw):
            r2, d2 = classify(rx2, ast2, g2, where, **kw); _, o, n = summary(r2, d2); return o, n
        pl = dict(file="lib/rt64/src/hle/rt64_workload_queue.cpp", line=99999, member="RDRAM", fn="WorkloadQueue::threadRenderFrame")
        o, n = run("C1", rx2=rx + [pl], ast2=ast + [pl]); res.append(("C1 planted read in a workload-thread fn -> OPEN", o >= 1))
        o, n = run("C2", ast2=ast[1:]); res.append(("C2 drop an AST row -> disagreement", n >= 1))
        o, n = run("C3", rx2=[r for r in rx if (r["file"], r["line"]) != (rx[0]["file"], rx[0]["line"])]); res.append(("C3 drop a regex row -> disagreement", n >= 1))
        o, n = run("C4", internal=False); res.append(("C4 no internal-linkage rule -> submit reached from render thread -> OPEN", o >= 1))
        o, n = run("C5", excl={}, sole={}); res.append(("C5 drop the Application::setup sole-caller rule -> OPEN", o >= 1))
        o, n = run("C6", gate=False); res.append(("C6 RDP_ASYNC default flipped on -> worker rows OPEN", o >= 1))
        pl2 = dict(file="lib/rt64/src/hle/rt64_state.cpp", line=99998, member="RDRAM", fn="State::nobodyCallsMe")
        r7, _ = classify(rx + [pl2], ast + [pl2], g, where)
        res.append(("C7 planted read in an uncalled fn -> dead (not sync)", [r["cls"] for r in r7 if r["line"] == 99998] == ["dead"]))
        gs7, _ = reach(g, where, GFX_ROOTS); ns7, _ = reach(g, where, NONGFX_ROOTS); called7 = set().union(*g.values())
        orphan = next(k for k in sorted(g) if k not in gs7 and k not in ns7 and k.split("::")[-1] in called7 and k not in INIT and "::" in k)
        pl3 = dict(file="lib/rt64/src/hle/rt64_state.cpp", line=99997, member="RDRAM", fn=orphan)
        o, n = run("C7b", rx2=rx + [pl3], ast2=ast + [pl3]); res.append(("C7b planted read in a called-but-not-Gfx-reachable fn (%s) -> OPEN" % orphan[:30], o >= 1))
        if "--witness-sample" in a:
            src = zopen(resolve(a[a.index("--witness-sample") + 1]) or a[a.index("--witness-sample") + 1]).read()
            tmp = os.path.join(ROOT, "scratch/s7616/ctl_sample.txt")
            cut = src.find("Total number in stack"); cut = len(src) if cut < 0 else cut
            open(tmp, "w").write(src[:cut] + "    1 Thread_9: RT64 Workload\n    + 1 RT64::State::fullSync()  (in RogueSquadron64Recomp)\n" + src[cut:])
            res.append(("C8 planted reader frame on RT64 Workload -> BAD", not witness(tmp, syms)["ok"] and len(witness(tmp, syms)["bad"]) == 1))
            src2 = re.sub(r"WorkloadQueue::threadRenderFrame\(", "XX(", src); open(tmp, "w").write(src2)
            res.append(("C9 strip the workload control frames -> witness FAIL", not witness(tmp, syms)["ok"]))
        for nme, passed in res: print("control %-75s %s" % (nme, "PASS" if passed else "FAIL"))
        print("controls %d/%d" % (sum(p for _, p in res), len(res)))
        ok = ok and all(p for _, p in res)
    print("VERDICT", "CLOSED" if ok else "NOT-CLOSED")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
