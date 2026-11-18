// s7607 class UW second source, C++ half: the _thread_func / run_thread_function shape. A recomp_context is set up like
// run_thread_function, the C chain (tools/s7607_uw_witness.c) is called inside try { } catch (thread_terminated&), and
// the host stub throws. PASS = catch reached, code after the call in every C frame skipped, a RAII lock_guard held
// in the root's frame released. With the no-unwind-tables control object std::terminate() must fire instead (exit 134).
#include <cstdio>
#include <mutex>
#include <exception>
#include "recomp.h"
namespace ultramodern { struct thread_terminated : std::exception {}; }   // same shape as ultramodern.hpp:86
extern "C" void s7607_entry(uint8_t* rdram, recomp_context* ctx);
extern "C" volatile int s7607_after;
extern "C" void s7607_destroy_recomp(uint8_t*, recomp_context* ctx) {
    if (ctx->r4 == 0) throw ultramodern::thread_terminated{};               // osDestroyThread: t_ == thread_self
}
static std::mutex mu;
int main() {
    static uint8_t ram[0x200000]; uint8_t* rdram = ram;
    recomp_context ctx{}; ctx.r29 = (gpr)(int32_t)0x8010FEC8; ctx.r4 = 1; ctx.mips3_float_mode = 0; ctx.f_odd = &ctx.f0.u32h;
    bool caught = false;
    try { std::lock_guard<std::mutex> lk(mu); s7607_entry(rdram, &ctx); }
    catch (ultramodern::thread_terminated&) { caught = true; }
    const bool unlocked = mu.try_lock(); if (unlocked) mu.unlock();
    std::printf("caught=%d after=%d unlocked=%d\n", (int)caught, (int)s7607_after, (int)unlocked);
    return (caught && s7607_after == 0 && unlocked) ? 0 : 1;
}
