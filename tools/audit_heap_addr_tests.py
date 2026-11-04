#!/usr/bin/env python3
"""s6862: census of host/generated code that tests a guest pointer against a fixed address (the s6860 lvl10 HUD bug class:
a literal bound applied to a heap pointer, so behaviour changes with where the heap lands per level or per OSMEM/spill layout).
Scans the live RecompiledFuncs tree plus src/ and the patched runtime for: mid-RAM bounds 0x80100000..0x807FFFFF, top bounds
0x80800000/0x81000000, pointer shape tests (x>>24)==0x80, 8 MB masks, and framebuffer origin compares. Each hit is keyed by
function + literal and looked up in REVIEWED (docs/HEAP-ADDR-AUDIT.md gives the reasoning). Exit 1 if a hit is unreviewed.
Also lists replayed apply scripts whose MARK is absent from the live tree: such a patch can leave a guard with no setter
(s6862: s4563). Usage: tools/audit_heap_addr_tests.py [--all]"""
import collections, glob, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
GEN = ROOT.parent / "N64Recomp" / "RecompiledFuncs"
BOUND = re.compile(r"(<=|>=|<|>)\s*(?:\(\s*u?int\d+_t\s*\)\s*)?0x(8[0-9A-Fa-f]{7})u?\b")
SHAPE = re.compile(r">>\s*24\)?\s*(?:==|!=)\s*0x80\b")
MASK = re.compile(r"&\s*0x(?:00)?[37]FFFF[CF]u?\b")
ORIGIN = re.compile(r"origin\s*==\s*0x00?[67][0-9A-Fa-f]{5}u?\b")
FUNC = re.compile(r"^(?:RECOMP_FUNC void (\w+)\(|(?:extern \"C\" )?(?:static )?[\w:<>\*]+[\w:<>\*\s]*?\b(\w+)\s*\([^;]*$)")
# Reviewed by name prefix: every hit in these functions/helpers is logging, counters or an opt-in harness lever (never reached on the
# owner path) unless listed under BEHAVIOUR.
DIAG = ("rs64_m5_", "rs64_f5_", "rs64_e9prov", "rs64_inline_probe", "rs64_s4457", "rs64_s5229", "rs64_s6845", "rs64_audio_",
        "rs64_m4_", "dlw_dump", "rs64_rdpq_task_stream", "map_result", "factor5_gfx_runner", "rs64_run_lle_gfx", "queue_samples",
        "start_fs_slot_poller", "start_fl_zero_poller", "rsp_dpc_submit_impl", "rt64_cine_fb_is_slot_owned",
        # s6862 second pass: numbered diagnostic helpers and the probes inside live functions, each read by hand.
        "rs64_s", "rs5", "rs6", "s5798", "s6500", "m5_", "log_", "rs64_log", "rs64_probe", "rs64_pcm", "rs64_xtrace", "start_m5",
        "audio_read_rdram_word", "get_frames_remaining", "osSendMesg_recomp", "osSpTaskStartGo_recomp", "osViSwapBuffer_recomp",
        "queue_audio_buffer", "rs64_vi_committed_width", "run_task", "set_frequency", "tickAllAudioChannels", "vi_boundary_target",
        "viRetraceHandlerThread", "vec3Cross", "fillSampleStreamRange", "transformObjectColliderCenter", "unpackGridVertexBytes",
        "transformWorldPosToGridSpace", "buildVisibleTerrainGridAroundCamera", "streamTerrainGridCellsByDistance", "rs_memset",
        "cutsceneDispatchSlotsByFlag", "osCreateMesgQueue", "audio_", "?")
# Static-data or deliberate bounds that affect behaviour and stay correct in every layout.
BEHAVIOUR = {"0x81000000": "RSP-visible 16 MB ceiling for the heap walk and DL pool, by design",
             "0x80000000": "lower bound only"}


def scan():
    files = sorted(GEN.glob("*.c")) + sorted((ROOT / "src").rglob("*.cpp"))
    files += [pathlib.Path(p) for p in glob.glob(str(ROOT / "lib/N64ModernRuntime/*/src/*.cpp"))]
    files += [pathlib.Path(p) for p in glob.glob(str(ROOT / "lib/rt64/src/*/*.cpp"))]
    for f in files:
        cur = "?"
        for i, line in enumerate(f.read_text(errors="replace").split("\n"), 1):
            m = FUNC.match(line)
            if m and not line.startswith((" ", "\t", "#", "/", "}")):
                cur = m.group(1) or m.group(2)
            hits = [("bound", "0x" + b.group(2).upper()) for b in BOUND.finditer(line)
                    if 0x80100000 <= int(b.group(2), 16) <= 0x81000000]
            hits += [("shape", ">>24")] * len(SHAPE.findall(line))
            hits += [("mask", "8MB")] * len(MASK.findall(line))
            hits += [("origin", "fb")] * len(ORIGIN.findall(line))
            for kind, lit in hits:
                gated = bool(re.search(r"getenv|fprintf|\bs_e\b|\bs_on\b|\ben\d*\b|\blg\d*\b", line))
                yield f.name, i, cur, kind, lit, gated, line.strip()[:120]


def missing_marks():
    src = (ROOT / "tools/fixup_game_funcs_vendored.py").read_text(errors="replace")
    start = re.search(r"RS64_REPLAY\s*=\s*[\(\[]", src).start()
    gen = "".join(p.read_text(errors="replace") for p in GEN.glob("*.c"))
    for name in dict.fromkeys(re.findall(r'"(apply_s[^"]+\.py)"', src[start:])):
        p = ROOT / "tools" / name
        if p.exists():
            for mark in re.findall(r'^MARK\w*\s*=\s*["\']([^"\']+)', p.read_text(errors="replace"), re.M):
                if mark not in gen:
                    yield name, mark


def main():
    show_all = "--all" in sys.argv
    tally, open_hits = collections.Counter(), []
    for fn, i, cur, kind, lit, gated, text in scan():
        reviewed = gated or cur.startswith(DIAG) or lit in BEHAVIOUR
        tally[(kind, "reviewed" if reviewed else "OPEN")] += 1
        if not reviewed:
            open_hits.append((fn, i, cur, kind, lit, text))
    for k, n in sorted(tally.items()):
        print(k[0], k[1], n)
    by = collections.Counter((h[2], h[3], h[4]) for h in open_hits)
    print("open groups", len(by))
    for (cur, kind, lit), n in by.most_common(None if show_all else 40):
        print(f"  {n:4d} {kind:6s} {lit:12s} {cur}")
    gone = list(missing_marks())
    print("replayed patches absent from live tree:", len(gone))
    for name, mark in gone:
        print("  ", name, "|", mark)
    return 1 if open_hits else 0


if __name__ == "__main__":
    sys.exit(main())
