#!/usr/bin/env python3
"""s7338 class M census: physical 8 MB RDRAM masks/ends (& 0x7FFFFx, < 0x800000, 0x800000 - x) in host code.
At dd>1 guest data reaches 0x80C00000 and host arenas (DLPOOLX 0x80C00000.., spill 0x81000000..0x81800000) feed the gfx
path, so a default-on mask would fold 0x80C01234 onto 0x00401234 (silent wrong read) or reject a live address.
Every site is classed by enclosing function:
  C comment | P in-ucode probe behind the s6715 call-site gate (PROBE_GATE_FNS in tools/fixup_factor5_ucode.py)
  G function opens with an early return on a log/env gate | D body env/log-gated (s7337 DIAG regex) or hand-classed diag
  R read-only audit (hash/key/log input; never feeds guest state or rendering) | X file/RDRAM dump of the first 8 MB
  S size cap, not an address | B behaviour: a default-on path that masks a live address (defect).
Unclassified or B => exit 1. --controls plants a default-on mask function and requires it to be reported.
Scope: the s7337 host list + src/rsp/*.cpp + lib/rt64/src/{gbi,hle,render,common}. RSP DMA (rsp.hpp dma_*) uses the
s7327 rs64_s7327_mask (0xFFFFF8 / 0x1FFFFF8), no 8 MB literal; the ucode C files carry none either (checked s7338)."""
import re, sys, pathlib, importlib.util
ROOT = pathlib.Path(__file__).resolve().parents[1]
_s = importlib.util.spec_from_file_location("s7337", ROOT / "tools/s7337_bound_census.py")
s7337 = importlib.util.module_from_spec(_s); _s.loader.exec_module(s7337)
MASK, FN, DIAG = s7337.MASK, s7337.FN, s7337.DIAG
HOST = s7337.HOST + ["src/rsp/*.cpp", "lib/rt64/src/gbi/*.cpp", "lib/rt64/src/hle/*.cpp", "lib/rt64/src/hle/*.h",
                     "lib/rt64/src/render/*.cpp", "lib/rt64/src/common/*.cpp"]
GATE = re.compile(r"^\s*if \(!?\s*(?:!|[\w:]*(?:log|_on|on_|probe|enabled|getenv|dlwalk|diag)\w*).*\breturn\b", re.I)
# Hand classification (s7338 review): reason in the comment.
CLASS = {
    "rs64_audio_hash_rdram": "R",       # FNV of an audio window for the M5 image-stage audit row; output only printed
    "rs64_filter_voice_guest_hash": "D", "rs64_filter_voice_guest_word": "D",   # filter-voice audit helpers (audit_row only)
    "rs64_filter_voice_guest_span_ok": "D", "rs64_filter_voice_guest_pointer": "D",
    "rs64_dump_ucode": "X",             # writes ucode_XXXXXX.bin once per ucode address
    "__osRdbSend_recomp": "S",          # s5258 rejects a size > 8 MB; address is not masked
    "rs64_s5229_entry": "D", "rs64_s5229_store": "D",   # rs64_s5229_on / g_s5229_pc (null unless armed)
    "rs64_s6845_base": "D", "rs64_s6845_entry": "D", "rs64_s6845_glyph": "D",   # rs64_s6845_on call-site gate
    "rs64_fill_note_hi": "D",           # stderr log of hi fills only
    "start_fl_zero_poller": "D",        # started only under ROGUESQ_LOG_FL_ZERO_WATCH
    "dlw_dump_words": "D",              # callers sit in dlwalk_on() paths
    "rs64_f5_vtxcolor_state": "D",      # only caller rs64_f5_state_probe (P)
    "rs64_inline_probe_trigen_stage": "R",  # stores masked copies read only by gated trigen log rows
    "rs64_s7331_reset_writer_req": "S",
    "factor5_gfx_runner": "D",          # sh2 shadow (ROGUESQ_SHADOW2), WIPE_DLWALK, FS_SLOT, DL_SYNC walkers: all env-gated
    "rs64_run_lle_gfx": "D", "map_result": "D", "snap": "X",
}
RT64_LINE = {  # rt64 sites inside huge member functions: classed by the line text
    "shadeDl = state->displayListAddress & 0x7FFFFFu": "R",   # rs64_shade_ordinal key + log/floor-mesh fields only
    "RDRAMSize = 0x7FFFFF": "X",                             # rt64_state.cpp:fwrite debug dump
    "fwrite(RDRAM, RDRAMSize": "X",
}

def probe_gate_fns():
    t = (ROOT / "tools/fixup_factor5_ucode.py").read_text()
    m = re.search(r"PROBE_GATE_FNS = \((.*?)\)\n", t, re.S)
    return set(re.findall(r'"(\w+)"', m.group(1))) if m else set()

def sites(path, pgf, extra_class=None):
    lines = path.read_text(errors="replace").splitlines()
    fn, start, incom, out = "?", 0, False, []
    cls = dict(CLASS, **(extra_class or {}))
    for i, l in enumerate(lines):
        was = incom
        if "/*" in l and "*/" not in l.split("/*", 1)[1]: incom = True
        if incom and "*/" in l and not ("/*" in l and l.rfind("/*") > l.rfind("*/")): incom = False
        if l and not l[0].isspace() and l[0] not in "#/}{":
            m = FN.match(l)
            if m and m.group(1) not in ("if", "for", "while", "switch", "return"): fn, start = m.group(1), i
        for m in MASK.finditer(l):
            pre = l[:m.start()]
            if was or "//" in pre or ("/*" in pre and "*/" not in pre[pre.rfind("/*"):]): c = "C"
            elif any(k in l for k in RT64_LINE): c = next(v for k, v in RT64_LINE.items() if k in l)
            elif fn in pgf: c = "P"
            elif any(GATE.match(x) for x in lines[start + 1:min(start + 8, i + 1)]): c = "G"
            elif fn in cls: c = cls[fn]
            elif DIAG.search("\n".join(lines[start:i + 1])): c = "D"
            else: c = "?"
            out.append((i + 1, fn, m.group(0), c, l.strip()[:140]))
    return out

def main():
    pgf = probe_gate_fns()
    if "--controls" in sys.argv:
        import tempfile
        t = pathlib.Path(tempfile.mkdtemp()) / "planted.cpp"
        t.write_text("static uint32_t live_fold(uint32_t a) {\n    uint32_t p = a & 0x7FFFFFu;\n    return p;\n}\n"
                     "static void logged(uint32_t a) {\n    if (!log_e9_provenance()) return;\n    a &= 0x7FFFFFu;\n}\n")
        got = {r[1]: r[3] for r in sites(t, pgf)}
        assert got == {"live_fold": "?", "logged": "G"}, f"control failed: {got}"
        assert len(pgf) >= 20, f"PROBE_GATE_FNS parse failed ({len(pgf)})"
        print(f"[s7338] controls: planted live mask reported '?', gated mask 'G', probe-gate fns={len(pgf)}")
    from collections import Counter
    rows, seen = [], set()
    for pat in HOST:
        for p in sorted(ROOT.glob(pat)):
            if p in seen: continue
            seen.add(p)
            for r in sites(p, pgf): rows.append((str(p.relative_to(ROOT)),) + r)
    cc = Counter(r[4] for r in rows)
    print(f"[s7338] class M sites={len(rows)} files={len(seen)} " + " ".join(f"{k}={v}" for k, v in sorted(cc.items())))
    bad = [r for r in rows if r[4] in "?B"]
    for r in rows:
        if r[4] in "RSX" or "-v" in sys.argv: print(f"  {r[4]} {r[0]}:{r[1]} [{r[2]}] {r[5]}")
    for r in bad: print(f"  DEFECT/UNCLASSIFIED {r[0]}:{r[1]} [{r[2]}] {r[3]} :: {r[5]}")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
