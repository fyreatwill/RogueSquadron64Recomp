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
// s6942: loop 0 = NEON CI4 + table, 1 = s6935 per-byte loop, 2 = s6935 table without NEON. MUTANT=1 drops nibble 15 from the NEON mask (must fail).
static uint64_t H(const uint8_t *m, const LoadTile &t, uint16_t w, uint16_t h, uint32_t tl, uint32_t v, int loop) { rs64TmemHashByteLoop = loop == 1; rs64TmemHashNeonCI4 = loop == 0; return TMEMHasher::hash(m, t, w, h, tl, v); }
int main() {
    if (wordCheck()) return 2;
    static uint8_t T[4096 + 8]; uint64_t n = 0, bad = 0, ctl_used = 0, ctl_used_bad = 0, ctl_unused = 0, ctl_unused_bad = 0, tl = 0;
    srand(6935);
    for (int it = 0; it < 2000000; it++) {
        if ((it & 63) == 0) for (auto &b : T) b = rand();
        LoadTile t{}; t.siz = rand() & 3; t.fmt = rand() % 5; t.line = 1 + rand() % 40; t.tmem = rand() & 511; t.palette = rand() & 15;
        const uint16_t w = 1 + rand() % 128, h = 1 + rand() % 64; const uint32_t tlut = rand() & 3 ? (rand() & 3) : 0, v = 2 + rand() % 4;
        n++; tl += tlut != 0; { const uint64_t h0 = H(T, t, w, h, tlut, v, 0); if (h0 != H(T, t, w, h, tlut, v, 1) || h0 != H(T, t, w, h, tlut, v, 2)) bad++; }
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
    // s6942 CI4 palette controls in NEON mode (loop 0): texels use nibbles 0..14 only; palette 3 entry e is 8 bytes at 2048 + 3*128 + e*8.
    // Changing entry 15 must not move the hash; changing the entry of a used nibble must. Also a tile with one 15 nibble in the scalar tail.
    uint64_t c4u = 0, c4ub = 0, c4n = 0, c4nb = 0, c4t = 0, c4tb = 0;
    for (int it = 0; it < 20000; it++) {
        for (int i = 0; i < 4096; i++) { uint8_t a = rand() % 15, b = rand() % 15; T[i] = i < 2048 ? uint8_t(a | (b << 4)) : rand(); }
        LoadTile t{}; t.siz = G_IM_SIZ_4b; t.fmt = G_IM_FMT_CI; t.line = 2 + rand() % 6; t.tmem = 0; t.palette = 3; const uint16_t w = 2 + rand() % 60, h = 1 + rand() % 40;
        const uint32_t pal = 2048 + 3 * 128; const uint64_t a = H(T, t, w, h, 2, 5, 0);
        T[pal + 15 * 8 + 1] ^= 0x5A; c4n++; if (H(T, t, w, h, 2, 5, 0) != a) c4nb++; T[pal + 15 * 8 + 1] ^= 0x5A;
        const int e = T[0] & 15; T[pal + e * 8 + 1] ^= 0x5A; c4u++; if (H(T, t, w, h, 2, 5, 0) == a) c4ub++; T[pal + e * 8 + 1] ^= 0x5A;
        T[0] = (T[0] & 0xF0) | 15; const uint64_t b2 = H(T, t, w, h, 2, 5, 0);
        T[pal + 15 * 8 + 1] ^= 0x5A; c4t++; if (H(T, t, w, h, 2, 5, 0) == b2) c4tb++; T[pal + 15 * 8 + 1] ^= 0x5A;
    }
    printf("ci4 ctl unused=%llu moved=%llu used=%llu missed=%llu nib15=%llu missed=%llu\n", (unsigned long long)c4n, (unsigned long long)c4nb, (unsigned long long)c4u, (unsigned long long)c4ub, (unsigned long long)c4t, (unsigned long long)c4tb);
    if (c4nb || c4ub || c4tb) return 3;
    { LoadTile t{}; t.siz = G_IM_SIZ_4b; t.fmt = G_IM_FMT_CI; t.line = 4; const uint16_t w = 64, h = 64; uint64_t sink = 0; double ns[3];
      for (int loop = 0; loop < 3; loop++) { auto a = std::chrono::steady_clock::now(); for (int i = 0; i < 300000; i++) { T[i & 2047]++; sink += H(T, t, w, h, 2, 5, loop); } ns[loop] = std::chrono::duration<double, std::nano>(std::chrono::steady_clock::now() - a).count() / 300000; }
      printf("ci4 64x64 bench: neon %.0f ns loop %.0f ns table %.0f ns sink=%llu\n", ns[0], ns[1], ns[2], (unsigned long long)(sink & 1)); }
    LoadTile t{}; t.siz = G_IM_SIZ_8b; t.fmt = G_IM_FMT_CI; t.line = 8; const uint16_t w = 64, h = 32; uint64_t sink = 0; double ns[2];
    for (int loop = 0; loop < 2; loop++) { auto a = std::chrono::steady_clock::now(); for (int i = 0; i < 300000; i++) { T[i & 2047]++; sink += H(T, t, w, h, 2, 5, loop); } ns[loop] = std::chrono::duration<double, std::nano>(std::chrono::steady_clock::now() - a).count() / 300000; }
    printf("n=%llu tlut=%llu bad=%llu used_ctl=%llu missed=%llu unused_ctl=%llu moved=%llu table %.0f ns loop %.0f ns sink=%llu\n", (unsigned long long)n, (unsigned long long)tl, (unsigned long long)bad, (unsigned long long)ctl_used, (unsigned long long)ctl_used_bad, (unsigned long long)ctl_unused, (unsigned long long)ctl_unused_bad, ns[0], ns[1], (unsigned long long)(sink & 1));
    return bad || ctl_used_bad || ctl_unused_bad;
}
