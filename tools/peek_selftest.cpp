// s5230 positive control for src/main/rs64_rdram_peek.h.
// Build+run: clang++ -std=c++17 -I src/main tools/peek_selftest.cpp -o /tmp/peek && /tmp/peek
#include "rs64_rdram_peek.h"
#include <cstdio>
int main() {
    alignas(4) uint8_t r[8] = {0};
    const uint8_t g[8] = {0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0};
    for (int a = 0; a < 8; a++) r[a ^ 3] = g[a];  // MEM_B-style store
    bool ok = rs64_rdram_u32(r, 0) == 0x12345678u && rs64_rdram_u32(r, 4) == 0x9ABCDEF0u &&
              rs64_rdram_u8(r, 5) == 0xBC;
    uint32_t naive = (uint32_t)r[0] << 24 | r[1] << 16 | r[2] << 8 | r[3];  // old pattern
    printf("helper_ok=%d old_pattern=0x%08X (expect 0x78563412)\n", ok, naive);
    return (!ok || naive != 0x78563412u);
}
