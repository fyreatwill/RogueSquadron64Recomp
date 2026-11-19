#!/usr/bin/env python3
"""s7350 class AA census: memcpy between ranges that may overlap.
`memcpy(dst, src, n)` with overlapping [dst, dst+n) and [src, src+n) is UB (arm64 libc copies backward in some size classes, so
the bytes really come out wrong); std::copy over raw pointers is safe only when dst is not inside (src, src+n).
Scope = s7343 files_in_scope(). A site = memcpy / std::memcpy / __builtin_memcpy / std::copy / std::copy_n (memmove counted, not a site).
Classes: C/P/G/D from tools/s7338_mask_census.py sites() (rt64 G/D re-checked with s7343 body_gated(); CORE demotion as s7344)
  DISJ dst and src are different objects and at least one is an object, not a pointer that could alias the other: a local /
       static array or scalar (`&v`, `buf`, `&s.idx`), a std::vector / std::array / std::string (`.data()`), or one side is a
       DMEM / TMEM / save-buffer array and the other guest RDRAM
  CHK  an overlap test (`d + n <= s || s + n <= d`, or an explicit `!=` / disjoint assert) dominates the call
  H    hand-verified (reason in HAND)   B same base object (both `rdram + ..`), no check: defect   ?  unclassified
'?' or B => exit 1. --controls plants `memcpy(rdram + task->dst, rdram + task->src, task->len)` ('?' / B), a memmove twin (not a
site), a disjoint twin (local buf -> DISJ), a checked twin (CHK) and a gated twin (G)."""
import re, sys, pathlib, importlib.util
import importlib.util as _ilu_cr, sys as _sys_cr
if "census_rules" not in _sys_cr.modules:  # s7654 shared text-anchored rules (one instance per process)
    _crs = _ilu_cr.spec_from_file_location("census_rules", __import__("pathlib").Path(__file__).resolve().parent / "census_rules.py")
    _sys_cr.modules["census_rules"] = _ilu_cr.module_from_spec(_crs); _crs.loader.exec_module(_sys_cr.modules["census_rules"])
census_rules = _sys_cr.modules["census_rules"]
from collections import Counter
ROOT = pathlib.Path(__file__).resolve().parents[1]
def _load(name, f):
    s = importlib.util.spec_from_file_location(name, ROOT / f); mod = importlib.util.module_from_spec(s); s.loader.exec_module(mod); return mod
s44 = _load("s7344", "tools/s7344_wrap_census.py")
s43, m = s44.s43, s44.s43.m

CALL = re.compile(r"(?<![\w.>])(?:std::)?(memcpy|__builtin_memcpy|memmove|copy_n|copy)\s*\(")
OBJT = re.compile(r"^(?:const\s+)?(?:std::)?(?:vector|array|string|basic_string|span)\b")
DEVOBJ = {"RS64_DMEM_BASE", "g_dmem_cur", "dmem", "TMEM", "rs64ChkCopy", "before", "save_context"}
HAND = [  # (file suffix, needle in line, class, reason) -- s7350 review
    ("main.cpp", "sn.names[bi], names[bi]", "DISJ", "snaps[slot].names (static snapshot table) <- local names[][] of the sampler"),
    ("mods.cpp", "target_func_u8 + offset, bytes", "H", "host code page of a recompiled function <- patch byte literal (mod loader, never guest data)"),
    ("mods.cpp", "data.replaced_bytes.data()", "DISJ", "host code page <- std::vector replaced_bytes saved earlier"),
    ("mods.cpp", "cur_replacement_data.replaced_bytes.data", "DISJ", "std::vector replaced_bytes <- host code page"),
    ("overlays.cpp", "patch_data.data(), patch", "DISJ", "std::vector patch_data (freshly sized) <- static patch table"),
    ("pi.cpp", "save_context.save_buffer[offset], in", "DISJ", "save_buffer std::array <- flash write_buffer / guest DMA staging (separate object)"),
    ("librecomp/src/rsp.cpp", "memcpy(prev, cur, sizeof(cur))", "DISJ", "two distinct static arrays prev[] / cur[] of rs64_s4214_scan"),
    ("s7331_reset_writer.cpp", "memcpy(c, g, n)", "DISJ", "c = b->copy.data() (std::vector shadow) <- g = guest RDRAM + phys(ptr)"),
    ("rt64_gbi_s2dex.cpp", "struct_buffer", "DISJ", "S2D.struct_buffer std::array <- RDRAM (and S2DEX HLE is never dispatched: LLE port)"),
    ("rt64_framebuffer_storage.cpp", "rdramData.data() + dstIndex, data", "DISJ", "rdramData std::vector (owned copy store) <- caller's RDRAM span"),
    ("rt64_rsp.cpp", "&vertices[dstIndex], dlVerts", "DISJ", "RSP vertices[] member array <- RDRAM DL vertices (HLE vertex load, never run LLE)"),
    ("rt64_shader_compiler.cpp", "infoLog.data(), error->GetBufferPointer()", "DISJ", "std::string infoLog <- D3D blob"),
    ("rt64_filesystem_zip.cpp", "fileData, zipFileData", "DISJ", "fileData freshly allocated <- zip archive buffer"),
    ("rsp.hpp", "RS64_DMEM_BASE + dmem_addr", "DISJ", "SP DMA: DMEM array <-> guest RDRAM (separate objects)"),
    ("dpc_bridge.cpp", "q.ram.data(), g_rdram_for_submit", "DISJ", "std::vector snapshot <- RDRAM"),
    ("rt64_framebuffer.cpp", "memcpy(fl_snap, fl_host", "DISJ", "fl_snap = malloc(fl_snap_n) fresh block <- RDRAM freelist window (M5 boundary diag)"),
    ("rt64_framebuffer.cpp", "memcpy(fl_host, fl_snap", "DISJ", "RDRAM window <- the malloc'd fl_snap copy"),
    ("rt64_framebuffer.cpp", "memcpy(fl_host + off, fl_snap + off", "DISJ", "RDRAM header <- the malloc'd fl_snap copy"),
    ("rt64_interpreter.cpp", "pendingCommandBuffer.data()", "DISJ", "RDP pendingCommandBuffer std::vector <- DL bytes in RDRAM"),
    ("rt64_state.cpp", "RDRAM + kOstWatchPhys", "DISJ", "ost_wb_read_fields: callers pass &ctx / &pri host locals <- RDRAM"),
    ("rt64_buffer_uploader.cpp", "dstData + srcOffset", "DISJ", "dstData = uploadBuffer->map() GPU upload heap <- CPU srcData"),
    ("rt64_native_target.cpp", "memcpy(dstData, data, bufferSize)", "DISJ", "dstData = nativeUploadBuffer->map() <- RDRAM span"),
    ("rt64_native_target.cpp", "memcpy(data, readbackData + bufferOffset", "DISJ", "RDRAM span <- readbackData = nativeReadbackBuffer->map() GPU readback heap"),
    ("rt64_texture_cache.cpp", "&dst[i * dstRowPitch], &src[i * srcRowPitch]", "DISJ", "memcpyRows: both callers pass a ->map() upload buffer <- CPU image / DDS bytes"),
    ("rt64_texture_cache.cpp", "memcpy(dst, src, dstRowPitch * rowCount)", "DISJ", "memcpyRows: both callers pass a ->map() upload buffer <- CPU image / DDS bytes"),
    ("rt64_texture_cache.cpp", "memcpy(uploadData, bytes", "DISJ", "uploadData = freshly created upload buffer ->map() <- file bytes"),
    ("rt64_texture_cache.cpp", "upload.bytesTMEM.data()", "DISJ", "tmemUploadResources[i]->map() <- std::vector bytesTMEM"),
]

def strip(a):
    a = a.strip()
    for _ in range(4):
        a = re.sub(r"^(?:reinterpret_cast|static_cast|const_cast)\s*<[^<>]*(?:<[^<>]*>)?[^<>]*>\s*\(\s*(.*)\)\s*$", r"\1", a)
        a = re.sub(r"^\(\s*(?:const\s+)?[\w:]+(?:\s*\*)+\s*\)\s*", "", a).strip()
        if a.startswith("(") and a.endswith(")") and s43.args_of(a, 1) and len(s43.args_of(a, 1)) == 1 and a.count("(") == a.count(")"):
            inner = a[1:-1]
            if inner.count("(") == inner.count(")"): a = inner.strip()
    return a

def side(a):
    """(base name, is_addr_of) of one memcpy pointer argument."""
    a = strip(a); addr = a.startswith("&")
    a = a.lstrip("&").strip()
    a = re.sub(r"^\(\s*(.*?)\s*\)", r"\1", a)
    b = re.split(r"->|\.|\[|\s*[-+]\s*|\s", a)[0]
    return b, addr, a

def kind(b, body, ftext):
    """'obj' (array / scalar / std container: a distinct object), 'ptr' (pointer: may alias), None (unknown)."""
    if b in DEVOBJ: return "dev"
    v = re.escape(b)
    for text in (body, ftext):
        for mo in reversed(list(re.finditer(r"\b((?:const\s+)?(?:unsigned\s+)?[\w:]+(?:\s*<[^;{}]*?>)?)\s*([*&]*)\s*\b%s\s*(\[|=|;|\{|,|\))" % v, text))):
            t, star, nxt = mo.group(1), mo.group(2), mo.group(3)
            if t in ("return", "else", "case", "sizeof", "delete", "if", "while"): continue
            if "*" in star or "&" in star: return "ptr"
            if nxt == "[" or OBJT.match(t): return "obj"
            if re.search(r"\b%s\s*=\s*(?:new\b|\(?\s*[\w:]+\s*\*\s*\)|[\w.>-]*(?:data|get|ptr)\s*\()" % v, text): return "ptr"
            return "obj" if t != "auto" else None
    return None

def checked(dn, sn, body):
    d, s = re.escape(dn), re.escape(sn)
    return bool(re.search(r"%s\s*\+\s*\w+\s*<=\s*%s[^|;]*\|\|\s*%s\s*\+\s*\w+\s*<=\s*%s" % (d, s, s, d), body) or
                re.search(r"%s\s*\+\s*\w+\s*<=\s*%s[^|;]*\|\|\s*%s\s*\+\s*\w+\s*<=\s*%s" % (s, d, d, s), body))

st = {"MM": 0}
def census(files, pgf):
    rows = []
    for p in files:
        rel = str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else p.name
        lines, fns = s43.ln_fn(p); ftext = "\n".join(lines)
        m.MASK = CALL
        for (ln, fn, mk, c, text) in m.sites(p, pgf):
            l = lines[ln - 1]
            mm = CALL.search(l, l.find(mk)) if l.find(mk) >= 0 else CALL.search(l)
            if not mm: continue
            if mm.group(1) == "memmove": st["MM"] += 1; continue
            if mm.group(1) == "copy" and not re.search(r"std::copy\s*\(", mk + l[l.find(mk):l.find(mk) + 12]) and "std::" not in mk:
                continue   # some_object.copy(...) / copy() helpers, not std::copy
            a = s43.args_of(l, mm.end())
            if len(a) < 2: continue
            if mm.group(1) in ("copy", "copy_n"):   # std::copy(first, last, d_first) / copy_n(first, n, d_first)
                dst, src = (a[2] if len(a) > 2 else ""), a[0]
            else:
                dst, src = a[0], a[1]
            start = fns[ln - 1][1]; body = "\n".join(lines[start:ln])
            cc, why = c, ""
            if cc in "GD" and rel.startswith("lib/rt64/") and not s43.body_gated(lines, ln): cc = "?"
            if cc == "D" and fn in s44.CORE: cc = "?"
            if cc == "?":
                (db, dad, dx), (sb, sad, sx) = side(dst), side(src)
                hh = s43.hand(rel, fn, l, HAND)
                dk = "obj" if dad and kind(db, body, ftext) != "ptr" else kind(db, body, ftext)
                sk = "obj" if sad and kind(sb, body, ftext) != "ptr" else kind(sb, body, ftext)
                if hh: cc, why = hh
                elif db == sb and db:
                    off = lambda x: re.sub(r"^%s\s*\+\s*" % re.escape(db), "", x).strip("() ")
                    cc, why = ("CHK", "overlap test dominates") if checked(off(dx), off(sx), body) else ("?", f"same base {db}")
                elif dk == "obj" or sk == "obj": cc, why = "DISJ", f"{db}:{dk} / {sb}:{sk}"
                elif {dk, sk} == {"dev", "ptr"} or (dk == "dev" and sk == "dev" and db != sb): cc, why = "DISJ", f"{db}:{dk} / {sb}:{sk}"
                else: why = f"{db}:{dk} / {sb}:{sk}"
            rows.append((rel, ln, fn, cc, why, f"{mm.group(1)}({dst[:30]}, {src[:30]})", l.strip()))
    return rows

PLANT = ("static void planted(uint8_t* rdram, OSTask* task) {\n    memcpy(rdram + task->dst, rdram + task->src, task->len);\n}\n"
         "static void mm_twin(uint8_t* rdram, OSTask* task) {\n    memmove(rdram + task->dst, rdram + task->src, task->len);\n}\n"
         "static void disj_twin(uint8_t* rdram, OSTask* task) {\n    uint8_t buf[64];\n    memcpy(buf, rdram + task->src, 64);\n}\n"
         "static void chk_twin(uint8_t* rdram, OSTask* task) {\n    uint32_t d = task->dst, s = task->src, n = task->len;\n"
         "    if (d + n <= s || s + n <= d) memcpy(rdram + d, rdram + s, n);\n}\n"
         "static void gated_twin(uint8_t* rdram, OSTask* task) {\n    if (!rs64_dlwalk_on()) return;\n"
         "    memcpy(rdram + task->dst, rdram + task->src, task->len);\n}\n")

def main():
    pgf = m.probe_gate_fns()
    if "--controls" in sys.argv:
        import tempfile
        t = pathlib.Path(tempfile.mkdtemp()) / "planted.cpp"
        t.write_text(PLANT)
        got = {(r[2], r[3]) for r in census([t], pgf)}
        want = {("planted", "?"), ("disj_twin", "DISJ"), ("chk_twin", "CHK"), ("gated_twin", "G")}
        assert got == want and st["MM"] == 1, f"control failed: {got ^ want} mm={st['MM']}"
        print("[s7350] controls: planted memcpy(rdram+dst, rdram+src) '?', memmove twin excluded, local-buf twin 'DISJ', "
              "checked twin 'CHK', gated twin 'G'")
        st["MM"] = 0
    files = s43.files_in_scope()
    rows = census(files, pgf)
    cc = Counter(r[3] for r in rows)
    print(f"[s7350] memmove (safe, not sites)={st['MM']}")
    print(f"[s7350] class AA sites={len(rows)} files={len(files)} " + " ".join(f"{k}={v}" for k, v in sorted(cc.items())))
    for r in rows:
        if r[3] in ("?", "B") or "-v" in sys.argv or ("-h" in sys.argv and r[3] in ("H", "CHK")):
            print(f"  {r[3]} {r[0]}:{r[1]} {r[2]} {r[4]} :: {r[5]}")
    bad = [r for r in rows if r[3] in ("?", "B")]
    print(f"[s7350] unclassified/defect: {len(bad)}")
    bad = list(bad) + census_rules.report("s7350")  # s7654: a stale shared rule fails the gate (after the row printers)
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
