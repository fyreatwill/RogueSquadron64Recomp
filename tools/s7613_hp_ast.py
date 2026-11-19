#!/usr/bin/env python3
"""s7613 class HP second source: clang -ast-dump census of every VarDecl with STATIC storage duration (static, thread_local,
namespace/file scope, static member) whose type contains a pointer ('*'), over the same scope as the regex census
(src/*, librecomp/src, ultramodern/src, generated RecompiledFuncs). Uses build/compile_commands.json flags.
Output: JSON list {file, line, name, type, storage} (file = repo-relative, RF/<base> for generated) on stdout or --out.
Parses clang's stateful text locations (a path is printed only when the file changes) in print order."""
import json, os, re, shlex, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.normpath(os.path.join(ROOT, "../N64Recomp/RecompiledFuncs"))
LOC = re.compile(r"(?:<|, |> )((?:/[^:<>,]+?):(\d+):\d+|line:(\d+):\d+|col:\d+)")
FN = ("FunctionDecl", "CXXMethodDecl", "CXXConstructorDecl", "CXXDestructorDecl", "CXXConversionDecl", "LambdaExpr",
      "BlockDecl", "ObjCMethodDecl")
STRARR = re.compile(r"^'(const )?(unsigned )?char \*( ?const)?\[\d*\]'")
SKIPT = re.compile(r"^'(const )?(char|wchar_t|FILE) \*( ?const)?'")

def in_scope(f):
    f = os.path.normpath(f)
    if f.startswith(GEN + "/") and f.endswith(".c"):
        return True
    rel = os.path.relpath(f, ROOT)
    return bool(re.match(r"(src/[^/]+/[^/]+\.(cpp|mm|h)|lib/N64ModernRuntime/(librecomp|ultramodern)/src/[^/]+\.cpp)$", rel))

def rel(f):
    f = os.path.normpath(f)
    return "RF/" + os.path.basename(f) if f.startswith(GEN + "/") else os.path.relpath(f, ROOT)

def parse(text, want):
    cur, cline = None, 0
    stack = []
    out = []
    for l in text.split("\n"):
        m = re.match(r"^([| `]*)[-`]?(\w+)", l)
        if not m:
            continue
        depth = len(m.group(1)) // 2
        kind = m.group(2)
        del stack[depth:]
        stack.append(kind)
        locs = list(LOC.finditer(l))
        name_loc = None
        for x in locs:
            if x.group(2):
                cur = x.group(1).rsplit(":", 2)[0]; cline = int(x.group(2))
            elif x.group(3):
                cline = int(x.group(3))
            name_loc = (cur, cline)
        if kind != "VarDecl" or not name_loc or not name_loc[0]:
            continue
        mm = re.search(r"(?:col:\d+|line:\d+:\d+|:\d+:\d+)\s+(?:(?:used|referenced|invalid|implicit)\s+)*(\w+)\s+('[^']*'(?::'[^']*')?)(.*)$", l)
        if not mm:
            continue
        name, ty, rest = mm.group(1), mm.group(2), mm.group(3)
        if ("*" not in ty and not re.search(r"\bu?intptr_t\b", ty)) or SKIPT.match(ty) or STRARR.match(ty):
            continue
        if re.search(r"\bextern\b", rest):
            continue
        local = any(k in FN for k in stack[:-1])
        st = "static" if re.search(r"\bstatic\b", rest) else "tls" if re.search(r"\btls\b", rest) else ("file" if not local else "")
        if not st:
            continue
        if not in_scope(name_loc[0]) or os.path.normpath(name_loc[0]) not in want:
            continue
        out.append(dict(file=rel(name_loc[0]), line=name_loc[1], name=name, type=ty.split("':'")[0].strip("'"), storage=st,
                        path=os.path.normpath(name_loc[0])))
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
    f = os.path.normpath(os.path.join(e["directory"], e["file"]))
    hdrs = {os.path.normpath(h) for h in [f] + [os.path.join(ROOT, x) for x in []]}
    want = {f} | {os.path.normpath(os.path.join(ROOT, h)) for h in HEADERS}
    return f, p.returncode, parse(p.stdout, want)

HEADERS = []

def main():
    a = sys.argv[1:]
    global HEADERS
    import glob
    HEADERS = [os.path.relpath(h, ROOT) for h in glob.glob(os.path.join(ROOT, "src/*/*.h"))]
    d = json.load(open(os.path.join(ROOT, "build/compile_commands.json")))
    seen, ents = set(), []
    for e in d:
        f = os.path.normpath(os.path.join(e["directory"], e["file"]))
        if in_scope(f) and f not in seen and not f.endswith(".h"):
            seen.add(f); ents.append(e)
    if "--only" in a:
        k = a[a.index("--only") + 1]; ents = [e for e in ents if k in e["file"]]
    res, fails = [], []
    with ThreadPoolExecutor(int(os.environ.get("J", "6"))) as ex:
        for f, rc, r in ex.map(run_one, ents):
            if rc != 0: fails.append(rel(f))
            res += r
    ded = {}
    for r in res:  # drop declaration-only `extern "C" T* x;` re-declarations (the definition is listed where it lives)
        src = open(r.pop("path"), errors="replace").read().split("\n")[r["line"] - 1]
        if re.match(r'^\s*extern "C"\s+[^{=]*;\s*$', src):
            continue
        ded[(r["file"], r["line"], r["name"])] = r
    res = sorted(ded.values(), key=lambda r: (r["file"], r["line"]))
    sys.stderr.write("tu=%d failed=%s vars=%d\n" % (len(ents), fails, len(res)))
    o = a[a.index("--out") + 1] if "--out" in a else None
    s = json.dumps(dict(tu=len(ents), failed=fails, vars=res), indent=0)
    (open(o, "w").write(s) if o else sys.stdout.write(s))

if __name__ == "__main__":
    main()
