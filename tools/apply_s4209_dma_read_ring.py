"""s4209: record audio-task RDRAM->DMEM reads (dram,len,src_nz,dmem_nz_after,dmem) in a ring; summarized per phase in rs64_s4207_after_audtask."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
hpp = R / "lib/N64ModernRuntime/librecomp/include/librecomp/rsp.hpp"
t = hpp.read_text()
call = "    rs64_m5_audio_source_dma(rdram, dram_addr, rd_len, dmem_addr);\n"
if "rs64_s4209_read" not in t:
    assert t.count(call) in (1, 2), t.count(call)
    t = t.replace(call, call + "    rs64_s4209_read(rdram, dram_addr, rd_len, dmem_addr);\n")
    anchor = 'extern "C" void rs64_probe_audio_dma_write('
    assert t.count(anchor) == 1
    t = t.replace(anchor, 'extern "C" void rs64_s4209_read(uint8_t* rdram, uint32_t dram_addr, uint32_t len, uint32_t dmem_addr);\n' + anchor)
    hpp.write_text(t); print("hpp patched")
rsp = R / "lib/N64ModernRuntime/librecomp/src/rsp.cpp"
c = rsp.read_text()
if "rs64_s4209_read" not in c:
    anchor = 'extern "C" void rs64_probe_audio_dma_write(uint8_t* rdram,'
    assert c.count(anchor) == 1
    c = c.replace(anchor, '''extern "C" { uint32_t rs64_s4209_rd[4096][5]; uint32_t rs64_s4209_n; }
extern "C" void rs64_s4209_read(uint8_t* rdram, uint32_t dram_addr, uint32_t len, uint32_t dmem_addr) {
    if (!rs64_s4208_active || rs64_s4209_n >= 4096u) return;
    uint32_t s = 0, d = 0;
    for (uint32_t i = 0; i < len; i++) {
        s += rdram[(dram_addr + i) & 0x007FFFFFu] != 0;
        d += RSP_MEM_BU(0, dmem_addr + i) != 0;
    }
    uint32_t* r = rs64_s4209_rd[rs64_s4209_n++];
    r[0] = dram_addr & 0x007FFFFFu; r[1] = len; r[2] = s; r[3] = d; r[4] = dmem_addr;
}
''' + anchor)
    o2 = "    if (is_audio_task) { rs64_s4208_n = 0; rs64_s4208_active = 1; }"
    assert c.count(o2) == 1
    c = c.replace(o2, "    if (is_audio_task) { rs64_s4208_n = 0; rs64_s4209_n = 0; rs64_s4208_active = 1; }")
    rsp.write_text(c); print("rsp patched")
f = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
s = f.read_text()
if "s4209" not in s:
    s = s.replace("extern uint32_t rs64_s4208_dma[4096][3]; extern uint32_t rs64_s4208_n;\n",
      "extern uint32_t rs64_s4208_dma[4096][3]; extern uint32_t rs64_s4208_n;\nextern uint32_t rs64_s4209_rd[4096][5]; extern uint32_t rs64_s4209_n;\n", 1)
    old = "    /* PATCH: s4208 dma intersect */\n"
    assert s.count(old) == 1
    new = old + r'''    /* PATCH: s4209 read ring summary */
    {
        static unsigned long r_tasks, r_n, r_bytes, r_srcnz, r_dmemnz, r_zsrc, r_zdmem_nzsrc;
        uint32_t nr = rs64_s4209_n;
        r_tasks++; r_n += nr;
        for (uint32_t i = 0; i < nr; ++i) {
            r_bytes += rs64_s4209_rd[i][1]; r_srcnz += rs64_s4209_rd[i][2]; r_dmemnz += rs64_s4209_rd[i][3];
            if (rs64_s4209_rd[i][1] >= 32 && rs64_s4209_rd[i][2] == 0) r_zsrc++;
            if (rs64_s4209_rd[i][2] != 0 && rs64_s4209_rd[i][3] == 0) r_zdmem_nzsrc++;
        }
        if (r_tasks <= 3 || (r_tasks % 128ul) == 0) {
            fprintf(stderr, "[m5-rd] phase=%u task=%lu reads=%u cum_reads=%lu cum_bytes=%lu cum_src_nz=%lu cum_dmem_nz=%lu cum_zero_src_reads(>=32B)=%lu cum_nzsrc_but_zero_dmem=%lu\n",
                    phase, r_tasks, nr, r_n, r_bytes, r_srcnz, r_dmemnz, r_zsrc, r_zdmem_nzsrc);
            for (uint32_t i = 0; i < nr && i < 12 && (r_tasks <= 3 || (r_tasks % 512ul) == 0); ++i)
                fprintf(stderr, "[m5-rd]   r%u dram=0x%06X len=%u src_nz=%u dmem_nz=%u dmem=0x%03X\n", i, rs64_s4209_rd[i][0], rs64_s4209_rd[i][1], rs64_s4209_rd[i][2], rs64_s4209_rd[i][3], rs64_s4209_rd[i][4]);
        }
    }
'''
    s = s.replace(old, new, 1); f.write_text(s); print("funcs patched")
