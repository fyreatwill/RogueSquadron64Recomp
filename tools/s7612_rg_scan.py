#!/usr/bin/env python3
"""s7612 class RG scanner: host static / thread_local / file-scope state holding a value taken from a guest REGISTER
(ctx->rN / ctx->fN / ctx->hi|lo, gpr[N] / fpr[N] arrays handed to hooks) and kept for a LATER call.

Reuses tools/s7611_sn_scan.py's static-store detector with a second taint source (SN stays closed with its own set):
  REG  the register token set above, direct on the stored RHS or through a same-function local;
  PARM parameters of every host function that some call site in scope passes a REG-tainted argument to (one hop,
       e.g. rs64_s7030_begin(rdram, U32(ctx->r4)) taints a0 inside rs64_s7030_begin).
Usage: s7612_rg_scan.py [--extra FILE...] -> JSON list of {file, line, name, text, auto, src} on stdout.
"""
import importlib.util, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_sp = importlib.util.spec_from_file_location("sn_scan", os.path.join(ROOT, "tools/s7611_sn_scan.py"))
sn = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(sn)

REG = re.compile(r"\bctx->(?:r\d+|f\d+|hi|lo)\b|\bgpr\s*\[\s*\d+\s*\]|\bfpr\s*\[\s*\d+\s*\]")
SKIP = {"if", "while", "for", "switch", "return", "sizeof", "U32", "S32", "ADD32", "SUB32", "MEM_W", "MEM_H", "MEM_B",
        "MEM_BU", "MEM_HU", "MEM_WU", "MEM_D", "LOOKUP_FUNC", "fprintf", "printf", "snprintf", "memcpy", "memset"}

def call_args(line, start):
    """balanced argument text of the call whose '(' is at line[start]."""
    d = 0
    for j in range(start, len(line)):
        if line[j] == "(":
            d += 1
        elif line[j] == ")":
            d -= 1
            if d == 0:
                return line[start + 1:j]
    return line[start + 1:]

def hot_functions(files):
    """names of functions called anywhere in scope with a REG token in their argument list, and that are DEFINED
    in scope (a call into libc/RT64 cannot park the value in our statics)."""
    called, defined = set(), set()
    for p in files:
        try:
            raw = open(p, errors="replace").read().split("\n")
        except OSError:
            continue
        for l in raw:
            s = sn.strip(l)
            if sn.FUNC_START.match(s):
                m = re.search(r"(\w+)\s*\(", s.replace("RECOMP_FUNC", ""))
                if m:
                    defined.add(m.group(1))
            if "ctx->" not in s and "gpr" not in s and "fpr" not in s:
                continue
            for m in re.finditer(r"\b(\w+)\s*\(", s):
                n = m.group(1)
                if n in SKIP or n.isupper():
                    continue
                if REG.search(call_args(s, m.end() - 1)):
                    called.add(n)
    return called & defined

def scan(extra=()):
    files = list(sn.scope_files()) + list(extra)
    hot = hot_functions(files)
    res = []
    for p in files:
        rel = os.path.relpath(p, ROOT) if p.startswith(ROOT) else "RF/" + os.path.basename(p) if p.startswith(sn.GEN) else p
        for c in sn.scan_file(p, rel, REG, hot):
            c["src"] = "REG" if REG.search(c["text"]) else "PARM/local"
            res.append(c)
    return res, hot

if __name__ == "__main__":
    a = sys.argv[1:]
    extra = a[a.index("--extra") + 1:] if "--extra" in a else []
    r, hot = scan(extra)
    json.dump(r, sys.stdout, indent=0)
