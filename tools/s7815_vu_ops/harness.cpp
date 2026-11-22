// s7815: every elementwise VU op the LLE gfx ucode compiles (plus their non-live siblings) - live ares bodies from
// librecomp rsp_vu_impl.hpp vs cxd4 (rs64-oracle mupen64plus-rsp-cxd4 vu/*.c compiled UNMODIFIED as a separate C unit,
// non-SSE path). Element broadcast for the reference is written here from the RSP manual. After every op the WHOLE ares
// vpu struct (32 regs, ACCH/ACCM/ACCL, VCOH/VCOL/VCCH/VCCL/VCE) is compared against the cxd4 state mapped back.
// Every e 0..15, distinct and vd==vs / vd==vt / vs==vt aliasing, random + edge inputs (0,1,7FFF,8000,FFFF,8001).
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
// ---- cxd4 (vu.c globals, non-SSE: VR is [32][16] with VR_STATIC_WRAPAROUND) ----
typedef int16_t i16; using r128 = RSP::r128; using cr128 = RSP::cr128;
extern "C" {
#ifndef CX_SSE
#define CX_SSE 0
#endif
#if CX_SSE
typedef int64x2_t cxv;   // cxd4 ARCH_MIN_SSE2 path via its bundled sse2neon: ops take/return a 128-bit vector
#define X(n) cxv n(cxv, cxv);
#else
extern i16 V_result[8];
#define X(n) void n(i16*, i16*);
#endif
extern i16 VR[32][16], VACC[3][8], cf_ne[8], cf_co[8], cf_clip[8], cf_comp[8], cf_vce[8];
uint32_t inst_word; void message(const char*) {}
X(mulf_v_msp) X(mulu_v_msp) X(mudl_v_msp) X(mudm_v_msp) X(mudn_v_msp) X(mudh_v_msp) X(macf_v_msp) X(macu_v_msp)
X(madl_v_msp) X(madm_v_msp) X(madn_v_msp) X(madh_v_msp) X(add_v_msp) X(sub_v_msp) X(abs_v_msp) X(addc_v_msp)
X(subc_v_msp) X(lt_v_msp) X(eq_v_msp) X(ne_v_msp) X(ge_v_msp) X(cl_v_msp) X(ch_v_msp) X(cr_v_msp) X(mrg_v_msp)
X(and_v_msp) X(nand_v_msp) X(or_v_msp) X(nor_v_msp) X(xor_v_msp) X(nxor_v_msp)
#undef X
}
enum { HI = 0, MD = 1, LO = 2 };
static int esel(int e, int i) {   // RSP manual: lane i of vt(e)
    if (e <= 1) return i;
    if (e <= 3) return (i & ~1) | (e - 2);
    if (e <= 7) return (i & ~3) | (e - 4);
    return e - 8;
}
static uint64_t rs = 0x9E3779B97F4A7C15ull;
static uint64_t rnd() { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static RSP R;
static uint16_t edge() { uint64_t k = rnd() & 15; static const uint16_t E[] = {0, 1, 0x7FFF, 0x8000, 0xFFFF, 0x8001};
    return k < 6 ? E[k] : (uint16_t)rnd(); }
static void randstate() {
    for (int r = 0; r < 32; r++) for (int i = 0; i < 8; i++) R.vpu.r[r].u16(i) = edge();
    for (int i = 0; i < 8; i++) { R.vpu.acch.u16(i) = edge(); R.vpu.accm.u16(i) = edge(); R.vpu.accl.u16(i) = edge(); }
    r128 *f[5] = {&R.vpu.vcoh, &R.vpu.vcol, &R.vpu.vcch, &R.vpu.vccl, &R.vpu.vce};
    for (auto *p : f) for (int i = 0; i < 8; i++) p->u16(i) = (rnd() & 1) ? 0xFFFF : 0;
}
static i16 *CF[5] = {cf_ne, cf_co, cf_clip, cf_comp, cf_vce};
static void to_ref() {
    memset(VR, 0, sizeof VR);
    for (int r = 0; r < 32; r++) for (int i = 0; i < 8; i++) VR[r][i] = (i16)R.vpu.r[r].u16(i);
    for (int i = 0; i < 8; i++) { VACC[HI][i] = (i16)R.vpu.acch.u16(i); VACC[MD][i] = (i16)R.vpu.accm.u16(i); VACC[LO][i] = (i16)R.vpu.accl.u16(i); }
    r128 *f[5] = {&R.vpu.vcoh, &R.vpu.vcol, &R.vpu.vcch, &R.vpu.vccl, &R.vpu.vce};
    for (int k = 0; k < 5; k++) for (int i = 0; i < 8; i++) CF[k][i] = f[k]->u16(i) ? 1 : 0;
}
static void from_ref(RSP::VU &x) {
    for (int r = 0; r < 32; r++) for (int i = 0; i < 8; i++) x.r[r].u16(i) = (uint16_t)VR[r][i];
    for (int i = 0; i < 8; i++) { x.acch.u16(i) = VACC[HI][i]; x.accm.u16(i) = VACC[MD][i]; x.accl.u16(i) = VACC[LO][i]; }
    r128 *f[5] = {&x.vcoh, &x.vcol, &x.vcch, &x.vccl, &x.vce};
    for (int k = 0; k < 5; k++) for (int i = 0; i < 8; i++) f[k]->u16(i) = CF[k][i] ? 0xFFFF : 0;
}
static const char *fld(size_t off) {
    static char b[32]; size_t reg = off / 16, ln = (off % 16) / 2;
    static const char *nm[] = {"ACCH", "ACCM", "ACCL", "VCOH", "VCOL", "VCCH", "VCCL", "VCE"};
    if (reg < 32) snprintf(b, sizeof b, "v%zu[%zu]", reg, ln); else snprintf(b, sizeof b, "%s[%zu]", nm[reg - 32], ln);
    return b;
}
#if CX_SSE
typedef cxv (*CxOp)(cxv, cxv);
#else
typedef void (*CxOp)(i16*, i16*);
#endif
struct OpStat { long n = 0, bad = 0, alias_bad[4] = {0,0,0,0}; char ex[512] = ""; char first[256] = ""; unsigned fieldmask = 0; };
// fieldmask bits: 0 vd/reg, 1 ACCH, 2 ACCM, 3 ACCL, 4 VCO, 5 VCC, 6 VCE
static int g_alias = 0;
template<int E, typename F> static void one(const char *name, F ares, CxOp cx, int vd, int vs, int vt, OpStat &st) {
    randstate(); to_ref(); RSP::VU before = R.vpu;
    i16 vte[8]; for (int i = 0; i < 8; i++) vte[i] = VR[vt][esel(E, i)];
    inst_word = ((uint32_t)E << 21) | ((uint32_t)vt << 16) | ((uint32_t)vs << 11) | ((uint32_t)vd << 6);
#if CX_SSE
    { cxv a, b, r; memcpy(&a, VR[vs], 16); memcpy(&b, vte, 16); r = cx(a, b); memcpy(VR[vd], &r, 16); }
#else
    cx(VR[vs], vte); for (int i = 0; i < 8; i++) VR[vd][i] = V_result[i];   // cxd4 dispatcher: VR[vd] = V_result
#endif
    ares(R.vpu.r[vd], R.vpu.r[vs], R.vpu.r[vt]);
    RSP::VU exp = before; from_ref(exp); st.n++;
    const uint8_t *a = (const uint8_t*)&exp, *b = (const uint8_t*)&R.vpu; bool bad = false;
    for (size_t o = 0; o < sizeof exp; o += 2) if (memcmp(a + o, b + o, 2)) {
        bad = true; size_t reg = o / 16;
        st.fieldmask |= reg < 32 ? 1 : reg < 35 ? 1u << (reg - 31) : reg < 37 ? 16 : reg < 39 ? 32 : 64;
        if (!st.first[0]) snprintf(st.first, sizeof st.first, "e=%d vd=%d vs=%d vt=%d %s cxd4=%04X ares=%04X",
            E, vd, vs, vt, fld(o), *(const uint16_t*)(a + o), *(const uint16_t*)(b + o));
    }
    if (bad) { st.bad++; st.alias_bad[g_alias]++;
        if (g_alias == 0 && !st.ex[0]) { int L = 0; const RSP::VU &B = before;
            L += snprintf(st.ex + L, sizeof st.ex - L, "e=%d vs=", E); for (int i = 0; i < 8; i++) L += snprintf(st.ex + L, sizeof st.ex - L, "%04X ", B.r[vs].u16(i));
            L += snprintf(st.ex + L, sizeof st.ex - L, "vt="); for (int i = 0; i < 8; i++) L += snprintf(st.ex + L, sizeof st.ex - L, "%04X ", B.r[vt].u16(i));
            L += snprintf(st.ex + L, sizeof st.ex - L, "\n         acc(H,M,L)/vco(h,l)/vcc(h,l)/vce per lane:");
            for (int i = 0; i < 8; i++) L += snprintf(st.ex + L, sizeof st.ex - L, " %04X%04X%04X/%d%d/%d%d/%d", B.acch.u16(i), B.accm.u16(i), B.accl.u16(i),
                !!B.vcoh.u16(i), !!B.vcol.u16(i), !!B.vcch.u16(i), !!B.vccl.u16(i), !!B.vce.u16(i));
            L += snprintf(st.ex + L, sizeof st.ex - L, "\n         vd cxd4="); for (int i = 0; i < 8; i++) L += snprintf(st.ex + L, sizeof st.ex - L, "%04X ", exp.r[vd].u16(i));
            L += snprintf(st.ex + L, sizeof st.ex - L, " ares="); for (int i = 0; i < 8; i++) L += snprintf(st.ex + L, sizeof st.ex - L, "%04X ", R.vpu.r[vd].u16(i)); } }
}
#define OPS(X) \
 X(VMULF, mulf_v_msp, 1) X(VMULU, mulu_v_msp, 0) X(VMUDL, mudl_v_msp, 1) X(VMUDM, mudm_v_msp, 1) X(VMUDN, mudn_v_msp, 1) \
 X(VMUDH, mudh_v_msp, 1) X(VMACF, macf_v_msp, 0) X(VMACU, macu_v_msp, 0) X(VMADL, madl_v_msp, 1) X(VMADM, madm_v_msp, 1) \
 X(VMADN, madn_v_msp, 1) X(VMADH, madh_v_msp, 1) X(VADD, add_v_msp, 1) X(VSUB, sub_v_msp, 1) X(VABS, abs_v_msp, 1) \
 X(VADDC, addc_v_msp, 1) X(VSUBC, subc_v_msp, 1) X(VLT, lt_v_msp, 1) X(VEQ, eq_v_msp, 1) X(VNE, ne_v_msp, 1) \
 X(VGE, ge_v_msp, 1) X(VCL, cl_v_msp, 1) X(VCH, ch_v_msp, 1) X(VCR, cr_v_msp, 1) X(VMRG, mrg_v_msp, 1) \
 X(VAND, and_v_msp, 1) X(VNAND, nand_v_msp, 0) X(VOR, or_v_msp, 0) X(VNOR, nor_v_msp, 0) X(VXOR, xor_v_msp, 1) \
 X(VNXOR, nxor_v_msp, 1)
static long g_n = 0, g_bad_live = 0, g_bad_dead = 0;
template<int E> static void run_e(int reps, OpStat *S) {
    int k = 0;
#define X(OP, CX, LIVE) { auto f = [](r128 &d, cr128 &s, cr128 &t) { R.OP<E>(d, s, t); }; \
    for (int r = 0; r < reps; r++) { int vd = rnd() & 31, vs = rnd() & 31, vt = rnd() & 31; \
        while (vs == vd) vs = rnd() & 31; while (vt == vd || vt == vs) vt = rnd() & 31; \
        g_alias = 0; one<E>(#OP, f, CX, vd, vs, vt, S[k]); g_alias = 1; one<E>(#OP, f, CX, vd, vd, vt, S[k]); \
        g_alias = 2; one<E>(#OP, f, CX, vd, vs, vd, S[k]); g_alias = 3; one<E>(#OP, f, CX, vd, vs, vs, S[k]); } k++; }
    OPS(X)
#undef X
}
template<int... Es> static void all(int reps, OpStat *S) { (run_e<Es>(reps, S), ...); }
// ---- third arm: CEN64 (n64dev/cen64 arch/x86_64/rsp/*.h, header-only SSE kernels, copied unmodified by run.sh, run here
// through sse2neon) for the ops where ares and cxd4 disagree. Flag/acc write-back transcribed from cen64 rsp/vfunctions.c.
#if CEN64
#include "s7815_cen64/clamp.h"
#include "s7815_cen64/vabs.h"
#include "s7815_cen64/vch.h"
#include "s7815_cen64/vcr.h"
#include "s7815_cen64/vmrg.h"
#include "s7815_cen64/vmuln.h"
#include "s7815_cen64/vmull.h"
static __m128i ld(const r128 &x) { uint16_t a[8]; for (int i = 0; i < 8; i++) a[i] = x.u16(i); __m128i v; memcpy(&v, a, 16); return v; }
static void st(r128 &x, __m128i v) { uint16_t a[8]; memcpy(a, &v, 16); for (int i = 0; i < 8; i++) x.u16(i) = a[i]; }
struct CenStat { long n = 0, bad = 0; char first[200] = ""; };
template<int E> static void cen_one(int op, CenStat &cs) {
    randstate(); RSP::VU B = R.vpu, X = B; int vd = rnd() & 31, vs = rnd() & 31, vt = rnd() & 31;
    r128 vte_r; for (int i = 0; i < 8; i++) vte_r.u16(i) = B.r[vt].u16(esel(E, i));
    __m128i S = ld(B.r[vs]), T = ld(vte_r), Z = _mm_setzero_si128(), res, lo = ld(B.accl), md = ld(B.accm), hi = ld(B.acch);
    switch (op) {
    case 0: res = rsp_vabs(S, T, Z, &lo); st(X.accl, lo); R.VABS<E>(R.vpu.r[vd], R.vpu.r[vs], R.vpu.r[vt]); break;
    case 1: { __m128i ge, le, eq, sg, vce; res = rsp_vch(S, T, Z, &ge, &le, &eq, &sg, &vce);
        st(X.vcch, ge); st(X.vccl, le); st(X.vcoh, eq); st(X.vcol, sg); st(X.vce, vce); st(X.accl, res);
        R.VCH<E>(R.vpu.r[vd], R.vpu.r[vs], R.vpu.r[vt]); break; }
    case 2: { __m128i ge, le; res = rsp_vcr(S, T, Z, &ge, &le);
        st(X.vcch, ge); st(X.vccl, le); st(X.vcoh, Z); st(X.vcol, Z); st(X.vce, Z); st(X.accl, res);
        R.VCR<E>(R.vpu.r[vd], R.vpu.r[vs], R.vpu.r[vt]); break; }
    case 3: res = rsp_vmrg(S, T, ld(B.vccl)); st(X.vcoh, Z); st(X.vcol, Z); st(X.accl, res);
        R.VMRG<E>(R.vpu.r[vd], R.vpu.r[vs], R.vpu.r[vt]); break;
    case 4: res = rsp_vmadn_vmudn(0x8, S, T, Z, &lo, &md, &hi); st(X.accl, lo); st(X.accm, md); st(X.acch, hi);
        R.VMADN<E>(R.vpu.r[vd], R.vpu.r[vs], R.vpu.r[vt]); break;
    default: res = rsp_vmadl_vmudl(0x8, S, T, Z, &lo, &md, &hi); st(X.accl, lo); st(X.accm, md); st(X.acch, hi);
        R.VMADL<E>(R.vpu.r[vd], R.vpu.r[vs], R.vpu.r[vt]); break;
    }
    st(X.r[vd], res); cs.n++;
    if (memcmp(&X, &R.vpu, sizeof X)) { cs.bad++; if (!cs.first[0]) {
        const uint8_t *a = (const uint8_t*)&X, *b = (const uint8_t*)&R.vpu;
        for (size_t o = 0; o < sizeof X; o += 2) if (memcmp(a + o, b + o, 2)) { snprintf(cs.first, sizeof cs.first,
            "e=%d %s cen64=%04X ares=%04X", E, fld(o), *(const uint16_t*)(a + o), *(const uint16_t*)(b + o)); break; } } }
}
static CenStat g_cen[6];
template<int E> static void cen_e(int reps) { for (int op = 0; op < 6; op++) for (int r = 0; r < reps * 4; r++) cen_one<E>(op, g_cen[op]); }
template<int... Es> static void cen_all(int reps) { (cen_e<Es>(reps), ...); }
#endif
int main(int argc, char **argv) {
    int reps = argc > 1 ? atoi(argv[1]) : 1000;
    static OpStat S[64];
    all<0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15>(reps, S);
    int k = 0; long ops_live_bad = 0, ops_dead_bad = 0;
#define X(OP, CX, LIVE) { OpStat &s = S[k++]; g_n += s.n; (LIVE ? g_bad_live : g_bad_dead) += s.bad; \
    if (s.bad) (LIVE ? ops_live_bad : ops_dead_bad)++; \
    printf("%-6s %s %8ld/%-8ld bad alias[dist,vd=vs,vd=vt,vs=vt]=%ld,%ld,%ld,%ld fields=%02X %s\n", #OP, LIVE ? "live" : "dead", s.bad, s.n, s.alias_bad[0], s.alias_bad[1], s.alias_bad[2], s.alias_bad[3], s.fieldmask, s.first); \
    if (s.ex[0] && getenv("S7815_EX")) printf("       %s\n", s.ex); }
    OPS(X)
#undef X
#if CEN64
    { static const char *nm[] = {"VABS", "VCH", "VCR", "VMRG", "VMADN", "VMADL"}; long cb = 0;
      cen_all<0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15>(reps);
      for (int i = 0; i < 6; i++) { cb += g_cen[i].bad; printf("cen64-vs-ares %-6s %ld/%ld bad %s\n", nm[i], g_cen[i].bad, g_cen[i].n, g_cen[i].first); }
      printf("[s7815] cen64-vs-ares bad=%ld -> %s\n", cb, cb ? "DIFFER" : "IDENTICAL"); }
#endif
    printf("[s7815] cx_sse=%d neon_mac=%d compares=%ld bad_live=%ld (%ld ops) bad_dead=%ld (%ld ops) -> %s\n", CX_SSE, RS64_RSP_NEON_MAC, g_n,
        g_bad_live, ops_live_bad, g_bad_dead, ops_dead_bad, (g_bad_live || g_bad_dead) ? "DIFFER" : "IDENTICAL");
    return (g_bad_live || g_bad_dead) ? 1 : 0;
}
