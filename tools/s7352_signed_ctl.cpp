// s7352 class AC standalone control: the RSP VRCP/VRSQ magnitude step from librecomp rsp_vu_impl.hpp (copied verbatim below;
// tools/s7352_signed_census.py checks the header still carries these lines). Build with -fsanitize=signed-integer-overflow
// -fno-sanitize-recover. Arm "guarded" (the real code) must run every input clean, including INT_MIN = DIVIN 0x8000 : 0x0000.
// Arm "unguarded" (the same step without `if (input > -32768)`) is the positive control: UBSan must abort it at INT_MIN.
#include <cstdint>
#include <cstdio>
#include <cstring>
typedef int32_t s32;
static s32 guarded(s32 input) {
    s32 mask = input >> 31;
    s32 data = input ^ mask;
    if (input > -32768) data -= mask;
    return data;
}
static s32 unguarded(s32 input) {
    s32 mask = input >> 31;
    s32 data = input ^ mask;
    data -= mask;
    return data;
}
int main(int argc, char** argv) {
    const bool ctl = argc > 1 && !strcmp(argv[1], "unguarded");
    volatile uint32_t sink = 0;
    uint64_t n = 0;
    // every 16-bit single-precision input, every DIVIN:low double-precision edge, and a 2^24-stride sweep of all 32-bit inputs
    for (int32_t v = -32768; v <= 32767; v++, n++) sink = sink + (uint32_t)(ctl ? unguarded(v) : guarded(v));
    const uint32_t edges[] = {0x80000000u, 0x80000001u, 0x7FFFFFFFu, 0xFFFF8000u, 0xFFFF7FFFu, 0xFFFFFFFFu, 0u, 1u, 0x8000FFFFu};
    for (uint32_t e : edges) { sink += ctl ? unguarded((s32)e) : guarded((s32)e); n++; }
    for (uint64_t u = 0; u <= 0xFFFFFFFFull; u += 0x101u) { sink += ctl ? unguarded((s32)(uint32_t)u) : guarded((s32)(uint32_t)u); n++; }
    std::printf("[s7352-ctl] %s: %llu inputs clean (INT_MIN included)\n", ctl ? "unguarded" : "guarded", (unsigned long long)n);
    return 0;
}
