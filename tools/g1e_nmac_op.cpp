// s6941 G1e: one arm of the NEON multiply-op equivalence check (tools/g1e_nmac_equiv.zsh compiles it twice:
// RS64_RSP_NEON_MAC=0 -> SSE-via-sse2neon bodies, =1 -> native NEON bodies). in: vs[8] vt[8] acch[8] accm[8] accl[8] as
// lane index n (u16(n)); out: vd[8] acch[8] accm[8] accl[8].
#define RS64_RSP_HOOKS_GATE 0
#define RS64_DMEM_BASE rs64_eq_dmem
#include <cstdint>
static uint8_t rs64_eq_dmem[0x1000];
#include "librecomp/rsp.hpp"
#include "librecomp/rsp_vu_impl.hpp"
#define CAT2(a, b) a##b
#define CAT(a, b) CAT2(a, b)
template<int E> static void call(RSP& r, int op) {
    auto& v = r.vpu.r;
    switch (op) {
    case 0: r.VMUDN<E>(v[3], v[1], v[2]); break;
    case 1: r.VMUDM<E>(v[3], v[1], v[2]); break;
    case 2: r.VMUDH<E>(v[3], v[1], v[2]); break;
    case 3: r.VMADL<E>(v[3], v[1], v[2]); break;
    case 4: r.VMADN<E>(v[3], v[1], v[2]); break;
    case 5: r.VMADM<E>(v[3], v[1], v[2]); break;
    case 6: r.VMADH<E>(v[3], v[1], v[2]); break;
    // in-place forms (vd aliases vs / vt), as the ucode uses them
    case 7: r.VMADN<E>(v[1], v[1], v[2]); break;
    case 8: r.VMADH<E>(v[2], v[1], v[2]); break;
    }
}
extern "C" void CAT(rs64_eq_run_, TAG)(const uint16_t* in, int op, int e, uint16_t* out) {
#ifdef RS64_EQ_MUTANT  // positive control: this arm runs the neighbouring op, the check must fail
    op = op == 4 ? 5 : op;
#endif
    static RSP r;
    for (int n = 0; n < 8; n++) {
        r.vpu.r[1].u16(n) = in[n]; r.vpu.r[2].u16(n) = in[8 + n];
        r.vpu.acch.u16(n) = in[16 + n]; r.vpu.accm.u16(n) = in[24 + n]; r.vpu.accl.u16(n) = in[32 + n];
        r.vpu.r[3].u16(n) = 0x5A5A;
    }
    switch (e) {
#define E(x) case x: call<x>(r, op); break;
    E(0) E(1) E(2) E(3) E(4) E(5) E(6) E(7) E(8) E(9) E(10) E(11) E(12) E(13) E(14) E(15)
    }
    int vd = op == 7 ? 1 : op == 8 ? 2 : 3;
    for (int n = 0; n < 8; n++) {
        out[n] = r.vpu.r[vd].u16(n); out[8 + n] = r.vpu.acch.u16(n); out[16 + n] = r.vpu.accm.u16(n); out[24 + n] = r.vpu.accl.u16(n);
    }
}
// s6941: BENCH=1 timing loop, 64 dependent ops per call on the resident state (accumulators chain), e = 8
extern "C" uint16_t CAT(rs64_eq_bench_, TAG)(int op, long iters) {
    static RSP r; auto& v = r.vpu.r;
    for (int n = 0; n < 8; n++) { v[1].u16(n) = 0x1234 + n * 77; v[2].u16(n) = 0xF00D - n * 33; }
    for (long i = 0; i < iters; i++) for (int k = 0; k < 64; k++) {
        switch (op) {
        case 0: r.VMUDN<8>(v[3], v[1], v[2]); r.VMADN<8>(v[1], v[3], v[2]); break;
        case 1: r.VMADH<8>(v[3], v[1], v[2]); r.VMADH<8>(v[1], v[3], v[2]); break;
        case 2: r.VMADM<8>(v[3], v[1], v[2]); r.VMADM<8>(v[1], v[3], v[2]); break;
        case 3: r.VMADN<8>(v[3], v[1], v[2]); r.VMADN<8>(v[1], v[3], v[2]); break;
        }
        asm volatile("" ::: "memory");
    }
    return v[1].u16(0) ^ r.vpu.accl.u16(3);
}
