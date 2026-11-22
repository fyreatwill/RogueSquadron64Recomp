// s7814: live ares VMOV<e>/VSAR<e> (librecomp rsp_vu_impl.hpp) vs cxd4 (rs64-oracle mupen64plus-rsp-cxd4, non-SSE
// path, extracted verbatim by run.sh). Element broadcast for the reference is written here from the RSP manual, not
// taken from either emulator. The whole ares vpu struct is compared after every op (catches stray writes to
// VCO/VCC/VCE/other registers/accumulator slices), for every e 0..15, every de 0..7, vd!=vt and vd==vt aliasing.
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <cstdlib>
#include "rsp_vu.hpp"
static uint8_t g_dm[0x2000];
#define RS64_DMEM_BASE g_dm
extern "C" int rs64_g1e_dmem; int rs64_g1e_dmem = 1;
#define RS64_RSP_HOOKS_GATE rs64_rsp_hooks_on
extern "C" int rs64_rsp_hooks_on; int rs64_rsp_hooks_on = 0;
extern "C" void rs64_m5_audio_dmem_store(uint32_t, uint32_t, uint32_t, uint32_t) {}
extern "C" void rs64_m5_audio_dmem_vector_store(uint32_t, uint32_t, uint32_t) {}
extern "C" void rs64_spike_sdv_note(uint32_t, uint32_t, const uint32_t*) {}
extern "C" int rs64_sdv_snap_enabled(void) { return 0; }
extern "C" int rs64_vu_ring_enabled(void) { return 0; }
extern "C" void rs64_vld_note(uint32_t, uint32_t, const char*) {}
extern "C" void rs64_vu_ring_vte(uint32_t, const uint16_t*) {}
extern "C" uint32_t rs64_vu_ring_prev_vd(void) { return 0; }
extern "C" void rs64_vu_ring_capture_prev(const uint16_t*) {}
extern "C" void rs64_vu_ring_push(uint32_t, uint32_t, uint32_t, const uint16_t*) {}
#include "dmem_block.inc"
uint16_t rspReciprocals[512], rspInverseSquareRoots[512];
#include "rsp_vu_impl.hpp"
// ---- cxd4 reference environment (non-SSE build of vu.h) ----
typedef int16_t i16; typedef int32_t i32; typedef i16 *pi16; typedef pi16 v16;
#define VECTOR_OPERATION void
#define COMPILER_FENCE()
#define HI 0
#define MD 1
#define LO 2
static i16 VR[32][8], VACC[3][8], V_result[8];
#define VACC_L (VACC[LO])
static uint32_t inst_word;
static void message(const char*) {}
#define vector_copy(vd, vs) { for (int _i = 0; _i < 8; _i++) (vd)[_i] = (vs)[_i]; }
#define vector_wipe(vd) { for (int _i = 0; _i < 8; _i++) (vd)[_i] = 0; }
#include "cxd4_ops.inc"
// RSP manual element selection: lane i of vt(e).
static int esel(int e, int i) {
    if (e <= 1) return i;
    if (e <= 3) return (i & ~1) | (e - 2);
    if (e <= 7) return (i & ~3) | (e - 4);
    return e - 8;
}
static uint64_t rs = 0x9E3779B97F4A7C15ull;
static uint64_t rnd() { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static RSP R;
static long g_cmp = 0, g_bad = 0;
static void edge(uint16_t &h) { uint64_t k = rnd() & 15; static const uint16_t E[] = {0, 1, 0x7FFF, 0x8000, 0xFFFF, 0x8001};
    h = k < 6 ? E[k] : (uint16_t)rnd(); }
static void randstate() {
    uint16_t *p = (uint16_t*)&R.vpu; for (size_t i = 0; i < sizeof(R.vpu) / 2; i++) edge(p[i]);
}
// ares element i <-> cxd4/manual element i
static void to_ref() {
    for (int r = 0; r < 32; r++) for (int i = 0; i < 8; i++) VR[r][i] = (i16)R.vpu.r[r].u16(i);
    for (int i = 0; i < 8; i++) { VACC[HI][i] = (i16)R.vpu.acch.u16(i); VACC[MD][i] = (i16)R.vpu.accm.u16(i); VACC[LO][i] = (i16)R.vpu.accl.u16(i); }
}
static void from_ref(RSP::VU &x) {
    for (int r = 0; r < 32; r++) for (int i = 0; i < 8; i++) x.r[r].u16(i) = (uint16_t)VR[r][i];
    for (int i = 0; i < 8; i++) { x.acch.u16(i) = VACC[HI][i]; x.accm.u16(i) = VACC[MD][i]; x.accl.u16(i) = VACC[LO][i]; }
}
template<int E> static void one(int which, int de, int vd, int vt, long &bad, long &n) {
    randstate(); to_ref(); RSP::VU before = R.vpu;
    i16 vte[8]; for (int i = 0; i < 8; i++) vte[i] = VR[vt][esel(E, i)];
    if (which == 0) {
        inst_word = (0x12u << 26) | (1u << 25) | ((uint32_t)E << 21) | ((uint32_t)vt << 16) | ((uint32_t)de << 11) | ((uint32_t)vd << 6) | 0x33;
        VMOV(nullptr, vte);
        R.VMOV<E>(R.vpu.r[vd], (u8)de, R.vpu.r[vt]);
    } else {
        int vs = (int)(rnd() & 31);
        inst_word = (0x12u << 26) | (1u << 25) | ((uint32_t)E << 21) | ((uint32_t)vt << 16) | ((uint32_t)vs << 11) | ((uint32_t)vd << 6) | 0x1D;
        VSAW(VR[vs], vte); vector_copy(VR[vd], V_result);   // cxd4 dispatcher: VR[vd] = V_result
        R.VSAR<E>(R.vpu.r[vd], R.vpu.r[vs]);
    }
    RSP::VU exp = before; from_ref(exp); n++;
    if (memcmp(&exp, &R.vpu, sizeof exp)) { if (bad < 3) {
        fprintf(stderr, "  diff %s<%d> de=%d vd=%d vt=%d\n", which ? "VSAR" : "VMOV", E, de, vd, vt); } bad++; }
}
template<int E> static void op_e(int reps) {
    long bm = 0, nm = 0, bs = 0, ns = 0;
    for (int r = 0; r < reps; r++) for (int de = 0; de < 8; de++) {
        int vd = (int)(rnd() & 31), vt = (int)(rnd() & 31); if (vt == vd) vt = (vt + 1) & 31;
        one<E>(0, de, vd, vt, bm, nm); one<E>(0, de, vd, vd, bm, nm);   // distinct + aliased
        one<E>(1, de, vd, vt, bs, ns); one<E>(1, de, vd, vd, bs, ns);
    }
    printf("VMOV<%2d> %ld/%ld bad   VSAR<%2d> %ld/%ld bad\n", E, bm, nm, E, bs, ns);
    g_cmp += nm + ns; g_bad += bm + bs;
}
template<int... Es> static void all(int reps) { (op_e<Es>(reps), ...); }
int main(int argc, char **argv) {
    int reps = argc > 1 ? atoi(argv[1]) : 4000;
    all<0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15>(reps);
    printf("[s7814] compares=%ld bad=%ld -> %s\n", g_cmp, g_bad, g_bad ? "DIFFER" : "IDENTICAL");
    return g_bad ? 1 : 0;
}
