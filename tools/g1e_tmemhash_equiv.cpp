// s6935 G1e: TMEMHasher store-only TLUT table vs the old byte loop, on the real header. Random TMEM and tiles over every siz/fmt, row and block paths, wrap,
// TLUT on/off, hash versions 2-5. Controls: changing a palette entry a texel uses must change the hash, an unused one must not (version 5), in both modes.
// Build, repo root: clang++ -std=c++17 -O2 -w -Ilib/rt64/src -Ilib/rt64/src/contrib -Ilib/rt64/src/contrib tools/g1e_tmemhash_equiv.cpp -o scratch/s6935/teq && scratch/s6935/teq
#include <cassert>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <algorithm>
#include "xxHash/xxh3.h"
enum { G_IM_SIZ_4b, G_IM_SIZ_8b, G_IM_SIZ_16b, G_IM_SIZ_32b, G_IM_FMT_RGBA = 0, G_IM_FMT_CI = 2 };
#include "common/rt64_load_types.h"
#include "common/rt64_tmem_hasher.h"
extern "C" { int g_rs64_tmem_fast = 1; }
// Reference: the byte loop in loadWord (lib/rt64/src/hle/rt64_rdp.cpp), non-RGBA32 non-TLUT case.
static void refWord(uint8_t *TMEM, uint32_t t, uint32_t x, const uint8_t *RDRAM, uint32_t a, uint32_t m) { for (uint32_t i = 0; i < 8; i++) TMEM[(t + i) ^ x] = RDRAM[((a + i) & m) ^ 3]; }
static int wordCheck() {
    static uint8_t R[0x1000000 + 16], A[4096], B[4096]; for (uint32_t i = 0; i < sizeof R; i += 4099) R[i] = i; for (auto &b : R) b = rand();
    const uint32_t m = 0xFFFFFF; uint64_t n = 0, fast = 0, bad = 0, slow = 0;
    for (int it = 0; it < 3000000; it++) {
        const uint32_t t = (it & 1 ? rand() & 4095 : (rand() & 511) << 3) & ~(it & 2 ? 7u : 0u), x = (rand() & 1) << 2;
        uint32_t a = ((uint32_t)rand() << 3) ^ rand(); if (it & 4) a &= ~3u; if ((it & 1023) == 0) a = m - (rand() & 15);
        if (t + 8 > 4096) continue;
        n++; memcpy(B, A, 4096); refWord(B, t, x, R, a, m);
        if (rs64LoadWordFast(A, t, x, R, a, m)) { fast++; if (memcmp(A, B, 4096)) bad++; } else slow++;
        memcpy(A, B, 4096);
        if ((it & 0xFFFF) == 0) { /* keep the copy cost down */ }
    }
    printf("word n=%llu fast=%llu slow=%llu bad=%llu\n", (unsigned long long)n, (unsigned long long)fast, (unsigned long long)slow, (unsigned long long)bad);
    return bad != 0 || fast == 0 || slow == 0;
}
using namespace RT64;
static uint64_t H(const uint8_t *m, const LoadTile &t, uint16_t w, uint16_t h, uint32_t tl, uint32_t v, int loop) { rs64TmemHashByteLoop = loop; return TMEMHasher::hash(m, t, w, h, tl, v); }
int main() {
    if (wordCheck()) return 2;
    static uint8_t T[4096 + 8]; uint64_t n = 0, bad = 0, ctl_used = 0, ctl_used_bad = 0, ctl_unused = 0, ctl_unused_bad = 0, tl = 0;
    srand(6935);
    for (int it = 0; it < 2000000; it++) {
        if ((it & 63) == 0) for (auto &b : T) b = rand();
        LoadTile t{}; t.siz = rand() & 3; t.fmt = rand() % 5; t.line = 1 + rand() % 40; t.tmem = rand() & 511; t.palette = rand() & 15;
        const uint16_t w = 1 + rand() % 128, h = 1 + rand() % 64; const uint32_t tlut = rand() & 3 ? (rand() & 3) : 0, v = 2 + rand() % 4;
        n++; tl += tlut != 0; if (H(T, t, w, h, tlut, v, 0) != H(T, t, w, h, tlut, v, 1)) bad++;
    }
    // Palette controls: CI8, indices limited to 0..15, block path, tile at TMEM 0. Palette entry i is 8 bytes at 2048 + i * 8.
    for (int it = 0; it < 20000; it++) {
        for (int i = 0; i < 4096; i++) T[i] = i < 2048 ? rand() & 15 : rand();
        LoadTile t{}; t.siz = G_IM_SIZ_8b; t.fmt = G_IM_FMT_CI; t.line = 4; t.tmem = 0; const uint16_t w = 32, h = 16;
        for (int loop = 0; loop < 2; loop++) {
            const uint64_t a = H(T, t, w, h, 2, 5, loop);
            T[2048 + (T[5] * 8) + 2] ^= 0x55; ctl_used++; if (H(T, t, w, h, 2, 5, loop) == a) ctl_used_bad++; T[2048 + (T[5] * 8) + 2] ^= 0x55;
            T[2048 + 200 * 8 + 2] ^= 0x55; ctl_unused++; if (H(T, t, w, h, 2, 5, loop) != a) ctl_unused_bad++; T[2048 + 200 * 8 + 2] ^= 0x55;
        }
    }
    LoadTile t{}; t.siz = G_IM_SIZ_8b; t.fmt = G_IM_FMT_CI; t.line = 8; const uint16_t w = 64, h = 32; uint64_t sink = 0; double ns[2];
    for (int loop = 0; loop < 2; loop++) { auto a = std::chrono::steady_clock::now(); for (int i = 0; i < 300000; i++) { T[i & 2047]++; sink += H(T, t, w, h, 2, 5, loop); } ns[loop] = std::chrono::duration<double, std::nano>(std::chrono::steady_clock::now() - a).count() / 300000; }
    printf("n=%llu tlut=%llu bad=%llu used_ctl=%llu missed=%llu unused_ctl=%llu moved=%llu table %.0f ns loop %.0f ns sink=%llu\n", (unsigned long long)n, (unsigned long long)tl, (unsigned long long)bad, (unsigned long long)ctl_used, (unsigned long long)ctl_used_bad, (unsigned long long)ctl_unused, (unsigned long long)ctl_unused_bad, ns[0], ns[1], (unsigned long long)(sink & 1));
    return bad || ctl_used_bad || ctl_unused_bad;
}
