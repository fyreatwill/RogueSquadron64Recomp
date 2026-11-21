#!/usr/bin/env python3
"""s7654 shared hand rules for the s7339-s7353 host-code censuses (closed-gate-drift).

s7652 hand-read every site these 12 gates flagged after later sessions (s7475-s7647 instruments, G6b bind code, G6c stand-ins)
added code, and found 0 behaviour defects, but wrote no rules, so the gates stayed RED. The rules live here once instead of 12
times. Each rule is keyed by TEXT, never by line number (s7535/s7538/s7652: line-keyed reviews drift silently):

  (file suffix, function as the census attributes it ('*' = every function of an instrument-only file), needle that must be in
   the site's line text (None = any site of that function), class, anchors, reason)

anchors = [(file suffix or None for the rule's own file, regex)]: the text that PROVES the reason (the env gate at the call site,
the bound, the clamp). check() re-proves every rule on each run: a missing file, a function the census no longer attributes,
a needle in no line of that function, or an anchor that matches nothing is a STALE row and fails the gate. So a rule cannot
outlive the code it describes, and a removed gate turns the gate RED instead of hiding a now-live site.
Classes: G = env/build-gated diagnostic, D = default-on but log/diag-only, K = bounded by a visible constant / clamp,
H = hardware field width, FLT = float maths, PTR = pointer declaration misparsed as a product."""
import re, pathlib, importlib.util
ROOT = pathlib.Path(__file__).resolve().parents[1]

UC, MAIN, SI = "src/main/upstream_compat.cpp", "src/main/main.cpp", "src/main/rs64_standins.cpp"
FBM, RDP = "lib/rt64/src/hle/rt64_framebuffer_manager.cpp", "lib/rt64/src/hle/rt64_rdp.cpp"
RULES = [
    # --- main.cpp instruments (s7495-s7551) and G6b bind code
    (MAIN, "s7496_query", None, "G", [(None, r'getenv\("ROGUESQ_S7495_POOL"\)'), (None, r"if \(s7495_on\(\) && kind <= 1\) rs64_s7495_img")],
     "s7496 overlap query: callers are rs64_s7495_img and the s7495 pool row, both under s7495_on (ROGUESQ_S7495_POOL)"),
    (MAIN, "rs64_s7495_img", None, "G", [(None, r"if \(s7495_on\(\) && kind <= 1\) rs64_s7495_img")], "ROGUESQ_S7495_POOL only"),
    (MAIN, "rs64_s7500_draw", None, "G", [(RDP, r"if \(rs64_s7500_on\) rs64_s7500_draw")], "RT64 caller gated on rs64_s7500_on"),
    (MAIN, "rs64_s7500_tex", None, "G", [(RDP, r"if \(rs64_s7500_on\) rs64_s7500_tex")], "RT64 caller gated on rs64_s7500_on"),
    (MAIN, "rs64_s7500_up", None, "G", [(FBM, r"if \(rs64_s7500_on\) rs64_s7500_up")], "RT64 caller gated on rs64_s7500_on"),
    (MAIN, "rs64_s7501_up", None, "G", [(FBM, r"if \(rs64_s7501_on\) rs64_s7501_up")], "RT64 caller gated on rs64_s7501_on"),
    (MAIN, "s7501_push_locked", "pg < kS7501Pages", "K", [(None, r"pg <= \(\(hi \? hi - 1 : lo\) >> 12\) && pg < kS7501Pages")],
     "page loop also bounded by kS7501Pages (s7501 instrument state only)"),
    (MAIN, "rs64_s7551_gk_rect", "constexpr uint32_t kWbwPage", "K", [(None, r"constexpr uint32_t kWbwPage = 16384, kWbwPages = 0x1000000u / kWbwPage")],
     "16 MB / page size = a constexpr page count, not an address mask"),
    (MAIN, "writer", "e < 48", "K", [(None, r"while \(e < n && e < 48 && b\[e\]")], "stderr-cap tag scan: string index e < n && e < 48"),
    (MAIN, "F", "c8 = (c5 << 3) | (c5 >> 2)", "K", [(None, r"for \(uint32_t d = 0; d < 8 && !any; d\+\+\) any = F\(pv16, d\)"), (None, r"std::min<uint32_t>\(c8 \+ d, 255u\)")],
     "c8 <= 255 and callers pass a dither d < 8: sum <= 262, clamped to 255 (s7551 requant model)"),
    (MAIN, "rs64_bind_selftest_step", None, "G", [(None, r"if \(s_selftest\) rs64_bind_selftest_step"), (None, r'rs64_bind_flag\("ROGUESQ_BIND_SELFTEST"\)')],
     "G6b selftest (ROGUESQ_BIND_SELFTEST / BIND_PANEL_TEST): LCG hash products wrap by design; axv[] has 8 entries, index & 7 / % 8"),
    (MAIN, "rs64_bind_poll", "std::min(s.nkeys, (int)SDL_NUM_SCANCODES)", "K", [(None, r"keycopy\[SDL_NUM_SCANCODES\]")],
     "default-on G6b poll: copy length clamped to SDL_NUM_SCANCODES = sizeof keycopy"),
    # --- upstream_compat.cpp heap/stale-line instruments (s7475-s7545)
    (UC, "rs64_s7496_ctl", None, "G", [(MAIN, r"const int c = rs64_s7496_ctl\(&cb\)")], "only caller: the s7495 pool row (ROGUESQ_S7495_POOL)"),
    (UC, "s7475_check1", None, "G", [(None, r'getenv\("ROGUESQ_S7475_CANARY"\)'), (None, r"if \(!s7475_on\(\)\) return;")], "s7475 canary walk/free check"),
    (UC, "s7480_locate", None, "G", [(None, r"if \(!s7480_on\(\) \|\| !g_rs64_s7475_bm")], "s7480 UAF (ROGUESQ_S7480_UAF, needs S7475_CANARY)"),
    (UC, "s7480_trim", None, "G", [(None, r"if \(!s7480_on\(\) \|\| !g_rs64_s7475_bm")], "s7480 UAF free path only"),
    (UC, "s7484_load", None, "G", [(None, r"return s7484_load\(pc, a, w, fn\); \}"), (None, r'getenv\("ROGUESQ_S7480_UAF"\)')],
     "s7484 load watch, reached through rs64_s7484_load (armed with the s7480 bitmap)"),
    (UC, "s7490_marked", None, "G", [(None, r"g_rs64_s7484_on && s7490_marked"), (None, r"o < 0x1800000u && \(\(g_rs64_s7475_bm\[o >> 3\]")],
     "bitmap index o < 0x1800000 into a 0x1800000>>3 table; s7490 zmemcpy hook only"),
    (UC, "s7518_load", None, "G", [(None, r"if \(s7518_watch\(\)\) \{ s7519_load\(pc, a, w, fn\); return s7518_load")], "ROGUESQ_S7518_STALEWATCH"),
    (UC, "s7519_load", None, "G", [(None, r"if \(s7518_watch\(\)\) \{ s7519_load")], "ROGUESQ_S7518_STALEWATCH"),
    (UC, "s7519_store", None, "G", [(None, r"if \(s7518_watch\(\)\) return s7519_store")], "ROGUESQ_S7518_STALEWATCH"),
    (UC, "s7519_ev", None, "G", [(None, r"if \(!g_rs64_s7484_on \|\| !n\) return;")], "callers return unless the s7518 watch armed the bitmap"),
    (UC, "s7519_row", None, "G", [(None, r'getenv\("ROGUESQ_S7518_STALEWATCH"\)')], "log row of the s7519 store/load watch"),
    (UC, "s7545_host", None, "G", [(None, r'getenv\("ROGUESQ_S7545_THRWATCH"\)'), (None, r"if \(s7545_on\(\)\) \{ if \(kind")], "ROGUESQ_S7545_THRWATCH"),
    # --- rt64
    ("lib/rt64/src/hle/rt64_framebuffer.cpp", "rs64_log_m5_host_boundary", None, "G", [(None, r'getenv\("ROGUESQ_LOG_M5_HOST_BOUNDARY"\)')],
     "M5 host-boundary log (ROGUESQ_LOG_M5_HOST_BOUNDARY / LOG_ALL)"),
    ("lib/rt64/src/hle/rt64_state.cpp", "rs64_lookup_image_word", "r < 240u", "G", [(None, r"if \(s_cpuupLog && \(currentHash"), (None, r'getenv\("ROGUESQ_S7387_LOG"\)')],
     "(attributed to the prototype above) s7388 content stats under ROGUESQ_S7387_LOG; r < 240, rowB = bytes / 240"),
    ("lib/rt64/src/hle/rt64_present_queue.cpp", "rs64PresentTestStall", "r < 240u", "G", [(None, r'getenv\("ROGUESQ_S7388_PRES"\)'), (None, r"if \(s_pres\) \{")],
     "(attributed to the helper above) s7388 present probe under ROGUESQ_S7388_PRES; r < 240, rowB = bytes / 240"),
    (FBM, "?", "(1u << fb->siz) >> 1", "H", [(None, r"std::max\(1u, \(1u << fb->siz\) >> 1\)")], "fb->siz is the 2-bit RDP image size field (0..3)"),
    (FBM, "?", "if (rs64_s7501_on) rs64_s7501_up(", "G", [(None, r"if \(rs64_s7501_on\) rs64_s7501_up")], "s7501 argument only (needle at line start: censuses truncate site text to 140 chars)"),
    (RDP, "rs64SkipDraw", None, "G", [(None, r'getenv\("ROGUESQ_SKIP_DRAW"\)'), (None, r"__builtin_expect\(g_rs64SkipDrawArmed, 0\) && rs64SkipDrawSlow")],
     "ROGUESQ_SKIP_DRAW slow path / rs64LoadRepCensus (attributed to the inline gate above them)"),
    # --- librecomp
    ("lib/N64ModernRuntime/librecomp/src/cont.cpp", "rs64_pak_row", None, "G", [(None, r"if \(rs64_pak_log\(\)\) rs64_pak_row"), (None, r"ch >= 0 && ch < 4")],
     "ROGUESQ_LOG_PAK_SHAPE log row; channel checked 0..3"),
    ("lib/N64ModernRuntime/librecomp/src/overlays.cpp", "rs64_s7528_post_load", "a < (uint32_t)ram + ns.size", "D", [(None, r'fprintf\(stderr, "\[s7528\] post idx')],
     "default-on one log row per overlay load; ram is the KSEG0 section base, size < 8 MB: no wrap; count is only printed"),
    # --- dpc_bridge
    ("src/rsp/dpc_bridge.cpp", "rs64_spike_scan", "(int32_t)(w0 << 18)", "K", [("CMakeLists.txt", r"set\(CMAKE_CXX_STANDARD 20\)")],
     "default-on spike scan: 14-bit RDP y field sign-extension; C++20 defines the conversion and >>; |y4| < 2^13"),
    ("src/rsp/dpc_bridge.cpp", "rs64_spike_scan", "dl * (yl4 - ym4)", "K", [(None, r"const int32_t yl4 = \(\(int32_t\)\(w0 << 18\)\) >> 18")],
     "differences of 14-bit sign-extended y values (|d| < 2^14), products in int64"),
    ("src/rsp/dpc_bridge.cpp", "rs64_s7634_nullwalk", None, "G", [(None, r"if \(s7634null\) \{ rs64_s7634_nullwalk"), (None, r'getenv\("ROGUESQ_S7634_NULLWALK"\)')],
     "ROGUESQ_S7634_NULLWALK"),
    ("src/rsp/dpc_bridge.cpp", "rsp_dpc_submit_impl", "if (rstat) for (uint32_t x = r.first", "G", [(None, r'getenv\("ROGUESQ_G1E_RSTAT"\)')], "ROGUESQ_G1E_RSTAT"),
    # --- instrument-only files
    ("src/rsp/s7389_fbld.cpp", "*", None, "G", [("CMakeLists.txt", r'option\(ROGUESQ_FB_LDWATCH "[^"]*" OFF\)'), (None, r"nothing calls rs64_fbld_hit")],
     "built only with -DROGUESQ_FB_LDWATCH=ON (default OFF), then ROGUESQ_S7389_FBLD"),
    ("src/main/s7391_spwm.cpp", "*", None, "G", [("CMakeLists.txt", r'option\(ROGUESQ_SP_WATCH "[^"]*" OFF\)'), (None, r"nothing calls rs64_spwm_new")],
     "built only with -DROGUESQ_SP_WATCH=ON (default OFF), then ROGUESQ_S7391_SPWM"),
    ("src/rsp/s7523_slow_rdp.cpp", "*", None, "G", [(None, r'getenv\("ROGUESQ_S7523_SLOWRDP"\)'), ("src/rsp/dpc_bridge.cpp", r"if \(rs64_s7523_on\) rs64_s7523_task")],
     "every entry behind rs64_s7523_on (ROGUESQ_S7523_SLOWRDP)"),
    ("src/rsp/s7521_ucode_watch.cpp", "*", None, "G", [(None, r'getenv\("ROGUESQ_S7521_UCODEWATCH"\)'), ("librecomp/rsp.hpp", r"if \(rs64_s7521_on\) rs64_s7521_imem")],
     "entries behind rs64_s7521_on (ROGUESQ_S7521_UCODEWATCH)"),
    ("src/rsp/s7535_ga_chk.cpp", "*", None, "G", [(None, r'getenv\("ROGUESQ_S7535_GA_CHK"\)'), ("ultramodern/src/events.cpp", r"if \(rs64_s7535_on\) rs64_s7535_snap")],
     "entries behind rs64_s7535_on (ROGUESQ_S7535_GA_CHK)"),
    ("src/rsp/s7702_fbread.cpp", "*", None, "G", [(None, r'getenv\("ROGUESQ_S7702_FBREAD"\)'), ("src/rsp/dpc_bridge.cpp", r"if \(rs64_s7702_on\) rs64_s7702_rdp"),
     ("src/rsp/s7094_dma_shape.cpp", r"if \(rs64_s7702_on && !\(mem & 0x1000\)\) rs64_s7702_dma")],
     "s7707: both entries behind rs64_s7702_on (ROGUESQ_S7702_FBREAD, default off); history/hit tables index-bounded (16/256/32)"),
    ("rt64_state.cpp", "rs64_lookup_image_word", "0xF83FF83Fu", "G", [(None, r'getenv\("ROGUESQ_S7704_POISON"\)'), (None, r"if \(b1 <= 0x1000000u\) \{")],
     "s7707: s7704 magenta poison inside fullSync (census attributes it to rs64_lookup_image_word), ROGUESQ_S7704_POISON=<width> (default 0 = off); span b0..b1 < 16 MB RDRAM"),
    ("src/rsp/s7644_rspdma.cpp", "*", None, "G", [(None, r'getenv\("ROGUESQ_S7644_RSPDMA"\)')], "ROGUESQ_S7644_RSPDMA; gsum is a log row"),
    ("src/rsp/s7751_task_snap.cpp", "*", None, "G", [(None, r'getenv\("ROGUESQ_S7751_SNAP"\)'), (None, r"if \(!dir\(\) \|\| g_cur < 0\) return;"),
     ("src/rsp/dpc_bridge.cpp", r"if \(s7751\) rs64_s7751_rdp"), (None, r"if \(ep <= sp \|\| ep > kRam\) return;")],
     "s7751 gfx task snapshot for the cxd4 replay, every entry returns on !dir() (ROGUESQ_S7751_SNAP, default off); RDRAM copy is the "
     "fixed 16 MB RSP DMA window kRam, inside the 512 MB mapping; rdp index a < ep <= kRam"),
    # --- G6c stand-ins (opt-in ROGUESQ_STANDINS)
    (SI, "bk_ret_impl", "dy + dz", "FLT", [(None, r"const float dx = rf\(rdram, s\.state\) - x, dy = rf\(rdram, s\.state \+ 4u\) - y, dz")],
     "s7672 handoff: float squared distance between stand-in and real object (dx/dy/dz are const float)"),
    (SI, "find_model", "(sum % 25u) * 2u", "K", [(None, r'getenv\("ROGUESQ_STANDINS"\)')], "hash index < 25 halfwords into the game's 25-entry model hash"),
    (SI, "build_state", "rf(rdram, item + 0x28u) / rf(rdram, model + 0x34u)", "FLT", [(None, r'getenv\("ROGUESQ_STANDINS"\)')],
     "IEEE float division, the game's own scale formula"),
    (SI, "rebuild", "inst + 0x1000u > kRegionEnd", "K", [(None, r"if \(inst \+ 0x1000u > kRegionEnd\) break;")], "inst < kRegionEnd (guest KSEG0), + 4 KB cannot wrap"),
    (SI, "?", "v >> (24 - 8 * i)", "K", [(None, r"v >> \(24 - 8 \* i\)")], "w32 byte loop i = 0..3: shifts 24..0"),
    (SI, "mips_call", "if (i < 12)", "K", [(None, r"if \(i < 12\) ww\(rdram")], "at most 12 stack args, 4u * i <= 44"),
    ("src/main/rs64_apf.h", "rs64_apf", "std::vsnprintf(b + o, cap - (size_t)o", "K", [(None, r"if \(\(size_t\)o >= cap - 1\) \{ b\[cap - 1\] = 0;")],
     "the bounded-append helper itself: o < cap - 1 checked first"),
    # --- rt64_render_context.cpp gb:: (s7539) helpers, attributed to map_result
    ("src/main/rt64_render_context.cpp", "map_result", "(start + r * stride) & 0xFFFFFFu", "G", [(None, r'getenv\("ROGUESQ_S7539_GB_CHK"\)')],
     "gb::rows_cmp (ROGUESQ_S7539_GB_CHK); end clamped to SZ"),
    ("src/main/rt64_render_context.cpp", "map_result", "std::memcpy(snap[i], rdram, SZ)", "G", [(None, r"if \(gb::on\) \{ RT64::Application \*a")],
     "gb::at_exit snapshot, called under gb::on; snap buffers are SZ bytes"),
    ("src/main/rt64_render_context.cpp", "map_result", "(const uint32_t *)snap[b]", "G", [(None, r'getenv\("ROGUESQ_S7539_GB_CHK"\)')], "gb:: word compare"),
    ("src/main/rt64_render_context.cpp", "rs64_s7539_load", None, "G", [(RDP, r"if \(rs64_s7539_on\) rs64_s7539_load"), (None, r'getenv\("ROGUESQ_S7539_GB_CHK"\)')],
     "RT64 callers gated on rs64_s7539_on (ROGUESQ_S7539_GB_CHK); copies are 4-byte words into uint32_t locals / gb::snap"),
    ("src/main/rt64_render_context.cpp", "rs64_s7541_span", None, "G", [(None, r"if \(!gb::on \|\| !rdram \|\| !bytes \|\| kind < 0 \|\| kind > 4\) return;"),
     (None, r"if \(\(uint64_t\)addr \+ bytes > gb::SZ\) bytes = gb::SZ - addr;")], "returns unless gb::on; span clamped to gb::SZ"),
    ("src/main/rt64_render_context.cpp", "map_result", "RT64::Application *a = g_rt64_app.load()", "PTR", [(None, r"RT64::Application \*a = g_rt64_app\.load\(\)")],
     "pointer declaration, not a product"),
]

_hits = {}

def lookup(rel, fn, text):
    """(class, reason) of the first rule covering this site, or None."""
    for i, (f, rf, needle, c, _a, why) in enumerate(RULES):
        if str(rel).endswith(f) and (rf == "*" or rf == fn) and (needle is None or needle in text):
            _hits[i] = _hits.get(i, 0) + 1
            return c, "s7654 rule: " + why
    return None

def _find(suffix):
    if (ROOT / suffix).exists(): return ROOT / suffix
    for base in ("src", "lib", "."):
        for p in (ROOT / base).rglob(pathlib.Path(suffix).name):
            if str(p).endswith(suffix) and "/build" not in str(p): return p
    return None

def _ln_fn(path):
    s = importlib.util.spec_from_file_location("s43r", ROOT / "tools/s7343_buffer_copy_census.py")
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m.ln_fn(path)

def check(rules=None):
    """STALE rows: rules whose file, function, needle or anchor no longer exists. Empty = every rule re-proved."""
    out, cache = [], {}
    for (f, rf, needle, c, anchors, why) in (RULES if rules is None else rules):
        p = _find(f)
        if p is None: out.append(f"STALE {f} {rf}: file missing"); continue
        if p not in cache: cache[p] = _ln_fn(p)
        lines, fns = cache[p]
        if rf != "*":
            mine = [lines[i] for i, (n, _s) in enumerate(fns) if n == rf]
            if not mine: out.append(f"STALE {f} {rf}: function not attributed any more"); continue
            if needle is not None and not any(needle in l for l in mine):
                out.append(f"STALE {f} {rf}: needle {needle!r} in no line of the function"); continue
        for (af, rx) in anchors:
            ap = p if af is None else _find(af)
            if ap is None or not re.search(rx, ap.read_text(errors="replace")):
                out.append(f"STALE {f} {rf}: anchor {rx!r} not in {af or f}")
    return out

def report(tag):
    """print STALE rows; return them (callers add them to `bad`)."""
    st = check()
    for s in st: print(f"  [{tag}] {s}")
    print(f"[{tag}] s7654 shared rules {len(RULES)} re-proved, stale {len(st)}, applied {sum(_hits.values())}")
    return st

def controls():
    """planted stale anchor and planted stale needle must both be STALE; a live rule must not be."""
    live = [r for r in RULES if r[1] == "rs64_bind_poll"]
    bad_anchor = [(live[0][0], live[0][1], live[0][2], "K", [(None, r"keycopy\[SDL_NUM_SCANCODES_PLANTED\]")], "ctl")]
    bad_needle = [(live[0][0], live[0][1], "min(s.nkeys_PLANTED", "K", [], "ctl")]
    ok = not check(live) and len(check(bad_anchor)) == 1 and len(check(bad_needle)) == 1 and \
        lookup("src/main/main.cpp", "rs64_bind_poll", "x std::min(s.nkeys, (int)SDL_NUM_SCANCODES) y") is not None and \
        lookup("src/main/main.cpp", "rs64_bind_poll", "memcpy(keycopy, s.keys, s.nkeys)") is None
    return ok

if __name__ == "__main__":
    import sys
    st = report("census_rules")
    c = controls(); print(f"[census_rules] controls {'PASS' if c else 'FAIL'} (live rule clean, planted anchor+needle STALE, unclamped twin not covered)")
    sys.exit(1 if st or not c else 0)
