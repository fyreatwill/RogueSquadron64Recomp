// s7364 class AO two-arm control. Each case reproduces one heap/container hole found by the census + reviews, with the
// pre-fix logic (arm "pre", must trip ASan) and the landed fix (arm "post", must run clean). Usage: ao_ctl <case> pre|post
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <vector>
#include <algorithm>
static volatile uint32_t sink;
struct CallTile { uint32_t a[8]; };
// rt64_state.cpp: drawCall.tileIndex survives Workload::begin (callTiles cleared); a draw with no state change reuses it.
static int c_wlreset(bool post) {
    std::vector<CallTile> callTiles; uint32_t tileIndex = 0, tileCount = 0; bool texChanged = true;
    auto load = [&] { tileCount = 1; tileIndex = (uint32_t)callTiles.size(); callTiles.resize(tileIndex + tileCount); texChanged = false; };
    for (int i = 0; i < 40; i++) { if (texChanged) load(); callTiles[tileIndex].a[0] = i; texChanged = true; }  // 40 textured draws
    load();
    callTiles.clear(); callTiles.shrink_to_fit(); callTiles.reserve(4);      // FULLSYNC: nextWorkload.begin()
    if (post) texChanged = true;                                              // s7364: mark every draw attribute changed
    if (texChanged) load();
    callTiles[tileIndex].a[0] = 7;                                           // updateCallTexcoords
    printf("wlreset tileIndex=%u size=%zu\n", tileIndex, callTiles.size()); return 0;
}
// pi.cpp save_read RS64_EEP_TRACE dump printed save_buffer[offset+0..7] for a 4-byte read at the end.
static int c_eep(bool post) {
    std::vector<uint8_t> buf(0x8000); uint32_t off = 0x7FFC, count = 4;
    if ((uint64_t)off + count > buf.size()) return 1;
    if (!post || (uint64_t)off + 8 <= buf.size()) { uint32_t s = 0; for (int k = 0; k < 8; k++) s += buf[off + k]; sink = s; }
    printf("eep ok\n"); return 0;
}
// dpc_bridge.cpp s4272 shadow compare: 4-byte word loop over an unaligned (hi-lo)%4 != 0 range.
static int c_shadow(bool post) {
    uint32_t lo = 0x1000, hi = 0x1000 + 0x1E;                                   // 30 bytes
    std::vector<uint8_t> sh(hi - lo); std::vector<uint8_t> ram(0x2000);
    unsigned long d = 0;
    for (uint32_t x = lo; post ? (x + 4 <= hi) : (x < hi); x += 4) { uint32_t was, now; memcpy(&was, &sh[x - lo], 4); memcpy(&now, &ram[x], 4); d += was != now; }
    printf("shadow d=%lu\n", d); return 0;
}
// main.cpp ROGUESQ_SHADOW2 LIVE DIFF: buffer sized by the first task, later task's sh2_size larger.
static int c_sh2(bool post) {
    std::vector<uint8_t> buf; std::vector<uint8_t> ram(0x800000);
    uint32_t phys[2] = {0x7E0000, 0x100000};
    for (uint32_t p : phys) {
        uint32_t size = 0x82000; if (p + size > 0x800000) size = 0x800000 - p;
        if (buf.empty()) buf.resize(size);
        uint32_t n = post ? (uint32_t)std::min<size_t>(size, buf.size()) : size, nd = 0;
        for (uint32_t k = 0; k < n; k++) nd += ram[p + k] != buf[k];
        sink = nd;
    }
    printf("sh2 ok\n"); return 0;
}
// mods.cpp init_mod_code: section rom_addr+size never checked against mod_binary.bin.
static int c_modbin(bool post) {
    std::vector<char> bin(16); uint32_t rom_addr = 0, size = 0x100;
    if (post && (uint64_t)rom_addr + size > bin.size()) { printf("modbin rejected\n"); return 0; }
    uint32_t s = 0; for (uint32_t i = 0; i < size; i++) s += (uint8_t)bin[rom_addr + i]; sink = s;
    printf("modbin ok\n"); return 0;
}
// funcs_13.c rs5834_post: who is reset to the 2 sentinel; a post without a pre indexed rs5834_n[2].
static unsigned n2[2], hit2[2];
static int c_who(bool post) {
    unsigned *n = new unsigned[2](); unsigned w = 2;                      // heap so ASan sees it (the real array is static)
    if (post && w > 1) { printf("who skipped\n"); delete[] n; return 0; }
    n[w]++; sink = n[w] + n2[0] + hit2[0]; delete[] n; printf("who ok\n"); return 0;
}
int main(int argc, char **argv) {
    if (argc < 3) return 2;
    bool post = !strcmp(argv[2], "post");
    const char *c = argv[1];
    if (!strcmp(c, "wlreset")) return c_wlreset(post);
    if (!strcmp(c, "eep")) return c_eep(post);
    if (!strcmp(c, "shadow")) return c_shadow(post);
    if (!strcmp(c, "sh2")) return c_sh2(post);
    if (!strcmp(c, "modbin")) return c_modbin(post);
    if (!strcmp(c, "who")) return c_who(post);
    return 2;
}
