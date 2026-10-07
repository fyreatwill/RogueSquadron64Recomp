"""s4211: who writes the audio task data_ptr buffer? PI-DMA ring (pi.cpp do_dma) + per-data_ptr content-change tracker and retrospective ring query (rsp.cpp)."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
pi = R / "lib/N64ModernRuntime/librecomp/src/pi.cpp"
t = pi.read_text()
if "rs64_s4211_pi" not in t:
    anchor = "void do_dma(RDRAM_ARG PTR(OSMesgQueue) mq, gpr rdram_address"
    assert t.count(anchor) == 1
    code = r'''extern "C" uint32_t rs64_phase_ord();
extern "C" volatile uint32_t g_rs64_last_guest_pc;
struct Rs64S4211Pi { uint32_t dram, size, rom_off, phase, pc; };
Rs64S4211Pi rs64_s4211_pi_ring[8192];
uint64_t rs64_s4211_pi_n;
static void rs64_s4211_pi_note(uint32_t dram, uint32_t size, uint32_t rom_off) {
    Rs64S4211Pi& e = rs64_s4211_pi_ring[rs64_s4211_pi_n % 8192];
    e.dram = dram & 0x7FFFFFu; e.size = size; e.rom_off = rom_off; e.phase = rs64_phase_ord(); e.pc = g_rs64_last_guest_pc;
    rs64_s4211_pi_n++;
}
'''
    t = t.replace(anchor, code + anchor)
    o = "            recomp::do_rom_read(rdram, rdram_address, physical_addr, size);\n"
    assert t.count(o) == 1
    t = t.replace(o, o + "            rs64_s4211_pi_note((uint32_t)rdram_address, size, physical_addr - recomp::rom_base);\n")
    pi.write_text(t); print("pi patched")
rsp = R / "lib/N64ModernRuntime/librecomp/src/rsp.cpp"
t = rsp.read_text()
if "rs64_s4211_task" not in t:
    anchor = 'extern "C" void rs64_probe_audio_dma_write(uint8_t* rdram,'
    assert t.count(anchor) == 1
    code = r'''struct Rs64S4211Pi { uint32_t dram, size, rom_off, phase, pc; };
extern Rs64S4211Pi rs64_s4211_pi_ring[8192];
extern uint64_t rs64_s4211_pi_n;
extern "C" void rs64_s4211_task(uint8_t* rdram, uint32_t dp_virt) {
    struct Slot { uint32_t dp; uint32_t hash; uint64_t tasks, changes, first_phase; };
    static Slot slots[32]; static int nslots;
    static uint32_t ph_key = 0xFFFFFFFFu; static unsigned long ph_tasks, ph_changes;
    uint32_t phase = rs64_phase_ord();
    if (phase != ph_key) { ph_key = phase; ph_tasks = ph_changes = 0; }
    const uint32_t dp = dp_virt & 0x7FFFFFu;
    const uint32_t lo = dp - 0x10, len = 0x130;
    auto byte = [&](uint32_t p) { return rdram[(p) ^ 3]; };
    uint32_t h = 2166136261u;
    for (uint32_t i = 0; i < len; i++) { h ^= byte(lo + i); h *= 16777619u; }
    Slot* s = nullptr;
    for (int i = 0; i < nslots; i++) if (slots[i].dp == dp) s = &slots[i];
    ph_tasks++;
    if (!s) {
        if (nslots >= 32) return;
        s = &slots[nslots++]; *s = Slot{dp, h, 0, 0, phase};
        std::fprintf(stderr, "[s4211-new] phase=%u dp=0x%06X pi_ring_total=%llu ascii0x10=\"", phase, dp, (unsigned long long)rs64_s4211_pi_n);
        for (uint32_t i = 0; i < 0x30; i++) { uint8_t c = byte(dp + i); std::fputc((c >= 32 && c < 127) ? c : '.', stderr); }
        std::fprintf(stderr, "\"\n");
        uint64_t total = rs64_s4211_pi_n, avail = total < 8192 ? total : 8192; int hits = 0;
        for (uint64_t k = 0; k < avail && hits < 4; k++) {
            const Rs64S4211Pi& e = rs64_s4211_pi_ring[(total - 1 - k) % 8192];
            if (e.dram < lo + len && e.dram + e.size > lo) {
                std::fprintf(stderr, "[s4211-pi-hit] dp=0x%06X age=%llu dram=0x%06X size=0x%X rom_off=0x%08X dma_phase=%u guest_pc=0x%08X\n", dp, (unsigned long long)k, e.dram, e.size, e.rom_off, e.phase, e.pc);
                hits++;
            }
        }
        if (avail) {
            const Rs64S4211Pi& e = rs64_s4211_pi_ring[(total - 1) % 8192];
            std::fprintf(stderr, "[s4211-ctl] dp=0x%06X pi_hits=%d newest_dma=0x%06X+0x%X self_overlap=%d\n", dp, hits, e.dram, e.size, (int)(e.size > 0 && e.dram < e.dram + e.size));
        } else std::fprintf(stderr, "[s4211-ctl] dp=0x%06X pi_hits=%d ring_empty\n", dp, hits);
        std::fflush(stderr);
        return;
    }
    s->tasks++;
    if (h != s->hash) {
        s->changes++; ph_changes++; s->hash = h;
        if (s->changes <= 3) std::fprintf(stderr, "[s4211-chg] phase=%u dp=0x%06X change#%llu at task#%llu\n", phase, dp, (unsigned long long)s->changes, (unsigned long long)s->tasks);
    }
    if ((ph_tasks % 1024ul) == 0) {
        std::fprintf(stderr, "[s4211-sum] phase=%u phase_tasks=%lu phase_changes=%lu slot_dp=0x%06X slot_tasks=%llu slot_changes=%llu\n", phase, ph_tasks, ph_changes, dp, (unsigned long long)s->tasks, (unsigned long long)s->changes);
        std::fflush(stderr);
    }
}
'''
    t = t.replace(anchor, code + anchor)
    o = "    if (is_audio_task) { rs64_s4208_n = 0;"
    assert t.count(o) == 1
    t = t.replace(o, "    if (is_audio_task) { rs64_s4211_task(rdram, static_cast<uint32_t>(task->t.data_ptr)); }\n" + o)
    rsp.write_text(t); print("rsp patched")
