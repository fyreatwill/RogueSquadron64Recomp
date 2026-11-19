#!/usr/bin/env python3
"""s7614 class HM: join of tools/s7614_hm_ast.py output. For every static-storage VarDecl whose (element) type names a repo
record (qualified-name match on clang's desugared spelling; unnamed records by location; global-namespace and function-local
records preferring the var's own file), list the record's POINTER-like members, recursing into member records (depth 4).
Field kinds (auto, from the desugared field type):
  fnptr   function pointer / std::function / callback typedef      host code
  str     char* / const char* / atomic<const char*>                 host string tag (literal or host buffer)
  file    FILE*                                                     host handle
  queue   moodycamel / std:: internals (ProducerBase*, Block*, ...) host container internals
  ptr     any other T*, T*[N], atomic<T*>, iterator, void*          needs a ROW in the census
API: members(ast) -> list of dict(file,line,var,type,record,rqname,field,ftype,kind)."""
import json, os, re, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def desug(t):
    t = t.strip("'")
    return t.split("':'")[-1]

FNT = set()  # function-type typedef names, from the AST (fn_typedefs)

def fkind(t):
    d = desug(t)
    if re.search(r"\(\*\)|std::function|GenericFunction|std::variant<[^>]*\(\*\)", d) or \
       re.fullmatch(r"(?:const )?(%s) \*(?: ?const)?" % "|".join(map(re.escape, FNT)), d) if FNT else False:
        return "fnptr"
    if re.fullmatch(r"(?:std::atomic<)?(?:const )?(?:volatile )?char \*(?: ?const)?(?:>)?(?:\[\d*\])?", d):
        return "str"
    if re.match(r"^(?:FILE|__sFILE|struct __sFILE) \*", d):
        return "file"
    args = d[d.find("<"):] if "<" in d else ""
    while re.search(r"\([^()]*\)", args):
        args = re.sub(r"\([^()]*\)", "", args)
    if re.search(r"ProducerBase|ImplicitProducer|ExplicitProducer|LightweightSemaphore|std::promise", d) or \
       (re.search(r"moodycamel|ConcurrentQueue", d) and "*" not in args):
        return "queue"  # container internals; a queue whose ELEMENT is a pointer falls through to 'ptr' (held views)
    if "*" in d or "iterator" in d or re.search(r"\bu?intptr_t\b", t):
        return "ptr"
    return None

class Idx:
    def __init__(self, ast):
        self.byq = collections.defaultdict(list); self.byloc = {}
        for r in ast["records"]:
            self.byloc[r["loc"]] = r
            if r["name"]:
                self.byq[r["qname"]].append(r)
                self.byq["@" + r["name"]].append(r)
        self.memo = {}

    def refs(self, t, file):
        d = desug(t)
        out = []
        for m in re.finditer(r"unnamed (?:struct|union|class) at ([^)]+)\)", d):
            if m.group(1) in self.byloc:
                out.append(self.byloc[m.group(1)])
        d2 = d.replace("(anonymous namespace)", "__ANON__")
        d2 = re.sub(r"\((?:unnamed [^)]*|lambda at [^)]*)\)", "", d2)
        while re.search(r"\([^()]*\)", d2):  # function signatures: their parameter types are not held members
            d2 = re.sub(r"\([^()]*\)", "", d2)
        d2 = d2.replace("__ANON__", "(anonymous namespace)")
        for m in re.finditer(r"(?:(?:\(anonymous namespace\)|[A-Za-z_]\w*)::)*[A-Za-z_]\w*", d2):
            q = m.group(0)
            if q in self.byq:
                c = self.byq[q]
                if len(c) > 1:  # same qualified name defined in several TUs (anonymous namespaces): own file, else headers
                    c = [r for r in c if r["file"] == file] or [r for r in c if re.search(r"\.(h|hpp)$", r["file"])] or c
                out += c
            elif "::" not in q and "@" + q in self.byq:
                c = self.byq["@" + q]
                # bare spelling: a record of that name defined in the var's own file, else in a header
                same = [r for r in c if r["file"] == file]
                out += same or [r for r in c if re.search(r"\.(h|hpp)$", r["file"])]
        u = []
        for r in out:
            if r not in u: u.append(r)
        return u

    def ptr_fields(self, r, file, depth=0):
        k = r["loc"]
        if k in self.memo:
            return self.memo[k]
        self.memo[k] = []
        res = []
        for n, t in r["fields"]:
            kd = fkind(t)
            if kd and "concurrentqueue" in r["file"]:
                kd = "queue"  # moodycamel container internals (host blocks / producers)
            if kd:
                res.append((n, t, kd))
            if depth < 4 and kd != "fnptr":
                for s in self.refs(t, r["file"]):
                    if s is not r:
                        res += [(n + "." + n2, t2, k2) for n2, t2, k2 in self.ptr_fields(s, file, depth + 1)]
        self.memo[k] = res
        return res

def members(ast):
    FNT.clear(); FNT.update(ast.get("fn_typedefs", []))
    ix = Idx(ast)
    out = []
    seen = set()
    for v in ast["vars"]:
        top = desug(v["type"])
        while re.search(r"<[^<>]*>", top):
            top = re.sub(r"<[^<>]*>", "T", top)
        if "*" in re.sub(r"\((?:anonymous namespace|unnamed [^)]*|lambda at [^)]*)\)", "", top):
            continue  # pointer to a record: the var itself is class HP; the pointee's members are not static storage
        for r in ix.refs(v["type"], v["file"]):
            for n, t, kd in ix.ptr_fields(r, v["file"]):
                key = (v["file"], v["name"], v["line"], r["loc"], n)
                if key in seen: continue
                seen.add(key)
                out.append(dict(file=v["file"], line=v["line"], var=v["name"], type=desug(v["type"]), record=r["name"] or "(unnamed)",
                                rqname=r["qname"] or r["loc"].split("/")[-1], rfile=r["file"], field=n, ftype=desug(t), kind=kd))
    return out

if __name__ == "__main__":
    ast = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "scratch/s7614/ast.json")))
    m = members(ast)
    c = collections.Counter(x["kind"] for x in m)
    print("members", len(m), dict(c), "vars", len({(x["file"], x["var"]) for x in m}))
    for x in m:
        if x["kind"] == "ptr":
            print("%s:%d %s | %s | %s.%s : %s" % (x["file"], x["line"], x["var"], x["type"][:50], x["rqname"], x["field"], x["ftype"][:50]))
