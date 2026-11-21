// s7751: gfx task snapshot for an independent-RSP replay (tools/s7751_cxd4_task/).
// ROGUESQ_S7751_SNAP=<dir> (off by default, no cost when unset). At each gfx task begin the whole 16 MB
// physical RDRAM window (the RSP's DMA reach) and DMEM are copied into a ring of 3 in-memory slots, and every
// RDP byte the ucode hands the DPC bridge (rsp_dpc_submit, before any cull/merge) is appended to that slot.
// rs64_s7751_dump(k) (called by POSE_FREEZE after its sleep, when no task is running) writes the completed slots to
// <dir>/k<k>_s<serial>.bin. Format (little-endian u32 words; RDRAM/DMEM in the runtime's native word layout,
// i.e. byte a at [a^3], the same layout cxd4 expects):
//   "S751" ver=1 serial vi rdram_size dmem[4096] rdram[rdram_size] nbytes rdp[nbytes] (rdp = plain big-endian RDP command bytes)
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <vector>

extern "C" volatile uint32_t rs64_vi_n_g;

namespace {
constexpr uint32_t kRam = 0x01000000u;
struct Slot { std::vector<uint8_t> ram, rdp; uint8_t dmem[4096]; uint32_t serial = 0, vi = 0; bool done = false, used = false; };
Slot g_slot[3];
int g_cur = -1;
uint32_t g_serial = 0, g_base = 0xFFFFFFFFu, g_last = 0;
std::mutex g_mu;
const char* dir() { static const char* d = [] { const char* e = std::getenv("ROGUESQ_S7751_SNAP"); return (e && *e && *e != '0') ? e : nullptr; }(); return d; }
}

extern "C" int rs64_s7751_on(void) { return dir() != nullptr; }

extern "C" void rs64_s7751_task_begin(const uint8_t* rdram, const uint8_t* dmem) {
    if (!dir() || !rdram || !dmem) return;
    std::lock_guard<std::mutex> lk(g_mu);
    g_cur = (int)(++g_serial % 3u);
    Slot& s = g_slot[g_cur];
    s.ram.resize(kRam);
    std::memcpy(s.ram.data(), rdram, kRam);
    std::memcpy(s.dmem, dmem, 4096);
    s.rdp.clear(); s.serial = g_serial; s.vi = rs64_vi_n_g; s.done = false; s.used = true;
    g_base = 0xFFFFFFFFu; g_last = 0;
}

// Same windowing as rsp_dpc_submit_impl: start = DPC_START, end grows; forward only bytes not yet seen.
extern "C" void rs64_s7751_rdp(const uint8_t* rdram, uint32_t start, uint32_t end) {
    if (!dir() || g_cur < 0) return;
    const uint32_t sp = start & 0x00FFFFFFu, ep = end & 0x00FFFFFFu;
    if (ep <= sp || ep > kRam) return;
    uint32_t from = (sp != g_base) ? sp : g_last;
    if (sp != g_base) g_base = sp;
    if (from < sp || from > ep) from = sp;
    Slot& s = g_slot[g_cur];
    for (uint32_t a = from; a < ep; a++) s.rdp.push_back(rdram[a ^ 3u]);  // stored as a plain big-endian byte stream
    g_last = ep;
}

extern "C" void rs64_s7751_task_end(void) {
    if (!dir() || g_cur < 0) return;
    std::lock_guard<std::mutex> lk(g_mu);
    g_slot[g_cur].done = true;
}

extern "C" void rs64_s7751_dump(unsigned k) {
    if (!dir()) return;
    std::lock_guard<std::mutex> lk(g_mu);
    for (Slot& s : g_slot) {
        if (!s.used || !s.done) continue;
        char p[1024];
        std::snprintf(p, sizeof p, "%s/k%u_s%u.bin", dir(), k, s.serial);
        FILE* f = std::fopen(p, "wb");
        if (!f) { std::fprintf(stderr, "[s7751] open failed %s\n", p); continue; }
        const uint32_t hdr[5] = {0x31353753u /* "S751" */, 1u, s.serial, s.vi, kRam};
        std::fwrite(hdr, 4, 5, f);
        std::fwrite(s.dmem, 1, 4096, f);
        std::fwrite(s.ram.data(), 1, kRam, f);
        const uint32_t n = (uint32_t)s.rdp.size();
        std::fwrite(&n, 4, 1, f);
        std::fwrite(s.rdp.data(), 1, n, f);
        std::fclose(f);
        std::fprintf(stderr, "[s7751] dumped k=%u serial=%u vi=%u rdp_bytes=%u -> %s\n", k, s.serial, s.vi, n, p);
    }
    std::fflush(stderr);
}
