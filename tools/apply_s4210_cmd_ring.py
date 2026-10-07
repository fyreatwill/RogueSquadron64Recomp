"""s4210: per-command struct ring for the audio ucode (factor5_ucode_b stage-0 hook, DMEM 0x350 0x50-byte record) + per-write-index nz + DMEM exit nz map, summarized per phase in rsp.cpp."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
rsp = R / "lib/N64ModernRuntime/librecomp/src/rsp.cpp"
t = rsp.read_text()
if "rs64_s4210_cmd" not in t:
    anchor = 'extern "C" void rs64_probe_audio_dma_write(uint8_t* rdram,'
    assert t.count(anchor) == 1
    code = r'''extern "C" { uint32_t rs64_s4210_cmd[512][12]; uint32_t rs64_s4210_n; }
extern "C" void rs64_s4210_cmd_rec(uint32_t src) {
    if (!rs64_s4208_active || rs64_s4210_n >= 512u) return;
    uint32_t nz = 0;
    for (uint32_t i = 0; i < 0x50; i++) nz += RSP_MEM_BU(0, 0x350 + i) != 0;
    auto w = [](uint32_t o) { return (uint32_t)(RSP_MEM_BU(0, 0x350 + o) << 24 | RSP_MEM_BU(0, 0x351 + o) << 16 | RSP_MEM_BU(0, 0x352 + o) << 8 | RSP_MEM_BU(0, 0x353 + o)); };
    uint32_t* r = rs64_s4210_cmd[rs64_s4210_n++];
    r[0] = src; r[1] = nz; r[2] = w(0x3C); r[3] = w(0x40); r[4] = w(0x2C);
    r[5] = w(0x00); r[6] = w(0x04); r[7] = w(0x08); r[8] = w(0x0C); r[9] = w(0x24); r[10] = w(0x30); r[11] = w(0x38);
}
extern "C" void rs64_s4210_summary(void) {
    static uint32_t ph_key = 0xFFFFFFFFu;
    static unsigned long tasks, cmds, cmd_nz0, b3c_nz, b3d_nz, h2c_nz, h40_nz, ctrl_nz, wr_total, wr_nz;
    uint32_t phase = rs64_phase_ord();
    if (phase != ph_key) { ph_key = phase; tasks = cmds = cmd_nz0 = b3c_nz = b3d_nz = h2c_nz = h40_nz = ctrl_nz = wr_total = wr_nz = 0; }
    tasks++;
    uint32_t n = rs64_s4210_n;
    cmds += n;
    for (uint32_t i = 0; i < n; i++) {
        const uint32_t* r = rs64_s4210_cmd[i];
        if (r[1] == 0) cmd_nz0++;
        if (r[2] >> 24) b3c_nz++;
        if ((r[2] >> 16) & 0xFF) b3d_nz++;
        if (r[4] >> 16) h2c_nz++;
        if (r[3] >> 16) h40_nz++;
        if (r[1] != 0) ctrl_nz++;
    }
    uint32_t nw = rs64_s4208_n;
    for (uint32_t i = 0; i < nw; i++) { wr_total++; if (rs64_s4208_dma[i][2]) wr_nz++; }
    if (tasks <= 3 || (tasks % 128ul) == 0) {
        std::fprintf(stderr, "[m5-cmd] phase=%u task=%lu cmds=%u cum_cmds=%lu empty_struct=%lu b3c_nz=%lu b3d_nz=%lu h2c_nz=%lu h40_nz=%lu struct_nz=%lu | writes_this=%u cum_writes=%lu cum_writes_nz=%lu\n",
                     phase, tasks, n, cmds, cmd_nz0, b3c_nz, b3d_nz, h2c_nz, h40_nz, ctrl_nz, nw, wr_total, wr_nz);
        for (uint32_t i = 0; i < nw && i < 8; i++)
            std::fprintf(stderr, "[m5-cmd]   w%u dram=0x%06X len=%u nz=%u\n", i, rs64_s4208_dma[i][0], rs64_s4208_dma[i][1], rs64_s4208_dma[i][2]);
        for (uint32_t i = 0; i < n && i < 6; i++) {
            const uint32_t* r = rs64_s4210_cmd[i];
            std::fprintf(stderr, "[m5-cmd]   c%u src=0x%06X nz=%u b3c..3f=%08X h40,42=%08X h2c=%08X w0=%08X w4=%08X w8=%08X wC=%08X w24=%08X w30=%08X w38=%08X\n",
                         i, r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11]);
        }
        std::fprintf(stderr, "[m5-cmd]   dmem_nz/256B:");
        for (uint32_t c = 0; c < 16; c++) { uint32_t z = 0; for (uint32_t i = 0; i < 256; i++) z += RSP_MEM_BU(0, c * 256 + i) != 0; std::fprintf(stderr, " %u", z); }
        std::fputc('\n', stderr);
        std::fflush(stderr);
    }
}
'''
    t = t.replace(anchor, code + anchor)
    o = "    if (is_audio_task) { rs64_s4208_n = 0; rs64_s4209_n = 0; rs64_s4208_active = 1; }"
    assert t.count(o) == 1
    t = t.replace(o, "    if (is_audio_task) { rs64_s4208_n = 0; rs64_s4209_n = 0; rs64_s4210_n = 0; rs64_s4208_active = 1; }")
    o = "    if (is_audio_task) { rs64_s4207_after_audtask(rdram, static_cast<int>(exit_reason)); }"
    assert t.count(o) == 1
    t = t.replace(o, "    if (is_audio_task) { rs64_s4210_summary(); rs64_s4207_after_audtask(rdram, static_cast<int>(exit_reason)); }")
    rsp.write_text(t); print("rsp patched")

# ucode hook (also appended to fixup_factor5_ucode.py so regen keeps it)
p = R / "build/factor5_ucode/factor5_ucode_b_recompiled.c"
s = p.read_text()
if "rs64_s4210_cmd_rec" not in s:
    old = "    rs64_audio_image_stage(0, rdram, r2, RSP_MEM_W_LOAD(0X348, 0), 0, 0);  /* fixup: image-stage audit */\n"
    assert s.count(old) == 1
    s = s.replace(old, old + "    rs64_s4210_cmd_rec(r4);  /* fixup: s4210 cmd ring */\n")
    s = s.replace('extern "C" void rs64_audio_image_break(uint32_t pc);', 'extern "C" void rs64_s4210_cmd_rec(uint32_t src);\nextern "C" void rs64_audio_image_break(uint32_t pc);', 1)
    p.write_text(s); print("ucode patched")
fx = R / "tools/fixup_factor5_ucode.py"
f = fx.read_text()
if "s4210 cmd ring" not in f:
    f += '''
# --- s4210 cmd ring: hook the stage-0 call in factor5_ucode_b (idempotent; see tools/apply_s4210_cmd_ring.py) ---
_p4210 = Path(path).parent / "factor5_ucode_b_recompiled.c" if "path" in globals() else None
if _p4210 is not None and _p4210.exists():
    _s = _p4210.read_text()
    _old = "    rs64_audio_image_stage(0, rdram, r2, RSP_MEM_W_LOAD(0X348, 0), 0, 0);  /* fixup: image-stage audit */\\n"
    if "rs64_s4210_cmd_rec" not in _s and _s.count(_old) == 1:
        _s = _s.replace(_old, _old + "    rs64_s4210_cmd_rec(r4);  /* fixup: s4210 cmd ring */\\n")
        _s = _s.replace('extern "C" void rs64_audio_image_break(uint32_t pc);', 'extern "C" void rs64_s4210_cmd_rec(uint32_t src);\\nextern "C" void rs64_audio_image_break(uint32_t pc);', 1)
        _p4210.write_text(_s)
'''
    fx.write_text(f); print("fixup patched")
