#!/usr/bin/env python3
"""s7616 class RQ regex source: every reference to the guest-RDRAM base (->RDRAM / .RDRAM / fromRDRAM( / bare RDRAM
inside State methods = implicit this) in lib/rt64/src (minus contrib) + src/main/rt64_render_context.cpp, with the
enclosing function chain, plus a short-name call graph over the same files used to decide which rows are reachable
from a NON-gfx thread entry. Comments and string literals are blanked first (line numbers kept). JSON on stdout/--out."""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KW = {"if", "for", "while", "switch", "catch", "return", "sizeof", "defined", "decltype", "alignof", "static_assert"}
HEAD = re.compile(r"((?:\w+::)*~?\w+)\s*\(([^;{}()]*(?:\([^;{}()]*\)[^;{}()]*)*)\)\s*(?:const\s*)?(?:noexcept\s*)?(?:override\s*)?(?:final\s*)?(?:->\s*[\w:<>\*&\s]+)?(?::[^;{}]*)?$")
LAM = re.compile(r"\[[^\[\]]*\]\s*(?:\([^()]*\))?\s*(?:mutable\s*)?(?:->\s*[\w:<>\*&\s]+)?$")
CLS = re.compile(r"\b(?:struct|class)\s+(\w+)[^;{}()]*$")

def files():
    fs = [f for f in glob.glob(os.path.join(ROOT, "lib/rt64/src/**/*"), recursive=True)
          if f.endswith((".cpp", ".h", ".mm")) and "/contrib/" not in f]
    return sorted(fs) + [os.path.join(ROOT, "src/main/rt64_render_context.cpp")]

def strip(t):
    out, i, n = [], 0, len(t)
    while i < n:
        c = t[i]
        if t.startswith("//", i):
            j = t.find("\n", i); j = n if j < 0 else j; out.append(" " * (j - i)); i = j
        elif t.startswith("/*", i):
            j = t.find("*/", i + 2); j = n if j < 0 else j + 2; out.append(re.sub(r"[^\n]", " ", t[i:j])); i = j
        elif c == '"' or (c == "'" and not (i and (t[i-1].isalnum()))):
            j = i + 1
            while j < n and t[j] != c:
                j += 2 if t[j] == "\\" else 1
            out.append(c + re.sub(r"[^\n]", " ", t[i+1:j]) + c); i = j + 1
        elif c == "#":  # preprocessor line: keep #if structure out of the head matcher
            j = t.find("\n", i); j = n if j < 0 else j
            while t[j-1] == "\\" and j < n:
                k = t.find("\n", j + 1); j = n if k < 0 else k
            out.append(re.sub(r"[^\n]", " ", t[i:j])); i = j
        else:
            out.append(c); i += 1
    return "".join(out)

def scan(path):
    t = strip(open(path, errors="replace").read())
    rel = os.path.relpath(path, ROOT)
    stack = []  # entries: (kind, name, params)
    rows, bodies = [], {}
    line, last = 1, 0
    for m in re.finditer(r"[{};\n]|(->|\.)\s*RDRAM\b|\bfromRDRAM\s*\(|\bRDRAM\b", t):
        tok = m.group(0)
        if tok == "\n":
            line += 1; continue
        fnchain = [s for s in stack if s[0] in ("fn", "lam")]
        if tok == "{":
            pre = t[last:m.start()].replace("\n", " ").strip()
            h = HEAD.search(pre); c = CLS.search(pre)
            if LAM.search(pre):
                stack.append(("lam", "<lambda>", ""))
            elif h and h.group(1).split("::")[-1] not in KW and not re.search(r"\b(?:else|do|try)\s*$", pre) and not (fnchain and not re.search(r"^\w[\w:<>\s\*&,]*\s(?:\w+::)*\w+\s*\($", pre[:h.start()+len(h.group(1))+1].split(";")[-1] + "(")):
                name = h.group(1)
                if not fnchain and stack and stack[-1][0] == "cls" and "::" not in name:
                    name = stack[-1][1] + "::" + name
                stack.append(("fn", name, h.group(2)))
            elif c and not fnchain:
                stack.append(("cls", c.group(1), ""))
            else:
                stack.append(("blk", "", ""))
            last = m.end(); continue
        if tok == "}":
            if stack: stack.pop()
            last = m.end(); continue
        if tok == ";":
            last = m.end(); continue
        fns = [s for s in stack if s[0] in ("fn", "lam")]
        chain = ">".join(s[1] for s in fns)
        if tok.startswith("fromRDRAM"):
            if fns and not re.search(r"(?:->|\.)\s*$", t[max(0, m.start()-4):m.start()]) and fns[-1][1].startswith("State::"):
                kind = "fromRDRAM"  # implicit this->fromRDRAM inside State
            elif re.search(r"(?:->|\.)\s*$", t[max(0, m.start()-4):m.start()]):
                kind = "fromRDRAM"
            else:
                continue  # declaration / definition head
            if fns: rows.append(dict(file=rel, line=line, member="fromRDRAM", fn=chain))
            continue
        if m.group(1):
            if fns: rows.append(dict(file=rel, line=line, member="RDRAM", fn=chain))
            continue
        # bare RDRAM: implicit this only inside State methods with no RDRAM param/local
        if re.search(r"(?:->|\.)\s*$", t[max(0, m.start()-4):m.start()]):
            continue
        if not fns or not fns[0][1].startswith("State::"):
            continue
        if any(re.search(r"\bRDRAM\b", s[2]) for s in fns):
            continue
        body_start = t.rfind("\n", 0, m.start())
        fnstart = t.rfind(fns[0][1].split("::")[-1] + "(", 0, m.start())
        if re.search(r"\*\s*RDRAM\s*=|\*\s*RDRAM\s*;", t[fnstart:m.start()]) or re.search(r"\bRDRAM\s*=", t[m.start():m.end()+3]) and re.search(r"\*\s*$", t[m.start()-3:m.start()]):
            continue
        rows.append(dict(file=rel, line=line, member="RDRAM", fn=chain, implicit=True))
    return rows

def callgraph(paths):
    """short-name call graph: fn-qualified-name -> set(callee short names); plus thread-entry lambda bodies."""
    g = {}
    for p in paths:
        t = strip(open(p, errors="replace").read())
        rel = os.path.relpath(p, ROOT)
        stack, last = [], 0
        for m in re.finditer(r"[{};]|\b(\w+)\s*(?:<(?:[^<>;{}()]|\([^()]*\))*>\s*)?\(", t):
            tok = m.group(0)
            fns = [s for s in stack if s[0] in ("fn",)]
            if tok == "{":
                pre = t[last:m.start()].replace("\n", " ").strip(); h = HEAD.search(pre); c = CLS.search(pre)
                if h and h.group(1).split("::")[-1] not in KW and not LAM.search(pre) and not fns:
                    name = h.group(1)
                    if stack and stack[-1][0] == "cls" and "::" not in name: name = stack[-1][1] + "::" + name
                    stack.append(("fn", name)); g.setdefault(name, set())
                elif c and not fns: stack.append(("cls", c.group(1)))
                else: stack.append(("blk", ""))
                last = m.end(); continue
            if tok == "}":
                if stack: stack.pop()
                last = m.end(); continue
            if tok == ";":
                last = m.end(); continue
            if fns and m.group(1) not in KW:
                g[fns[-1][1]].add(m.group(1))
    return g

ROOTS_NONGFX = ["WorkloadQueue::renderThreadLoop", "WorkloadQueue::idleThreadLoop", "PresentQueue::threadLoop",
                "BufferUploader::threadLoop", "TextureCache::StreamThread::loop", "StreamThread::loop",
                "TextureCache::uploadThreadLoop", "RasterShaderCache::CompilationThread::loop", "CompilationThread::loop",
                "RasterShaderUber::threadCreatePipelines", "worker"]

def reach(g, roots):
    by_short = {}
    for k in g: by_short.setdefault(k.split("::")[-1], set()).add(k)
    seen, path, todo = set(), {}, []
    for r in roots:
        for k in g:
            if k == r or k.endswith("::" + r) or (r == "worker" and k == "worker"):
                if k not in seen: seen.add(k); path[k] = [k]; todo.append(k)
    while todo:
        f = todo.pop()
        for cs in g.get(f, ()):
            for k in by_short.get(cs, ()):
                if k not in seen:
                    seen.add(k); path[k] = path[f] + [k]; todo.append(k)
    return seen, path

def main():
    a = sys.argv[1:]
    ps = files()
    rows = []
    for p in ps: rows += scan(p)
    g = callgraph(ps)
    seen, path = reach(g, ROOTS_NONGFX)
    for r in rows:
        top = r["fn"].split(">")[0]
        r["nongfx_path"] = path.get(top)
    out = dict(rows=rows, nfn=len(g), nongfx_reach=len(seen))
    s = json.dumps(out, indent=0)
    o = a[a.index("--out") + 1] if "--out" in a else None
    (open(o, "w").write(s) if o else sys.stdout.write(s))
    sys.stderr.write("rows=%d fns=%d nongfx_reachable_fns=%d rows_reachable=%d\n" % (
        len(rows), len(g), len(seen), sum(1 for r in rows if r["nongfx_path"])))

if __name__ == "__main__":
    main()
