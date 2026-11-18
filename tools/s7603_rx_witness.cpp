// s7603 class RX known-value witness: drives the REAL librecomp _return<T> helper and the REAL ultramodern
// osVirtualToPhysical, then compares r2 the way recompiled code does (64-bit beq against a lui-built constant,
// i.e. (gpr)(int32_t)K). Positive control: the zero-extended store form must FAIL the same compare.
// Build: c++ -std=c++20 -I lib/N64ModernRuntime/N64Recomp/include -I lib/N64ModernRuntime/librecomp/include \
//   -I lib/N64ModernRuntime/ultramodern/include tools/s7603_rx_witness.cpp lib/N64ModernRuntime/ultramodern/src/misc_ultra.cpp -o /tmp/s7603w && /tmp/s7603w
#include <cstdio>
#include <cstdint>
#include "librecomp/helpers.hpp"
int main() {
    recomp_context c{}; int ok = 0, n = 0;
    auto chk = [&](const char* what, bool cond) { ++n; ok += cond; std::printf("%-58s %s\n", what, cond ? "ok" : "FAIL"); };
    const gpr lui_k = (gpr)(int32_t)0x80001000u;                 // what `lui t0,0x8000; ori t0,0x1000` leaves in t0
    _return<uint32_t>(&c, 0x80001000u); chk("_return<u32>(0x80001000) == lui constant (beq taken)", c.r2 == lui_k);
    _return<s32>(&c, -1);              chk("_return<s32>(-1) == 0xFFFFFFFFFFFFFFFF", c.r2 == ~(gpr)0);
    _return<uint16_t>(&c, 0xFFFF);      chk("_return<u16>(0xFFFF) == 0xFFFF (lhu semantics)", c.r2 == 0xFFFF);
    _return<float>(&c, 1.5f);           chk("_return<float>(1.5) -> f0.fl", c.f0.fl == 1.5f);
    c.r2 = (uint32_t)0x80001000u;       chk("CONTROL zero-extended store != lui constant (beq not taken)", c.r2 != lui_k);
    c.r2 = (gpr)(int32_t)0x80001000u;   chk("(gpr)(int32_t) store == lui constant", c.r2 == lui_k);
    c.r2 = osVirtualToPhysical((int32_t)0x80123450u);
    chk("osVirtualToPhysical(0x80123450) == 0x00123450 (KSEG0, small)", c.r2 == 0x00123450u);
    c.r2 = osVirtualToPhysical((int32_t)0xA0123450u);
    chk("osVirtualToPhysical(0xA0123450) == 0x00123450 (KSEG1)", c.r2 == 0x00123450u);
    c.r2 = osVirtualToPhysical(0);      chk("osVirtualToPhysical(0) == 0 (NULL yield ptr)", c.r2 == 0);
    std::printf("witness %d/%d\n", ok, n); return ok == n ? 0 : 1;
}
