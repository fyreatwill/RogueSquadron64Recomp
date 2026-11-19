#!/usr/bin/env python3
"""s7614 class HM second source: clang -ast-dump census of pointer MEMBERS of static aggregates.

Over the same TUs and scope as tools/s7613_hp_ast.py (src/*, librecomp/src, ultramodern/src, generated RecompiledFuncs),
collects per TU:
  records  every RecordDecl / CXXRecordDecl *definition* located in the repo (src/, include/, lib/N64ModernRuntime/),
           keyed by (file, name) - unnamed records by their 'file:line:col' location, which is how clang spells their type -
           with every FieldDecl (name, type).
  vars     every VarDecl with static storage duration (static, thread_local, namespace/file scope, static member) in an
           in-scope file, of ANY type (pointer-typed ones are class HP and are re-listed here only for the join).
Joining (which var holds a record with a pointer field, recursively) is done by tools/s7614_hm_census.py.
Output: JSON {tu, failed, records:[{file,line,name,loc,fields:[[name,type]...]}], vars:[{file,line,name,type,storage}]}."""
import json, os, re, sys
from concurrent.futures import ThreadPoolExecutor
import importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_sp = importlib.util.spec_from_file_location("hp_ast", os.path.join(ROOT, "tools/s7613_hp_ast.py"))
hpa = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(hpa)
LOC = hpa.LOC
FN = hpa.FN

def rec_scope(f):
    f = os.path.normpath(f)
    if f.startswith(hpa.GEN + "/"):
        return True
    r = os.path.relpath(f, ROOT)
    return r.startswith(("src/", "include/", "lib/N64ModernRuntime/")) and not r.startswith("..")

def parse(text, tu):
    cur, cline, ccol = None, 0, 0
    stack = []          # (kind, extra) per depth
    recs, vars_ = [], []
    open_rec = {}       # depth -> record dict
    scope = {}          # depth -> namespace / record name component (qualified-name stack)
    byaddr = {}         # record node address -> record (unnamed records adopt a `typedef struct {...} Name;` name)
    tdef = {}           # depth -> typedef name being declared
    fnt = set()         # function-type typedef names
    for l in text.split("\n"):
        m = re.match(r"^([| `]*)[-`]?(\w+)", l)
        if not m:
            continue
        depth = len(m.group(1)) // 2
        kind = m.group(2)
        del stack[depth:]
        for d in [d for d in open_rec if d >= depth]:
            del open_rec[d]
        for d in [d for d in scope if d >= depth]:
            del scope[d]
        for d in [d for d in tdef if d >= depth]:
            del tdef[d]
        if tdef and kind in ("CXXRecord", "Record"):
            ma = re.search(r"Record (0x[0-9a-f]+)", l)
            r0 = byaddr.get(ma.group(1)) if ma else None
            if r0 is not None and not r0["name"]:
                nmt = tdef[max(tdef)]
                r0["name"] = nmt; r0["qname"] = nmt if r0["local"] else "::".join(r0.pop("_scope") + [nmt]); r0["typedef"] = True
            continue
        if kind in ("TypedefDecl", "TypeAliasDecl"):
            mt = re.search(r"(?:col:\d+|line:\d+:\d+|:\d+:\d+)\s+(?:referenced\s+)?(\w+)\s+'", l)
            if mt:
                tdef[depth] = mt.group(1)
                mq = re.search(r"\s(\w+)\s+'([^']*)'", l)
                if mq and re.match(r"^(?!decltype|__typeof|typeof)[^()]+\((?:[^()]|\([^()]*\))*\)(?:\s*(?:noexcept|const))*$", mq.group(2)) and not re.search(r"\(\*\)|\(&\)", mq.group(2)):
                    fnt.add(mq.group(1))  # typedef / using of a FUNCTION type: `name *` fields are function pointers
        stack.append(kind)
        name_loc = None
        for x in LOC.finditer(l):
            if x.group(2):
                cur = x.group(1).rsplit(":", 2)[0]; cline = int(x.group(2)); ccol = int(x.group(1).rsplit(":", 1)[1])
            elif x.group(3):
                cline = int(x.group(3)); ccol = int(x.group(0).rsplit(":", 1)[1])
            else:
                ccol = int(x.group(1).split(":")[1])
            name_loc = (cur, cline, ccol)
        if kind == "NamespaceDecl":
            mm = re.search(r"(?:col:\d+|line:\d+:\d+|:\d+:\d+)\s+(?:inline\s+)?(\w+)?\s*$", l.split(" original ")[0])
            scope[depth] = (mm.group(1) if mm and mm.group(1) else "(anonymous namespace)")
            continue
        if kind in ("RecordDecl", "CXXRecordDecl") and " definition" in l and name_loc and name_loc[0]:
            if "implicit" in l.split(">")[-1].split()[:3]:
                continue
            if not rec_scope(name_loc[0]):
                continue
            mm = re.search(r"(?:struct|union|class)\s+(\w+)\s+definition", l)
            nm = mm.group(1) if mm else ""
            loc = "%s:%d:%d" % (os.path.normpath(name_loc[0]), name_loc[1], name_loc[2])
            local = any(k in FN for k in stack[:-1])
            q = "::".join([scope[d] for d in sorted(scope)] + [nm]) if nm and not local else nm
            if nm:
                scope[depth] = nm
            r = dict(file=hpa.rel(name_loc[0]), line=name_loc[1], name=nm, qname=q, local=local, loc=loc, fields=[],
                     _scope=[scope[d] for d in sorted(scope)])
            ma = re.match(r"^[| `]*[-`]?\w+ (0x[0-9a-f]+)", l)
            if ma:
                byaddr[ma.group(1)] = r
            recs.append(r); open_rec[depth] = r
            continue
        if kind == "FieldDecl" and (depth - 1) in open_rec:
            mm = re.search(r"(?:col:\d+|line:\d+:\d+|:\d+:\d+)\s+(?:(?:used|referenced|invalid|implicit)\s+)*(\w+)?\s*('[^']*'(?::'[^']*')?)", l)
            if mm:
                open_rec[depth - 1]["fields"].append([mm.group(1) or "", mm.group(2)])
            continue
        if kind != "VarDecl" or not name_loc or not name_loc[0]:
            continue
        mm = re.search(r"(?:col:\d+|line:\d+:\d+|:\d+:\d+)\s+(?:(?:used|referenced|invalid|implicit)\s+)*(\w+)\s+('[^']*'(?::'[^']*')?)(.*)$", l)
        if not mm:
            continue
        name, ty, rest = mm.group(1), mm.group(2), mm.group(3)
        if re.search(r"\bextern\b", rest):
            continue
        local = any(k in FN for k in stack[:-1])
        st = "static" if re.search(r"\bstatic\b", rest) else "tls" if re.search(r"\btls\b", rest) else ("file" if not local else "")
        if not st or not hpa.in_scope(name_loc[0]) or os.path.normpath(name_loc[0]) != tu:
            continue
        vars_.append(dict(file=hpa.rel(name_loc[0]), line=name_loc[1], name=name, type=ty, storage=st))
    for r in recs:
        r.pop("_scope", None)
    return recs, vars_, fnt

def run_one(e):
    import shlex, subprocess
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
    r, v, ft = parse(p.stdout, f)
    return f, p.returncode, r, v, ft

def main():
    a = sys.argv[1:]
    d = json.load(open(os.path.join(ROOT, "build/compile_commands.json")))
    seen, ents = set(), []
    for e in d:
        f = os.path.normpath(os.path.join(e["directory"], e["file"]))
        if hpa.in_scope(f) and f not in seen and not f.endswith(".h"):
            seen.add(f); ents.append(e)
    if "--only" in a:
        k = a[a.index("--only") + 1]; ents = [e for e in ents if k in e["file"]]
    recs, vars_, fails, fnts = {}, {}, [], set()
    with ThreadPoolExecutor(int(os.environ.get("J", "6"))) as ex:
        for f, rc, r, v, ft in ex.map(run_one, ents):
            if rc != 0: fails.append(hpa.rel(f))
            fnts |= ft
            for x in r:
                k = x["loc"]
                if k not in recs or len(x["fields"]) > len(recs[k]["fields"]) or (x["name"] and not recs[k]["name"]):
                    recs[k] = x
            for x in v:
                vars_[(x["file"], x["line"], x["name"])] = x
    out = dict(tu=len(ents), failed=fails, fn_typedefs=sorted(fnts), records=sorted(recs.values(), key=lambda r: r["loc"]),
               vars=sorted(vars_.values(), key=lambda r: (r["file"], r["line"])))
    sys.stderr.write("tu=%d failed=%s records=%d vars=%d\n" % (len(ents), fails, len(recs), len(vars_)))
    o = a[a.index("--out") + 1] if "--out" in a else None
    s = json.dumps(out, indent=0)
    (open(o, "w").write(s) if o else sys.stdout.write(s))

if __name__ == "__main__":
    main()
