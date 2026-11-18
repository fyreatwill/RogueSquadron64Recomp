// s7605 class FR second source: compiles against the real recomp.h / helpers.hpp and checks, with known values, the FPR
// layout and views the census calls ok, plus the pre-s7605 recomphook_get_return_double body it calls BAD.
// c++ -std=c++20 -I../N64Recomp/include -Ilib/N64ModernRuntime/librecomp/include -Ilib/N64ModernRuntime/ultramodern/include
//    tools/s7605_fr_witness.cpp -o /tmp/s7605_w && /tmp/s7605_w
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <vector>
#include "recomp.h"
#include "librecomp/helpers.hpp"
static int pass = 0, n = 0;
#define CHECK(c, what) do { ++n; bool ok_ = (c); pass += ok_; std::printf("%s %s\n", ok_ ? "PASS" : "FAIL", what); } while (0)
static uint32_t bits(float f) { uint32_t u; std::memcpy(&u, &f, 4); return u; }
int main() {
    std::vector<uint8_t> ram(0x10000); uint8_t* rdram = ram.data();
    recomp_context c{}; recomp_context* ctx = &c;
    ctx->f_odd = &ctx->f0.u32h; ctx->mips3_float_mode = 0;   // FR=0, as run_thread_function / reset set it
    CHECK(sizeof(fpr) == 8 && offsetof(recomp_context, f1) - offsetof(recomp_context, f0) == 8, "fpr is one 64-bit slot");
    ctx->f12.d = 1.5;
    uint64_t u; std::memcpy(&u, &ctx->f12.d, 8);
    CHECK(ctx->f12.u32l == (uint32_t)u && ctx->f12.u32h == (uint32_t)(u >> 32), "double lives whole in f12.d (u32l/u32h halves)");
    CHECK(&ctx->f_odd[(13 - 1) * 2] == &ctx->f12.u32h, "FR=0: odd f13 moves alias f12.u32h (high half of the f12 double)");
    ctx->f_odd = &ctx->f1.u32l;
    CHECK(&ctx->f_odd[(13 - 1) * 2] == &ctx->f13.u32l, "FR=1: odd f13 moves alias f13.u32l");
    ctx->f_odd = &ctx->f0.u32h;
    ctx->f12.fl = 0.75f;
    CHECK((_arg<0, float>(rdram, ctx)) == 0.75f, "_arg<0,float> = f12.fl");
    ctx->r5 = (gpr)(int32_t)bits(-2.5f);                    // sign-extended float bits in a1 (int arg0, float arg1)
    CHECK(_arg_float_a1(rdram, ctx) == -2.5f, "_arg_float_a1 reinterprets sign-extended a1 bits");
    ctx->f14.fl = 3.0f;
    CHECK(_arg_float_f14(rdram, ctx) == 3.0f, "_arg_float_f14 = f14.fl");
    _return(ctx, 6.25f);
    CHECK(ctx->f0.fl == 6.25f, "_return<float> writes f0.fl");
    recomp_context h{}; h.f0.d = 3.25;                       // hooked function returned 3.25 (double)
    recomp_context o{};
    o.f0.fl = (gpr)(uint8_t)h.f0.fl; o.f1.fl = (gpr)(uint8_t)h.f1.fl;   // pre-s7605 body
    CHECK(o.f0.d != 3.25, "control: pre-s7605 recomphook_get_return_double loses the value");
    recomp_context f{}; f.f0.d = h.f0.d;                     // s7605 body
    CHECK(f.f0.d == 3.25, "fix: f0.d copy returns 3.25");
    float fm = 1234.5f; ctx->f4.fl = fm;
    CHECK(ctx->f4.fl == fm && ctx->f4.u32l == bits(fm), "s6904 fog hook: .fl write is what trunc.w.s $f4 (f4.fl) reads");
    std::printf("witness %d/%d\n", pass, n);
    return pass == n ? 0 : 1;
}
