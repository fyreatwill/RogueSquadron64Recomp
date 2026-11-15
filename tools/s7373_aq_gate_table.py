#!/usr/bin/env python3
"""s7373 AQ runtime half, offline: name the GATE of every s7366 lockset row a coverage run never executed.
usage: s7373_aq_gate_table.py <lockset_rows.txt> <llvm-cov export json (whole run)> [--all] [--tsv out.tsv]
Rows (file, container, function, unlocked@lines) come from tools/s7366 census; coverage is the s7372 COV=1 export.
Per row whose unlocked@ lines all have count 0 (or every row with --all), the class is decided from the coverage data
and the source, in this order:
  G-dtor   the line's enclosing function is a destructor (~X) or a shutdown routine (named destroy/shutdown/release_all)
  G-const  the line only reads <container>.size() and <container> is declared std::array<...> (compile-time constant;
           no runtime access exists to cover)
  G-branch the enclosing function RAN (entry count > 0) but the line did not: a branch not taken. Reported with the
           nearest enclosing if/else/case text so the condition can be read.
  G-env    the enclosing function never ran and the first executed ancestor (walking call sites up to 4 levels) skips
           the call under a condition naming ROGUESQ_* / getenv / an env-cache flag within the gating window
  G-route  never ran, no env token found on the gating path: a default path the run's route did not reach (needs a run)
  G-dead   never ran and no call site exists in the compiled tree (function-pointer use counts as a call site)
Hand classes (OVERRIDE table, --auto shows the walker alone): G-build (compiled out of the TSan build), G-input (needs a
host hotkey), G-error (invalid-ROM path), G-cfg (RT64 texture-pack load, inspector UI only), G-route-confined (default
path this route did not reach, container proven single-thread by instance ownership).
Positive controls (iron rule 1, exit 2 if either fails): the rt64_texture_cache.cpp TextureCache row must be G-dtor and the
present/workload previousWriteCursor rows must be G-const."""
import json, re, sys, os, subprocess, bisect, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows_path, cov_path = sys.argv[1], sys.argv[2]
want_all = "--all" in sys.argv
tsv = sys.argv[sys.argv.index("--tsv") + 1] if "--tsv" in sys.argv else None
data = json.load(open(cov_path))
# per file: line segments (for line counts) and function spans (start,end,count,name)
segs, spans = {}, collections.defaultdict(list)
mangled = []
for d in data["data"]:
    for f in d["files"]:
        segs[f["filename"]] = sorted(s[:6] for s in f.get("segments", []))
    for fn in d.get("functions", []):
        r0 = fn["regions"][0]
        spans[fn["filenames"][r0[5]]].append([r0[0], r0[2], fn["count"], fn["name"]])
        mangled.append(fn["name"])
names = sorted(set(mangled))
dem = subprocess.run(["c++filt"], input="\n".join(n.split(":", 1)[1] if ".cpp:" in n or ".h:" in n else n for n in names),
                     capture_output=True, text=True).stdout.splitlines()
demap = dict(zip(names, dem)) if len(dem) == len(names) else {n: n for n in names}
for fk in spans:
    agg = {}
    for s, e, c, n in spans[fk]:  # template/inline copies: merge identical spans, max count
        k = (s, e); a = agg.setdefault(k, [s, e, 0, demap.get(n, n)]); a[2] = max(a[2], c)
    spans[fk] = sorted(agg.values())

def fkey(rel):
    return next((k for k in segs if k.endswith("/" + rel) or k.endswith(rel)), None)

def line_count(fk, L):
    sg = segs.get(fk, [])
    i = bisect.bisect_left(sg, [L])
    cand = [sg[i - 1]] if i else []
    while i < len(sg) and sg[i][0] == L: cand.append(sg[i]); i += 1
    cs = [s[2] for s in cand if s[3] and not s[5]]
    return max(cs) if cs else 0

def enclosing(fk, L):  # innermost function span containing L (lambdas nest inside their parent)
    best = None
    for s, e, c, n in spans.get(fk, []):
        if s <= L <= e and (best is None or (e - s) < (best[1] - best[0])): best = (s, e, c, n)
    return best

src_cache = {}
def src(path):
    if path not in src_cache:
        try: src_cache[path] = open(path, errors="replace").read().splitlines()
        except OSError: src_cache[path] = []
    return src_cache[path]

ENV = re.compile(r"ROGUESQ_|getenv|rs64_env|env_flag|env_on|env_int|ENV_|_env\b|g_[a-z0-9_]*(?:diag|log|probe|trace|dump|census)|"
                 r"s_[a-z0-9_]*(?:on|enabled|armed)\b|\bdiag|\blog_on|\bprobe_on|\benabled\b|\barmed\b", re.I)
def gate_text(lines, L, s):  # condition lines that dominate line L inside a function starting at s
    out = []; depth = 0
    for i in range(L - 2, max(s - 1, L - 200) - 1, -1):
        t = lines[i]
        depth += t.count("}") - t.count("{")
        if depth < 0 or re.search(r"^\s*(?:if|else if|while|for|case|switch)\b|return\b.*;\s*$|\?\s", t) and depth <= 0:
            if re.search(r"\b(?:if|else|while|case|switch)\b|return", t): out.append((i + 1, t.strip()[:110]))
            depth = min(depth, 0)
        if len(out) >= 6: break
    return out

CTRL = re.compile(r"\b(?:if|while|for|case|switch|return)\b|\?|&&|\|\|")
def cov_gate(fk, L, s):  # executed control line nearest above L: the branch whose untaken arm holds L
    lines = src(fk)
    for i in range(L - 1, s - 1, -1):
        if line_count(fk, i) > 0 and CTRL.search(lines[i - 1]): return (i, lines[i - 1].strip()[:110])
    return None
def env_ident(fk, txt):  # a bare flag in the condition whose initialiser reads the environment
    for idn in set(re.findall(r"\b([A-Za-z_]\w{2,})\b", txt)) - {"if", "return", "while", "nullptr", "true", "false"}:
        for t in src(fk):
            if idn in t and re.search(r"\b" + re.escape(idn) + r"\b\s*=", t) and ENV.search(t): return idn
    return None
def gate_env(lines, L, s, fk=None):
    if fk is not None:
        cg = cov_gate(fk, L, s)
        if cg:
            if ENV.search(cg[1]) or env_ident(fk, cg[1]): return [cg], [cg]
            return [], [cg]
    g = gate_text(lines, L, s)
    # an early return guarded by an env token anywhere before L in the function also gates it
    early = [(i + 1, lines[i].strip()[:110]) for i in range(s - 1, L - 1)
             if ENV.search(lines[i]) and re.search(r"\bif\b|return|\?", lines[i])]
    return [x for x in g + early if ENV.search(x[1])], g

SRC_DIRS = ["src", "lib/rt64/src", "lib/N64ModernRuntime/librecomp/src", "lib/N64ModernRuntime/ultramodern/src"]
# corpus = every source file the coverage build linked (headers included), loaded once
CORPUS = [k for k in segs if k.startswith(ROOT) and "/contrib/" not in k]
for _sd in SRC_DIRS:  # headers declare std::array members but carry no segments when unused
    for _dp, _dn, _fn in os.walk(os.path.join(ROOT, _sd)):
        if "/contrib" in _dp: continue
        CORPUS += [os.path.join(_dp, x) for x in _fn if x.endswith((".h", ".hpp")) and os.path.join(_dp, x) not in CORPUS]
def call_sites(fn):
    rx = re.compile(r"(?:^|[^A-Za-z0-9_])" + re.escape(fn) + r"(?:[^A-Za-z0-9_]|$)")
    return [(path, i + 1, t) for path in CORPUS for i, t in enumerate(src(path)) if fn in t and rx.search(t)]
def array_decl(cont):
    rx = re.compile(r"std::array<[^;]*>\s+" + re.escape(cont) + r"\b")
    return next((t.strip() for path in CORPUS for t in src(path) if cont in t and rx.search(t)), "")

def short(n): return n.split("(")[0].split("::")[-1] if "::~" not in n else "~" + n.split("::~")[-1].split("(")[0]

GENERIC = {"operator", "enabled", "get", "on", "run", "main", "init", "clear", "reset", "update", "begin", "end", "size"}
def walk(fn, fk_def, defline, depth, seen):
    """returns (class, evidence) for a never-executed function."""
    if depth > 4 or fn in seen: return "G-route", f"depth>{depth}"
    seen.add(fn)
    sites = []
    if fn.startswith("$") or fn in GENERIC or len(fn) < 5:
        return "G-route", f"generic/lambda name {fn!r}: manual"
    for p, ln, t in call_sites(fn):
        fk = fkey(p)
        if fk is None: continue  # not linked in this build
        enc = enclosing(fk, ln)
        if enc is None: continue  # file-scope use (table init / registration) -> handled below
        if enc[0] == ln and short(enc[3]) == fn: continue  # its own definition line
        if fk == fk_def and enc[0] <= defline <= enc[1] and short(enc[3]) == fn: continue  # inside itself (recursion)
        sites.append((p, fk, ln, t, enc))
    if not sites:
        return "G-dead", "no call site inside a linked function"
    reasons = []
    for p, fk, ln, t, enc in sites:
        if enc[2] > 0:  # caller ran, call line did not (else the callee would have a count)
            envg, g = gate_env(src(fk), ln, enc[0], fk)
            if envg: return "G-env", f"{os.path.relpath(p, ROOT)}:{ln} in {short(enc[3])} (ran {enc[2]}) gated by L{envg[0][0]} {envg[0][1]}"
            reasons.append(f"{os.path.relpath(p, ROOT)}:{ln} in {short(enc[3])} ran {enc[2]}, call line {line_count(fk, ln)}; cond {g[:1]}")
    if reasons: return "G-route", " | ".join(reasons[:2])
    sub = []
    for p, fk, ln, t, enc in sites:
        c, ev = walk(short(enc[3]), fk, enc[0], depth + 1, seen)
        sub.append((c, f"<- {short(enc[3])} ({os.path.relpath(p, ROOT)}:{ln}) {ev}"))
        if c == "G-env": return c, sub[-1][1]
    order = ["G-route", "G-dtor", "G-dead"]
    sub.sort(key=lambda x: order.index(x[0]) if x[0] in order else 0)
    return sub[0]

# s7373 hand adjudication of rows the walker cannot settle (generic/lambda names, function-call flags, non-env gates).
# key (file basename, container, function) -> (class, evidence). Every entry was read at the cited line on the s7372 tree.
OVERRIDE = {
 ("main.cpp", "cur", "s4578_poll"): ("G-env", "main.cpp:2074 s4578_on() = ROGUESQ_LOG_S4578"),
 ("main.cpp", "cur", "start_level_poller"): ("G-env", "main.cpp:8776 early return unless ROGUESQ_LOG_LEVEL / FORCE_MISSION / FORCE_SEL"),
 ("main.cpp", "cur", "rs64_s6843_note"): ("G-env", "rs64_s6843_len set only by ROGUESQ_STORE_WATCH (main.cpp:2165) or the [wipescan] diag (dpc_bridge.cpp:5791)"),
 ("main.cpp", "cur", "rs64_s7355_altstack_drop"): ("G-build", "main.cpp:12818 rs64_s7355_altstack_install returns under RS64_TSAN_BUILD (s7366); default build runs it"),
 ("main.cpp", "cur", "rs64_s7355_altstack_here"): ("G-build", "main.cpp:12818 same TSan-build skip; `cur` is a stack_t local, not a shared container"),
 ("main.cpp", "g_audio_route_pref", "audio_route_apply_cycle"): ("G-input", "main.cpp:8036 presses<=0 return: needs the audio-route hotkey; static H-safe-thread"),
 ("recomp.cpp", "game_roms", "select_rom"): ("G-error", "main.cpp:13240 only when recomp::is_rom_valid fails (bad/missing ROM)"),
 ("dpc_bridge.cpp", "last", "rs64_g5b_frame"): ("G-env", "dpc_bridge.cpp:3609 f = fopen(ROGUESQ_G5B_FRAME)"),
 ("dpc_bridge.cpp", "last", "rs64_dpc_defer_begin"): ("G-env", "dpc_bridge.cpp:8009 g_bf_mode = ROGUESQ_G1E_BUMPFAST (dpc_bridge.cpp:6410)"),
 ("dpc_bridge.cpp", "g_f5_last_writer", "rs64_f5_last_writer_ensure"): ("G-env", "dpc_bridge.cpp:1736 rs64_f5_shadow_on() = ROGUESQ_LOG_F5_STORE_SHADOW"),
 ("rt64_framebuffer_renderer.cpp", "dynamicTextureViewVector", "submitRasterScene"): ("G-env", "fb_renderer.cpp:2198 floorCapture needs ROGUESQ_FLOOR_SHADER_DIR (:1547)"),
 ("rt64_framebuffer_renderer.cpp", "textureCacheTextureReplacements", "submitRasterScene"): ("G-env", "fb_renderer.cpp:2198 floorCapture (ROGUESQ_FLOOR_SHADER_DIR)"),
 ("rt64_framebuffer_renderer.cpp", "textureCacheTextures", "submitRasterScene"): ("G-env", "fb_renderer.cpp:2198 floorCapture (ROGUESQ_FLOOR_SHADER_DIR)"),
 ("rt64_framebuffer_renderer.cpp", "raw", "rs64FloorRdramPrepare"): ("G-env", "fb_renderer.cpp:1093 depthDirOn() = ROGUESQ_FLOOR_DEPTH_DIR"),
 ("rt64_framebuffer_renderer.cpp", "raw", "rs64FloorRdramNoteSwap"): ("G-env", "fb_renderer.cpp:1117 snap->present only after depthDirOn() (ROGUESQ_FLOOR_DEPTH_DIR)"),
 ("rt64_framebuffer_renderer.cpp", "raw", "rdramFillCols"): ("G-env", "callers fb_renderer.cpp:1112/1126/1155 all behind depthDirOn() (ROGUESQ_FLOOR_DEPTH_DIR)"),
 ("rt64_framebuffer_renderer.cpp", "raw", "rs64DepthHistFlush"): ("G-env", "depth-histogram slot armed only by the ROGUESQ_FLOOR_DEPTH_DIR / width probe at fb_renderer.cpp:1835"),
 ("rt64_framebuffer_renderer.cpp", "dynamicTextureBarrierVector", "getTextureIndex"): ("G-route-confined", "fb_renderer.cpp:279 only when callTile.tileCopyUsed (none this route); member of a FramebufferRenderer owned by ONE thread (State :653 / WorkloadQueue :178 separate instances) -> H-safe-thread by construction"),
 ("rt64_framebuffer_renderer.cpp", "dynamicTextureViewVector", "getTextureIndex"): ("G-route-confined", "same tileCopyUsed gate; per-instance member, one owning thread"),
 ("rt64_framebuffer_renderer.cpp", "textureCacheFreeSpaces", "getDestinationIndex"): ("G-route-confined", "called only from getTextureIndex (:391); per-instance member, one owning thread"),
 ("rt64_rdp.cpp", "bucket", "drawTris"): ("G-env", "rt64_rdp.cpp:2456 s_uv = ROGUESQ_LOG_UVSCALE"),
 ("rt64_render_context.cpp", "pool", "submit_rdp_range"): ("G-env", "rt64_render_context.cpp:1994 s_img from env"),
 ("rt64_texture_cache.cpp", "replacementDirectories", "clear"): ("G-cfg", "ReplacementMap::clear runs on texture-pack load (rt64_state.cpp:4368-4437, RT64 inspector UI only); the port never loads a pack"),
 ("rt64_texture_cache.cpp", "relativePath", "addLoadedTexture"): ("G-cfg", "texture-pack stream results only (no pack loaded)"),
 ("rt64_texture_cache.cpp", "relativePath", "getFromRelativePath"): ("G-cfg", "texture-pack resolved paths only (no pack loaded)"),
 ("rt64_texture_cache.cpp", "relativePath", "hashFromRelativePath"): ("G-cfg", "called from addLoadedTexture only (texture packs)"),
 ("rsp.cpp", "g_audio_image_sources", "audio_image_match_source_locked"): ("G-env", "rs64_audio_image_stage main.cpp:6216 needs g_rs64_audio_identity.valid, set only under ROGUESQ_LOG_M5_ROUTE_* (main.cpp:4280-4336)"),
 ("rsp.cpp", "g_audio_image_sources", "audio_image_source_census_locked"): ("G-env", "same M5 route-identity gate"),
 ("rsp.cpp", "g_audio_image_stages", "audio_image_source_census_locked"): ("G-env", "same M5 route-identity gate"),
 ("rsp.cpp", "g_audio_image_stages", "audio_image_summary_locked"): ("G-env", "same M5 route-identity gate"),
 ("rsp.cpp", "g_audio_join_pcm", "audio_image_match_stage_locked"): ("G-env", "same M5 route-identity gate"),
 ("rsp.cpp", "g_audio_join_pcm", "audio_image_report_locked"): ("G-env", "same M5 route-identity gate"),
 ("rsp.cpp", "g_audio_join_pcm", "audio_image_summary_locked"): ("G-env", "same M5 route-identity gate"),
 ("rsp.cpp", "g_audio_image_stages", "audio_image_match_pcm_locked"): ("G-env", "rs64_audio_join_pcm behind s_log_pcm_boundary (audio.cpp:45-53, env)"),
 ("rsp.cpp", "g_audio_join_pcm", "audio_image_match_pcm_locked"): ("G-env", "s_log_pcm_boundary (env)"),
 ("rsp.cpp", "g_audio_join_pcm", "audio_join_match_pcm_locked"): ("G-env", "s_log_pcm_boundary (env)"),
 ("rsp.cpp", "g_audio_join_pcm", "audio_join_report_locked"): ("G-env", "s_log_pcm_boundary (env)"),
 ("rsp.cpp", "g_audio_join_tasks", "audio_join_match_pcm_locked"): ("G-env", "s_log_pcm_boundary (env)"),
 ("rsp.cpp", "g_audio_join_pcm", "audio_join_match_task_locked"): ("G-env", "rsp.cpp:1802 probe_audio = s_log_audio_run (env)"),
 ("upstream_compat.cpp", "big", "rs64_s6063_malloc"): ("G-env", "upstream_compat.cpp:3350 s6063_on() = ROGUESQ_HEAPLOG"),
 ("upstream_compat.cpp", "big", "s6127_walk"): ("G-env", "callers in rs64_s6063_malloc behind s6063_on() (ROGUESQ_HEAPLOG)"),
 ("upstream_compat.cpp", "big", "rs64_s6094_tick"): ("G-env", "ROGUESQ_BUCKETLOG"),
 ("upstream_compat.cpp", "caller", "osViSwapBuffer_recomp"): ("G-env", "upstream_compat.cpp:1127 s_log_callers (env)"),
 ("upstream_compat.cpp", "cur", "rs64_s6919_base"): ("G-env", "upstream_compat.cpp:124 m = ROGUESQ_DD_CUT_LIVE default 0 -> s6919_live(0) false"),
 ("upstream_compat.cpp", "cur", "rs64_cine_progress_log"): ("G-dead", "only caller is the watchdog spawned by rs64_cine_iter_tick, which has no caller in src/ or tools/"),
 ("upstream_compat.cpp", "cur", "rs64_s7326_scan"): ("G-env", "upstream_compat.cpp:4639 rs64_s7325_heapsync body behind s7317_on() (ROGUESQ_S7317_ALLOCMAP)"),
 ("upstream_compat.cpp", "out", "g5a_walk"): ("G-env", "callers s7334_nonheap / s7325_guest (both from the S7317_ALLOCMAP classifier :4587-4588), rs64_s7333_above (rs64_s7331_on), rs64_g5a_wblive (:4747 ROGUESQ_G5A_WBLIVE)"),
 ("upstream_compat.cpp", "out", "rs64_s7324_sym"): ("G-env", "s7324_rcp_spill.cpp:106 `if (!o) return` (env report file)"),
 ("upstream_compat.cpp", "s_s7317_live", "s7318_blk"): ("G-env", "callers rs64_s7318_bcmp / rs64_s7324_class / s7317 map, all S7317_ALLOCMAP or bcmp-probe diag"),
 ("upstream_compat.cpp", "s_s7332_carve", "s7318_blk"): ("G-env", "same S7317_ALLOCMAP / probe callers"),
 ("upstream_compat.cpp", "s_s7332_carve", "s7333_boot_register"): ("G-env", "callers s7318_blk (:3473) and rs64_s7331_task (s7331_reset_writer.cpp:206 rs64_s7331_on)"),
 ("upstream_compat.cpp", "s_s7333_keys", "s7333_boot_register"): ("G-env", "same"),
 ("upstream_compat.cpp", "s_s7333_keys", "s7333_ev"): ("G-env", "upstream_compat.cpp:3413 s7317_free behind s7317_on() (ROGUESQ_S7317_ALLOCMAP)"),
 ("upstream_compat.cpp", "sig", "rs64_s4230_poll_start"): ("G-env", "upstream_compat.cpp:2655 rs64_s4222_on() = ROGUESQ_LOG_S4222"),
}
rows = []
for l in open(rows_path):
    p = l.rstrip("\n").split("\t")
    if len(p) < 4 or not p[3].startswith("unlocked@"): continue
    rows.append((p[0], p[1], p[2], [int(x) for x in re.findall(r"\d+", p[3].split("@", 1)[1])]))
# stale-row check (s7373): the s7366 rows were cut from a tree edited since (s7368/s7371), and a line that no longer names
# its container reads count 0 -> a false "never executed". Count rows where NO cited line mentions the container.
stale = []
for file, cont, fn, lines in rows:
    fk = fkey(file)
    if fk and not any(L <= len(src(fk)) and re.search(r"\b" + re.escape(cont) + r"\b", src(fk)[L - 1]) for L in lines):
        stale.append(f"{file.split('/')[-1]}:{cont}:{fn}@{lines[0]}")
print(f"STALE rows {len(stale)}/{len(rows)}" + (": " + " ".join(stale[:8]) if stale else ""))
if stale and "--allow-stale" not in sys.argv:
    print("re-cut the rows on this tree: python3 tools/s7366_lockset_census.py -v | grep unlocked@ > rows.txt"); sys.exit(3)
out = []; cls_n = collections.Counter(); ctl = {}
for file, cont, fn, lines in rows:
    fk = fkey(file)
    if fk is None:
        c, ev, ex = "NOTLINKED", "file absent from the coverage build", None
    else:
        ex = max(line_count(fk, L) for L in lines)
        if ex and not want_all: continue
        L = lines[0]; t = src(fk)[L - 1] if L <= len(src(fk)) else ""
        enc = enclosing(fk, L)
        decl = array_decl(cont)
        if enc and ("~" in enc[3].split("(")[0] or re.search(r"(?i)(destroy|shutdown|release_all|teardown)", short(enc[3]))):
            c, ev = "G-dtor", f"{short(enc[3])} ran {enc[2]}: {t.strip()[:80]}"
        elif all(re.search(re.escape(cont) + r"\s*(?:\.|->)\s*size\(\)", src(fk)[x - 1]) for x in lines) and decl:
            c, ev = "G-const", f"{cont}.size() of std::array ({decl.strip().splitlines()[0][:60]})"
        elif enc and enc[2] > 0:
            cg = cov_gate(fk, L, enc[0])
            g = [cg] if cg else gate_text(src(fk), L, enc[0])
            envg = [x for x in g if ENV.search(x[1]) or env_ident(fk, x[1])]
            c = "G-branch"
            ev = f"{short(enc[3])} ran {enc[2]}, L{L} 0; " + (f"env cond L{envg[0][0]} {envg[0][1]}" if envg else
                                                             (f"cond L{g[0][0]} {g[0][1]}" if g else "no cond found"))
            if envg: c = "G-branch-env"
        elif enc is None:
            c, ev = "G-route", f"L{L} outside any covered function: {t.strip()[:80]}"
        else:
            envg, g = gate_env(src(fk), L, enc[0], None)
            if envg:
                c, ev = "G-env", f"own body: L{envg[0][0]} {envg[0][1]}"
                # an env test inside the never-run function does not explain why it never ran; prefer the caller chain
                c2, ev2 = walk(short(enc[3]), fk, enc[0], 0, set())
                if c2 in ("G-env", "G-dead", "G-dtor"): c, ev = c2, ev2
            else:
                c, ev = walk(short(enc[3]), fk, enc[0], 0, set())
    key = (file.split("/")[-1], cont, fn)
    if key in OVERRIDE and "--auto" not in sys.argv:
        c, ev = OVERRIDE[key][0], "HAND: " + OVERRIDE[key][1] + " || auto: " + c
    if c == "G-branch-env": c = "G-env"
    cls_n[c] += 1
    ctl[key] = c
    out.append((c, file.split("/")[-1], cont, fn, ",".join(map(str, lines)), ex, ev))
out.sort()
for o in out: print(f"{o[0]:13s} {o[1]:28s} {o[2][:30]:30s} {o[3][:34]:34s} L{o[4]:10s} {o[6][:230]}")
print("CLASSES", dict(cls_n), "rows", len(out))
if tsv:
    with open(tsv, "w") as f:
        f.write("class\tfile\tcontainer\tfunction\tlines\texec\tevidence\n")
        for o in out: f.write("\t".join(map(str, o)) + "\n")
c1 = ctl.get(("rt64_texture_cache.cpp", "tmemUploadResources", "TextureCache"))
c2 = [ctl.get((f, k, "previousWriteCursor")) for f, k in (("rt64_present_queue.cpp", "presents"), ("rt64_workload_queue.cpp", "workloads"))]
ok = c1 == "G-dtor" and all(x == "G-const" for x in c2)
print(f"CONTROL {'PASS' if ok else 'FAIL'}: TextureCache={c1} previousWriteCursor={c2}")
sys.exit(0 if ok else 2)
