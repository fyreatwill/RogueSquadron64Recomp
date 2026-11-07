// s6941 G1e: driver for tools/g1e_nmac_op.cpp. Random lanes, a quarter of them edge values, 9 op forms x 16 e x N cases.
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
extern "C" void rs64_eq_run_old(const uint16_t*, int, int, uint16_t*);
extern "C" void rs64_eq_run_new(const uint16_t*, int, int, uint16_t*);
int rs64_g1e_dmem = 1, rs64_rsp_hooks_on = 0;
static uint64_t s = 0x9E3779B97F4A7C15ull;
static uint16_t rnd() { s ^= s << 13; s ^= s >> 7; s ^= s << 17; static const uint16_t ed[] = {0, 1, 2, 0x7FFF, 0x8000, 0x8001, 0xFFFF, 0xFFFE};
    return (s >> 60) < 4 ? ed[(s >> 40) & 7] : (uint16_t)(s >> 20); }
int main(int argc, char** argv) {
    long N = argc > 1 ? atol(argv[1]) : 200000; long bad[9] = {0}, total = 0;
    const char* nm[9] = {"VMUDN", "VMUDM", "VMUDH", "VMADL", "VMADN", "VMADM", "VMADH", "VMADN vd=vs", "VMADH vd=vt"};
    uint16_t in[40], a[32], b[32];
    for (long i = 0; i < N; i++) for (int op = 0; op < 9; op++) for (int e = 0; e < 16; e++) {
        for (auto& x : in) x = rnd();
        rs64_eq_run_old(in, op, e, a); rs64_eq_run_new(in, op, e, b); total++;
        if (memcmp(a, b, sizeof a)) { if (!bad[op]++) { printf("DIFF %s e=%d\n", nm[op], e); } }
    }
    long nb = 0; for (int op = 0; op < 9; op++) { printf("%-12s mismatches %ld\n", nm[op], bad[op]); nb += bad[op]; }
    printf("cases %ld, mismatches %ld\n", total, nb);
    return nb ? 1 : 0;
}
