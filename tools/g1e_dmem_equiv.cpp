// s6774 G1e: equivalence harness for the RSP DMEM fast paths (librecomp rsp.hpp rs64_dmem_*, rsp_vu_impl.hpp LDV/SDV/LLV/SLV/
// LSV/SSV/LQV/SQV) and the constexpr element-select table. Hashes DMEM + vt after every op x element 0-15 x address 0-0x100F x
// imm -1..1, then scalar W/H/HU loads/stores and all 16 selects. Arg 1 = fast paths on, 0 = byte loops; build once against
// pre-change headers (-I<copy>) to check the select table too. s6774: ref == new(1) == new(0), 130/130 lines; a mutant
// rs64_dmem_h_set mask is caught at SSV. Build (repo root, L=lib/N64ModernRuntime):
//   clang++ -std=c++20 -O2 -w -I$L/librecomp/include -I$L/ultramodern/include -I$L/thirdparty/sse2neon -I$L/N64Recomp/include \
//     tools/g1e_dmem_equiv.cpp -o /tmp/eq && cmp <(/tmp/eq 1) <(/tmp/eq 0)
#include "librecomp/rsp.hpp"
#include "librecomp/rsp_vu_impl.hpp"
#include <utility>
uint8_t dmem[0x1000]; uint8_t dmem_audio[0x1000];
uint16_t rspReciprocals[512]; uint16_t rspInverseSquareRoots[512];
extern "C" { int rs64_rsp_hooks_on = 0; int rs64_g1e_dmem = 1; int rs64_g1e_fast = 1;
void rs64_m5_audio_dmem_store(uint32_t, uint32_t, uint32_t, uint32_t) {}
void rs64_spike_sdv_note(uint32_t, uint32_t, const uint32_t*) {} int rs64_sdv_snap_enabled(void) { return 0; }
void rs64_m5_audio_dmem_vector_store(uint32_t, uint32_t, uint32_t) {}
void rs64_m5_audio_input_dma(uint8_t*, uint32_t, uint32_t, uint32_t) {} void rs64_m5_audio_dmem_dma_write(uint32_t, uint32_t) {}
void rs64_m5_audio_stage_boundary(const OSTask*, uint32_t) {}
int rs64_vu_ring_enabled(void) { return 0; } void rs64_vld_note(uint32_t, uint32_t, const char*) {}
void rs64_vu_ring_vte(uint32_t, const uint16_t*) {} uint32_t rs64_vu_ring_prev_vd(void) { return 0; }
void rs64_vu_ring_capture_prev(const uint16_t*) {} void rs64_vu_ring_push(uint32_t, uint32_t, uint32_t, const uint16_t*) {} }
static uint64_t H = 1469598103934665603ull;
static void mix(const void* p, size_t n) { auto b = (const uint8_t*)p; for (size_t i = 0; i < n; i++) { H ^= b[i]; H *= 1099511628211ull; } }
static uint32_t rng = 12345; static uint32_t rnd() { rng = rng * 1664525u + 1013904223u; return rng; }
static RSP rsp{};
static void reset(RSP::r128& v) { for (int i = 0; i < 0x1000; i++) dmem[i] = (uint8_t)rnd(); for (int i = 0; i < 4; i++) ((uint32_t*)&v.u128)[i] = rnd(); }
#define OPTEST(NAME, CALL) template<u8 e> void t_##NAME() { \
    for (uint32_t a = 0; a < 0x1010; a++) for (int imm = -1; imm <= 1; imm++) { RSP::r128& vt = rsp.vpu.r[5]; reset(vt); \
        CALL; mix(dmem, sizeof dmem); mix(&vt.u128, 16); } }
OPTEST(LDV, rsp.LDV<e>(vt, a, imm)) OPTEST(SDV, rsp.SDV<e>(vt, a, imm)) OPTEST(LLV, rsp.LLV<e>(vt, a, imm))
OPTEST(SLV, rsp.SLV<e>(vt, a, imm)) OPTEST(LSV, rsp.LSV<e>(vt, a, imm)) OPTEST(SSV, rsp.SSV<e>(vt, a, imm))
OPTEST(LQV, rsp.LQV<e>(vt, a, imm)) OPTEST(SQV, rsp.SQV<e>(vt, a, imm))
#define ALLE(NAME) [&]<size_t... I>(std::index_sequence<I...>) { ((t_##NAME<(u8)I>(), printf(#NAME "<%zu> %016llx\n", I, (unsigned long long)H)), ...); }(std::make_index_sequence<16>{})
int main(int argc, char** argv) {
    rs64_g1e_dmem = argc > 1 ? atoi(argv[1]) : 1;
    ALLE(LDV); ALLE(SDV); ALLE(LLV); ALLE(SLV); ALLE(LSV); ALLE(SSV); ALLE(LQV); ALLE(SQV);
    for (uint32_t a = 0; a < 0x1010; a++) { RSP::r128 v; reset(v); uint32_t w = rnd();
        uint32_t r1 = RSP_MEM_W_LOAD(0, a), r2 = RSP_MEM_HU_LOAD(0, a), r3 = RSP_MEM_H_LOAD(0, a); mix(&r1, 4); mix(&r2, 4); mix(&r3, 4);
        RSP_MEM_W_STORE(0, a, w); mix(dmem, sizeof dmem); RSP_MEM_H_STORE(0, a, w >> 3); mix(dmem, sizeof dmem); }
    printf("scalar %016llx\n", (unsigned long long)H);
    for (int k = 0; k < 4096; k++) { RSP::r128 v; reset(v); for (u32 i = 0; i < 16; i++) { RSP::r128 r = v(i); mix(&r.u128, 16); } }
    printf("select %016llx\n", (unsigned long long)H);
}
