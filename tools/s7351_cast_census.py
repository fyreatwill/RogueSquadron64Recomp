#!/usr/bin/env python3
"""s7351 class AB census: typed loads/stores through a cast guest pointer.
`*(uint32_t*)(rdram + a)` / `*reinterpret_cast<const uint16_t*>(RDRAM + a)` / `((float*)p)[i]` with a guest-chosen address is UB
when the address is not a multiple of the type size (alignment + strict aliasing): clang may fold low address bits, pair or
vectorise the access, and an atomic on it faults on arm64. The guest RDRAM buffer itself is page-aligned, so alignment of the
access = alignment of the guest offset. Scope = s7343 files_in_scope(). Two idioms:
  CAST  a C-style or reinterpret_cast to a pointer to a >1-byte integer / float type
  MEM   host uses of the recomp MEM_W / MEM_H / MEM_HU / MEM_D accessors (the same operation a recompiled lw/lh/ld performs)
Classes: C/P/G/D from tools/s7338_mask_census.py sites() (rt64 G/D re-checked with s7343 body_gated(); CORE demotion as s7344)
  HOST operand is host memory (std container .data(), GPU ->map(), &u128, &userConfig, ROM image, frame pointer, code page):
       not a guest-alignment question (counted, not a site)
  K    guest offset is a literal (or literal + k*size / i*size) that is a multiple of the access size
  ALN  the offset is masked (`& ~3u`, `& 0x..FC`, `& ~7`) or an `(x & 3)` / `% 4` test on it dominates the access
  SP   MEM_* at a constant offset from the guest stack pointer (ctx->r29 / sp): 8-aligned by the MIPS o32 ABI
  GF   the address is a guest pointer the guest itself loads/stores with lw/sw (OSTask fields, ctx->rN argument,
       a field read by MEM_W): misalignment would be a retail address-error exception, so it is aligned by construction
  H    hand-verified (reason in HAND)   B default-on, unproven alignment: defect   ?  unclassified
'?' or B => exit 1. --controls plants `*(uint32_t*)(rdram + task->a)` ('?'), a masked twin `& ~3u` (ALN), a memcpy twin (not a
site), a literal twin (K), a host-container twin (HOST) and a gated twin (G)."""
import re, sys, pathlib, importlib.util
from collections import Counter
ROOT = pathlib.Path(__file__).resolve().parents[1]
def _load(name, f):
    s = importlib.util.spec_from_file_location(name, ROOT / f); mod = importlib.util.module_from_spec(s); s.loader.exec_module(mod); return mod
s44 = _load("s7344", "tools/s7344_wrap_census.py")
s43, m = s44.s43, s44.s43.m

T = r"(?:volatile\s+)?(?:std::)?(u?int(?:16|32|64)_t|float|double|u16|u32|u64|s16|s32|s64|gpr|unsigned(?:\s+(?:int|short|long))?|short|int|long)"
CAST = re.compile(r"(?:reinterpret_cast\s*<\s*(?:const\s+)?%s\s*(?:const\s*)?\*\s*>|\(\s*(?:const\s+)?%s\s*(?:const\s*)?\*\s*\))" % (T, T))
MEMX = re.compile(r"\bMEM_(W|WU|H|HU|D)\s*\(")
SIZE = {"16": 2, "32": 4, "64": 8, "float": 4, "double": 8, "short": 2, "int": 4, "long": 8, "gpr": 8,
        "W": 4, "WU": 4, "H": 2, "HU": 2, "D": 8}
GUEST = re.compile(r"\b(?:rdram|RDRAM|rd|r|g_rdram_for_submit|fromRDRAM|TMEM|DMEM|ram)\b")
HOSTB = re.compile(r"(?:\.data\s*\(|->map\s*\(|&\s*u128|&\s*userConfig|&\s*enhancementConfig|calloc\s*\(|malloc\s*\(|\bfp\b|\bpc\b|"
                   r"fileBytes|&\s*bytes\[|rom\.data|&\s*b\b|g_wp_addr|nativeSwappedRAM)")
LIT = re.compile(r"^(?:0x[0-9A-Fa-f]+|\d+)[uUlL]*$")
HAND = [  # (file suffix, needle in line, class, reason) -- s7351 review
    ("main.cpp", "*(volatile int*)", "HOST", "deliberate test crash (null store) under ROGUESQ test-crash env"),
    ("main.cpp", "const volatile uint64_t* c = (const volatile uint64_t*)p", "HOST", "p = host stack/page pointer scanned for the crash reporter"),
    ("upstream_compat.cpp", "s7239_rw(const uint8_t* rd, uint32_t a)", "H", "callers pass literal level-table / gfx-state addresses + 4k (s7239 sky probe, all 4-aligned)"),
    ("upstream_compat.cpp", "s7239_rh(const uint8_t* rd, uint32_t a)", "H", "callers pass literal + 2k halfword addresses (^2 = BE halfword swizzle)"),
    ("upstream_compat.cpp", "reinterpret_cast<uint32_t*>(rd + (a.cmd - 0x80000000u))", "GF", "a.cmd = a display-list command pointer (DL words are 8-aligned, the gfx ucode DMAs them as dwords)"),
    ("upstream_compat.cpp", "s6892_word(uint8_t* rdram, uint32_t a)", "ALN", "every caller passes s2 + 4k / s2 + 0x18 after s6892_valid(s2) ((v & 3) == 0)"),
    ("upstream_compat.cpp", "s6963_hu(const uint8_t* rd, uint32_t a)", "GF", "a = guest u16 field addresses the guest reads with lhu"),
    ("upstream_compat.cpp", "s6963_w(const uint8_t* rd, uint32_t a)", "GF", "a = guest u32 field / pointer the guest reads with lw"),
    ("upstream_compat.cpp", "*(volatile uint32_t*)(rdram + A[i])", "K", "A[] = static table of literal 4-aligned addresses"),
    ("rt64_render_context.cpp", "reinterpret_cast<uint32_t*>(const_cast<uint8_t*>(rdram) + (a - 0x80000000u))", "GF", "a = guest struct field address the guest stores with sw"),
    ("rt64_render_context.cpp", "auto W = [&](uint32_t a) { return *reinterpret_cast<const uint32_t*>(rdram + (a - 0x80000000u)); };", "GF",
     "lambda reads guest pointer chains (each hop a value the guest loads with lw) + literal 4-aligned field offsets"),
    ("rt64_render_context.cpp", "rdram + (msg + 0x14 - 0x80000000u)", "GF", "msg = OSMesg request pointer the guest passes in a0 (struct, 4-aligned) + 0x14"),
    ("rt64_render_context.cpp", "app->core.RDRAM + (a - 0x80000000u)) = v", "ALN", "ROGUESQ_DEBUG_WRITE only, and the condition requires (a & 3) == 0"),
    ("dpc_bridge.cpp", "g_rdram_for_submit + ph)", "D", "ROGUESQ_G5H_BAND file only (s_bd); literal 4-aligned addresses and cam + 4i after (cam & 3) == 0"),
    ("events.cpp", "rdram + addrs", "K", "addrs[] = static table of literal 4-aligned rodata float addresses (g1c)"),
    ("events.cpp", "rdram + ia[i]", "K", "ia[] = static table of literal 4-aligned int addresses (g1c)"),
    ("events.cpp", "rdram + a)", "K", "rf/rw/a over static literal 4-aligned address tables"),
    ("main.cpp", "rdram + (0x149700u ^ 2u)", "K", "literal 0x149700 ^ 2: even (s4578_poll, ROGUESQ_LOG_S4578 thread)"),
    ("main.cpp", "for (uint32_t p = 0x1496F8u; p < 0x149720u; p += 4)", "K", "literal 0x1496F8 + 4k (s4578_poll)"),
    ("recomp.cpp", "MEM_W(os", "K", "osTvType/osRomBase/osResetType = constexpr 0x80000300/308/30C"),
    ("threads.cpp", "((uint64_t*)fp)", "HOST", "host frame-pointer walk"),
    ("pi.cpp", "*(uint32_t*)(rdram + a) ==", "ALN", "a loops a += 4 from a 4-aligned base (DMA reference scan)"),
    ("pi.cpp", "*(uint32_t*)(rdram + b)", "ALN", "b = a + 4k, a 4-aligned loop index"),
    ("rt64_gbi.cpp", "&RDRAM[dataAddress + 0x4", "GF", "dataAddress = OSTask ucode_data the guest DMA-aligns (8); +0x410 / +0x414^2 aligned"),
    ("rt64_gbi.cpp", "&RDRAM[(dataAddress + 0x", "GF", "dataAddress = OSTask ucode_data (8-aligned) + even literal, ^2 BE halfword"),
    ("rt64_gbi.cpp", "&RDRAM[dataAddress + 0x31C]", "GF", "dataAddress = OSTask ucode_data (8-aligned) + 0x31C"),
    ("rt64_gbi_extended.cpp", "state->fromRDRAM(rdramAddress)", "GF", "extended-GBI return address in a DL word (never dispatched: LLE port)"),
    ("rt64_application.cpp", "reinterpret_cast<uint64_t *>(dl", "D", "inside #if SCRIPT_ENABLED (compiled out)"),
    ("rt64_framebuffer_manager.cpp", "reinterpret_cast<const uint32_t *>(old.data())", "HOST", "std::vector snapshot"),
    ("rt64_framebuffer_manager.cpp", "reinterpret_cast<const uint32_t *>(fbRAM)", "D", "ROGUESQ_LOG_FBUPLOAD (s_fbup) block only"),
    ("rt64_rdp.cpp", "(const uint32_t *)g_s4271_dl", "D", "s4271-cimg stderr log block (budgeted diag)"),
    ("rt64_rsp.cpp", "fromRDRAM(rdramAddress)", "GF", "HLE matrix / light load (never dispatched: LLE port); addresses are 8-aligned DL operands"),
    ("rt64_rsp.cpp", "fromRDRAM(vertexRdramAddress)", "GF", "HLE vertex load (never dispatched: LLE port)"),
    ("rt64_framebuffer_renderer.cpp", "colorBytes + off", "HOST", "colorBytes = depth-probe GPU readback ->map(), off = row * pitch"),
    ("rt64_framebuffer_renderer.cpp", "reinterpret_cast<const uint16_t *>(cp)", "HOST", "cp = floor-attach GPU readback ->map() + row * pitch"),
    ("rt64_texture_cache.cpp", "&bytes[byteCursor]", "HOST", "DDS/RTZ file bytes (host buffer)"),
    ("rt64_state.cpp", "&RDRAM[(colorFb->addressStart + (r * colorWriteWidth + c) * 2) ^ 2]", "D",
     "ROGUESQ_WB_VAL_PROBE / ROGUESQ_WB_COL_PROBE lambdas (called only under wbval / probe)"),
    ("rt64_interpreter.cpp", "(const uint32_t *)(dl + i * 8)", "D", "s4282Probe / s4271-list stderr diag (DL ring dump)"),
    ("rt64_interpreter.cpp", "g_s4282_prev.data() + o", "D", "s4282Probe / s4271-list stderr diag (DL ring dump)"),
    ("rt64_interpreter.cpp", "(const uint32_t *)(rdram + a)", "D", "s4282Probe / s4271-list stderr diag (DL ring dump)"),
    ("rt64_interpreter.cpp", "g_s4281_snap.data() + o", "D", "s4282Probe / s4271-list stderr diag (DL ring dump)"),
    ("rt64_interpreter.cpp", "(const uint32_t *)(rdram + pe)", "D", "s4282Probe / s4271-list stderr diag (DL ring dump)"),
    ("rt64_interpreter.cpp", "(const uint32_t *)(last - 0x100)", "D", "s4282Probe / s4271-list stderr diag (DL ring dump)"),
]

def operand(l, end):
    """text of the expression the cast applies to."""
    s = l[end:].lstrip()
    if s.startswith("("):
        a = s43.args_of(s, 1)
        return a[0] if a else s
    mo = re.match(r"[&\w\.\->\[\]\s+*]+", s)
    return mo.group(0) if mo else s[:40]

def offset_of(op):
    """offset expression after the guest base: `rdram + X` / `&RDRAM[X]` / `rd + (X)`."""
    mo = re.search(r"&\s*(?:\w+(?:->|\.))*(?:RDRAM|rdram)\s*\[(.*)\]\s*$", op)
    if mo: return mo.group(1)
    mo = re.search(r"\b(?:rdram|RDRAM|rd|r|g_rdram_for_submit|ram)\b\s*\)?\s*\+\s*(.*)$", op)
    return mo.group(1) if mo else None

def lit_aligned(off, sz):
    off = off.strip().strip("()").strip()
    parts = [p.strip().strip("()") for p in re.split(r"\s*\+\s*", off)]
    for p in parts:
        if LIT.match(p):
            if int(re.sub(r"[uUlL]+$", "", p), 0) % sz: return False
        elif re.match(r"^(?:\d+[uU]?\s*\*\s*\w+|\w+\s*\*\s*\d+[uU]?)$", p):
            k = int(re.search(r"\d+", p.replace("u", "")).group(0))
            if k % sz: return False
        else: return False
    return True

def masked(off, sz, body):
    if re.search(r"&\s*(?:~\s*%du|~\s*%d\b|0x[0-9A-Fa-f]*[CcFf8]{1}[uU]?\b)" % (sz - 1, sz - 1), off): return True
    var = re.findall(r"[A-Za-z_]\w*", off)
    return any(re.search(r"\(\s*!?\(?\s*%s\s*&\s*%d\s*\)?|%s\s*%%\s*%d" % (re.escape(v), sz - 1, re.escape(v), sz), body) for v in var)

def census(files, pgf):
    rows = []
    for p in files:
        rel = str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else p.name
        lines, fns = s43.ln_fn(p)
        for idiom, rx in (("CAST", CAST), ("MEM", MEMX)):
            m.MASK = rx
            for (ln, fn, mk, c, text) in m.sites(p, pgf):
                l = lines[ln - 1]
                if l.lstrip().startswith("#define"): continue
                mm = rx.search(l, max(0, l.find(mk)))
                g = mm.group(1) or (mm.group(2) if mm.lastindex and mm.lastindex >= 2 else None)
                tk = next(x for x in mm.groups() if x)
                sz = next((v for k, v in SIZE.items() if k in tk), 4) if idiom == "CAST" else SIZE[tk]
                if sz < 2: continue
                start = fns[ln - 1][1]; body = "\n".join(lines[start:ln])
                cc, why = c, ""
                if cc in "GD" and rel.startswith("lib/rt64/") and not s43.body_gated(lines, ln): cc = "?"
                if cc == "D" and fn in s44.CORE: cc = "?"
                if idiom == "CAST":
                    op = operand(l, mm.end())
                    if (re.search(r"\bcalloc\s*\(|\bmalloc\s*\(", l) or ("&" in op and not GUEST.search(op)) or HOSTB.search(op)) \
                            and not s43.hand(rel, fn, l, HAND):
                        rows.append((rel, ln, fn, "HOST", "host memory", idiom, l.strip())); continue
                    if cc == "?":
                        hh = s43.hand(rel, fn, l, HAND)
                        off = offset_of(op) if GUEST.search(op) else None
                        if hh: cc, why = hh
                        elif off is not None and lit_aligned(off, sz): cc, why = "K", f"literal offset {off.strip()[:30]} % {sz} == 0"
                        elif off is not None and masked(off, sz, body + "\n" + l): cc, why = "ALN", f"mask/test on {off.strip()[:30]}"
                        else: why = f"op={op[:50]}"
                else:
                    a = s43.args_of(l, mm.end())
                    o, b = (a + ["", ""])[:2]
                    if cc == "?":
                        hh = s43.hand(rel, fn, l, HAND)
                        if hh: cc, why = hh
                        elif re.search(r"ctx->r29|\bsp\b", b) and (LIT.match(o) or not o): cc, why = "SP", f"sp + {o}"
                        elif (LIT.match(o) or re.match(r"^\w+\s*\*\s*\d+$|^\d+\s*\*\s*\w+$", o)) and \
                                (re.search(r"\(int32_t\)\s*0x8[0-9A-Fa-f]{7}\)?$", b) or LIT.match(b) or re.match(r"^os\w+$|^\w+$", o)):
                            cc, why = "K", f"MEM_{tk}({o}, {b[:30]})"
                        if cc == "?" and (re.search(r"ctx->r\d+|guest|buf_ptr|reloc_word_addr|flash_\w+|data\b|\bm\b|\ba\b", b)):
                            cc, why = "GF", f"guest pointer {b[:30]} (+{o}) as the guest's own lw/sw would use"
                        if cc == "?": why = f"MEM_{tk}({o}, {b})"
                rows.append((rel, ln, fn, cc, why, idiom, l.strip()))
    return rows

PLANT = ("static uint32_t planted(uint8_t* rdram, OSTask* task) {\n    return *(uint32_t*)(rdram + task->a);\n}\n"
         "static uint32_t masked_twin(uint8_t* rdram, OSTask* task) {\n    return *(uint32_t*)(rdram + (task->a & ~3u));\n}\n"
         "static uint32_t memcpy_twin(uint8_t* rdram, OSTask* task) {\n    uint32_t v; memcpy(&v, rdram + task->a, 4); return v;\n}\n"
         "static uint32_t lit_twin(uint8_t* rdram) {\n    return *reinterpret_cast<const uint32_t*>(rdram + 0x137DBCu);\n}\n"
         "static uint32_t host_twin(std::vector<uint8_t>& v) {\n    return *reinterpret_cast<const uint32_t*>(v.data());\n}\n"
         "static uint32_t gated_twin(uint8_t* rdram, OSTask* task) {\n    if (!rs64_dlwalk_on()) return 0;\n"
         "    return *(uint32_t*)(rdram + task->a);\n}\n")

def main():
    pgf = m.probe_gate_fns()
    if "--controls" in sys.argv:
        import tempfile
        t = pathlib.Path(tempfile.mkdtemp()) / "planted.cpp"
        t.write_text(PLANT)
        got = {(r[2], r[3]) for r in census([t], pgf)}
        want = {("planted", "?"), ("masked_twin", "ALN"), ("lit_twin", "K"), ("host_twin", "HOST"), ("gated_twin", "G")}
        assert got == want, f"control failed: {got ^ want}"
        print("[s7351] controls: planted *(uint32_t*)(rdram + task->a) '?', masked twin 'ALN', memcpy twin not a site, "
              "literal twin 'K', host-container twin 'HOST', gated twin 'G'")
    files = s43.files_in_scope()
    rows = census(files, pgf)
    for idiom in ("CAST", "MEM"):
        rr = [r for r in rows if r[5] == idiom]
        cc = Counter(r[3] for r in rr)
        print(f"[s7351] {idiom} sites={len(rr)} " + " ".join(f"{k}={v}" for k, v in sorted(cc.items())))
    for r in rows:
        if r[3] in ("?", "B") or "-v" in sys.argv or ("-h" in sys.argv and r[3] in ("H", "GF")):
            print(f"  {r[3]} {r[5]} {r[0]}:{r[1]} {r[2]} {r[4]} :: {r[6][:110]}")
    bad = [r for r in rows if r[3] in ("?", "B")]
    print(f"[s7351] files={len(files)} unclassified/defect: {len(bad)}")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
