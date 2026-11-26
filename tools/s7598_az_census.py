#!/usr/bin/env python3
"""s7598 class AZ: host allocations whose SIZE can derive from guest data (guest RAM words, RDP/RSP command fields, VI
registers, DMA lengths) in shipped host code.

Scope: src/, librecomp/src, ultramodern/src, lib/rt64/src (skips tests/tools/contrib/examples/demos), // comments stripped.
Kinds:
  alloc   std::vector/string resize/reserve/assign, new T[...], malloc/calloc/realloc
  gputex  device->createTexture(...)  (Metal newTexture fails past 16384 per side / on a huge commit)
Verdict prefixes: const (fixed size), bounded (guest-derived but clamped; the clamp is named), host (size from host/file/ROM
data, not runtime guest state), gated (env-gated diagnostic off in the owner recipe), fixed (this class's fix).
Every site must match a ROW (file, kind, line substring) or a FILE rule, else OPEN.
--controls: (1) plant an unclamped `resize(guest_word)` into a copy of rt64_rdp.cpp, (2) drop one row; both must report
OPEN; (3) the AZ-1 clamp line must be present in rt64_rdp.cpp. Exit 0 only if 0 open + 0 stale + 3/3 controls.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRS = ["src", "lib/N64ModernRuntime/librecomp/src", "lib/N64ModernRuntime/ultramodern/src", "lib/rt64/src"]
SKIP = re.compile(r"/(tests?|tools|contrib|examples?|demos?)/")
EXT = (".cpp", ".cc", ".c", ".h", ".hpp", ".mm")
KINDS = [
    ("alloc", re.compile(r"\.(resize|reserve|assign)\(|\bnew [A-Za-z_:<>]+\[|\b(malloc|calloc|realloc)\(")),
    ("gputex", re.compile(r"->createTexture\(")),
]
G = "gated: env-gated diagnostic, off in the owner recipe"
FB = "bounded: FramebufferManager::get refuses width>1280 or a range past 16 MB; heights from 10.2 rect coords (<=1024)"
RT = "bounded: computeScaledSize/std::clamp to RenderTarget::MaxDimension 0x4000 of an FB that passed the get() caps"
FILES = {  # every site in the file shares one verdict
    "librecomp/src/mods.cpp": "host: mod .nrm/manifest/regenlist sizes (no mods shipped; class XC covers the scan)",
    "librecomp/src/mod_manifest.cpp": "host: mod zip/file sizes",
    "librecomp/src/mod_hooks.cpp": "host: hook slot count from the recompiled mod tables",
    "librecomp/src/mod_events.cpp": "host: event count from the recompiled tables",
    "librecomp/src/patcher.cpp": "host: BPS patch sizes from a patch file (none shipped)",
    "librecomp/src/euc-jp.cpp": "host: string conversion of a host string",
    "rt64/src/hle/rt64_game_frame.cpp": "bounded: host workload vectors sized by draw/transform/scene counts of one frame (DL length capped by ROGUESQ_UCODE_CAP)",
    "rt64/src/render/rt64_raster_shader.cpp": "host: pipeline thread pool size",
    "rt64/src/common/rt64_profiling_timer.cpp": "const: profiler history",
    "rt64/src/common/rt64_filesystem.h": "host: file size of a host file",
    "rt64/src/preset/rt64_preset_draw_call.cpp": "const: 8 hashes",
    "rt64/src/render/rt64_framebuffer_renderer.cpp": "const/host: fixed reserves, dummy targets, textureCacheSize descriptor table",
    "rt64/src/render/rt64_buffer_uploader.cpp": "host: format view count",
    "rt64/src/hle/rt64_workload_queue.cpp": "host: interpolated frame count from the user FPS config",
    "rt64/src/hle/rt64_present_queue.cpp": "host: swap-chain texture count",
    "rt64/src/render/rt64_render_target.cpp": "bounded: target dims come only from resize()/computeScaledSize clamped to MaxDimension (rows framebuffer_manager)",
}
ROWS = {
    ("src/main/rs64_owner_text.h", "alloc", "if (nl != std::string::npos) v.resize(nl);"): "bounded: s7959 shrinks to the first newline (nl < size); the only caller (audio_route_load_pref) caps the file text at 4096 bytes",
    # src/ diagnostics
    ("src/rsp/s7097_edit_census.cpp", "alloc", "g_s0.assign(rd + g_glo"): G,
    ("src/rsp/dpc_bridge.cpp", "alloc", "s_shw.resize(nw); s_sop.assign(nw, 0xFF)"): "gated: s7635 fused=2/3 (ROGUESQ_S7634_FUSE=chk|inj) only; default 1 and 0 return above; nw = words of one bridge walk range [lo, hi)",
    ("src/rsp/s7644_rspdma.cpp", "alloc", "t_g.buf.resize(m)"): "gated: ROGUESQ_S7644_RSPDMA&2 (gfx_pi_pre returns on !g_gon); m clamped to 0x200000 one line above",
    ("src/rsp/s7751_task_snap.cpp", "alloc", "s.ram.resize(kRam)"): "gated: ROGUESQ_S7751_SNAP (task_begin returns on !dir()); const kRam = 16 MB, 3 slots",
    ("src/rsp/s7535_ga_chk.cpp", "alloc", "g_sh.resize(kSpHi + 8u)"): "const: SP range constant",
    ("src/main/s7391_spwm.cpp", "alloc", "t_snap.resize((top - bot) / 4)"): "bounded: top-bot <= 0x4000 checked just above; gated stack watermark",
    ("src/rsp/dpc_bridge.cpp", "alloc", "k.reserve(g_bc_sh.size())"): "host: size of a host map",
    ("src/rsp/dpc_bridge.cpp", "alloc", "g_f5_last_writer.resize(0x200000u)"): "const: 2M entries, once",
    ("src/rsp/dpc_bridge.cpp", "alloc", "frame_depths.resize(depth + 1)"): "gated: log_e9_provenance only; depth = slot/8 of a 32-bit slot word (unbounded but diagnostic-only)",
    ("src/rsp/dpc_bridge.cpp", "alloc", "q.ram.resize(kSubmitRamEnd)"): "gated: ROGUESQ_G5B_FRAME_TRIG ring, constant size",
    ("src/rsp/dpc_bridge.cpp", "alloc", "q.rng.resize(o + 12 + n)"): "gated: ROGUESQ_G5B_FRAME_TRIG; n = submit range hi-lo inside kSubmitRamEnd",
    ("src/rsp/dpc_bridge.cpp", "alloc", "shK.resize(cap)"): "host: power-of-two table cap",
    ("src/rsp/dpc_bridge.cpp", "alloc", "shIdx.reserve(g_s4272_sh.size())"): "host: size of a host table",
    ("src/rsp/dpc_bridge.cpp", "alloc", "wm_chk.assign(g_rdram_for_submit + wm_lo"): "gated: s_wm_chk watermark check, range inside RDRAM",
    ("src/rsp/dpc_bridge.cpp", "alloc", "uc_post.assign(g_rdram_for_submit + wm_lo"): "gated: uc_on census, same range",
    ("src/rsp/dpc_bridge.cpp", "alloc", "g_s4272_sh.reserve(g_bfsh_pk_sh * 2)"): "host: reserve from host peak counters (bfsh arm)",
    ("src/rsp/s7096_fwd_cover.cpp", "alloc", "snap.insert(snap.end(), rd + lo, rd + hi); else snap.resize"): G,
    ("src/rsp/s7331_reset_writer.cpp", "alloc", "b.copy.assign(mem.begin() + 0x100"): "const: 0x200 bytes",
    ("src/rsp/s7331_reset_writer.cpp", "alloc", "b->copy.assign(r + phys(ptr)"): "bounded: req <= 0x800000 and phys+req <= 0x1800000 checked above; gated rs64_s7331_on",
    ("src/main/rt64_render_context.cpp", "alloc", "snap[0] = (uint8_t *)std::malloc(SZ)"): "const: SZ, once",
    ("src/main/upstream_compat.cpp", "alloc", "std::calloc(0x1800000u >> 3, 1); if (g_rs64_s7475_bm)"): "const: 3 MB bitmap",
    ("src/main/upstream_compat.cpp", "alloc", "s_s7518_ln.assign(0x1800000u / 16u"): "const",
    ("src/main/upstream_compat.cpp", "alloc", "if (!g_rs64_s7475_bm) g_rs64_s7475_bm = (unsigned char*)std::calloc"): "const",
    ("src/main/upstream_compat.cpp", "alloc", "s_s7519_dt.assign(0x1800000u / 16u"): "const",
    ("src/main/upstream_compat.cpp", "alloc", "k.assign(cap, 0); v.assign(cap, 0)"): "host: power-of-two table cap",
    ("src/main/upstream_compat.cpp", "alloc", "m.reserve(1 << 16)"): "const",
    ("src/main/upstream_compat.cpp", "alloc", "rev.assign(1 << 16, 0)"): "const",
    ("src/main/main.cpp", "alloc", "g_s5229_pc = (uint32_t*)std::calloc(0x800000"): "const",
    ("src/main/main.cpp", "alloc", "s_s7783_g.assign(ext / 16u + 1u, 0)"): G + " (s7783 fb-shared-slot granules, ROGUESQ_S7779_ARENA; ext masked to 0x7FFFFF -> <=512 KB)",
    ("src/main/main.cpp", "alloc", "g_s5229_val = (uint8_t*)std::calloc(0x800000"): "const",
    ("src/main/main.cpp", "alloc", "g_s5229_w = (uint8_t*)std::calloc(0x800000"): "const",
    ("src/main/main.cpp", "alloc", "g_s4457_tab = (S4457W*)std::calloc(0x100000"): "const",
    ("src/main/main.cpp", "alloc", "s_sh2_buf.resize(sh2_size)"): "bounded: sh2_size const 0x82000, trimmed to 8 MB; gated s_sh2",
    ("src/main/main.cpp", "alloc", "img.reserve((size_t)R * C * 3)"): "host: contact-sheet image dims",
    ("src/main/main.cpp", "alloc", "g_s7501_ring.resize(kS7501Ring)"): "const",
    ("src/main/main.cpp", "alloc", "g_s7501_pg.resize(kS7501Pages)"): "const",
    ("src/main/main.cpp", "alloc", "s.snap.resize(s.bytes)"): "bounded: total of span bytes capped at 6 MB; gated s7551",
    ("src/main/main.cpp", "alloc", "t_pre.resize(bytes)"): "bounded: phys+bytes <= 16 MB checked above; gated s7551",
    ("src/main/main.cpp", "alloc", "g_shadow.assign(0x1000000u, 0)"): "const",
    ("src/main/main.cpp", "alloc", "std::malloc(16)"): "const: plant control",
    # librecomp / ultramodern
    ("librecomp/src/overlays.cpp", "alloc", "patch_data.resize(size)"): "host: ROM patch section size (static tables)",
    ("librecomp/src/overlays.cpp", "alloc", "patch_code_sections_by_rom.reserve"): "host: static table count",
    ("librecomp/src/overlays.cpp", "alloc", "calloc(sections_info.total_num_sections"): "host: static table count (s7356 null check)",
    ("librecomp/src/overlays.cpp", "alloc", "s7.offmap.resize"): "host: static table count",
    ("librecomp/src/overlays.cpp", "alloc", "s7.prevbad.resize"): "host: static table count",
    ("librecomp/src/recomp.cpp", "alloc", "ret.resize(static_cast<size_t>(size))"): "host: file size (s7357 tellg check)",
    ("librecomp/src/recomp.cpp", "alloc", "rom_data.resize((rom_data.size() + 3) & ~3)"): "host: ROM size",
    ("librecomp/src/rsp.cpp", "alloc", "task.ranges.reserve(probe.ranges.size())"): "host: probe range vector size",
    ("librecomp/src/rsp.cpp", "alloc", "audio_dma_probe.ranges.reserve(64)"): "const",
    ("librecomp/src/pi.cpp", "alloc", "save_buffer.resize(get_save_size"): "const: save type size",
    ("ultramodern/src/events.cpp", "alloc", "buf.reserve(8192)"): "const",
    # rt64 hle
    ("rt64/src/gbi/rt64_gbi_rdp.cpp", "alloc", "vec.resize(min_size + min_size / 2)"): "bounded: setMinSize callers pass DL-derived counts within one task (DL capped)",
    ("rt64/src/hle/rt64_framebuffer.cpp", "alloc", "nativeSwappedRAM.resize(nativeSize)"): "bounded: width<=1280 (get() cap) << siz<=3 >>1 * rowCount<=fb height -> <=10 MB",
    ("rt64/src/hle/rt64_framebuffer.cpp", "alloc", "fl_snap = (uint8_t *)malloc(fl_snap_n)"): "bounded: min(s_fl_walk_cap, rangeEnd-hdr); gated freelist restore",
    ("rt64/src/hle/rt64_framebuffer_manager.cpp", "alloc", "colorTarget.resize(renderWorker, rtWidth, rtHeight)"): RT,
    ("rt64/src/hle/rt64_framebuffer_manager.cpp", "alloc", "depthTarget.resize(renderWorker, rtWidth, rtHeight)"): RT,
    ("rt64/src/hle/rt64_framebuffer_manager.cpp", "gputex", "tileCopy.texture = renderWorker->device->createTexture"): "bounded: tileWidth/Height std::clamp to MaxDimension; fbTile from 10.2 tile coords",
    ("rt64/src/hle/rt64_framebuffer_manager.cpp", "gputex", "dstTile.texture = renderWorker->device->createTexture"): "bounded: dstTileWidth/Height clamped to MaxDimension (line 424)",
    ("rt64/src/hle/rt64_framebuffer_manager.cpp", "gputex", "dummyTLUTTexture"): "const",
    ("rt64/src/hle/rt64_framebuffer_changes.cpp", "gputex", "changes.pixelTexture"): "bounded: aligned dims of a render target (MaxDimension)",
    ("rt64/src/hle/rt64_framebuffer_changes.cpp", "gputex", "changes.booleanTexture"): "bounded: same",
    ("rt64/src/hle/rt64_framebuffer_storage.cpp", "alloc", "rdramData.resize(newSize, 0)"): "bounded: store() sizes are FB RAMBytes / readFbBytes inside the 16 MB range checks (fbsync-oob-skip); reset per workload",
    ("rt64/src/hle/rt64_interpreter.cpp", "alloc", "g_s4281_snap.assign"): "bounded: n = min(dl span, 0x40000)",
    ("rt64/src/hle/rt64_command_warning.cpp", "alloc", "warning.message.resize(size_t(reqSize))"): "host: vsnprintf length (s7346 negative check)",
    ("rt64/src/hle/rt64_state.cpp", "alloc", "out.reserve((b1 - b0) * s.height * 2)"): "gated: band writeback census; s from the VI FB that passed the 16 MB check",
    ("rt64/src/hle/rt64_state.cpp", "alloc", "drawData.rdpTiles.resize(requiredSize"): "bounded: tileCount <= 8 per draw call",
    ("rt64/src/hle/rt64_state.cpp", "alloc", "drawData.callTiles.resize(requiredSize"): "bounded: same",
    ("rt64/src/hle/rt64_state.cpp", "alloc", "gpuTiles.resize(workload.drawData.callTiles.size())"): "bounded: same",
    ("rt64/src/hle/rt64_state.cpp", "alloc", "present.storage.resize(screenFbBytes)"): "bounded: screenFbBytes = 0 when origin+bytes > 16 MB (s6130 line above)",
    ("rt64/src/common/rt64_common.h", "alloc", "vector.reserve(expectedSize * 2)"): "bounded: adjustVector callers pass per-frame host counts",
    ("rt64/src/common/rt64_common.h", "alloc", "vector.resize(expectedSize)"): "bounded: same",
    # rt64 render
    ("rt64/src/render/rt64_texture_cache.cpp", "alloc", "fileSystemStreamResolvedPaths.resize(fileSystemCount)"): "host: texture-pack filesystem count",
    ("rt64/src/render/rt64_texture_cache.cpp", "gputex", "Texture2D(width, height, 1, dstTexture->format)"): "host: texture-pack replacement image dims (no pack shipped)",
    ("rt64/src/render/rt64_texture_cache.cpp", "gputex", "dstTexture->texture = device->createTexture(desc)"): "host: DDS replacement dims",
    ("rt64/src/render/rt64_texture_cache.cpp", "gputex", "newTexture->texture = device->createTexture(textureDesc)"): "host: replacement texture desc",
    ("rt64/src/render/rt64_texture_cache.cpp", "gputex", "newTexture->tmem = copyWorker->device->createTexture"): "const: TMEM bytes (4096)",
    ("rt64/src/render/rt64_texture_cache.cpp", "gputex", "Texture2D(upload.width, upload.height"): "bounded: decodeTMEM only when !requiresRawTMEM (sample fits 4 KB TMEM) or >4096 sample shrunk to maxTexcoord (state.cpp FIXME block); plant witness masks=15 wrap: max upload 65x65, [s7598-bigtex] 0; AZ-1 mask clamp on top",
}
FIXED = ["AZ-1 s7598 (fidelity, not an allocation defect): RDP::setTile kept SETTILE masks/maskt 11-15 raw; hardware/angrylion "
         "clamp to 10 (tex.c masksclamped). Now clamped at setTile ([s7598-mask], ROGUESQ_S7598_MASK=0 = old)"]


def short(path):
    return path.replace("lib/N64ModernRuntime/", "").replace("lib/rt64/", "rt64/")


def census(plant=False, drop=None):
    rows = dict(ROWS)
    if drop: rows.pop(drop)
    seen, open_, counts = set(), [], {}
    for d in DIRS:
        for dp, _, fs in os.walk(os.path.join(ROOT, d)):
            for f in fs:
                p = os.path.join(dp, f); rel = os.path.relpath(p, ROOT)
                if not f.endswith(EXT) or SKIP.search("/" + rel): continue
                text = open(p, errors="replace").read()
                if plant and rel.endswith("hle/rt64_rdp.cpp"):
                    text = text.replace("        auto &t = tiles[tile];", "        static std::vector<uint8_t> pv; pv.resize(size_t(line) << 20); // planted_control\n        auto &t = tiles[tile];", 1)
                for ln, line in enumerate(text.split("\n"), 1):
                    code = re.sub(r"//.*", "", line) if "planted_control" not in line else line
                    bare = re.sub(r'"([^"\\]|\\.)*"', '""', code)
                    for kind, rx in KINDS:
                        if not rx.search(bare): continue
                        counts[kind] = counts.get(kind, 0) + 1
                        if short(rel) in FILES and "planted_control" not in line: seen.add(("FILE", short(rel))); continue
                        cands = [k for k in rows if k[0] == short(rel) and k[1] == kind and k[2] in code]
                        key = max(cands, key=lambda k: len(k[2])) if cands else None
                        if key: seen.add(key)
                        else: open_.append(f"{rel}:{ln} {kind} {line.strip()[:100]}")
    stale = [k for k in rows if k not in seen] + [f for f in FILES if ("FILE", f) not in seen]
    return open_, stale, counts, len(seen)


def main():
    o, st, counts, n = census()
    print(f"[s7598-az] sites {counts} rows+files matched={n}/{len(ROWS) + len(FILES)} open={len(o)} stale={len(st)}")
    verd = {}
    for v in list(ROWS.values()) + list(FILES.values()):
        k = v.split(":")[0]; verd[k] = verd.get(k, 0) + 1
    print("[s7598-az] verdicts", verd)
    for x in o: print("  OPEN", x)
    for k in st: print("  STALE", k)
    for x in FIXED: print("  FIXED", x)
    ok = not o and not st
    if "--controls" in sys.argv:
        c1 = census(plant=True)[0]; c2 = census(drop=next(iter(ROWS)))[0]
        src = open(os.path.join(ROOT, "lib/rt64/src/hle/rt64_rdp.cpp")).read()
        f1, f2, f3 = any("planted_control" in x for x in c1), len(c2) >= 1, "if (masks > 10) masks = 10;" in src
        print(f"[s7598-az] controls plant={'FIRED' if f1 else 'MISSED'} drop={'FIRED' if f2 else 'MISSED'} "
              f"clamp={'PRESENT' if f3 else 'MISSING'} ({int(f1)+int(f2)+int(f3)}/3)")
        ok = ok and f1 and f2 and f3
    sys.exit(0 if ok else 1)


main()
