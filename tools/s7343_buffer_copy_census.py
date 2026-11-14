#!/usr/bin/env python3
"""s7343 class T census: host fixed buffers written with a guest-derived length.
A stack/static/std::array buffer filled by memcpy / memmove / memset / strcpy / fread / snprintf or a copy loop whose
length or end comes from guest data (rdram word, OSTask field, DL word, SP/DP DMA length, DPC start/end) overflows the
host buffer on a larger-than-retail length (dd>1 scenes, spill-sized DLs, garbage word) instead of rejecting it.
Scope = s7342 (s7338 HOST + EXTRA, 183 files). Four sink families:
  F1 CALL   memcpy/memmove/memset/strncpy/strcpy/fread
  F2 LOOP   `for (i = ..; i < BOUND; ..)` whose next 6 lines write `T[..i..] =` into a sized host array (tables(path, 1))
  F3 FMT    snprintf/vsnprintf: the size argument must be sizeof(dest) / a constant <= the dest size
  F4 GUEST  writes into the fixed guest-facing host buffers: RDP TMEM (4096 B), RSP DMEM/IMEM (0x1000), S2D struct_buffer
Classes: C/P/G/D/R/X/S from tools/s7338_mask_census.py sites(), then
  K constant length (literal / sizeof / named constant) or a scalar destination
  L clamped: std::min / `if (n > N) n = N` / `n &= MASK` / `&& i < N` / loop bound sizeof/std::size/.size() in the function
  M index masked to the buffer (F4: & tmemMask, & 0xFFF, RSP_MEM_B macro)
  V destination grows to the length (vector resize / insert) or is guest RAM (classes N/O covered those)
  H hand-verified (reason in HAND)   B default-on, guest-derived length, no clamp (defect)   ? unclassified
'?' or B => exit 1. --controls plants a default-on `uint8_t b[64]; memcpy(b, rdram + a, task->data_size);` ('?'), the
clamped twin ('L'), a gated twin ('G'), an unclamped loop ('?'), and a snprintf with a size larger than the buffer ('?')."""
import re, sys, pathlib, importlib.util
from collections import Counter
ROOT = pathlib.Path(__file__).resolve().parents[1]
_s = importlib.util.spec_from_file_location("s7342", ROOT / "tools/s7342_addr_index_census.py")
s42 = importlib.util.module_from_spec(_s); _s.loader.exec_module(s42)
m = s42.m

CALL = re.compile(r"\b(?:std::)?(memcpy|memmove|memset|strncpy|strcpy|fread)\s*\(")
FMT = re.compile(r"\b(?:std::)?(v?snprintf)\s*\(")
FOR = re.compile(r"for\s*\(\s*(?:[\w:]+\s+)?(\w+)\s*=\s*[^;]*;\s*\1\s*<=?\s*([^;]+?)\s*;")
GUEST = re.compile(r"(?:\bTMEM\s*\[|\bTMEM\s*\+|RS64_DMEM_BASE\s*\+|\bstruct_buffer\b)")
SIZEOF = re.compile(r"^\s*(?:sizeof\s*\(?[^()]*\)?|sizeof\s*\([^()]*(?:\([^()]*\))?[^()]*\)|std::size\s*\(\s*\w+\s*\)|\w+(?:\.|->)size\(\)|\d+u?|0x[0-9A-Fa-f]+u?)(?:\s*[-*/+]\s*(?:\d+|sizeof\s*\([^()]*\)))*\s*$")

# Hand classes (s7343 review). Key (file suffix, function, needle in line) -> (class, reason).
HAND = [
    ("librecomp/src/pi.cpp", "save_write_ptr", "memcpy", "H", "save_buffer is a std::vector; callers pass EEPROM/SRAM/flash offsets "
     "bounded by the save type; assert(offset + count <= size) (debug); not a fixed buffer, length is a PI save size"),
    ("src/rsp/s7331_reset_writer.cpp", "compare_locked", "memcpy(c, g, n)", "L", "n = std::min(kLine, b->req - off) into b->copy (vector sized b->req)"),
    ("rt64_gbi_s2dex.cpp", "?", "struct_buffer", "L", "loadSize &= 0xFF into std::array<uint8_t, 256> struct_buffer"),
    ("rt64_framebuffer_storage.cpp", "?", "rdramData.data()", "V", "rdramData resized to rdramUsed before the copy"),
    ("rt64_rsp.cpp", "?", "memcpy(&vertices[dstIndex]", "L", "setVertex returns unless dstIndex + vtxCount <= RSP_MAX_VERTICES (HLE path; F5 is LLE)"),
    ("rt64_shader_compiler.cpp", "?", "infoLog.data()", "V", "infoLog sized to GetBufferSize() first; host compiler output"),
    ("rt64_filesystem_zip.cpp", "?", "memcpy(fileData", "V", "fileData allocated to uncompressedSize; host zip file, not guest"),
    ("librecomp/src/mods.cpp", "patch_func", "memcpy", "H", "host mod patch bytes, count from the mod loader, not guest data"),
    ("librecomp/src/mods.cpp", "unpatch_func", "memcpy", "V", "copies replaced_bytes.size() back from the same vector"),
    ("librecomp/src/mods.cpp", "resolve_code_dependencies", "memcpy", "V", "replaced_bytes sized before the copy"),
    ("librecomp/src/overlays.cpp", "register_patches", "memcpy", "V", "patch_data sized to size; host patch table"),
    ("librecomp/include/librecomp/rsp.hpp", "rs64_m5_audio_stage_boundary", "RS64_DMEM_BASE", "M", "DMEM accessor: (a & 0xFFC)/(0xFFE)"),
    ("librecomp/include/librecomp/rsp.hpp", "dma_dmem_to_rdram", "memcpy(rdram + dram_addr", "L",
     "dmem_addr &= 0xFFF; wr_len clamped to 0x1000 - dmem_addr and to rs64_s7327_limit() - dram_addr"),
    ("librecomp/include/librecomp/rsp.hpp", "dma_rdram_to_dmem", "memcpy(RS64_DMEM_BASE + dmem_addr", "L",
     "dmem_addr &= 0xFFF; rd_len clamped to 0x1000 - dmem_addr and to rs64_s7327_limit() - dram_addr"),
    ("librecomp/src/rsp.cpp", "rs64_s4214_scan", "memcpy(prev, cur, sizeof(cur))", "K", "sizeof(cur), prev same type"),
    ("src/rsp/dpc_bridge.cpp", "rs64_rw_cmd", "memcpy(g_rdram_for_submit", "V", "guest RAM destination, & kSubmitRamMask, 4 bytes"),
    ("src/rsp/dpc_bridge.cpp", "rs64_dpc_defer_end_impl", "g_s4272_shadow", "K", "4 bytes into the deferred-end shadow at e.off + (a - e.lo), a in [e.lo, e.hi)"),
    ("src/rsp/dpc_bridge.cpp", "rs64_dpc_defer_end_impl", "memcpy(&now", "K", "4 bytes into a scalar"),
    ("ultramodern/src/events.cpp", "run", "strncpy((char *)nr + 16, xi.pth_name, 63)", "K", "63 bytes into nr[80] at +16 (79 <= 80); host thread name"),
    ("ultramodern/src/events.cpp", "run", "std::memcpy(buf.data() + 2", "K", "2 bytes into the record vector header"),
    ("ultramodern/src/events.cpp", "g_row", "memset", "K", "Snap ctor clears its own member arrays with sizeof"),
    ("src/main/main.cpp", "fl_zero_sample_game_threads", "sizeof(names[bi])", "K", "sizeof(names[bi]), same element type"),
    ("src/main/main.cpp", "?", "fread(s_ref, 4, 64, fr)", "K", "64 x 4 bytes into s_ref[64] (uint32); host pose file"),
    ("src/main/main.cpp", "rs64_pcm_writer_phase_reset", "g_rs64_pcm_writer_printed", "K", "sizeof(g_rs64_pcm_writer_printed) on the next line"),
    ("src/rsp/s7096_fwd_cover.cpp", "selftest", "sizeof(uint64_t) * D_N", "K", "by is uint64_t by[D_N]"),
    ("rt64_framebuffer.cpp", "?", "fl_snap", "V", "fl_snap = malloc(fl_snap_n), fl_snap_n = min(cap, rangeEnd - hdr)"),
    ("rt64_interpreter.cpp", "?", "pendingCommandBuffer", "H", "pendingCommandBuffer is std::array<uint8_t, 256>; every copy is part of ONE "
     "command of commandWordLengths[op & 0x3F] words, max 22 (tri shade+tex+z) = 176 B; toCopy < cmdLength * 8 / remaining"),
    ("rt64_rdp.cpp", "?", "RDP_TMEM_BYTES)", "K", "whole-TMEM copy RDP_TMEM_BYTES into a RDP_TMEM_BYTES buffer"),
    ("rt64_state.cpp", "?", "memset(&RDRAM[storageAddress]", "L", "guest RAM dest; rejected unless storageAddress + readFbBytes <= kRdramBytes; s_riclr env"),
    ("rt64_state.cpp", "?", "memset(&RDRAM[colorFb->addressStart]", "G", "ROGUESQ_WB_CLEAR (s_wbclr) diagnostic arm"),
    ("rt64_state.cpp", "?", "present.storage.data()", "V", "present.storage.resize(screenFbBytes); screenFbBytes = 0 past 16 MB (s6130)"),
    ("rt64_buffer_uploader.cpp", "?", "memcpy(dstData + srcOffset", "V", "upload buffer created for the same srcData range (host GPU)"),
    ("rt64_framebuffer_renderer.cpp", "?", "floorFragmentZero->map()", "V", "buffer created with floorBufferBytes"),
    ("rt64_native_target.cpp", "?", "memcpy(dstData, data, bufferSize)", "V", "nativeUploadBuffer created with bufferSize"),
    ("rt64_native_target.cpp", "?", "readbackData + bufferOffset", "V", "readback buffer sized to the target; data sized by caller"),
    ("rt64_texture_cache.cpp", "?", "memcpy(", "V", "GPU upload buffers created with the same byte count / row pitch (host texture cache)"),
    ("rt64_texture_cache.cpp", "?", "memset(dstData, 0, totalSize)", "V", "upload resource created with totalSize"),
    ("rt64_rdp_tmem.cpp", "?", "&TMEM[byteOffset], byteCount", "L", "s7343: byteCount clamped to RDP_TMEM_BYTES - byteOffset (was a 128 B OOB READ at CI4 palette 15)"),
    ("rt64_gbi_s2dex2.cpp", "?", "struct_buffer.fill(0)", "K", "std::array::fill"),
    ("rt64_rdp.h", "?", "uint64_t TMEM[RDP_TMEM_WORDS]", "K", "declaration"),
    ("rt64_rsp.h", "?", "std::array<uint8_t, 256> struct_buffer", "K", "declaration"),
    # FMT: callee takes (char *out, size_t n); every caller passes sizeof(its buffer) or the matching literal (s7343 caller read)
    ("upstream_compat.cpp", "rs64_s7324_sym", "snprintf(out, n", "H", "callers s7324_rcp_spill.cpp:111-142 pass 128 into [128] / sizeof a[j]"),
    ("upstream_compat.cpp", "rs64_wt_sym", "snprintf(buf, n", "H", "callers pass sb, sizeof sb"),
    ("upstream_compat.cpp", "rs64_fill_flush_summary_locked", "snprintf(", "K", "spans + used, sizeof(spans) - used; used + 20 < sizeof(spans) loop bound"),
    ("dpc_bridge.cpp", "rs64_bl_eq", "snprintf(dst, 48", "K", "dst is c0[48] / c1[48]"),
    ("dpc_bridge.cpp", "rs64_bl_eq", "snprintf(out, n", "H", "callers pass tri_bl / g_ft.untex_bl with sizeof"),
    ("ultramodern/src/events.cpp", "run", "snprintf((char *)r6 + 16, 80", "K", "r6[96]: 16 + 80 = 96"),
    ("s7097_edit_census.cpp", "diff", "s.ex[s.nex++], 200", "K", "ex[8][200], guarded s.nex < 8"),
    ("rt64_gbi_rdp.cpp", "?", "snprintf(out, n", "H", "rs64_cc_equation/rs64_cca_equation callers pass sizeof(cc_eq)/sizeof(cca_eq) (:1551)"),
    ("rt64_command_warning.cpp", "?", "vsnprintf(", "V", "message.resize(reqSize) from the vsnprintf(nullptr, 0) probe"),
    ("rt64_framebuffer_renderer.cpp", "?", "snprintf(dst, n", "H", "copyRamCounts callers pass counts, sizeof(counts) (:975, :1010)"),
]
# Loop hand classes: (file suffix, line needle) -> (class, reason)
LOOP_HAND = [
    ("src/main/main.cpp", "s_s7334_n", "H", "w[4] written only for i < 4 (s_s7334_n is the s7334 holder count, capped 4 at its store)"),
    ("src/main/main.cpp", "base + i < 0x800000u", "L", "g_s5229_* tables are 0x800000 entries; base + i < 0x800000u in the bound"),
    ("src/main/main.cpp", "flags", "H", "flags[8] indexed by i < n where n <= 8 (local count of a fixed 8-slot list)"),
    ("src/main/main.cpp", "nframes", "H", "nframes = backtrace(frames, 64): <= 64; saddrs[32] indexed by i < min(nframes, 32) (hand-read)"),
    ("src/main/main.cpp", "nsnap", "H", "nsnap counts snaps into a 24-slot array (bounded at its increment)"),
    ("src/main/main.cpp", "s_ntg", "H", "s_ntg <= 64 (bounded at its increment); s_vis[64]"),
    ("src/main/upstream_compat.cpp", "rs64_ram_top - 0x80000000u", "H", "buf[512] is written by an inner chunk loop, not by the outer RAM-span index"),
    ("src/main/upstream_compat.cpp", "copy[i] = g_recv_stats[i]", "L", "n clamped to kRecvMqCap first"),
    ("src/main/upstream_compat.cpp", "ok.size()", "H", "k[3] indexed by a 3-way flag, not i"),
    ("src/main/rt64_render_context.cpp", "udata_size", "V", "std::vector<uint8_t> buf(udata_size) (diag ucode dump)"),
    ("src/rsp/dpc_bridge.cpp", "before[i]", "L", "sample clamped to the before[] size by the caller row (kF5 sample <= 112)"),
    ("src/rsp/dpc_bridge.cpp", "after[i]", "K", "n = kF5HostTgtEnd - kF5HostTgtBegin, after[] has exactly that size"),
    ("src/rsp/dpc_bridge.cpp", "snapshot", "H", "registration[32]: snapshot = min(count, 32) (hand-read)"),
    ("src/rsp/dpc_bridge.cpp", "nk", "H", "order[48]: nk <= 48 table rows"),
    ("src/rsp/dpc_bridge.cpp", "nrows", "H", "order[48]: nrows <= 48 table rows"),
    ("librecomp/src/rsp.cpp", "0x128u && b < l", "L", "rec[1072] bound 0x128 (296) words"),
    ("rt64_gbi_rdp.cpp", "b1", "H", "snap[40] debug ring"),
]

def ln_fn(path):
    """function name per line (same rules as s7338 sites())."""
    lines = path.read_text(errors="replace").splitlines()
    fn, out, start = "?", [], 0
    for i, l in enumerate(lines):
        if l and not l[0].isspace() and l[0] not in "#/}{":
            mm = m.FN.match(l)
            if mm and mm.group(1) not in ("if", "for", "while", "switch", "return"): fn, start = mm.group(1), i
        out.append((fn, start))
    return lines, out

def args_of(s, k):
    """split the call arguments starting at index k (just after '(')."""
    depth, cur, out = 0, "", []
    for ch in s[k:]:
        if ch in "([{": depth += 1
        elif ch in ")]}":
            if depth == 0: out.append(cur.strip()); return out
            depth -= 1
        if ch == "," and depth == 0: out.append(cur.strip()); cur = ""; continue
        cur += ch
    out.append(cur.strip()); return out

def clamped(var, body):
    v = re.escape(var)
    return bool(re.search(r"\b%s\s*=\s*(?:std::)?min\b|\b%s\s*=\s*\(?\s*%s\s*>|if\s*\(\s*%s\s*>=?\s*[^)]*\)\s*%s\s*=|\b%s\s*&=\s*0x|"
                          r"\bstd::min(?:<\w+>)?\s*\(\s*%s\b" % (v, v, v, v, v, v, v), body))

RT64GATE = re.compile(r"\b(?:if\s*\(\s*!?\s*(?:s_\w+|g_rs64_\w*(?:on|log|arm|dump|census)\w*|rs64\w*(?:On|Log|Enabled)\w*|\w*getenv)|std::getenv)\b")
def body_gated(lines, ln):
    """rt64: the nearest enclosing indented member opens with a gate within its first 8 lines (env static / log flag)."""
    ind = len(lines[ln - 1]) - len(lines[ln - 1].lstrip())
    for j in range(ln - 2, max(0, ln - 400), -1):
        l = lines[j]
        if l.strip() and (len(l) - len(l.lstrip())) < ind and re.search(r"^\s+(?:template|static|inline|__forceinline|void|bool|uint\w+|int|auto|[\w:<>]+\s+[\w:]+\s*\()", l) and "(" in l:
            return any(RT64GATE.search(x) and "return" in x for x in lines[j + 1:j + 9])
    return False

def hand(rel, fn, text, table):
    for h in table:
        if len(h) == 5:
            f, hf, needle, c, why = h
            if rel.endswith(f) and (hf == fn or hf == "?") and needle in text: return c, why
        else:
            f, needle, c, why = h
            if rel.endswith(f) and needle in text: return c, why
    return None

def census(files, pgf):
    rows = []
    for p in files:
        rel = str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else p.name
        lines, fns = ln_fn(p)
        sizes = s42.tables(p, 1); names = s42.names_of(lines)
        for fam, rx in (("CALL", CALL), ("FMT", FMT), ("GUEST", GUEST)):
            m.MASK = rx
            for (ln, fn, mk, c, text) in m.sites(p, pgf):
                l = lines[ln - 1]; why = ""
                start = fns[ln - 1][1]; body = "\n".join(lines[start:ln])
                if fam == "GUEST" and CALL.search(l) and not re.search(r"\bstruct_buffer\b", l): continue  # counted by CALL
                if c in "GD" and rel.startswith("lib/rt64/") and not body_gated(lines, ln):
                    c = "?"   # rt64 namespace members are indented: the top-level fn/gate attribution is not theirs
                if c == "?":
                    hh = hand(rel, fn, text, HAND)
                    if fam == "CALL":
                        mm = CALL.search(l[l.find(mk):]) or CALL.search(l); a = args_of(l, l.find(mm.group(0)) + len(mm.group(0)))
                        ln_arg = a[2] if mm.group(1) in ("memcpy", "memmove", "memset", "strncpy") and len(a) > 2 else \
                                 (a[1] + "*" + a[2] if mm.group(1) == "fread" and len(a) > 2 else "")
                        dst = a[0] if a else ""
                        if hh: c, why = hh
                        elif mm.group(1) == "strcpy" and len(a) > 1 and re.fullmatch(r'"[^"]{0,7}"', a[1]): c, why = "K", f"literal {a[1]}"
                        elif ln_arg and (SIZEOF.match(ln_arg) or s42.ev(ln_arg, names) is not None): c, why = "K", f"length {ln_arg[:40]}"
                        elif ln_arg and re.fullmatch(r"\w+", ln_arg) and clamped(ln_arg, body): c, why = "L", f"{ln_arg} clamped in {fn}"
                        elif dst.startswith("&") and "[" not in dst and ln_arg and len(ln_arg) < 4: c, why = "K", "scalar dest"
                    elif fam == "FMT":
                        mm = FMT.search(l); a = args_of(l, l.find(mm.group(0)) + len(mm.group(0)))
                        dst, n = (a + ["", ""])[:2]
                        base = re.sub(r"^\(?\s*(?:char\s*\*\s*\)\s*)?", "", dst).split("+")[0].strip().lstrip("&")
                        base = re.sub(r"\[.*$", "", base)
                        nv = s42.ev(n, names); dv = sizes.get(base, (None,))[0]
                        if hh: c, why = hh
                        elif re.search(r"sizeof\s*\(?\s*%s\b" % re.escape(base), n) or re.search(r"\b%s\s*\.size\(\)" % re.escape(base), n):
                            c, why = "K", f"size {n[:40]}"
                        elif nv is not None and dv is not None and nv <= dv: c, why = "K", f"size {nv} <= {base}[{dv}]"
                        elif re.search(r"sizeof", n) and "-" in n and re.search(r"\b%s\b" % re.escape(base), n): c, why = "K", f"remaining {n[:40]}"
                        elif re.search(r"\bsizeof\b", n): c, why = "K", f"size {n[:40]} (sizeof of the destination object)"
                    elif fam == "GUEST":
                        if hh: c, why = hh
                        elif re.search(r"&\s*(?:tmemMask|RDP_TMEM_MASK\w*|0xFF[CEF]|0x7FF|0x3FF)\b|RSP_MEM_B", l): c, why = "M", "index masked"
                        elif "TMEM" in l and re.search(r"\bTMEM\s*\[\s*\(\s*\(?\s*tmemAddress\b", l) and "tmemAddress = (tmemAddress" in "\n".join(lines):
                            c, why = "M", "tmemAddress = (.. ) & tmemMask, 8-aligned; +0..7 ^ xor stays in the word"
                        elif re.search(r"memcpy\s*\(\s*(?:TMEM|rs64ChkCopy|before)\b[^,]*,\s*TMEM\b[^,]*,\s*RDP_TMEM_BYTES|memcpy\s*\(\s*\w+\s*,\s*TMEM\s*,\s*RDP_TMEM_BYTES", l):
                            c, why = "K", "whole-TMEM copy RDP_TMEM_BYTES"
                rows.append((fam, rel, ln, fn, c, why, text))
        FORH = re.compile(r"for\s*\(")
        m.MASK = FORH
        for (ln, fn, mk, c, text) in m.sites(p, pgf):
            l = lines[ln - 1]
            for mm in FOR.finditer(l):
                v, b = mm.group(1), mm.group(2)
                if s42.ev(b, names) is not None: continue
                body = "\n".join(lines[ln - 1:ln + 5])
                tabs = {t for t in re.findall(r"\b(\w+)\s*\[[^\]]*\b%s\b[^\]]*\]\s*(?:\.\w+\s*)?=[^=]" % re.escape(v), body) if t in sizes}
                if not tabs: continue
                cc, why = c, ""
                if cc == "?":
                    start = fns[ln - 1][1]; fb = "\n".join(lines[start:ln])
                    lim = re.search(r"&&\s*%s\s*<\s*(\w+)" % re.escape(v), b) or re.match(r"\s*(\w+)\s*&&", b)
                    hh = hand(rel, fn, "\n".join(lines[ln - 1:ln + 5]), LOOP_HAND)
                    if hh: cc, why = hh
                    elif lim and s42.ev(lim.group(1), names) is not None and all(s42.ev(lim.group(1), names) <= sizes[t][0] for t in tabs):
                        cc, why = "L", f"&& {v} < {lim.group(1)}"
                    elif re.fullmatch(r"(?:sizeof\s*\(?\s*\w+\s*\)?|std::size\s*\(\s*\w+\s*\)|\w+\.size\(\))", b.strip()) and \
                            re.search(r"\b(%s)\b" % "|".join(map(re.escape, tabs)), b):
                        cc, why = "L", f"bound {b.strip()}"
                    elif re.fullmatch(r"\w+", b) and clamped(b, fb): cc, why = "L", f"{b} clamped in {fn}"
                rows.append(("LOOP", rel, ln, fn, cc, why, f"[{','.join(sorted(tabs))}] < {b[:40]} :: {text}"))
    return rows

def files_in_scope():
    files, seen = [], set()
    for pat in m.HOST + s42.EXTRA:
        for p in sorted(ROOT.glob(pat)):
            if p not in seen: seen.add(p); files.append(p)
    return files

def main():
    pgf = m.probe_gate_fns()
    if "--controls" in sys.argv:
        import tempfile
        t = pathlib.Path(tempfile.mkdtemp()) / "planted.cpp"
        t.write_text("static void planted(uint8_t* rdram, uint32_t a, OSTask* task) {\n    uint8_t b[64];\n"
                     "    memcpy(b, rdram + a, task->data_size);\n}\n"
                     "static void clamped_twin(uint8_t* rdram, uint32_t a, OSTask* task) {\n    uint8_t b[64];\n"
                     "    uint32_t n = std::min<uint32_t>(task->data_size, sizeof b);\n    memcpy(b, rdram + a, n);\n}\n"
                     "static void gated_twin(uint8_t* rdram, uint32_t a, OSTask* task) {\n    if (!rs64_dlwalk_on()) return;\n"
                     "    uint8_t b[64];\n    memcpy(b, rdram + a, task->data_size);\n}\n"
                     "static void looped(uint8_t* rdram, uint32_t a, OSTask* task) {\n    static uint8_t lb[64];\n"
                     "    for (uint32_t i = 0; i < task->data_size; i++) lb[i] = rdram[a + i];\n}\n"
                     "static void fmt_bad(int v) {\n    char fb[16];\n    snprintf(fb, 64, \"%d\", v);\n}\n"
                     "static void fmt_ok(int v) {\n    char fb[16];\n    snprintf(fb, sizeof fb, \"%d\", v);\n}\n")
        got = {(r[3], r[0], r[4]) for r in census([t], pgf)}
        want = {("planted", "CALL", "?"), ("clamped_twin", "CALL", "L"), ("gated_twin", "CALL", "G"), ("looped", "LOOP", "?"),
                ("fmt_bad", "FMT", "?"), ("fmt_ok", "FMT", "K")}
        assert got == want, f"control failed: {got ^ want}"
        print("[s7343] controls: planted memcpy(b[64], task->data_size) '?', clamped twin 'L', gated twin 'G', unclamped loop '?', "
              "snprintf size 64 > fb[16] '?', sizeof twin 'K'")
    files = files_in_scope()
    rows = census(files, pgf)
    for fam in ("CALL", "LOOP", "FMT", "GUEST"):
        cc = Counter(r[4] for r in rows if r[0] == fam)
        print(f"[s7343] {fam} sites={sum(cc.values())} " + " ".join(f"{k}={v}" for k, v in sorted(cc.items())))
    print(f"[s7343] files={len(files)} total={len(rows)}")
    for r in rows:
        if r[4] not in "CPGDRXS" or "-v" in sys.argv:
            if r[4] in "?B" or "-v" in sys.argv or "-h" in sys.argv:
                print(f"  {r[4]} {r[0]} {r[1]}:{r[2]} {r[3]} {r[5]} :: {r[6][:150]}")
    bad = [r for r in rows if r[4] in "?B"]
    tm = (ROOT / "lib/rt64/src/hle/rt64_rdp_tmem.cpp").read_text(errors="replace")
    if "clampTmemRange(byteOffset, byteCount)" not in tm:      # the rt64_rdp_tmem 'L' row is pinned to the s7343 clamp
        print("  DEFECT rt64_rdp_tmem.cpp uploadTMEM: s7343 TLUT clamp missing (CI4 palette 15 reads 128 B past TMEM)"); bad.append(None)
    print(f"[s7343] unclassified/defect: {len(bad)}")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
