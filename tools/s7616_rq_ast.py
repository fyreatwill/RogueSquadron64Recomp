#!/usr/bin/env python3
"""s7616 class RQ second source: clang -ast-dump census of every MemberExpr naming the guest-RDRAM base (member RDRAM of
any record, incl. implicit this->RDRAM inside State methods) or State::fromRDRAM, over lib/rt64/src (minus contrib) and
src/main/rt64_render_context.cpp. Each row: file, line (member-name location = end of the expr range), member, enclosing
function chain (outer>inner, lambdas as <lambda>). Uses build/compile_commands.json flags. --out <json>."""
import json, os, re, shlex, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOC = re.compile(r"(?:<|, |> )((?:/[^:<>,]+?):(\d+):\d+|line:(\d+):\d+|col:\d+)")
FN = ("FunctionDecl", "CXXMethodDecl", "CXXConstructorDecl", "CXXDestructorDecl", "CXXConversionDecl")
NAME = re.compile(r"(?:col:\d+|line:\d+:\d+|:\d+:\d+)>?\s+(?:(?:used|referenced|implicit|invalid|constexpr|inline|static)\s+)*(\w+|operator\S*)\s+'")
MEM = re.compile(r"(?:->|\.)(RDRAM|fromRDRAM) 0x[0-9a-f]+")

def in_scope(f):
    r = os.path.relpath(os.path.normpath(f), ROOT)
    return (r.startswith("lib/rt64/src/") and "/contrib/" not in r) or r == "src/main/rt64_render_context.cpp"

def parse(text):
    cur, cline = None, 0
    stack = []  # (depth, kind, name)
    out = []
    for l in text.split("\n"):
        m = re.match(r"^([| `]*)[-`]?(\w+)", l)
        if not m:
            continue
        depth = len(m.group(1)) // 2
        kind = m.group(2)
        while stack and stack[-1][0] >= depth:
            stack.pop()
        last = None
        rng = l.split(">", 1)[0] if "<" in l else ""
        for x in LOC.finditer(l):
            if x.group(2):
                cur = x.group(1).rsplit(":", 2)[0]; cline = int(x.group(2))
            elif x.group(3):
                cline = int(x.group(3))
            last = (cur, cline)
        if kind in FN:
            mm = NAME.search(l)
            stack.append((depth, kind, mm.group(1) if mm else "?"))
        elif kind == "LambdaExpr":
            stack.append((depth, kind, "<lambda>"))
        elif kind == "MemberExpr":
            mm = MEM.search(l)
            if mm and last and last[0] and in_scope(last[0]):
                out.append(dict(file=os.path.relpath(os.path.normpath(last[0]), ROOT), line=last[1], member=mm.group(1),
                                implicit=False, fn=">".join(s[2] for s in stack)))
        elif kind == "CXXThisExpr" and "implicit" in l and out and stack:
            pass
    return out

def run_one(e):
    args = e.get("arguments") or shlex.split(e["command"])
    a, skip = [], False
    for x in args:
        if skip: skip = False; continue
        if x == "-o": skip = True; continue
        if x == "-c": continue
        a.append(x)
    a += ["-fsyntax-only", "-Xclang", "-ast-dump", "-fno-color-diagnostics", "-w"]
    p = subprocess.run(a, cwd=e["directory"], capture_output=True, text=True, errors="replace")
    return e["file"], p.returncode, parse(p.stdout)

def main():
    a = sys.argv[1:]
    d = json.load(open(os.path.join(ROOT, "build/compile_commands.json")))
    seen, ents = set(), []
    for e in d:
        f = os.path.normpath(os.path.join(e["directory"], e["file"]))
        if in_scope(f) and f not in seen and f.endswith((".cpp", ".mm")):
            seen.add(f); ents.append(e)
    res, fails = {}, []
    with ThreadPoolExecutor(int(os.environ.get("J", "6"))) as ex:
        for f, rc, r in ex.map(run_one, ents):
            if rc != 0: fails.append(os.path.relpath(f, ROOT))
            for x in r:
                res[(x["file"], x["line"], x["member"], x["fn"])] = x
    rows = sorted(res.values(), key=lambda r: (r["file"], r["line"]))
    sys.stderr.write("tu=%d failed=%s rows=%d\n" % (len(ents), fails, len(rows)))
    s = json.dumps(dict(tu=len(ents), failed=fails, rows=rows), indent=0)
    o = a[a.index("--out") + 1] if "--out" in a else None
    (open(o, "w").write(s) if o else sys.stdout.write(s))

if __name__ == "__main__":
    main()
