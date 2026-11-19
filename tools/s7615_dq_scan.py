#!/usr/bin/env python3
"""s7615 class DQ regex side: deferred guest reads through host queues and host threads.

 (Q) queue census: every declaration whose type is a moodycamel queue or std::deque / queue / priority_queue / list / stack /
     forward_list (any storage: static, thread_local, file scope, record member), in the s7611 scope files plus the
     librecomp / ultramodern headers. moodycamel internals and LightweightSemaphore are not queues. Function-local
     non-static queues are listed with storage=local (lifetime one call: auto-fresh unless a thread captures them).
 (P) producer census: every `X.enqueue(` / try_enqueue / push / push_back / push_front / emplace* call whose receiver's last
     name component is a census queue name in the same file (or the record-member queue's owner file).
 (T) thread census: every std::thread / std::async / pthread_create / dispatch_async creation, with its capture list or
     argument list, the entry body (lambda body, or the named entry function's body in the same file) and whether that body
     touches guest memory (sn.G tokens: MEM_*, rdram*, rs64_rdram_u*, ...), and the nearest enclosing gate text.
Output JSON: {queues:[{file,line,name,type,storage}], producers:[{file,line,queue,op,arg}], threads:[{file,line,key,caps,
             guest,body_lines,gate}]}."""
import glob, importlib.util, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_sp = importlib.util.spec_from_file_location("sn_scan", os.path.join(ROOT, "tools/s7611_sn_scan.py"))
sn = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(sn)
_sp = importlib.util.spec_from_file_location("hm_scan", os.path.join(ROOT, "tools/s7614_hm_scan.py"))
hm = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(hm)

HEADERS = ("lib/N64ModernRuntime/librecomp/include/*/*.h*", "lib/N64ModernRuntime/ultramodern/include/*/*.h*", "include/*.h")
QT = re.compile(r"\b(?:moodycamel::)?(?:Blocking)?(?:Concurrent|ReaderWriter)Queue\s*<|\bstd::(?:deque|queue|priority_queue|list|stack|forward_list)\s*<")
OPS = r"(enqueue|try_enqueue|enqueue_bulk|try_enqueue_bulk|push|push_back|push_front|emplace|emplace_back|emplace_front)"
GT = re.compile(sn.G.pattern + r"|\bTO_PTR\s*\(|\bPTR\s*\(|RDRAM_ARG|PASS_RDRAM")
THR = re.compile(r"\bstd::thread\s*(?:\w+\s*)?[({]|\bstd::jthread\b|\bstd::async\s*\(|\bpthread_create\s*\(|\bdispatch_async\w*\s*\(")

def files(root=ROOT, gen=None):
    fs = [f for f in sn.scope_files(root, gen or sn.GEN) if not f.endswith(".c") or "/src/" in f]
    fs = [f for f in fs if not os.path.normpath(f).startswith(os.path.normpath(gen or sn.GEN))]  # generated C has no queues
    for p in HEADERS:
        fs += sorted(glob.glob(os.path.join(root, p)))
    return fs

def rel(p, root=ROOT):
    return os.path.relpath(os.path.normpath(p), root)

def tmpl_end(t, i):
    """t[i] == '<' -> index after the matching '>' (parens / nested <> respected)."""
    d = 0; p = 0
    for j in range(i, len(t)):
        c = t[j]
        if c == "(": p += 1
        elif c == ")": p -= 1
        elif c == "<" and p == 0: d += 1
        elif c == ">" and p == 0:
            d -= 1
            if d == 0: return j + 1
        elif c in ";{" and p == 0: return -1
    return -1

def enclosing_depth(t, i):
    """brace depth at i and whether the innermost open brace belongs to a function body (heuristic: ')' before '{')."""
    st = []
    for j in range(i):
        c = t[j]
        if c == "{":
            k = j - 1
            while k >= 0 and t[k] in " \t\n": k -= 1
            pre = t[max(0, k - 80):k + 1]
            if t[k] == ")" or re.search(r"\)\s*(?:const|noexcept|override|mutable)?\s*(?:->\s*[\w:<>]+)?\s*$", pre):
                st.append("f")
            elif re.search(r"\bnamespace\b[^;{}()]*$", t[max(0, k - 200):k + 1]):
                st.append("n")
            elif re.search(r"\b(?:struct|class|union)\b[^;{}()]*$", t[max(0, k - 200):k + 1]) or t[k] == "=" :
                st.append("s")
            else:
                st.append("b")
        elif c == "}" and st:
            st.pop()
    return st

def scan_queues(fs, root=ROOT):
    out = []
    for f in fs:
        t = hm.clean(open(f, errors="replace").read())
        for m in QT.finditer(t):
            lt = t.rfind("<", m.start(), m.end())
            e = tmpl_end(t, lt)
            if e < 0: continue
            typ = re.sub(r"\s+", " ", t[m.start():e])
            if "LightweightSemaphore" in typ: continue
            # declarators after the type: name [, name ...] terminated by ; { = (
            rest = t[e:e + 400]
            md = re.match(r"\s*((?:[*&]?\s*\w+\s*(?:\[[^\]]*\])?\s*(?:\{[^{}]*\}|=[^,;]*)?\s*,\s*)*[*&]?\s*\w+)\s*(?:\[[^\]]*\])?\s*(?:[;{=]|\{)", rest)
            if not md: continue
            pre = t[max(0, t.rfind("\n", 0, m.start())):m.start()]
            if re.search(r"(?:\(|,)\s*(?:const\s+)?$", pre) or re.search(r"\b(?:return|typedef|using)\b", pre) or "::iterator" in t[e:e+12]:
                continue  # parameter / typedef / alias, not storage
            names = [re.sub(r"[*&\s]|\[.*|\{.*|=.*", "", x) for x in re.split(r",(?![^{]*\})", md.group(1))]
            st = enclosing_depth(t, m.start())
            static = re.search(r"\b(?:static|thread_local)\b[^;{}]*$", t[max(0, t.rfind("\n", 0, m.start()) - 1):m.start()]) is not None
            if "f" in st or "b" in st and "s" not in st:
                storage = "static" if static else "local"
            elif "s" in st:
                storage = "member" if not static else "static"
            else:
                storage = "static" if static else "file"
            for n in names:
                if n and re.fullmatch(r"\w+", n) and n not in ("const",):
                    out.append(dict(file=rel(f, root), line=t[:m.start()].count("\n") + 1, name=n, type=typ, storage=storage))
    return out

def scan_producers(fs, queues, root=ROOT):
    qn = {}
    for q in queues: qn.setdefault(q["name"], set()).add(q["file"])
    out = []
    P = re.compile(r"([\w\]\)]+(?:\s*(?:\.|->)\s*\w+)*)\s*(?:\.|->)\s*" + OPS + r"\s*\(")
    for f in fs:
        t = hm.clean(open(f, errors="replace").read())
        for m in P.finditer(t):
            last = re.split(r"\.|->", m.group(1))[-1].strip()
            if last not in qn: continue
            a0 = m.end(); d = 1; j = a0
            while j < len(t) and d:
                d += {"(": 1, ")": -1}.get(t[j], 0); j += 1
            out.append(dict(file=rel(f, root), line=t[:m.start()].count("\n") + 1, queue=last, op=m.group(2),
                            arg=re.sub(r"\s+", " ", t[a0:j - 1])[:160]))
    return out

def body_after(t, i):
    """first balanced {...} or (...) body starting at/after i (lambda / call)."""
    j = i
    while j < len(t) and t[j] not in "({": j += 1
    if j >= len(t): return ""
    o = t[j]; c = ")" if o == "(" else "}"; d = 0
    for k in range(j, len(t)):
        if t[k] == o: d += 1
        elif t[k] == c:
            d -= 1
            if d == 0: return t[j:k + 1]
    return t[j:]

def fn_body(t, name):
    m = re.search(r"\b" + re.escape(name) + r"\s*\([^;{}]*\)\s*(?:noexcept\s*)?\{", t)
    if not m: return None
    i = m.end() - 1; d = 0
    for k in range(i, len(t)):
        if t[k] == "{": d += 1
        elif t[k] == "}":
            d -= 1
            if d == 0: return t[i:k + 1]
    return None

def scan_threads(fs, root=ROOT, G=None):
    G = G or GT
    out = []
    for f in fs:
        if f.endswith(".h") or f.endswith(".hpp"): continue
        t = hm.clean(open(f, errors="replace").read())
        for m in THR.finditer(t):
            line = t[:m.start()].count("\n") + 1
            call = body_after(t, m.end() - 1)
            caps = ""; entry = None; body = call
            ml = re.match(r"[({]\s*\[([^\]]*)\]", call)
            if ml:
                caps = "[" + ml.group(1).strip() + "]"
            else:
                inner = call[1:-1]
                if m.group(0).startswith("pthread_create"):
                    parts = [x.strip() for x in inner.split(",")]
                    entry = parts[2] if len(parts) > 2 else None
                    caps = "(" + ",".join(parts[3:]) + ")"
                else:
                    parts = [x.strip() for x in re.split(r",(?![^(]*\))", inner)]
                    entry = re.sub(r"^&", "", parts[0]) if parts else None
                    caps = "(" + ",".join(parts[1:]) + ")"
                fb = fn_body(t, entry) if entry and re.fullmatch(r"[\w:]+", entry) else None
                body = (fb or "") + call
            ln = t.rfind("\n", 0, m.start())
            ctx = t[max(0, t.rfind("\n", 0, max(0, ln - 1)) ):m.start()]
            gate = re.sub(r"\s+", " ", ctx).strip()[-140:]
            key = (entry or caps or "lambda")
            hop = []  # one hop: same-file functions the entry body calls whose own body touches guest memory
            for cn in sorted(set(re.findall(r"(?<!\.)(?<!->)\b([A-Za-z_]\w*)\s*\(", body)) - {"if", "for", "while", "switch", "return", "sizeof"}):
                cb = fn_body(t, cn)
                if cb and cb not in body and G.search(cb): hop.append(cn)
            out.append(dict(file=rel(f, root), line=line, key=re.sub(r"\s+", "", key)[:60], caps=re.sub(r"\s+", "", caps)[:80],
                            guest=bool(G.search(body)), hop=hop, body_lines=body.count("\n") + 1, gate=gate))
    return out

VT = re.compile(r"\bstd::vector\s*<")
def vec_used_as_queue(t, n):
    """a vector used as a FIFO / pending list: appended (push_back / emplace_back / insert) AND erased in the same file."""
    return bool(re.search(r"\b%s\s*(?:\.|->)\s*(?:push_back|emplace_back|insert)\s*\(" % re.escape(n), t) and
                re.search(r"\b%s\s*(?:\.|->)\s*erase\s*\(" % re.escape(n), t))

def scan_vecq(fs, root=ROOT):
    out = []
    for f in fs:
        t = hm.clean(open(f, errors="replace").read())
        for m in VT.finditer(t):
            lt = t.rfind("<", m.start(), m.end()); e = tmpl_end(t, lt)
            if e < 0: continue
            md = re.match(r"\s*(\w+)\s*(?:\{[^{}]*\})?\s*[;=]", t[e:e + 160])
            if not md: continue
            pre = t[max(0, t.rfind("\n", 0, m.start())):m.start()]
            if re.search(r"(?:\(|,)\s*(?:const\s+)?$", pre): continue
            st = enclosing_depth(t, m.start())
            if "f" in st and not re.search(r"\bstatic\b", pre): continue  # function-local: lifetime one call
            n = md.group(1)
            if vec_used_as_queue(t, n):
                out.append(dict(file=rel(f, root), line=t[:m.start()].count("\n") + 1, name=n,
                                type=re.sub(r"\s+", " ", t[m.start():e]), storage="vecq"))
    return out

def scan(root=ROOT, gen=None, extra=()):
    fs = files(root, gen) + list(extra)
    q = scan_queues(fs, root)
    return dict(queues=q, producers=scan_producers(fs, q, root), threads=scan_threads(fs, root), vecq=scan_vecq(fs, root))

if __name__ == "__main__":
    r = scan()
    if "--summary" in sys.argv:
        for q in r["queues"]: print("Q", q["file"], q["line"], q["storage"], q["name"], q["type"][:90])
        for p in r["producers"]: print("P", p["file"], p["line"], p["queue"], p["op"], p["arg"][:80])
        for v in r["vecq"]: print("V", v["file"], v["line"], v["name"], v["type"][:90])
        for th in r["threads"]: print("T", th["file"], th["line"], th["key"], th["caps"], "guest=%d" % th["guest"], "hop=" + ",".join(th["hop"])[:60], "|", th["gate"][-70:])
    else:
        json.dump(r, sys.stdout, indent=0)
