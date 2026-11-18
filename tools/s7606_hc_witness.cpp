// s7606 class HC second source: compiles against the real recomp.h + ultramodern ultra64.h and checks, with the stack
// values the runtime logged ([m5-runtime-context] site=run_thread_function), the guest-call contract the census calls ok.
// c++ -std=c++20 -I../N64Recomp/include -Ilib/N64ModernRuntime/librecomp/include -Ilib/N64ModernRuntime/ultramodern/include
//    tools/s7606_hc_witness.cpp -o /tmp/s7606_w && /tmp/s7606_w
#include <cstdio>
#include <cstdint>
#include <type_traits>
#include <vector>
#include "recomp.h"
#include "ultramodern/ultra64.h"
static int pass = 0, n = 0;
#define CHECK(c, what) do { ++n; bool ok_ = (c); pass += ok_; std::printf("%s %s\n", ok_ ? "PASS" : "FAIL", what); } while (0)
static recomp_context rtf(uint64_t addr, uint64_t sp, uint64_t arg) {   // run_thread_function's ctx setup, verbatim
    (void)addr; recomp_context ctx{}; ctx.r29 = sp; ctx.r4 = arg; ctx.mips3_float_mode = 0; ctx.f_odd = &ctx.f0.u32h; return ctx;
}
int main() {
    std::vector<uint8_t> ram(0x800000); uint8_t* rdram = ram.data();
    CHECK((std::is_same_v<decltype(OSThread::sp), int32_t>), "real OSThread.sp is int32_t");
    const int32_t top = (int32_t)0x8010FED8u;                 // idle thread: logged sp 0x8010FEC8 = top - 0x10
    OSThread t{}; t.sp = top - 0x10;                          // osCreateThread
    const int32_t entry = (int32_t)0x800017A0u, arg = (int32_t)0x801546F0u;
    recomp_context c = rtf(entry, t.sp, arg);                 // _thread_func -> run_thread_function(PASS_RDRAM entrypoint, self->sp, arg)
    CHECK(c.r29 == 0xFFFFFFFF8010FEC8ull, "r29 sign-extended from int32 OSThread.sp");
    CHECK(c.r4 == 0xFFFFFFFF801546F0ull, "a0 sign-extended from PTR(void) arg");
    CHECK(&MEM_W(0, c.r29) == (int32_t*)(rdram + 0x10FEC8), "MEM_W(0, sp) lands on the logged stack slot");
    CHECK(c.f_odd == &c.f0.u32h && c.mips3_float_mode == 0 && c.r28 == 0 && c.r31 == 0, "FR=0, gp=0, ra=0 (never read live)");
    for (int i = 0; i < 4; ++i) MEM_W(i * 4, c.r29) = 0x11111111 * (i + 1);   // callee homes a0-a3 at 0..12(sp)
    const uintptr_t lo = (uintptr_t)(rdram + 0x10FEC8), hi = (uintptr_t)(rdram + (uint32_t)top - 0x80000000u);
    CHECK((uintptr_t)&MEM_W(12, c.r29) + 4 == hi && (uintptr_t)&MEM_W(0, c.r29) == lo, "o32 home slots fill exactly [top-16, top)");
    // controls: zero-extended sp, missing arg area
    recomp_context z{}; z.r29 = (uint64_t)(uint32_t)t.sp;
    CHECK((uintptr_t)(rdram + ((z.r29 + 0) - 0xFFFFFFFF80000000ull)) - (uintptr_t)rdram == 0x10010FEC8ull,
          "control: zero-extended r29 puts MEM_W 4 GB past rdram");
    recomp_context w = rtf(entry, top, arg);
    CHECK((uintptr_t)&MEM_W(0, w.r29) == hi, "control: without -0x10 the a0 home slot is at the stack top (outside the stack)");
    recomp_context b{}; b.r29 = S32(0x803Fu << 16); b.r29 = b.r29 | 0xFFF0;   // recomp_entrypoint's first two statements
    CHECK(b.r29 == 0xFFFFFFFF803FFFF0ull && &MEM_W(0, b.r29) == (int32_t*)(rdram + 0x3FFFF0), "boot entry sets a valid sp itself");
    std::printf("witness %d/%d\n", pass, n);
    return pass == n ? 0 : 1;
}
