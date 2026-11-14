#!/usr/bin/env python3
"""s7340 class O census: host KSEG0 16 MB upper bounds (0x81000000 / 0xFFFFFFFF81000000) vs the spill arena.
The spill arena is 0x81000000-0x81800000 (s7326) and rs64_ram_top reaches 0x81800000 (s7336): a default-on host
validator `a < 0x81000000` (or `a >= 0x81000000 -> reject`) on a guest pointer drops spill-resident objects.
Reuses tools/s7338_mask_census.py (same scope and C/P/G/D/R/X/S classes) with a class-O regex, plus:
  H the bound is on an RCP-visible address (RDP/VI/RSP buses are 24-bit; s7324/s7327 keep those below 16 MB)
  K value used only as a key / log field   W bound is max(0x81000000, rs64_ram_top) or the spill branch itself
Unclassified or B => exit 1. --controls plants a default-on reject (must be '?') and a widened bound (must be 'W')."""
import re, sys, pathlib, importlib.util
from collections import Counter
ROOT = pathlib.Path(__file__).resolve().parents[1]
_s = importlib.util.spec_from_file_location("s7338", ROOT / "tools/s7338_mask_census.py")
m = importlib.util.module_from_spec(_s); _s.loader.exec_module(m)
m.MASK = re.compile(r"0x(?:FFFFFFFF)?0*81000000(?:u|ull|ULL|U|LL)?\b", re.I)
WLINE = re.compile(r"rs64_ram_top|rs64_s7324_class|spill")
CLASS = {  # s7340 hand review: every s_s7317_live / s_s7332_carve entry is written only under s7317_on() (ROGUESQ_S7317_ALLOCMAP,
           # upstream_compat.cpp malloc hook and rs64_s7325_heapsync's `if (!s7317_on()) return;`), so readers of those maps are D.
    "s7333_hdr": "D",            # carve-key header read (keys exist only under ALLOCMAP); the < 0x81000000 bound guards the 24-bit fold
    "rs64_s7318_bcmp": "D",      # ROGUESQ_S7318_BCMP probe (rs64_s7318_on); lower_bound(0x81000000) = first spill block (ctl source)
    "rs64_s7324_class": "W",     # ROGUESQ_S7324_RCPREF: 0x81000000|q builds the spill alias of an RCP address on purpose
    "rs64_s7324_near": "D", "rs64_s7324_lowspill": "D",   # s7324 RCPREF helpers (only caller src/rsp/s7324_rcp_spill.cpp)
    "g5a_walk": "D",             # ROGUESQ_G5A_WBLIVE walker of the guest rs_malloc arenas (guest heap < 16 MB by construction)
    "rs64_s7326_scan": "D",      # called from rs64_s7325_heapsync after its s7317_on() return; iterates spill blocks on purpose
}

def classify(path, pgf):
    out = []
    for (ln, fn, mk, c, text) in m.sites(path, pgf):
        if c == "?" and WLINE.search(text): c = "W"
        elif c == "?" and fn in CLASS: c = CLASS[fn]
        out.append((ln, fn, mk, c, text))
    return out

def main():
    pgf = m.probe_gate_fns()
    if "--controls" in sys.argv:
        import tempfile
        t = pathlib.Path(tempfile.mkdtemp()) / "planted.cpp"
        t.write_text("static bool live_ok(uint32_t a) {\n    return a >= 0x80000000u && a < 0x81000000u;\n}\n"
                     "static bool wide_ok(uint32_t a) {\n    return a < std::max<uint32_t>(0x81000000u, rs64_ram_top);\n}\n")
        got = {r[1]: r[3] for r in classify(t, pgf)}
        assert got == {"live_ok": "?", "wide_ok": "W"}, f"control failed: {got}"
        print("[s7340] controls: planted default-on 16 MB reject reported '?', widened bound 'W'")
    rows, seen = [], set()
    for pat in m.HOST:
        for p in sorted(ROOT.glob(pat)):
            if p in seen: continue
            seen.add(p)
            for r in classify(p, pgf): rows.append((str(p.relative_to(ROOT)),) + r)
    cc = Counter(r[4] for r in rows)
    print(f"[s7340] class O sites={len(rows)} files={len(seen)} " + " ".join(f"{k}={v}" for k, v in sorted(cc.items())))
    bad = [r for r in rows if r[4] in "?B"]
    for r in rows:
        if r[4] in "RSXKHW" or "-v" in sys.argv: print(f"  {r[4]} {r[0]}:{r[1]} {r[2]} [{r[3]}] {r[5][:110]}")
    for r in bad: print(f"  DEFECT/UNCLASSIFIED {r[0]}:{r[1]} {r[2]} [{r[3]}] :: {r[5][:120]}")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
