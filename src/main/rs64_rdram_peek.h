#pragma once
// Host-side diagnostic reads of guest RDRAM. rdram[] is stored word-swapped
// (guest byte at offset a lives at rdram[a ^ 3], as MEM_B does), so a raw
// rdram[p] or a hand-composed rdram[p]<<24|rdram[p+1]<<16... read returns a
// byte-reversed value. Use these for every census/probe read (s5229, s5230).
#include <cstdint>
static inline uint32_t rs64_rdram_u8(const volatile uint8_t* rdram, uint32_t phys) {
    return rdram[phys ^ 3u];
}
static inline uint32_t rs64_rdram_u32(const volatile uint8_t* rdram, uint32_t phys) {
    const uint32_t b = phys & ~3u;  // guest byte b+k is at rdram[b + (3 - k)]
    return (uint32_t(rdram[b + 3]) << 24) | (uint32_t(rdram[b + 2]) << 16) |
           (uint32_t(rdram[b + 1]) << 8) | uint32_t(rdram[b]);
}
