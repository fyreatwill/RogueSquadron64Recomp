"""s4208: record every audio-task DMEM->RDRAM write (dram,len,nonzero) in a global ring and intersect with +0x7C output buffers in rs64_s4207_after_audtask."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
rsp = R / "lib/N64ModernRuntime/librecomp/src/rsp.cpp"
t = rsp.read_text()
if "rs64_s4208_dma" not in t:
    old = ("    AudioDmaProbe* probe = g_audio_dma_probe;\n    if (probe == nullptr) return;\n"
           "    const OSTask_s& task = probe->task->t;")
    assert t.count(old) == 1
    new = ("    if (rs64_s4208_active && rs64_s4208_n < 4096u) {\n"
           "        uint32_t nz = 0;\n"
           "        for (uint32_t i = 0; i < len; i++) nz += rdram[(dram_addr + i) & 0x007FFFFFu] != 0;\n"
           "        rs64_s4208_dma[rs64_s4208_n][0] = dram_addr & 0x007FFFFFu;\n"
           "        rs64_s4208_dma[rs64_s4208_n][1] = len;\n"
           "        rs64_s4208_dma[rs64_s4208_n][2] = nz;\n"
           "        rs64_s4208_n++;\n    }\n" + old)
    t = t.replace(old, new)
    decl = 'extern "C" void rs64_probe_audio_dma_write(uint8_t* rdram,\n                                              uint32_t dram_addr, uint32_t len,\n                                              uint32_t dmem_addr) {'
    assert t.count(decl) == 1
    t = t.replace(decl, 'extern "C" { uint32_t rs64_s4208_dma[4096][3]; uint32_t rs64_s4208_n; int rs64_s4208_active; }\n' + decl)
    o2 = "    RspExitReason exit_reason = ucode_func(rdram, task->t.ucode);\n    g_audio_dma_probe = previous_audio_probe;\n"
    assert t.count(o2) == 1
    t = t.replace(o2, "    if (is_audio_task) { rs64_s4208_n = 0; rs64_s4208_active = 1; }\n    RspExitReason exit_reason = ucode_func(rdram, task->t.ucode);\n    rs64_s4208_active = 0;\n    g_audio_dma_probe = previous_audio_probe;\n")
    rsp.write_text(t)
    print("rsp patched")
f = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
c = f.read_text()
if "s4208" not in c:
    c = c.replace("uint32_t rs64_s4207_ring[8192];\nuint32_t rs64_s4207_n;\n",
      "uint32_t rs64_s4207_ring[8192];\nuint32_t rs64_s4207_n;\nextern uint32_t rs64_s4208_dma[4096][3]; extern uint32_t rs64_s4208_n;\n", 1)
    old = "    uint32_t cnt = rs64_s4207_n, tout = 0, tsrc = 0;\n"
    assert c.count(old) == 1
    new = old + r'''    /* PATCH: s4208 dma intersect */
    static unsigned long d_tasks, d_writes, d_bytes, d_nzb, d_hit_recs, d_hit_nz, d_recs;
    {
        uint32_t nd = rs64_s4208_n, hit = 0, hitnz = 0;
        d_tasks++; d_writes += nd;
        for (uint32_t i = 0; i < nd; ++i) { d_bytes += rs64_s4208_dma[i][1]; d_nzb += rs64_s4208_dma[i][2]; }
        for (uint32_t k = 0; k < cnt; ++k) {
            gpr r = (gpr)(int32_t)rs64_s4207_ring[k];
            uint32_t p = (uint32_t)MEM_W(0x7C, r);
            if (p < 0x80000000u || p >= 0x807FFF00u) continue;
            uint32_t ph = p & 0x7FFFFFu; ++d_recs;
            int h = 0, hn = 0;
            for (uint32_t i = 0; i < nd; ++i) {
                uint32_t a = rs64_s4208_dma[i][0], l = rs64_s4208_dma[i][1];
                if (a < ph + 0x100u && ph < a + l) { h = 1; if (rs64_s4208_dma[i][2]) hn = 1; }
            }
            hit += h; hitnz += hn;
        }
        d_hit_recs += hit; d_hit_nz += hitnz;
        if (d_tasks <= 3 || (d_tasks % 128ul) == 0) {
            fprintf(stderr, "[m5-dma] phase=%u task=%lu exit=%d dma_writes=%u recs=%u rec_out_overlap=%u overlap_nzdata=%u cum_writes=%lu cum_bytes=%lu cum_nzbytes=%lu cum_out_recs=%lu cum_overlap=%lu cum_overlap_nz=%lu\n",
                    phase, d_tasks, exit_reason, nd, cnt, hit, hitnz, d_writes, d_bytes, d_nzb, d_recs, d_hit_recs, d_hit_nz);
            for (uint32_t i = 0; i < nd && i < 6 && d_tasks <= 3; ++i)
                fprintf(stderr, "[m5-dma]   w%u dram=0x%06X len=%u nz=%u\n", i, rs64_s4208_dma[i][0], rs64_s4208_dma[i][1], rs64_s4208_dma[i][2]);
        }
    }
'''
    c = c.replace(old, new, 1)
    f.write_text(c)
    print("funcs patched")
