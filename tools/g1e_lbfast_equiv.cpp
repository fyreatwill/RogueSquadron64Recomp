// s6957: offline equivalence of rs64LoadBlockRuns (copy of lib/rt64/src/hle/rt64_rdp.cpp) vs RT64's per-word LoadBlock loop, random inputs.
// build: clang++ -O2 -std=c++17 tools/g1e_lbfast_equiv.cpp -o scratch/s6957/eq && scratch/s6957/eq
#include <cstdint>
#include <cstring>
#include <cstdio>
#include <random>
#include <vector>
static bool runs(uint8_t *TMEM, const uint8_t *RDRAM, uint32_t textureStart, uint32_t tmemStart, uint32_t tmemStride, uint32_t wordCount, uint32_t dxt) {
    const uint32_t tmemMask = 4095;
    if (wordCount > 2048) wordCount = 2048;
    const uint32_t a0 = textureStart & 0xFFFFFFu;
    if ((a0 & 3u) || (tmemStart & 7u) || (tmemStride & 7u) || (uint64_t)a0 + 8ull * wordCount > 0x1000000ull) return false;
    const uint8_t *src = RDRAM + a0; uint32_t tA = tmemStart & tmemMask, x = 0, counter = 0;
    while (wordCount > 0) {
        uint32_t n = wordCount;
        if (dxt) { const uint32_t need = (0x800u - counter + dxt - 1u) / dxt; if (need < n) n = need; }
        for (uint32_t j = 0; j < n; j++) { uint64_t v; memcpy(&v, src, 8); v = __builtin_bswap64(v); if (!x) v = (v >> 32) | (v << 32); memcpy(TMEM + tA, &v, 8); src += 8; tA = (tA + 8u) & tmemMask; }
        wordCount -= n; counter += n * dxt;
        while (counter >= 0x800u) { tA = (tA + tmemStride) & tmemMask; counter -= 0x800u; x ^= 4u; }
    }
    return true;
}
static void ref(uint8_t *TMEM, const uint8_t *RDRAM, uint32_t textureStart, uint32_t tmemStart, uint32_t tmemStride, uint32_t wordsPerRow, uint32_t dxt) {
    if (wordsPerRow > 2048) wordsPerRow = 2048;
    const uint32_t tmemMask = 4095; uint32_t textureAddress = textureStart, tmemAddress = tmemStart & tmemMask, x = 0, c = 0;
    for (uint32_t w = 0; w < wordsPerRow; w++) {
        for (uint32_t i = 0; i < 8; i++) TMEM[(tmemAddress + i) ^ x] = RDRAM[((textureAddress + i) & 0xFFFFFF) ^ 3];
        c += dxt; while (c >= 0x800) { tmemAddress = (tmemAddress + tmemStride) & tmemMask; c -= 0x800; x ^= 4; }
        textureAddress += 8; tmemAddress = (tmemAddress + 8) & tmemMask;
    }
}
int main() {
    std::vector<uint8_t> R(0x1000000); std::mt19937 g(6957); for (auto &b : R) b = (uint8_t)g();
    uint8_t A[4096], B[4096]; unsigned long ok = 0, bad = 0, fall = 0;
    for (int it = 0; it < 400000; it++) {
        uint32_t ts = (g() & 0xFFFFFF) & ~7u; if (it & 1) ts = g() & 0x3FFFFF8; if (it % 7 == 0) ts |= 4;
        uint32_t tm = (g() & 0x1FF) << 3, st = (g() & 0x3F) << 3, wc = g() % 2100 + 1, dxt = (it % 5 == 0) ? 0 : g() & 0xFFF;
        if (it % 11 == 0) dxt = 2048 / ((g() % 16) + 1);
        for (int i = 0; i < 4096; i++) A[i] = B[i] = (uint8_t)g();
        if (!runs(A, R.data(), ts, tm, st, wc, dxt)) { fall++; continue; }
        ref(B, R.data(), ts, tm, st, wc, dxt);
        (memcmp(A, B, 4096) ? bad : ok)++;
    }
    for (int i = 0; i < 4096; i++) A[i] = B[i] = 0; runs(A, R.data(), 0x1000, 0, 16, 256, 0x80); ref(B, R.data(), 0x1000, 0, 16, 256, 0x80); A[3] ^= 1;
    printf("ok=%lu bad=%lu fall=%lu control=%d\n", ok, bad, fall, memcmp(A, B, 4096) != 0);
    return bad != 0;
}
