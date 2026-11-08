// s6961: offline equivalence of RT64::TMEMHasher::hash gather path (rs64TmemHashGather=1) vs the streaming path (=0), real header,
// random TMEM bytes / tile params / sizes / TLUT modes, both CI4 scan modes. Control: a one-byte TMEM flip inside the hashed span must
// change the hash (counted), and gather vs streaming with width+1 must differ.
// build: clang++ -O2 -std=c++17 -I lib/rt64/src -I lib/rt64/src/contrib -I lib/rt64/src/contrib/xxHash -I lib/rt64/src/contrib/nlohmann tools/g1e_hgather_equiv.cpp -o scratch/s6961/eq && scratch/s6961/eq
#include <cassert>
#include <cstdio>
#include <random>
#define XXH_INLINE_ALL
#include "xxhash.h"
namespace RT64 { struct LoadTile { uint8_t fmt, siz; uint16_t line, tmem; uint8_t palette, cms, cmt, masks, maskt, shifts, shiftt; uint16_t uls, ult, lrs, lrt; }; }
#define G_IM_SIZ_4b 0
#define G_IM_SIZ_8b 1
#define G_IM_SIZ_16b 2
#define G_IM_SIZ_32b 3
#define G_IM_FMT_RGBA 0
extern "C" { int g_rs64_tmem_fast = 1; }
#define RT64_LOAD_TYPES_H_STUB
#include "common/rt64_tmem_hasher.h"
int main() {
    std::mt19937_64 r(6961); uint8_t T[4096];
    uint64_t ok = 0, bad = 0, ctlDiff = 0, ctlN = 0, mutSame = 0, over = 0;
    for (int it = 0; it < 400000; it++) {
        for (auto &b : T) b = uint8_t(r());
        RT64::LoadTile lt{}; lt.siz = r() % 4; lt.fmt = (r() % 3 == 0) ? 0 : (r() % 5); lt.line = 1 + r() % ((r() & 1) ? 16 : 256); lt.tmem = r() % 512; lt.palette = r() % 16;
        uint16_t w = 1 + r() % ((r() & 1) ? 64 : 1024), h = 1 + r() % ((r() & 1) ? 64 : 256); uint32_t tlut = (r() % 3) ? 0 : (1 + r() % 3);
        rs64TmemHashNeonCI4 = int(r() & 1); rs64TmemHashByteLoop = (r() % 8 == 0);
        rs64TmemHashGather = 0; const uint64_t a = RT64::TMEMHasher::hash(T, lt, w, h, tlut, 5);
        rs64TmemHashGather = 1; rs64TmemHashGatherStat = 1; const uint64_t o0 = rs64HgOver;
        const uint64_t b = RT64::TMEMHasher::hash(T, lt, w, h, tlut, 5); over += (rs64HgOver != o0);
        (a == b ? ok : bad)++;
        if (it % 16 == 0) { rs64TmemHashGather = 0; mutSame += (RT64::TMEMHasher::hash(T, lt, uint16_t(w + 1), h, tlut, 5) == b); }
        if (it % 16 == 1) { const uint32_t p = uint32_t(lt.tmem) << 3; T[p & 4095] ^= 0x5A; if ((p & 2047) != (p & 4095)) T[p & 2047] ^= 0x5A; rs64TmemHashGather = 1; ctlN++; ctlDiff += (RT64::TMEMHasher::hash(T, lt, w, h, tlut, 5) != b); }
    }
    printf("ok=%llu bad=%llu overflowed=%llu mutant_same=%llu control_flip=%llu/%llu\n", (unsigned long long)ok, (unsigned long long)bad, (unsigned long long)over, (unsigned long long)mutSame, (unsigned long long)ctlDiff, (unsigned long long)ctlN);
    return bad != 0;
}
