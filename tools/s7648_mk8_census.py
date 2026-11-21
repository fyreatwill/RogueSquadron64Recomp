#!/usr/bin/env python3
"""s7648 class MK8 census: 8 MB physical-address masks (& 0x7FFFFF / 0x007FFFFF), phys end checks (0x800000, host) and 0x807Fxxxx near-variant guest bounds.
At dd>1 (OSMEM 12, DLPOOLX, spill arena) guest data lives at phys >= 8 MB, so an 8 MB mask ALIASES it onto low RAM and a
0x807Fxxxx bound REJECTS it. s7647 lost a lead to one such aliasing key (TS-4). s7337_bound_census.py closed class R
(0x80800000 literals) but only counted masks ("class M, open") and its generated-tree pattern misses 0x807Fxxxx.

Scopes:
  H  host sources (src/, lib/ N64ModernRuntime + rt64 non-third-party): every 8 MB mask outside a printf line.
  G  generated tree (RecompiledFuncs/funcs_*.c, build/factor5_ucode/*.c): masks and 0x807Fxxxx bounds.
Each site is classed D (inside an env-gated / diagnostic function or patch block), F (float mantissa mask, not an
address), or listed UNCLASSIFIED. Exit 1 on any unclassified site, so a new default-on 8 MB key fails the census.
--controls plants one ungated mask and one ungated generated bound in temp copies and requires both to be flagged.
s7650: host attribution is brace-aware (fn_spans): a site belongs to the innermost definition whose braces contain it;
a site in no definition is UNATTRIBUTED and needs a DIAG_SITE entry. --diff lists sites whose function changed vs the
s7648 backward scan.
Usage: s7648_mk8_census.py [--funcs DIR] [--controls] [--diff] [-v]"""
import re, sys, pathlib, tempfile, shutil
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

ROOT = pathlib.Path(__file__).resolve().parents[1]
FUNCS = ROOT.parent / "N64Recomp" / "RecompiledFuncs"
UCODE = ROOT / "build" / "factor5_ucode"
HOST = ["src/main/*.cpp", "src/rsp/*.cpp", "lib/N64ModernRuntime/ultramodern/src/*.cpp",
        "lib/N64ModernRuntime/librecomp/src/*.cpp", "lib/rt64/src/hle/*.cpp", "lib/rt64/src/hle/*.h",
        "lib/rt64/src/gbi/*.cpp", "lib/rt64/src/render/*.cpp"]
MASK = re.compile(r"0x(?:00)?7FFFFF(?:u|ull|ULL)?\b(?!F)", re.I)
END = re.compile(r"0x(?:00)?800000(?:u|ull|ULL)?\b(?![0-9A-F])", re.I)  # phys 8 MB end checks (host scope)
NEAR = re.compile(r"0x807F[0-9A-F]{4}(?:u|ull|ULL)?\b", re.I)
FLOAT = re.compile(r"0x7F800000u")
FN = re.compile(r'^(?:extern "C"\s+|static\s+|inline\s+|__attribute__\(\([^)]*\)\)\s+)*[A-Za-z_][\w:<>\*\s]*?\b([A-Za-z_]\w*)\s*\([^;]*$')
DIAG = re.compile(r"getenv|ROGUESQ_|g_rs64_store_diag|_on\(\)|log_\w+\(\)|\benabled\b|\bif \(!en\b|dlwalk_on|g_inline_probe\.active")
# Hand-reviewed s7648: always-called host functions whose 8 MB key only feeds diagnostic state/prints (no behaviour).
# Each was read in full: the masked value is stored in a diag struct, printed, or used to index a diag-only table.
DIAG_FN = {
    "rs64_m5_pcm_writer_dma": "g_rs64_pcm_last_dma_phys: printed by [m5-pcm] rows only",
    "rs64_s4457_list_check": "s4457/s4779 audio-node shadow scan: prints only (arena 0x80179400 is < 8 MB anyway)",
    "rs64_s5229_store": "diag writer table, allocated only when the s5229 probe is armed; addr already < 0x80800000",
    "rs64_s5229_entry": "s5229 diag query (returns unless tables allocated)",
    "rs64_f5_vtxcolor_state": "g_f5_vtxcolor_state pc/source: read back only by RT64 shade-diag prints (rt64_gbi_rdp.cpp)",
    "rs64_e9prov_task_begin": "g_e9prov.root_dl: consumed by diag prints / gated probes only",
    "rs64_s7645_gfx_read": "s7644 RSP-DMA instrument; the 8 MB key is the deliberate s7647 alias CONTROL",
    "start_fl_zero_poller": "ROGUESQ_FL_ZERO_ADDR poller thread",
    "rs64_s6843_store": "rs64_vsrc_* census, active only when rs64_vsrc_hi is set by a log env",
    "s7779_b": "s7779 FB-arena census byte reader (returns 0 unless ROGUESQ_S7779_ARENA=1; caller rs64_s7779_note is gated)",
    "rs64_m5_audio_input_dma": "M5 audio input census (prints)",
    "rs64_m5_host_write_census": "rs64_vsrc_* census, active only when rs64_vsrc_hi is set by a log env",
    "rs64_m5_pcm_writer_snapshot": "M5 PCM writer table lookup for [audio-join] rows",
    "rs64_audio_hash_rdram": "FNV of an audio field for M5 rows (callers env-gated)",
    "rs64_inline_probe_trigen_stage": "inline-probe diag atomics",
    "dlw_dump_words": "[dlwalk-zero] dump",
    # librecomp rsp.cpp M5 audio join / probe instruments: callers gated by probe_audio / rs64_s4208_active / LOG envs,
    # or read-only per-audio-task hashing of low-RAM audio structures (rs64_s4211_task)
    "audio_join_match": "M5 audio join", "audio_image_match": "M5 audio join", "audio_image_match_pcm_locked": "M5 audio join",
    "rs64_audio_join_image_stage": "M5 audio join", "rs64_audio_join_image_source": "M5 audio join",
    "rs64_audio_join_image_dma": "M5 audio join", "audio_dma_overlaps": "M5 audio probe (probe_audio rows)",
    "audio_hash_rdram": "M5 audio probe", "audio_read_rdram_word": "M5 audio probe field_pre/post",
    "rs64_s4209_read": "s4209 read ring (diag)", "rs64_s4211_task": "s4211 read-only dp hash census",
    "rs64_probe_audio_dma_write": "s4208 ring (rs64_s4208_active)", "rs64_s4214_scan": "ROGUESQ_LOG_S4213",
}
DIAG_FN.update({
    "rs64_filter_voice_guest_span_ok": "ROGUESQ_LOG_FILTER_VOICE_AUDIT rows only",
    "rs64_filter_voice_guest_hash": "ROGUESQ_LOG_FILTER_VOICE_AUDIT rows only",
    "nz_words": "s7391 SP write-watch instrument", "rs64_fill_note_hi": "fill-note diag (counts >8 MB fills)",
    "rs64_g1d_blk_unaligned": "G1d block diag (low-fill print budget)", "rs64_s7331_track": "rs64_s7331_on gated",
    "__osRdbSend_recomp": "rdb print size sanity (game never sends >8 MB)", "osSpTaskStartGo_recomp": "dump_frame RAM dump",
})
# Header constants (no enclosing function): RT64 RDRAMSize = 0x7FFFFF sizes only the debug RDRAM fwrite dump (rt64_state.cpp).
DIAG_LINE = {"const uint32_t RDRAMSize = 0x7FFFFF;"}
# s7650: unattributed / re-attributed sites classified by hand: (file name, stripped line) -> reason.
DIAG_SITE = {
    ("rt64_render_context.cpp", "auto b = [R](uint32_t a) { return (unsigned)R[(a & 0x7FFFFF) ^ 3]; };"):
        "s6835 [stall-dump] fprintf of arbiter/queue words (fires only after STALL_VI VIs with no fullsync, max 8)",
    ("rt64_render_context.cpp", "const uint32_t ta = s_ti_w1 & 0xFFFFFFu, ta8 = s_ti_w1 & 0x7FFFFFu;"):
        "[g1d-tex] inside if (s_cmd_log) (LOG_G1D_CMD); ta8 = printed old key (s7649)",
    ("rt64_render_context.cpp", "rs64_e9prov_current_root_dl() & 0x7FFFFFu,"): "[g1d-cmd] fprintf arg inside if (s_cmd_log)",
    ("dpc_bridge.cpp", "if (x > 0 && x < 0x800000u) a = (uint32_t)x;"):
        "fs_slot_addr (ROGUESQ_FS_SLOT_ADDR parse): read only under log_fs_slot() or opt-in ROGUESQ_FS_PIPE_INJECT",
    ("dpc_bridge.cpp", "return a & 0x7FFFFFu;"): "fs_slot_addr, same (default slot 0x76DF60 < 8 MB)",
    ("rt64_gbi_f3dfactor5.cpp", "if (phys < 0x800000u) {"): "[gbi-f5] byte dump inside if (gbi_log_enabled())",
    ("rt64_gbi_f3dfactor5.cpp", "uint8_t b = rdram[((phys + i) ^ 3) & 0x7FFFFFu];"): "[gbi-f5] byte dump, same block",
    ("rt64_gbi_f3dfactor5.cpp", "s_oddN, ow, fmt, siz, w0, w1, off, (off >= 0 && off < 0x800000) ? 1 : 0);"):
        "s5714 [cimg-odd] fprintf arg (in= flag only)",
    ("rt64_gbi_rdp.cpp", "const uint32_t shadeDl = state->displayListAddress & 0x7FFFFFu;"):
        "shadeDl feeds rs64_shade_ordinal only when shadeDiagOn and three fprintf rows (lines ~761/778/1263)",
}
GEN_TAG = re.compile(r"PATCH: (s\d+)|rs(?:64_s)?(\d{4})_")
# Generated-tree patch tags hand-reviewed s7648: opt-in or diag (the guarded block is env/enabled-gated).
GEN_OK = {"s4204", "s4207", "s4208", "s4209", "s6363", "6660", "6663", "s6660", "s6663", "s4208"}


def enclosing(lines, i):
    """s7648 attribution (legacy, kept for --diff): nearest column-0 FN match above line i, no brace check."""
    for j in range(i, -1, -1):
        l = lines[j]
        if l and not l[0].isspace() and not l.startswith(("if", "for", "while", "return", "}", "#", "//")):
            m = FN.match(l)
            if m:
                return m.group(1), j
    return "?", 0


from census_attr import HEAD, KW, _clean, fn_spans, enclosing_braced  # s7651: shared module


def host_sites(files, diff=None):
    out = []
    for f in files:
        L = pathlib.Path(f).read_text(errors="replace").split("\n")
        S = None
        for i, l in enumerate(L):
            if not (MASK.search(l) or END.search(l)) or "printf" in l or l.strip().startswith("//"):
                continue
            if FLOAT.search(l):
                out.append(("F", f, i + 1, "-", l)); continue
            if S is None:
                S = fn_spans(L)
            fn, j = enclosing_braced(S, i)
            if diff is not None:
                ofn, _ = enclosing(L, i)
                if ofn != fn:
                    diff.append((f, i + 1, ofn, fn))
            body = "\n".join(L[j:i + 1]) if j is not None else l
            key = (pathlib.Path(f).name, l.strip())
            if j is not None and DIAG.search(body):
                cls = "D"
            elif fn in DIAG_FN or l.strip() in DIAG_LINE or key in DIAG_SITE:
                cls = "D*"
            else:
                cls = "?"
            out.append((cls, f, i + 1, fn, l))
    return out


def gen_sites(files):
    out = []
    for f in files:
        L = pathlib.Path(f).read_text(errors="replace").split("\n")
        for i, l in enumerate(L):
            if not (MASK.search(l) or NEAR.search(l)) or "printf" in l:
                continue
            if FLOAT.search(l):
                out.append(("F", f, i + 1, "-", l)); continue
            ctx = "\n".join(L[max(0, i - 120):i + 1])
            tags = {a or b for a, b in GEN_TAG.findall(ctx)}
            tags |= {"s" + t for t in tags if not t.startswith("s")}
            cls = "D" if (tags & GEN_OK and re.search(r"\benabled\b|\ben\b|getenv|ROGUESQ_|rs6660_ok|rs64_s4204_ok", ctx)) else "?"
            out.append((cls, f, i + 1, ",".join(sorted(tags))[:40], l))
    return out


def run(funcs, verbose=False, host_extra=(), gen_extra=(), show_diff=False):
    hf = [str(p) for g in HOST for p in sorted(ROOT.glob(g)) if "third_party" not in str(p) and "contrib" not in str(p)]
    gf = sorted(str(p) for p in pathlib.Path(funcs).glob("funcs_*.c")) + sorted(str(p) for p in UCODE.glob("*.c"))
    dl = []
    H = host_sites(list(hf) + list(host_extra), dl)
    if show_diff:
        print(f"[s7650] attribution changes vs s7648 backward scan: {len(dl)}")
        for f, ln, o, n in dl:
            print(f"  {pathlib.Path(f).relative_to(ROOT) if str(f).startswith(str(ROOT)) else f}:{ln} {o} -> {n}")
    G = gen_sites(list(gf) + list(gen_extra))
    bad = [s for s in H + G if s[0] == "?"]
    for scope, S in (("H", H), ("G", G)):
        c = {}
        for s in S:
            c[s[0]] = c.get(s[0], 0) + 1
        print(f"[s7648] {scope} sites={len(S)} " + " ".join(f"{k}={v}" for k, v in sorted(c.items())))
    for s in (H + G if verbose else bad):
        print(f"  {s[0]:2} {pathlib.Path(s[1]).relative_to(ROOT) if str(s[1]).startswith(str(ROOT)) else s[1]}:{s[2]} [{s[3]}] {s[4].strip()[:110]}")
    print(f"[s7648] unclassified={len(bad)}")
    return bad


def main():
    a = sys.argv[1:]
    funcs = a[a.index("--funcs") + 1] if "--funcs" in a else FUNCS
    if "--controls" in a:
        d = pathlib.Path(tempfile.mkdtemp(prefix="s7648ctl"))
        try:
            h = d / "ctl_host.cpp"; g = d / "funcs_ctl.c"
            h.write_text('extern "C" uint32_t rs64_ctl_key(uint32_t a) {\n    return a & 0x7FFFFFu;\n}\n')
            g.write_text('static int ok(uint32_t a) {\n    return a >= 0x80000000u && a < 0x807FFF00u;\n}\n')
            # s7650 attribution control: an ungated mask in a class-body inline member (no column-0 head) placed right
            # after a gated function. The s7648 backward scan attributed it to the gated function (D); brace-aware
            # attribution must leave it UNATTRIBUTED and unclassified.
            u = d / "ctl_attr.cpp"
            u.write_text('static void ctl_gated(void) {\n    if (getenv("ROGUESQ_CTL")) { }\n}\nstruct CtlS {\n'
                         '    uint32_t key(uint32_t a) {\n        return a & 0x7FFFFFu;\n    }\n};\n')
            bad = run(funcs, host_extra=[str(h), str(u)], gen_extra=[str(g)])
            hit = {pathlib.Path(s[1]).name for s in bad}
            names = ("ctl_host.cpp", "funcs_ctl.c", "ctl_attr.cpp")
            n = sum(x in hit for x in names)
            L = u.read_text().split("\n")
            legacy = enclosing(L, 5)[0]
            okc = n == 3 and legacy == "ctl_gated"
            print(f"[s7648] controls planted=3 flagged={n} (attr ctl legacy fn={legacy} -> braced "
                  f"{enclosing_braced(fn_spans(L), 5)[0]}) {'PASS' if okc else 'FAIL'}")
            sys.exit(0 if okc else 1)
        finally:
            shutil.rmtree(d)
    sys.exit(1 if run(funcs, "-v" in a, show_diff="--diff" in a) else 0)


if __name__ == "__main__":
    main()
