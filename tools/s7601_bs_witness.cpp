// s7601 class BS known-value witness: guest word 0x11223344 at guest phys 0x100 and byte 0xAB at guest 0x105, stored the way
// librecomp stores RDRAM on this LE host (native u32 words; guest byte A at host A ^ 3). Checks the OLD composer forms fixed in
// s7601 return the wrong value (positive control) and the NEW forms and the reference helper return the right one.
// Build: c++ -std=c++17 -I src/main tools/s7601_bs_witness.cpp -o /tmp/s7601/w && /tmp/s7601/w
#include <cstdio>
#include <cstring>
#include <cstdint>
#include "rs64_rdram_peek.h"
static uint8_t ram[0x200];
static uint32_t old_audio(const uint8_t* r, uint32_t a) { return (uint32_t)r[a] << 24 | (uint32_t)r[a + 1] << 16 | (uint32_t)r[a + 2] << 8 | r[a + 3]; }
static uint32_t new_audio(const uint8_t* r, uint32_t a) { return (uint32_t)r[(a) ^ 3] << 24 | (uint32_t)r[(a + 1) ^ 3] << 16 | (uint32_t)r[(a + 2) ^ 3] << 8 | r[(a + 3) ^ 3]; }
static uint32_t old_word(const uint8_t* p) { return (uint32_t)p[0] << 24 | (uint32_t)p[1] << 16 | (uint32_t)p[2] << 8 | p[3]; }
static uint32_t new_word(const uint8_t* p) { return (uint32_t)p[3] << 24 | (uint32_t)p[2] << 16 | (uint32_t)p[1] << 8 | p[0]; }
static uint32_t old_post(const uint8_t* r, uint32_t f, uint32_t n) { uint32_t v = 0; for (uint32_t i = 0; i < n; ++i) v = v << 8 | r[f + i]; return v; }
static uint32_t new_post(const uint8_t* r, uint32_t f, uint32_t n) { uint32_t v = 0; for (uint32_t i = 0; i < n; ++i) v = v << 8 | r[(f + i) ^ 3u]; return v; }
int main() {
    const uint32_t w = 0x11223344u; memcpy(ram + 0x100, &w, 4);       // guest word at 0x100 = native u32
    const uint32_t w2 = 0x00CDAB00u; memcpy(ram + 0x104, &w2, 4);     // guest bytes 0x104..7 = 00 CD AB 00 -> byte 0x105 = 0xCD, 0x106 = 0xAB
    int ok = 0, n = 0;
    auto chk = [&](const char* what, uint32_t got, uint32_t want, bool expect_eq) {
        const bool pass = (got == want) == expect_eq; ok += pass; ++n;
        printf("[s7601-w] %-34s got=0x%08X %s 0x%08X -> %s\n", what, got, expect_eq ? "==" : "!=", want, pass ? "PASS" : "FAIL"); };
    chk("ref rs64_rdram_u32", rs64_rdram_u32(ram, 0x100), w, true);
    chk("ref rs64_rdram_u8 0x106", rs64_rdram_u8(ram, 0x106), 0xAB, true);
    chk("ctl OLD audio_read_rdram_word", old_audio(ram, 0x100), w, false);
    chk("NEW audio_read_rdram_word", new_audio(ram, 0x100), w, true);
    chk("ctl OLD upstream word()", old_word(ram + 0x100), w, false);
    chk("NEW upstream word()", new_word(ram + 0x100), w, true);
    chk("ctl OLD main post len4", old_post(ram, 0x100, 4), w, false);
    chk("NEW main post len4", new_post(ram, 0x100, 4), w, true);
    chk("ctl OLD main post len1 @0x106", old_post(ram, 0x106, 1), 0xAB, false);
    chk("NEW main post len1 @0x106", new_post(ram, 0x106, 1), 0xAB, true);
    printf("[s7601-w] %d/%d\n", ok, n);
    return ok == n ? 0 : 1;
}
