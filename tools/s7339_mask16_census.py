#!/usr/bin/env python3
"""s7339 class N census: 16 MB physical masks/ends (& 0xFFFFFx, 0x1000000) in host code vs the spill arena.
The spill arena is 0x81000000-0x81800000 = phys 0x01000000+ (s7326) and rs64_ram_top is widened to its end (s7336), so a
host CPU-side `rdram + (a & 0xFFFFFF)` on a spill pointer folds onto phys 0x00xxxxxx, and an `< 0x1000000` bound rejects it.
Reuses tools/s7338_mask_census.py (same scope, same C/P/G/D/R/X/S classes) with a class-N regex, plus:
  H hardware-bus 24-bit address: VI origin register, RDP command/image/colour/texture addresses, RSP DMA, GBI segment math.
    Correct by design: the RDP/VI/RSP buses are 24-bit, and s7324/s7327 keep every RCP-visible address below 16 MB
    (or widen RSP DMA to 0x1FFFFF8 when spill is live).
  K value used only as a map key / compare key / log field (never dereferenced through the mask).
Unclassified or B => exit 1. --controls plants a default-on 16 MB fold (must be '?') and an H line (must be 'H').
Runtime second line (s7339, dd8 21:9 hangar->mission, spill live): [s7339] spai hi 0, vimode hi 0, selftest PASS."""
import re, sys, pathlib, importlib.util
import importlib.util as _ilu_cr, sys as _sys_cr
if "census_rules" not in _sys_cr.modules:  # s7654 shared text-anchored rules (one instance per process)
    _crs = _ilu_cr.spec_from_file_location("census_rules", __import__("pathlib").Path(__file__).resolve().parent / "census_rules.py")
    _sys_cr.modules["census_rules"] = _ilu_cr.module_from_spec(_crs); _crs.loader.exec_module(_sys_cr.modules["census_rules"])
census_rules = _sys_cr.modules["census_rules"]
from collections import Counter
ROOT = pathlib.Path(__file__).resolve().parents[1]
_s = importlib.util.spec_from_file_location("s7338", ROOT / "tools/s7338_mask_census.py")
m = importlib.util.module_from_spec(_s); _s.loader.exec_module(m)
m.MASK = re.compile(r"0x0*(?:FFFFF[0-9A-F]|1000000)(?:u|ull|ULL|U)?\b", re.I)
# H by line text: the masked value is a hardware-bus address.
HLINE = re.compile(r"VI_ORIGIN_REG|vi_committed_origin\(\)|RDP_ADDRESS_MASK|RSP_DMA_MASK|segments\[|imageTopSeg|"
                   r"maskPhysicalAddress|kSubmitRam|colorImage\.address|colorImg\.address|texture\.address|screenFbAddress|"
                   r"newVI\.origin|\bo\.origin|\bc\.origin|vi\.origin|addressStart|kRdramBytes|w1w? & 0x00FFFFFF|w1v & 0x00FFFFFF|"
                   r"w0 & 0xFFFFFF|addr24|g_cine_last_(?:cimg|settimg)_addr|origin &= 0x00FFFFFFu|origin & 0x00FFFFFFu|"
                   r"vi\.fbAddress|fb & 0x00FFFFFF|target_addr & 0x00FFFFFF|optr & 0xFFFFFFu|key\.address|prev & 0xFFFFFF|"
                   r"done\.phys|phys < 0x0|phys \+ 4u < 0x01000000u|last_drawn_fb|AddressMask = 0xFFFFF8|dl->w1 & 0x00FFFFFFu|"
                   r"load_w1|AddressMask|\bphys >= 0x01000000u|fb_phys")
CLASS = {  # s7339 hand review of the default-on functions; reason in the comment
    "rs64_pcm_writer_phase": "H", "rs64_m5_b40_writer_event": "H", "start_m5_task_write_fault_watch": "H",  # VI origin
    "rs64_m5_host_write_census": "D",   # rs64_s6843_len gate (s6843 host-write note)
    "s7333_hdr": "R",                   # carve audit header read; key bounded < 0x81000000 first, size cap; host-map audit
    "rs64_s7324_class": "R",            # the spill detector itself (q >= 0x01000000 = spill)
    "g5a_rd": "D", "g5a_walk": "D",     # ROGUESQ_G5A_WBLIVE walker; heads bounded < 0x81000000 first
    "rs64_g1d_fillpc_note": "D",        # G1d fill-PC note (rs64_g1d_blk_enabled path)
    "rs64_dpc_current_read": "H",       # kSubmitRamMask/End: the RDP command bus (s6690)
    "rs64_g5b_trigen": "D",             # G5b trigen log reader
    "rt64_cine_fb_is_slot_owned": "K",  # map key of a colour-image address (RDP 24-bit)
    "rs64_s4211_pi_note": "D", "rs64_s4211_task": "D",   # s4211 ring notes
    "audio_image_summary_locked": "K", "audio_image_scope_locked": "K",  # audio audit scope key
    "rs64_s7096_task": "D", "rs64_s7096_end": "D", "rs64_s7096_fwd": "D", "rs64_s7096_drop": "D",  # ROGUESQ_S7096_FWD
    "note": "D", "rs64_s7324_rdp": "D", # s7324 RCP-ref audit (ROGUESQ_S7324_RCPREF)
    "osViSetMode_recomp": "H",          # OSViMode pointer: static osViModeTable (s7339 runtime: 80128C90-80128E40, hi 0)
    "get_n64_input": "D",               # autopilot/aim/god harness rows, each behind its own env flag
    "run_task": "D",                    # ROGUESQ_LOG_HUDBIT block
}

def classify(path, pgf):
    out = []
    for (ln, fn, mk, c, text) in m.sites(path, pgf):
        if c in "?D" and HLINE.search(text): c = "H"
        elif c == "?" and fn in CLASS: c = CLASS[fn]
        elif c == "?" and census_rules.lookup(str(path), fn, text): c = census_rules.lookup(str(path), fn, text)[0]
        elif c == "?" and "/rt64/src/hle/" in str(path) or c == "?" and "/rt64/src/gbi/" in str(path): c = "H"
        out.append((ln, fn, mk, c, text))
    return out

def main():
    pgf = m.probe_gate_fns()
    if "--controls" in sys.argv:
        import tempfile
        t = pathlib.Path(tempfile.mkdtemp()) / "planted.cpp"
        t.write_text("static uint32_t live_fold(uint32_t a) {\n    uint32_t p = rdram[a & 0xFFFFFFu];\n    return p;\n}\n"
                     "static uint32_t vi_hw(void) {\n    return vi->VI_ORIGIN_REG & 0x00FFFFFFu;\n}\n")
        got = {r[1]: r[3] for r in classify(t, pgf)}
        assert got == {"live_fold": "?", "vi_hw": "H"}, f"control failed: {got}"
        print(f"[s7339] controls: planted live 16 MB fold reported '?', VI origin mask 'H'")
    rows, seen = [], set()
    for pat in m.HOST:
        for p in sorted(ROOT.glob(pat)):
            if p in seen: continue
            seen.add(p)
            for r in classify(p, pgf): rows.append((str(p.relative_to(ROOT)),) + r)
    cc = Counter(r[4] for r in rows)
    print(f"[s7339] class N sites={len(rows)} files={len(seen)} " + " ".join(f"{k}={v}" for k, v in sorted(cc.items())))
    bad = [r for r in rows if r[4] in "?B"]
    for r in rows:
        if r[4] in "RSXK" or "-v" in sys.argv: print(f"  {r[4]} {r[0]}:{r[1]} {r[2]} [{r[3]}] {r[5][:110]}")
    for r in bad: print(f"  DEFECT/UNCLASSIFIED {r[0]}:{r[1]} {r[2]} [{r[3]}] :: {r[5][:120]}")
    bad = list(bad) + census_rules.report("s7339")  # s7654: a stale shared rule fails the gate (after the row printers)
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
