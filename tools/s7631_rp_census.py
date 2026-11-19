#!/usr/bin/env python3
"""s7631 class RP census: join the regex source (tools/s7631_rp_scan.py) and the clang AST source (tools/s7631_rp_ast.py)
over lib/rt64/src, classify every store row, run the controls, print the verdict.

  python3 tools/s7631_rp_census.py SCAN.json AST.json [--plant-scan P.json --plant-ast P.json]

Store kinds compared: member / global (normalised to `store`), deref, array, push. `return` rows are info only.
Join key: (file, name, normalised kind) with |line diff| <= 2.  Classes:
  fresh   set and used within one call (interpreter cursor `*dl`, a bracketed set/clear)
  offset  kept across calls but only used as an address (subtracted from the base / compared), never dereferenced
  copy    the bytes are copied (vector assign), no pointer kept
  base    the RDRAM base itself (mapping lives for the process)
  gated   only reachable on a non-default path (HLE interpreter: LLE_FORCE/UNGATED/SOLO default 1) or an env gate
  host    the taint is a call argument; the stored value is a host object (false positive of the subtree rule)
  OPEN    anything else -> needs a runtime witness / fix
Propagation pass: any `X = <row name>` copy of a cross-call row into another non-local is listed and must be classified."""
import json, os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HLE = "gated: HLE interpreter only (Application::processDisplayLists isHLE=true); default LLE_FORCE=UNGATED=SOLO=1 returns before it (src/main/rt64_render_context.cpp send_dl)"
CUR = "fresh: *dl is the interpreter's local cursor passed as &dl (processRDPLists / processDisplayLists), set and consumed in the same call"
CLASS = {
    ("deref", "dl"): ("fresh", CUR),
    ("store", "g_s4271_dl"): ("fresh", "set to *dl immediately before rsp/rdp setColorImage and nulled right after it (same call); readers run inside that call"),
    ("store", "pre"): ("offset", "g_s4271_ring entry: only compared / subtracted from rdram in s4271DumpRing / s4282Probe; the one deref (last-0x100) reads the newest entry, written by the current processRDPLists before the command that triggers the dump"),
    ("store", "post"): ("offset", "g_s4271_ring entry: used only as e.post - e.pre and range compares"),
    ("store", "g_s4271_start"): ("offset", "printed as offset from rdram only"),
    ("store", "g_s4271_end"): ("offset", "printed as offset from rdram only"),
    ("store", "g_s4281_base"): ("offset", "used only as (g_s4281_base - rdram) to index the byte snapshot g_s4281_snap"),
    ("store", "g_s4282_prevbase"): ("offset", "used only as (g_s4282_prevbase - rdram) to index the byte snapshot g_s4282_prev"),
    ("push", "g_s4281_snap"): ("copy", "vector<uint8_t>::assign copies up to 256 KB of DL bytes; no pointer kept"),
    ("store", "RDRAM"): ("base", "State::RDRAM / Core::RDRAM = the rdram base (librecomp mapping lives for the process)"),
    ("store", "hleGBI"): ("host", "getGBIForUCode(state->RDRAM, ...) returns a GBIManager-owned GBI*, not an RDRAM address"),
    ("push", "returnAddressStack"): ("gated", HLE),
}
PER_FILE = {  # rows whose class depends on the file (HLE-only call sites of an otherwise default-on name)
    ("lib/rt64/src/hle/rt64_interpreter.cpp", 1160, "g_s4271_start"): ("gated", HLE),
    ("lib/rt64/src/hle/rt64_interpreter.cpp", 1164, "pre"): ("gated", HLE),
    ("lib/rt64/src/hle/rt64_interpreter.cpp", 1184, "post"): ("gated", HLE),
}

EXPLAINED = {  # one-source rows the other source cannot see by construction (regex has no types)
    ("lib/rt64/src/gbi/rt64_gbi_f3d.cpp", "dl"): "ast-only: `*dl = state->popReturnAddress()` is tainted by its DisplayList* return TYPE; regex sees a plain call",
    ("lib/rt64/src/hle/rt64_application.h", "RDRAM"): "ast-only: implicit copy constructor of Application::Core copies the base field (no source text)",
    ("lib/rt64/src/hle/rt64_interpreter.cpp", "hleGBI"): "ast-only: subtree rule sees state->RDRAM as a call ARGUMENT; regex requires the pointer value itself",
}

def norm(k): return "store" if k in ("member", "global") else k

def rows_of(p):
    return [r for r in json.load(open(p))["rows"] if r["kind"] != "return"]

def join(A, B):
    used, both, onlyA = set(), [], []
    for a in A:
        hit = None
        for j, b in enumerate(B):
            if j in used: continue
            if b["file"] == a["file"] and b["name"] == a["name"] and norm(b["kind"]) == norm(a["kind"]) and abs(b["line"] - a["line"]) <= 2:
                hit = j; break
        if hit is None: onlyA.append(a)
        else: used.add(hit); both.append(a)
    onlyB = [b for j, b in enumerate(B) if j not in used]
    return both, onlyA, onlyB

def classify(r):
    k = (r["file"], r["line"], r["name"])
    if k in PER_FILE: return PER_FILE[k]
    if r["file"].startswith("PLANT/"): return ("OPEN", "planted control")
    return CLASS.get((norm(r["kind"]), r["name"]), ("UNCLASSIFIED", ""))

def propagation(names):
    out = []
    for f in sorted(glob.glob(ROOT + "/lib/rt64/src/**/*.cpp", recursive=True)):
        rp = os.path.relpath(f, ROOT)
        if re.search(r"/(contrib|imgui|tools)/", rp): continue
        for i, l in enumerate(open(f, errors="replace"), 1):
            for m in re.finditer(r"\b(\w+)\s*=\s*(?:\([^()]*\)\s*)?(\w+)\s*;", l):
                if m.group(2) in names and m.group(1) not in names | {"auto"} and not re.search(r"[\w>*&]\s+%s\s*=" % m.group(1), l):
                    out.append(dict(file=rp, line=i, kind="global", name=m.group(1), src=m.group(2)))
    return out

def census(scan, ast, label):
    A, B = rows_of(scan), rows_of(ast)
    both, onlyA, onlyB = join(A, B)
    rows = both + onlyA + onlyB
    tally, table = {}, []
    for r in rows:
        c, why = classify(r)
        src = "both" if r in both else ("regex" if r in onlyA else "ast")
        tally[c] = tally.get(c, 0) + 1
        table.append((r["file"], r["line"], norm(r["kind"]), r["name"], c, src, why))
    cross = {n for (_, _, k, n, c, _, _) in table if c in ("offset", "OPEN")}
    prop = propagation(cross)
    for p in prop:
        c, why = classify(p)
        tally[c] = tally.get(c, 0) + 1
        table.append((p["file"], p["line"], "store", p["name"], c, "prop<-" + p["src"], why))
    return dict(label=label, both=len(both), onlyA=onlyA, onlyB=onlyB, tally=tally, table=table)

def main():
    a = sys.argv[1:]
    res = census(a[0], a[1], "real")
    print("== real: rows both=%d regex-only=%d ast-only=%d" % (res["both"], len(res["onlyA"]), len(res["onlyB"])))
    for t in sorted(res["table"]):
        print("  %-42s %5d %-6s %-20s %-12s %-14s %s" % (t[0].replace("lib/rt64/src/", ""), t[1], t[2], t[3], t[4], t[5], t[6][:90]))
    print("  tally:", res["tally"])
    une = [r for r in res["onlyA"] + res["onlyB"] if (r["file"], r["name"]) not in EXPLAINED]
    for r in res["onlyA"] + res["onlyB"]:
        print("  one-source %s:%d %s -> %s" % (r["file"].replace("lib/rt64/src/", ""), r["line"], r["name"], EXPLAINED.get((r["file"], r["name"]), "UNEXPLAINED")))
    ok = res["tally"].get("OPEN", 0) == 0 and res["tally"].get("UNCLASSIFIED", 0) == 0 and not une
    ctl = True
    if "--plant-scan" in a:
        ps, pa = a[a.index("--plant-scan") + 1], a[a.index("--plant-ast") + 1]
        pres = census(ps, pa, "plant")
        pl = [t for t in pres["table"] if t[0].startswith("PLANT/")]
        want = {"g_plant_kept", "plant_member"}
        got = {t[3] for t in pl if t[4] == "OPEN" and t[5] == "both"}
        c1 = got == want and pres["tally"].get("OPEN", 0) == 2
        print("== control planted OPEN rows (both sources): %s -> %s" % (sorted(got), "PASS" if c1 else "FAIL"))
        nofresh = not any(t[3] == "p" for t in pl)
        print("== control fresh local `p` gives no row: %s" % ("PASS" if nofresh else "FAIL"))
        A, B = rows_of(a[0]), rows_of(a[1])
        dA = [r for r in A if r["name"] == "g_s4281_base"][:1]; dB = [r for r in B if r["name"] == "returnAddressStack"][:1]
        _, oA, oB = join([r for r in A if r not in dA], [r for r in B if r not in dB])
        c3 = len(oA) == len(res["onlyA"]) + len(dB) and len(oB) == len(res["onlyB"]) + len(dA)
        print("== control drop one row per source -> join disagreements regex-only=%d ast-only=%d: %s" % (len(oA), len(oB), "PASS" if c3 else "FAIL"))
        ctl = c1 and nofresh and c3
    print("VERDICT:", ("RP CLOSED (0 OPEN, sources agree)" if ok else "RP NOT CLOSED"), "| controls", "PASS" if ctl else "FAIL")
    sys.exit(0 if ok and ctl else 1)

if __name__ == "__main__":
    main()
