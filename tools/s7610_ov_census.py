#!/usr/bin/env python3
"""s7610 class OV: host state keyed by a GUEST CODE ADDRESS (vram / rom offset / section index / ucode text address) that
survives the guest loading different code at that address. Premise (boring check): RS64 does swap code at runtime: sections
4 ovl_mission, 5 ovl_menu, 6 ovl_cinematic all link at vram 0x800A5130 and are PI-DMAed in by loadOverlay ->
load_overlays / load_overlays_by_start (pi.cpp); the RSP side swaps IMEM overlays inside the F5 gfx ucode (class FR s7521).

Two halves.
HOST: every line in src/ + librecomp + ultramodern + RT64's HLE ucode cache that touches func_map / loaded_sections /
section_addresses / code_sections_by_rom / manual_patch_symbols_by_vram, declares a container holding recomp_func_t* or
RspUcodeFunc*, a static function-pointer cache, or compares a ucode text address against a remembered one (PAT). printf
lines are 'print'. Every other line must match a SITE_ROWS entry:
  refresh   func_map / loaded_sections / section_addresses maintained by the load / evict / unload paths (C1-C3);
  lookup    per-call resolution through func_map (get_function, LOOKUP_FUNC): nothing cached, reads the current map;
  static    keyed by ROM offset or link vram of the section table (immutable after init_overlays) or by host pointer;
  value     per-task copy of the current OSTask field, rewritten at every task;
  mod       mod-loader state (mods/ is empty, no mod is ever loaded in RS64);
  diag:<F>  runs only with env flag F (default off) or only feeds a dump.
Contracts: C1 load_overlay calls rs64_s7528_pre_load and the evict arm defaults on (ROGUESQ_S7528_EVICT=0 old) and erases
func_map entries of every overlapping loaded section; C2 load_overlay re-inserts every function of the new section;
C3 get_function reads func_map on every call (no static/thread_local cache inside it); C4 get_rsp_microcode selects by
task->t.type only (no text-address cache); C5 RT64 HLE loadUCodeGBI (keyed by text address, no content hash) is only
reached when ROGUESQ_LLE_FORCE=0 (send_dl LLE branch default on).
GENERATED: N64Recomp output (../N64Recomp/RecompiledFuncs funcs_*.c + RecompiledPatches). Each function is mapped to its
section via recomp_overlays.inl. A DIRECT call `callee(rdram, ctx)` is BAD when the callee lives in a swappable overlay
section and the caller is not in that same section (main code calling overlay code, or overlay A calling overlay B by
name): that call runs B's recompiled body whatever bytes are resident. Such calls must go through LOOKUP_FUNC.
--controls: (1) plant a vram-keyed static fn cache in get_function -> OPEN; (2) drop a row -> OPEN; (3) remove the evict
erase from rs64_s7528_pre_load -> OPEN (C1); (4) plant a ucode text-address cache in get_rsp_microcode -> OPEN (C4);
(5) plant a direct main->overlay call in generated code -> OPEN; (6) plant an overlay A->overlay B direct call -> OPEN.
--witness LOG...: runtime second source from default-build route logs: [overlay] lines show >=2 table idx loaded at one ram
(premise) and every [s7528] post line has stale_window_entries=0 with evict=1. Positive control: the s7528 same-build
two-arm pair scratch/s7528_evict/log_{old,new}.txt.zst (ROGUESQ_S7528_CTL=1): evict=0 arm stale>0 + ctl_hit=1, evict=1 arm
stale 0 + ctl_hit=0. Usage: tools/s7610_ov_census.py --controls --witness scratch/s7608_tk/log_tkon.txt ...
Exit 0 only if 0 open, 0 stale rows, 6/6 controls, witness PASS when asked.
"""
import os, re, sys, glob, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("tk", os.path.join(ROOT, "tools/s7608_tk_census.py"))
tk = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(tk)
L = "lib/N64ModernRuntime"
OV = L + "/librecomp/src/overlays.cpp"
MODS = L + "/librecomp/src/mods.cpp"
MODH = L + "/librecomp/include/librecomp/mods.hpp"
OVH = L + "/librecomp/include/librecomp/overlays.hpp"
RC = "src/main/rt64_render_context.cpp"
MAIN = "src/main/main.cpp"
RT64I = "lib/rt64/src/hle/rt64_interpreter.cpp"
GEN = os.path.normpath(os.path.join(ROOT, "..", "N64Recomp", "RecompiledFuncs"))
PATCHES = os.path.join(ROOT, "RecompiledPatches")
PAT = re.compile(r"func_map\b|loaded_sections\b|section_addresses\b|code_sections_by_rom\b|manual_patch_symbols_by_vram\b|"
                 r"(map|set)<[^;]*(recomp_func_t|RspUcodeFunc)\s*\*|t\.ucode\s*(==|!=)|\bs_last_ucode\b|textAddress\s*(!=|==)|"
                 r"static\s+(thread_local\s+)?(const\s+)?(recomp_func_t|RspUcodeFunc)\s*\*|\bs_\w*ucode\w*\s*=\s*\(?\w*\)?\s*task")

SITE_ROWS = [
    (OV, "static std::unordered_map<uint32_t, uint16_t> code_sections_by_rom{};", "static", "ROM offset -> section index, set once"),
    (OV, "patch_code_sections_by_rom", "static", "patch sections by ROM offset, set at registration (3 lines)"),
    (OV, "static std::vector<LoadedSection> loaded_sections{};", "refresh", "resident set (C1-C2)"),
    (OV, "static std::unordered_map<int32_t, recomp_func_t*> func_map{};", "refresh", "vram -> fn, maintained by load/evict/unload"),
    (OV, "static std::unordered_map<std::string, recomp_func_t*> base_exports{};", "static", "keyed by name, registration only"),
    (OV, "static std::unordered_map<uint32_t, recomp_func_t*> manual_patch_symbols_by_vram;", "static",
     "patch symbols at their fixed link vram (patches live in main code, never swapped)"),
    (OV, "int32_t* section_addresses = nullptr;", "refresh", "per-section load address; 0 RELOC_* uses in generated code"),
    (OV, "std::unordered_map<uint32_t, recomp_func_t*> patch_func_vram_map{};", "static", "local in register_patches"),
    (OV, "return code_sections_by_rom;", "static", "accessor"),
    (OV, "func_map[ram] = func;", "refresh", "add_loaded_function (mod API, no RS64 caller)"),
    (OV, "for (auto it = loaded_sections.begin(); it != loaded_sections.end();) {", "refresh", "s7528 evict + unload_overlays walks (2)"),
    (OV, "{ func_map.erase(s.funcs[f].offset + it->loaded_ram_addr); ++funcs; }", "refresh", "s7528 evict (C1)"),
    (OV, "section_addresses[s.index] = s.ram_addr;", "refresh", "s7528 evict resets section address"),
    (OV, "it = loaded_sections.erase(it);", "refresh", "evict / unload erase (2)"),
    (OV, "for (const auto& kv : func_map) {", "diag:s7528-post", "stale-window count feeds the [s7528] post print only"),
    (OV, "func_map[ram + func.offset] = func.func;", "refresh", "load_overlay + load_special_overlay insert (C2)"),
    (OV, "loaded_sections.emplace_back(ram, section_table_index);", "refresh", "load_overlay"),
    (OV, "section_addresses[section.index] = ram;", "refresh", "load_overlay"),
    (OV, "std::find_if(loaded_sections.begin(), loaded_sections.end()", "refresh", "unload_overlay_by_id (no RS64 caller)"),
    (OV, "if (find_it != loaded_sections.end()) {", "refresh", "unload_overlay_by_id"),
    (OV, "func_map.erase(func_address);", "refresh", "unload_overlay_by_id + unload_overlays erase (2)"),
    (OV, "section_addresses[section.index] = section.ram_addr;", "refresh", "unload resets (2)"),
    (OV, "loaded_sections.erase(find_it);", "refresh", "unload_overlay_by_id"),
    (OV, "int32_t prev_address = section_addresses[section.index];", "refresh", "load_overlay_by_id (no RS64 caller)"),
    (OV, "func_map.clear();", "refresh", "init_overlays"),
    (OV, "section_addresses = (int32_t *)calloc(", "refresh", "init_overlays"),
    (OV, "if (section_addresses == nullptr && sections_info.total_num_sections != 0)", "refresh", "s7356 calloc check"),
    (OV, "section_addresses[sections_info.code_sections[section_index].index] = code_section->ram_addr;", "refresh", "init"),
    (OV, "code_sections_by_rom[code_section->rom_addr] = section_index;", "static", "init"),
    (OV, "manual_patch_symbols_by_vram.emplace(", "static", "init"),
    (OV, "manual_patch_symbols_by_vram.find(function_offset)", "static", "mod relocation lookup (2 lines)"),
    (OV, "find_it != manual_patch_symbols_by_vram.end()", "static", "mod relocation lookup"),
    (OV, "code_sections_by_rom.find(section_rom)", "static", "mod relocation lookup (2 lines)"),
    (OV, "find_section_it == code_sections_by_rom.end()", "static", "mod relocation lookup"),
    (OV, "loaded_sections.size());", "diag:service-resolution", "rs64_log_service_resolution dump"),
    (OV, "for (const LoadedSection& loaded : loaded_sections) {", "diag:service-resolution", "dump"),
    (OV, "std::vector<std::unordered_map<uint32_t, recomp_func_t*>> offmap;", "diag:ROGUESQ_S7520_CODE", "s7520 FQ checker"),
    (OV, "std::unordered_map<recomp_func_t*, int> patchset;", "diag:ROGUESQ_S7520_CODE", "s7520 FQ checker"),
    (OV, "if (func_map.count((int32_t)h)) ++c.ovl_mapped;", "diag:ROGUESQ_S7774_SLOTS", "s7774 stale NPC-slot scan reads current map"),
    (OV, "for (const auto& ls : loaded_sections) sig = sig * 131 + ls.section_table_index + 1;", "diag:ROGUESQ_S7774_SLOTS",
     "s7774 resident-set signature (read only)"),
    (OV, "auto func_find = func_map.find(addr);", "lookup", "get_function per call (C3)"),
    (OV, "if (func_find == func_map.end()) {", "lookup", "get_function miss -> fatal / stub"),
    (OV, "recomp::overlays::get_base_patched_funcs()", "static", "keyed by host fn pointer (mod loader)"),
    (OV, "std::unordered_map<recomp_func_t*, BasePatchedFunction> ret{};", "static", "host fn pointer"),
    (OV, "std::unordered_map<recomp_func_t*, BasePatchedFunction> all_patch_funcs{};", "static", "host fn pointer"),
    (OVH, "get_base_patched_funcs();", "static", "decl"),
    (MODH, "std::unordered_map<recomp_func_t*", "mod", "mod loader (3 lines)"),
    (MODH, "std::unordered_map<std::string, recomp_func_t*> native_library_exports;", "mod", "by name"),
    (MODH, "section_addresses", "mod", "mod-local section tables (6 lines)"),
    (MODS, "section_addresses", "mod", "mod loader (7 lines)"),
    (MODS, "std::unordered_map<recomp_func_t*", "mod", "mod loader (4 lines)"),
    (MAIN, "s_pending_task_ucode_data", "value", "copy of the CURRENT task's ucode_data/size, rewritten every gfx task (4 lines)"),
    (RC, "static uint32_t s_last_ucode = 0;", "diag:ROGUESQ_LLE_FORCE=0", "HLE send_dl change print"),
    (RC, "const bool ucode_changed = (task->t.ucode != s_last_ucode)", "diag:ROGUESQ_LLE_FORCE=0", "print gate only"),
    (RC, "s_last_ucode = task->t.ucode;", "diag:ROGUESQ_LLE_FORCE=0", "print state"),
    (RT64I, "if ((UCode.textAddress != maskedTextAddress) || (UCode.dataAddress != maskedDataAddress)) {", "diag:ROGUESQ_LLE_FORCE=0",
     "RT64 HLE GBI pick keyed by text address, no content hash (C5: unreachable in the LLE default)"),
]


def load(over=None):
    files = tk.load()
    p = os.path.join(ROOT, RT64I)
    if os.path.exists(p):
        files[RT64I] = open(p, errors="replace").read()
    if over:
        files.update(over)
    return files


def body(txt, sig):
    a = txt.find(sig)
    if a < 0:
        return ""
    b = txt.find("\n}\n", a)
    return txt[a:b if b > 0 else a + 4000]


def host(files, rows, opens, kinds):
    used = set()
    for rel, txt in sorted(files.items()):
        for i, ln in enumerate(tk.strip_comments(txt).split("\n"), 1):
            if not PAT.search(ln):
                continue
            if "printf" in ln:
                kinds["print"] = kinds.get("print", 0) + 1
                continue
            hit = next((k for k, r in enumerate(rows) if rel.endswith(r[0]) and r[1] in ln), None)
            if hit is None:
                opens.append(f"UNROWED {rel}:{i}: {ln.strip()[:120]}")
                continue
            used.add(hit)
            kd = rows[hit][2].split(":")[0]
            kinds[kd] = kinds.get(kd, 0) + 1
    ov, mn, rc, ri = (files.get(x, "") for x in (OV, MAIN, RC, RT64I))
    pre = body(ov, "static void rs64_s7528_pre_load(")
    if ('return e && *e == \'0\' ? 0 : 1;' not in pre or "if (!evict) { ++it; continue; }" not in pre
            or "func_map.erase(s.funcs[f].offset + it->loaded_ram_addr)" not in pre):
        opens.append("C1 load_overlay evict no longer default-on / no longer erases overlapping sections' func_map entries")
    lo = body(ov, "void load_overlay(size_t section_table_index, int32_t ram) {")
    if "rs64_s7528_pre_load(" not in lo or "func_map[ram + func.offset] = func.func;" not in lo:
        opens.append("C2 load_overlay lost the pre-load evict call or the per-function insert")
    gf = tk.strip_comments(body(ov, 'extern "C" recomp_func_t * get_function(int32_t addr) {'))
    if "func_map.find(addr)" not in gf or re.search(r"static\s+(thread_local\s+)?[^;(]*(recomp_func_t|func_t)\s*\*|static[^;]*map<[^;]*func", gf):
        opens.append("C3 get_function no longer resolves through func_map on every call (a cache sits in front)")
    gm = tk.strip_comments(body(mn, "RspUcodeFunc* get_rsp_microcode(const OSTask* task) {"))
    if "switch (task->t.type)" not in gm or re.search(r"t\.ucode\s*[!=]=|static[^;]*ucode\w*\s*=", gm):
        opens.append("C4 get_rsp_microcode keys on something other than task->t.type")
    sd = body(rc, "    void send_dl(const OSTask* task) override {")
    if "s_lle_force = (v && *v) ? (v[0] != '0') : 1;" not in sd or ri and "loadUCodeGBI" not in ri:
        opens.append("C5 LLE force is no longer default on: RT64's text-address-keyed GBI cache becomes live")
    return used


SEC_ARR = re.compile(r"static FuncEntry (section_(\d+)_\w+?_funcs)\[\] = \{(.*?)\n\};", re.S)
SEC_ROW = re.compile(r"\{ \.rom_addr = 0x([0-9A-F]+), \.ram_addr = 0x([0-9A-F]+), \.size = 0x([0-9A-F]+), \.funcs = (\w+),")
FDEF = re.compile(r"^RECOMP_FUNC void (\w+)\(uint8_t\* rdram, recomp_context\* ctx\) \{", re.M)
CALL = re.compile(r"\b(\w+)\(rdram, ctx\);")


def gen_load(gover=None):
    inl = open(os.path.join(GEN, "recomp_overlays.inl"), errors="replace").read()
    owner, secs = {}, {}
    arrs = {m.group(1): (int(m.group(2)), re.findall(r"\.func = (\w+),", m.group(3))) for m in SEC_ARR.finditer(inl)}
    for m in SEC_ROW.finditer(inl):
        idx, names = arrs[m.group(4)]
        secs[idx] = (int(m.group(2), 16), int(m.group(3), 16))
        for n in names:
            owner.setdefault(n, idx)
    ren = open(os.path.join(ROOT, "tools/rename_generated_symbols.py"), errors="replace").read()
    statics = {b: int(a) for a, b in re.findall(r'"static_(\d+)_[0-9A-Fa-f]+":\s*"(\w+)"', ren)}
    swap = set()
    for a, (ra, sa) in secs.items():
        for b, (rb, sb) in secs.items():
            if a != b and ra < rb + sb and rb < ra + sa:
                swap.add(a)
    srcs = {}
    for p in sorted(glob.glob(os.path.join(GEN, "funcs_*.c")) + glob.glob(os.path.join(PATCHES, "*.c"))):
        srcs[p] = open(p, errors="replace").read()
    if gover:
        srcs.update(gover)
    unowned = []
    for path, txt in srcs.items():
        for n in FDEF.findall(txt):
            if n in owner:
                continue
            if path.startswith(PATCHES):
                owner[n] = -1               # PatchesLib section: load_special_overlay at its own ram, never swapped
                continue
            m = re.match(r"static_(\d+)_[0-9A-F]+$", n)
            base = re.sub(r"_s\d+_(inner|impl)$", "", n)
            if m:
                owner[n] = int(m.group(1))
            elif n in statics:
                owner[n] = statics[n]       # N64Recomp static_<sec>_<vram>, renamed by tools/rename_generated_symbols.py
            elif base != n and base in owner:
                owner[n] = owner[base]      # fixup-split body (_sNNNN_inner/_impl) lives with its wrapper
            else:
                unowned.append(n)
    return owner, secs, swap, srcs, sorted(set(unowned))


def generated(opens, kinds, gover=None):
    owner, secs, swap, srcs, unowned = gen_load(gover)
    for n in unowned:
        opens.append(f"UNOWNED generated function {n}: no section (cannot tell whether its direct calls are resident)")
    direct = lookups = into_ovl_same = 0
    for p, txt in srcs.items():
        defs = list(FDEF.finditer(txt))
        for k, d in enumerate(defs):
            caller = d.group(1)
            seg = txt[d.end():defs[k + 1].start() if k + 1 < len(defs) else len(txt)]
            cs = owner.get(caller)
            lookups += seg.count("LOOKUP_FUNC(")
            for c in CALL.findall(seg):
                ts = owner.get(c)
                if ts is None:
                    continue
                direct += 1
                if ts in swap:
                    if cs == ts:
                        into_ovl_same += 1
                    else:
                        opens.append(f"BAD-DIRECT {os.path.basename(p)}: {caller} (sec {cs}) -> {c} (overlay sec {ts})")
    kinds["gen_direct"] = direct; kinds["gen_lookup"] = lookups; kinds["gen_same_overlay"] = into_ovl_same
    return owner, secs, swap


def run(over=None, rows=None, gover=None, verbose=False):
    rows = SITE_ROWS if rows is None else rows
    files = load(over)
    opens, kinds = [], {}
    used = host(files, rows, opens, kinds)
    stale = [r for k, r in enumerate(rows) if k not in used]
    owner, secs, swap = generated(opens, kinds, gover)
    if verbose:
        print(f"  sections {len(secs)}; swappable (shared vram) {sorted(swap)} at "
              + ",".join(sorted({f'{secs[s][0]:08X}' for s in swap})) + f"; generated functions {len(owner)}")
        for o in opens:
            print("  OPEN", o)
        for r in stale:
            print("  STALE", r[0], r[1])
    return {"open": opens, "stale": stale, "kinds": kinds, "rows": len(rows), "swap": swap}


def report(r, tag="real"):
    ks = " ".join(f"{k}={v}" for k, v in sorted(r["kinds"].items()))
    print(f"[{tag}] {ks} rows {r['rows']} open {len(r['open'])} stale {len(r['stale'])}")


def controls():
    base = load(); ok = 0; b0 = len(run()["open"]); ov = base[OV]; mn = base[MAIN]
    anchor = "    auto func_find = func_map.find(addr);"
    p = ov.replace(anchor, "    static std::unordered_map<int32_t, recomp_func_t*> s7610_cache;\n"
                   "    if (auto c = s7610_cache.find(addr); c != s7610_cache.end()) return c->second;\n" + anchor, 1)
    r = run({OV: p}); c = p != ov and len(r["open"]) > b0 and any(o.startswith(("UNROWED", "C3")) for o in r["open"]); ok += c
    print("  ctl1 vram fn cache in get_function:", len(r["open"]), "PASS" if c else "FAIL")
    rows = [x for x in SITE_ROWS if x[1] != "auto func_find = func_map.find(addr);"]
    r = run(rows=rows); c = len(r["open"]) > b0; ok += c; print("  ctl2 drop row:", len(r["open"]), "PASS" if c else "FAIL")
    q = ov.replace("        if (!evict) { ++it; continue; }\n        for (size_t f = 0; f < s.num_funcs; f++) { func_map.erase(s.funcs[f].offset + it->loaded_ram_addr); ++funcs; }\n",
                   "        if (!evict) { ++it; continue; }\n", 1)
    r = run({OV: q}); c = q != ov and any(o.startswith("C1") for o in r["open"]); ok += c
    print("  ctl3 evict erase removed:", len(r["open"]), "PASS" if c else "FAIL")
    a = "    switch (task->t.type) {\n    case M_GFXTASK:"
    t = mn.replace(a, "    static uint32_t s_s7610_text = 0; if (task->t.ucode == s_s7610_text) return &factor5_gfx_runner;\n" + a, 1)
    r = run({MAIN: t}); c = t != mn and any(o.startswith(("C4", "UNROWED")) for o in r["open"]); ok += c
    print("  ctl4 ucode text-address cache:", len(r["open"]), "PASS" if c else "FAIL")
    owner, secs, swap, srcs, _ = gen_load()
    inl_ovl = {}
    for n, s in owner.items():
        inl_ovl.setdefault(s, n)
    main_fn = next(n for n, s in owner.items() if s == 3)
    so = sorted(swap)
    ovl_a, ovl_b = inl_ovl[so[0]], inl_ovl[so[1]]
    p0 = next(iter(srcs))
    plant_main = (f"\nRECOMP_FUNC void {main_fn}(uint8_t* rdram, recomp_context* ctx) {{\n    {ovl_a}(rdram, ctx);\n}}\n")
    r = run(gover={p0: srcs[p0] + plant_main}); c = any("BAD-DIRECT" in o and ovl_a in o for o in r["open"]); ok += c
    print(f"  ctl5 direct main->overlay ({main_fn}->{ovl_a}):", len(r["open"]), "PASS" if c else "FAIL")
    plant_ab = (f"\nRECOMP_FUNC void {ovl_a}(uint8_t* rdram, recomp_context* ctx) {{\n    {ovl_b}(rdram, ctx);\n}}\n")
    r = run(gover={p0: srcs[p0] + plant_ab}); c = any("BAD-DIRECT" in o and ovl_b in o for o in r["open"]); ok += c
    print(f"  ctl6 direct overlay->overlay ({ovl_a}->{ovl_b}):", len(r["open"]), "PASS" if c else "FAIL")
    print(f"controls {ok}/6")
    return ok


def _lines(p):
    if p.endswith(".zst"):
        import subprocess
        return subprocess.run(["zstd", "-dc", p], capture_output=True, text=True, errors="replace").stdout.split("\n")
    return open(p, errors="replace")


def _scan(p):
    loads, posts, stale, ev, hit = {}, 0, 0, set(), {0: 0, 1: 0}
    for ln in _lines(p):
        m = re.search(r"\[overlay\] (?:load section idx=|start-match: section )(\d+) rom=0x[0-9A-F]+ at ram=0x([0-9A-F]+)", ln)
        if m:
            loads.setdefault(m.group(2), set()).add(int(m.group(1)))
        m = re.search(r"\[s7528\] pre idx=\d+ ram=[0-9A-F]+ size=[0-9A-F]+ evict=(\d)", ln)
        if m:
            ev.add(m.group(1))
        m = re.search(r"\[s7528\] post idx=\d+ ram=[0-9A-F]+ funcs=\d+ stale_window_entries=(\d+)", ln)
        if m:
            posts += 1; stale += int(m.group(1)) > 0
            h = re.search(r"ctl_hit=(\d)", ln)
            if h:
                hit[int(h.group(1))] += 1
    return loads, posts, stale, ev, hit


CTL_DIR = "scratch/s7528_evict"


def witness(paths):
    """Default-build route logs must show >1 table idx loaded at one ram (premise), every swap stale_window_entries=0 with
    evict=1. Positive control = the s7528 same-build two-arm pair (ROGUESQ_S7528_CTL=1 planted stale lookup): the evict=0
    arm must show stale>0 and ctl_hit=1 (instrument fires), the evict=1 arm stale 0 and ctl_hit=0 on the same probes."""
    shared, posts, bad, evs = {}, 0, 0, set()
    for p in paths:
        loads, n, st, ev, _ = _scan(p)
        posts += n; bad += st; evs |= ev
        for r, s in loads.items():
            shared.setdefault(r, set()).update(s)
    shared = {r: s for r, s in shared.items() if len(s) > 1}
    o = _scan(os.path.join(ROOT, CTL_DIR, "log_old.txt.zst")); n = _scan(os.path.join(ROOT, CTL_DIR, "log_new.txt.zst"))
    ctl = o[3] == {"0"} and o[2] > 0 and o[4][1] > 0 and n[3] == {"1"} and n[2] == 0 and n[4][1] == 0 and n[4][0] > 0
    print(f"witness ctl ({CTL_DIR}): evict=0 arm stale>0 {o[2]} ctl_hit=1 {o[4][1]}; evict=1 arm stale>0 {n[2]} "
          f"ctl_hit=1/0 {n[4][1]}/{n[4][0]} -> {'CONTROL PASS' if ctl else 'CONTROL FAIL'}")
    print(f"witness: {len(paths)} logs; ram with >1 table idx loaded: "
          + (" ".join(f"{r}:{sorted(s)}" for r, s in sorted(shared.items())) or "none")
          + f"; [s7528] post lines {posts}, stale>0 {bad}, evict arms {sorted(evs)}")
    good = ctl and bool(shared) and posts > 0 and bad == 0 and evs == {"1"}
    print("witness", "PASS" if good else "FAIL")
    return good


if __name__ == "__main__":
    r = run(verbose=True)
    report(r)
    good = not r["open"] and not r["stale"]
    if "--controls" in sys.argv:
        good = controls() == 6 and good
    if "--witness" in sys.argv:
        ws = sys.argv[sys.argv.index("--witness") + 1:]
        good = witness(ws) and good
    sys.exit(0 if good else 1)
