// s7604 class RA second source: compiles against the real recomp.h / helpers.hpp / ultra64.h and checks, with known
// sign-extended guest register values, the read idioms the census calls ok and the two it calls wrong.
// c++ -std=c++20 -I../N64Recomp/include -Ilib/N64ModernRuntime/librecomp/include -Ilib/N64ModernRuntime/ultramodern/include
//    tools/s7604_ra_witness.cpp -o /tmp/s7604_w && /tmp/s7604_w
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <vector>
#include "recomp.h"
#include "librecomp/helpers.hpp"
static int pass = 0, n = 0;
#define CHECK(c, what) do { ++n; bool ok_ = (c); pass += ok_; std::printf("%s %s\n", ok_ ? "PASS" : "FAIL", what); } while (0)
int main() {
    std::vector<uint8_t> ram(0x800000); uint8_t* rdram = ram.data();
    recomp_context c{}; recomp_context* ctx = &c;
    ctx->r4 = (gpr)(int32_t)0x80114388;  // lui/addiu result: sign-extended KSEG0 pointer
    ctx->r5 = (gpr)(int32_t)0x80000010;  // a u32 size >= 2 GB as the guest holds it
    CHECK(!(ctx->r4 == 0x80114388u), "control: raw gpr == u32 constant is FALSE (the BAD idiom)");
    CHECK((uint32_t)ctx->r4 == 0x80114388u, "ok-cast: (uint32_t)ctx->r4 == constant");
    CHECK(U32(ctx->r4) == 0x80114388u, "ok-cast: U32()");
    CHECK((_arg<0, u32>(rdram, ctx)) == 0x80114388u, "_arg<0,u32> truncates");
    MEM_W(0, ctx->r4) = 0x12345678;
    CHECK(*(uint32_t*)(rdram + 0x114388) == 0x12345678u, "ok-macro: MEM_W(0, sext r4) hits rdram+0x114388");
    CHECK(TO_PTR(uint32_t, ctx->r4) == (uint32_t*)(rdram + 0x114388), "ok-macro: TO_PTR(sext r4)");
    CHECK(TO_PTR(uint32_t, (gpr)0x80114388u) == (uint32_t*)(rdram + 0x114388), "TO_PTR also takes the zero-extended form");
    CHECK((uint32_t)(ctx->r4 >> 16) != 0x8011u, "control: (uint32_t)(r4 >> 16) pulls sign fill (the BAD idiom)");
    uint64_t pair = (ctx->r4 << 32) | ((ctx->r5 << 0) & 0xFFFFFFFFu);
    CHECK(pair == 0x8011438880000010ull, "ok-hilo: (hi << 32) | (lo & 0xFFFFFFFF) pair idiom");
    CHECK((size_t)ctx->r5 != 0x80000010u, "control: (size_t)r5 is 0xFFFFFFFF80000010 (old recomp_alloc size)");
    CHECK((size_t)(uint32_t)ctx->r5 == 0x80000010u, "fix: (size_t)(uint32_t)r5 is the real size");
    uint8_t* fake_null = nullptr;
    uint32_t old_off = (uint32_t)(fake_null - rdram);
    CHECK(old_off != 0 || rdram == nullptr, "control: old recomp_alloc NULL path returns a nonzero junk offset");
    std::printf("witness %d/%d\n", pass, n);
    return pass == n ? 0 : 1;
}
