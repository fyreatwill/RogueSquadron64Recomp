// s6941 G1e: the lean gfx ucode arm (src/rsp/factor5_ucode_lean.cpp) with the native NEON multiply-op bodies
// (RS64_RSP_NEON_MAC=1 in librecomp rsp_vu_impl.hpp: VMUDN/VMUDM/VMUDH, VMADL/VMADN/VMADM/VMADH). Those ops were 45% of
// the lean ucode's host time (s6941 xctrace) and ran the SSE algorithm through sse2neon (3 ops per carry, 8 per clamp).
// Bit-exact against the SSE bodies: tools/g1e_nmac_equiv.zsh (43.2M cases, 0 mismatches; MUTANT=1 fails).
// main.cpp picks it over the lean arm unless ROGUESQ_G1E_NMAC=0 (default on since s6941); ROGUESQ_G1E_NMAC_TOGGLE=<sec> flips them.
#define RS64_RSP_HOOKS_GATE 0
#define RS64_G1E_PROBES_ON 0
#define RS64_RSP_NEON_MAC 1
#define factor5_ucode factor5_ucode_nmac
#include "../../build/factor5_ucode/factor5_ucode_recompiled.c"

// s7468 class DY: planted positive control for the ucode-instrumented ASan arm (tools/build_asan.sh UCODE=1, which sets
// ROGUESQ_ASAN_UCODE=ON). It lives in THIS TU so it carries exactly the ucode TUs' sanitizer flags: with the CMakeLists
// exemption (-fno-sanitize=address,undefined) it reports nothing; instrumented, it reports one global-buffer-overflow READ
// one byte past dmem (the DMEM array the ucode indexes) and one signed-int overflow. main.cpp calls it only in an ASan build
// and only under ROGUESQ_S7468_UCODE_PLANT=1. Scored by tools/s7467_san_report.py --uplant <arm>.
#include <cstdio>
extern "C" __attribute__((noinline)) void rs64_s7468_ucode_plant(unsigned idx) {
    volatile unsigned char c = dmem[idx];            // s7468 UCODE PLANT global-buffer-overflow (idx = 0x1000 = sizeof dmem)
    volatile int big = 0x7FFFFFFF; volatile int one = (int)(idx >> 12);
    volatile int ov = big + one;                     // s7468 UCODE PLANT signed-integer-overflow
    std::fprintf(stderr, "[s7468] ucode plant fired c=%d ov=%d\n", (int)c, (int)ov);
}
