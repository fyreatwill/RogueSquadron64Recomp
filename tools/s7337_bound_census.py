#!/usr/bin/env python3
"""s7337 class R census: hard-coded 8 MB "end of guest RAM" bounds after osMemSize became 12 MB at dd>1 (s6858).
G (generated tree): every 0x80800000 literal in RecompiledFuncs/funcs_*.c must have become RS64_RAM_TOP
  (tools/fixup_ramtop.py). Any survivor is a defect.
H (host): every guest-range 8 MB literal (0x80800000 / 0x807FFFxx) in the host sources,
  classed by enclosing function: D = diagnostic (function body is env-gated logging/probe), A = deliberate host-arena
  layout (0x80800000..0x81000000 arenas, s7336 census), B = behaviour (must use rs64_ram_top), X = phys-only dump of the
  first 8 MB, unconverted but harmless. Unclassified non-D functions are listed for review.
Usage: s7337_bound_census.py [--funcs DIR] [--controls]. Exit 1 = G survivor or unclassified H site."""
import re, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
FUNCS = ROOT.parent / "N64Recomp" / "RecompiledFuncs"
HOST = ["src/main/main.cpp", "src/main/upstream_compat.cpp", "src/main/rt64_render_context.cpp", "src/rsp/dpc_bridge.cpp",
        "lib/N64ModernRuntime/ultramodern/src/*.cpp", "lib/N64ModernRuntime/librecomp/src/*.cpp"]
LIT = re.compile(r"0x(?:FFFFFFFF)?(?:80800000|807FFF[0-9A-F]{2})(?:u|ull|ULL|ll)?\b", re.I)
MASK = re.compile(r"0x(?:00800000|800000|7FFFF[0-9A-F])(?:u|ull|ULL)?\b", re.I)  # phys 8 MB masks/ends: counted only (class M, open)
GLIT = re.compile(r"0x80800000(?:u|ull|ULL)?\b")
FN = re.compile(r'^(?:extern "C" |static |inline |__attribute__\(\([^)]*\)\) )*[A-Za-z_][\w:<>\*\s]*?\b([A-Za-z_]\w*)\s*\([^;]*$')
DIAG = re.compile(r"getenv|g_rs64_store_diag|_on\(\)|_en\(\)|enabled\b|dump_frame")
# Hand classification (s7337 review). B sites must reference rs64_ram_top.
CLASS = {
    "rs64_guest_range_valid": "B",          # osSpTaskStartGo OSTask check: fixed s7337 (old bound kept as the A/B reference)
    "rs64_guest_range_valid_top": "B",
    "rs64_s6086_divert": "A", "rs64_s6558_cut": "A", "rs64_s6909_rebuild": "A", "rs64_s6993_mask": "A",
    "rs64_s7335_dlpool_cap": "A", "rs64_s6587_spill_base": "A", "rs64_g1c_apply_dd_policy": "A", "osCreateMesgQueue": "D",
    "rs64_s5229_store": "D", "rs64_floor_ownership": "D", "rs64_g5b_trigen": "D",
    "map_result": "D", "factor5_gfx_runner": "D", "snap": "X", "__osRdbSend_recomp": "X", "rs64_spai_guard_bad": "X",
    "rs64_dump_ucode": "X", "queue_samples": "D", "rs64_log_ai_output": "D",
}

def funcs_of(path):
    lines = path.read_text(errors="replace").splitlines()
    fn, start, out = "?", 0, []
    incom = False
    for i, l in enumerate(lines):
        was = incom
        if "/*" in l and "*/" not in l.split("/*", 1)[1]: incom = True
        if incom and "*/" in l and not ("/*" in l and l.rfind("/*") > l.rfind("*/")): incom = False
        if l and not l[0].isspace() and l[0] not in "#/}{":
            m = FN.match(l)
            if m and m.group(1) not in ("if", "for", "while", "switch", "return"):
                fn, start = m.group(1), i
        for m in LIT.finditer(l):
            pre = l[:m.start()]
            com = was or "//" in pre or ("/*" in pre and "*/" not in pre[pre.rfind("/*"):])
            out.append((i + 1, fn, m.group(0), l.strip()[:150], start, com))
    return lines, out

def host_census():
    rows, unk = [], []
    for pat in HOST:
        for p in sorted(ROOT.glob(pat)):
            lines, sites = funcs_of(p)
            for ln, fn, lit, text, start, com in sites:
                body = "\n".join(lines[start:ln])
                c = "C" if com else "I" if "rs64_ram_top = 0x80800000u" in text else \
                    CLASS.get(fn) or ("D" if DIAG.search(body) else "?")
                rows.append((str(p.relative_to(ROOT)), ln, fn, lit, c, text))
                if c == "?": unk.append(rows[-1])
                if c == "B" and "80800000" in lit and "rs64_guest_range_valid_top(" not in text and "0x80800000u : " not in text \
                        and "0x80800000u)" not in text and "rs64_ram_top" not in body:
                    unk.append(rows[-1])
    return rows, unk

def gen_census(d):
    surv = []
    for p in sorted(d.glob("funcs_*.c")):
        for i, l in enumerate(p.read_text(errors="replace").splitlines(), 1):
            if GLIT.search(l): surv.append((p.name, i, l.strip()[:150]))
    return surv

def main():
    d = pathlib.Path(sys.argv[sys.argv.index("--funcs") + 1]) if "--funcs" in sys.argv else FUNCS
    if "--controls" in sys.argv:  # positive controls: the scanners must fire on planted text
        import tempfile
        t = pathlib.Path(tempfile.mkdtemp()); (t / "funcs_0.c").write_text("if (a < 0x80800000u) x = 0x80800000ull;\n")
        assert len(gen_census(t)) == 1, "G control failed"
        print("[s7337] controls: G planted survivor found")
    rows, unk = host_census(); surv = gen_census(d)
    from collections import Counter
    cc = Counter(r[4] for r in rows)
    nm = sum(len(MASK.findall(q.read_text(errors="replace"))) for pat in HOST for q in ROOT.glob(pat))
    print(f"[s7337] phys-mask literals (class M, not classified here)={nm}")
    print(f"[s7337] host sites={len(rows)} " + " ".join(f"{k}={v}" for k, v in sorted(cc.items())))
    for r in rows:
        if r[4] in "BA": print(f"  {r[4]} {r[0]}:{r[1]} [{r[2]}] {r[5]}")
    for r in unk: print(f"  UNCLASSIFIED {r[0]}:{r[1]} [{r[2]}] {r[3]} :: {r[5]}")
    print(f"[s7337] generated survivors={len(surv)} ({d})")
    for s in surv: print(f"  G {s[0]}:{s[1]} {s[2]}")
    return 1 if (surv or unk) else 0

if __name__ == "__main__":
    sys.exit(main())
