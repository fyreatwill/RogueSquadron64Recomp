"""s5835: sphere-test probe. After transformObjectColliderCenter returns inside intersectSegmentWithObjectSphere (funcs_16.c, after_0 of 0x8006AE60),
read centre=v0 (xyz, r^2 at +0xC), seg origin=a2, seg dir=a3. Reports closest-approach^2 vs r^2 per shooter (P=player bolt, N=npc, via rs5834_who made global in funcs_13.c).
Prints first 20 P / 20 N rows (+ first 10 N rows with approach2<=r2 as positive control), per-4096 summary: min approach2, count approach2<=r2, count centre==0.
Under ROGUESQ_LOG_HITS=1. Read-only."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
T = "PATCH: s5835 sphere probe"
H = r'''/* PATCH: s5835 helpers */
#include <time.h>
extern unsigned rs5834_who; extern unsigned rs5856_cin;
uint32_t rs5856_sinobj; /* s5904 */ extern float rs5906_r2;
static struct { uint32_t w0; unsigned all, ret; uint32_t p58, p48, p4c, p50, p54, o58; unsigned fc, fr; float r2lo, r2hi; } rs5904_T[32]; float rs5906_r2; /* PATCH: s5906 */ /* PATCH: s5905 */ static unsigned rs5904_nT;
void rs5904_tally(uint8_t* rdram, uint32_t obj, int kind) { if ((obj >> 24) != 0x80) return; uint32_t w0 = (uint32_t)MEM_W(S32((int32_t)obj), 0); unsigned z; for (z = 0; z < rs5904_nT; z++) if (rs5904_T[z].w0 == w0) break; if (z == rs5904_nT) { if (z >= 32) return; rs5904_T[z].w0 = w0; rs5904_T[z].p58 = ((w0 >> 24) == 0x80) ? (uint32_t)MEM_W(S32((int32_t)w0), 0x58) : 0xdeadbeef; rs5904_T[z].p48 = ((w0 >> 24) == 0x80) ? (uint32_t)MEM_W(S32((int32_t)w0), 0x48) : 0xdeadbeef; rs5904_T[z].p4c = ((w0 >> 24) == 0x80) ? (uint32_t)MEM_W(S32((int32_t)w0), 0x4c) : 0xdeadbeef; rs5904_T[z].p50 = ((w0 >> 24) == 0x80) ? (uint32_t)MEM_W(S32((int32_t)w0), 0x50) : 0xdeadbeef; rs5904_T[z].p54 = ((w0 >> 24) == 0x80) ? (uint32_t)MEM_W(S32((int32_t)w0), 0x54) : 0xdeadbeef; rs5904_T[z].o58 = (uint32_t)MEM_W(S32((int32_t)obj), 0x58); rs5904_T[z].r2lo = 1e30f; rs5904_T[z].r2hi = -1e30f; rs5904_nT++; } if (kind == 2) rs5904_T[z].fc++; else if (kind == 3) rs5904_T[z].fr++; else if (kind) rs5904_T[z].ret++; else { rs5904_T[z].all++; if (rs5906_r2 < rs5904_T[z].r2lo) rs5904_T[z].r2lo = rs5906_r2; if (rs5906_r2 > rs5904_T[z].r2hi) rs5904_T[z].r2hi = rs5906_r2; } }
void rs5904_dump(void) { fprintf(stderr, "[s5904] w0 tally (all-sin / ret):"); for (unsigned z = 0; z < rs5904_nT; z++) fprintf(stderr, " %08x={all=%u ret=%u [w0+58]=%08x [w0+48,4c,50,54]=%08x,%08x,%08x,%08x [obj+58]=%08x fine=%u/%u r2=[%g,%g]}", rs5904_T[z].w0, rs5904_T[z].all, rs5904_T[z].ret, rs5904_T[z].p58, rs5904_T[z].p48, rs5904_T[z].p4c, rs5904_T[z].p50, rs5904_T[z].p54, rs5904_T[z].o58, rs5904_T[z].fc, rs5904_T[z].fr, rs5904_T[z].r2lo, rs5904_T[z].r2hi); fprintf(stderr, "\n"); }
static unsigned rs5835_sin[2], rs5835_sinp[2], rs5835_n[2], rs5835_in[2], rs5835_zc[2], rs5835_tot, rs5835_inprint; static float rs5835_min[2] = {1e30f, 1e30f}, rs5835_minr2[2], rs5835_minsd[2] = {1e30f, 1e30f}, rs5835_minsdr2[2]; static unsigned rs5835_mp[2]; static unsigned rs5837_tele, rs5837_en = 2, rs5837_cnt;
extern uint32_t rs5841_cand; static unsigned rs5841_cl[2][5];
static uint32_t rs5839_obj; static unsigned rs5839_cl[5], rs5839_tp, rs5839_tpc; 
extern uint32_t rs5856_proj;
/* s5897/s5898 bolt-life tracker: per projectile ptr, life-start pos, max dist^2 from start; histogram of life max dist at life end; hit distances; s5898: object word snapshots (0x80 B) at start/last sample, diff dumped at life end, hist2 excludes n<3 lives */
static struct { uint32_t pr; float s[3], l[3], md2; unsigned n; uint32_t w0[32], w1[32]; double t0, t1; } rs5897_L[32]; static double rs5898_now(void) { struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts); return ts.tv_sec * 1e3 + ts.tv_nsec / 1e6; } static unsigned rs5898_dth[6]; static unsigned rs5897_nL, rs5897_hist[8], rs5897_hist2[8], rs5897_lives, rs5897_lives2, rs5897_hn, rs5898_nd;
static void rs5897_flush(unsigned z) { float d = sqrtf(rs5897_L[z].md2); unsigned b = d < 1 ? 0 : d < 2 ? 1 : d < 4 ? 2 : d < 8 ? 3 : d < 16 ? 4 : d < 32 ? 5 : d < 64 ? 6 : 7; rs5897_hist[b]++; rs5897_lives++;
    if (rs5897_L[z].n >= 3) { { double dt = rs5897_L[z].t1 - rs5897_L[z].t0; rs5898_dth[dt < 20 ? 0 : dt < 40 ? 1 : dt < 80 ? 2 : dt < 160 ? 3 : dt < 500 ? 4 : 5]++; } rs5897_hist2[b]++; rs5897_lives2++; if ((d >= 1.0f || rs5898_nd < 8) && rs5898_nd < 40) { rs5898_nd++; fprintf(stderr, "[s5898] life pr=%08x n=%u maxd=%g dt_ms=%.1f diff:", rs5897_L[z].pr, rs5897_L[z].n, d, rs5897_L[z].t1 - rs5897_L[z].t0); for (int i = 0; i < 32; i++) if (rs5897_L[z].w0[i] != rs5897_L[z].w1[i]) fprintf(stderr, " +%x:%08x>%08x", 4*i, rs5897_L[z].w0[i], rs5897_L[z].w1[i]); fprintf(stderr, " | start:"); for (int i = 0; i < 32; i++) fprintf(stderr, " %x", rs5897_L[z].w0[i]); fprintf(stderr, "\n"); } }
    if ((rs5897_lives & 63) == 0) { fprintf(stderr, "[s5897] life maxdist hist <1,<2,<4,<8,<16,<32,<64,>=64: %u %u %u %u %u %u %u %u lives=%u\n", rs5897_hist[0], rs5897_hist[1], rs5897_hist[2], rs5897_hist[3], rs5897_hist[4], rs5897_hist[5], rs5897_hist[6], rs5897_hist[7], rs5897_lives); fprintf(stderr, "[s5898] hist(n>=3): %u %u %u %u %u %u %u %u lives=%u dt_ms hist <20,<40,<80,<160,<500,>=500: %u %u %u %u %u %u\n", rs5897_hist2[0], rs5897_hist2[1], rs5897_hist2[2], rs5897_hist2[3], rs5897_hist2[4], rs5897_hist2[5], rs5897_hist2[6], rs5897_hist2[7], rs5897_lives2, rs5898_dth[0], rs5898_dth[1], rs5898_dth[2], rs5898_dth[3], rs5898_dth[4], rs5898_dth[5]); } }
static void rs5897_track(uint8_t* rdram, uint32_t pr, const float* pp) {
    { static unsigned sn; if (sn < 300) { sn++; float po[3]; for (int i = 0; i < 3; i++) { union { uint32_t u; float f; } x; x.u = (uint32_t)MEM_W(S32((int32_t)pr), 0x4c + 4 * i); po[i] = x.f; } float q = 0; for (int i = 0; i < 3; i++) q += (pp[i] - po[i]) * (pp[i] - po[i]); fprintf(stderr, "[s5900] n=%u pr=%08x pp=%g,%g,%g obj4c=%g,%g,%g d=%g w00=%08x w60=%08x\n", sn, pr, pp[0], pp[1], pp[2], po[0], po[1], po[2], sqrtf(q), (uint32_t)MEM_W(S32((int32_t)pr), 0), (uint32_t)MEM_W(S32((int32_t)pr), 0x60)); } }
    unsigned z; for (z = 0; z < rs5897_nL; z++) if (rs5897_L[z].pr == pr) break;
    if (z == rs5897_nL) { if (z >= 32) return; rs5897_L[z].pr = pr; rs5897_L[z].n = 0; rs5897_nL++; }
    if (rs5897_L[z].n) { float q = 0; for (int i = 0; i < 3; i++) { float e = pp[i] - rs5897_L[z].l[i]; q += e*e; } if (q > 36.0f) { rs5897_flush(z); rs5897_L[z].n = 0; } }
    if (!rs5897_L[z].n) { for (int i = 0; i < 3; i++) rs5897_L[z].s[i] = pp[i]; rs5897_L[z].md2 = 0; rs5897_L[z].t0 = rs5898_now(); for (int i = 0; i < 32; i++) rs5897_L[z].w0[i] = (uint32_t)MEM_W(S32((int32_t)pr), 4 * i); }
    rs5897_L[z].t1 = rs5898_now(); for (int i = 0; i < 32; i++) rs5897_L[z].w1[i] = (uint32_t)MEM_W(S32((int32_t)pr), 4 * i);
    rs5897_L[z].n++; float q = 0; for (int i = 0; i < 3; i++) { rs5897_L[z].l[i] = pp[i]; float e = pp[i] - rs5897_L[z].s[i]; q += e*e; } if (q > rs5897_L[z].md2) rs5897_L[z].md2 = q;
}
unsigned rs5897_dist2(uint32_t pr) { for (unsigned z = 0; z < rs5897_nL; z++) if (rs5897_L[z].pr == pr) { float q = 0; for (int i = 0; i < 3; i++) { float e = rs5897_L[z].l[i] - rs5897_L[z].s[i]; q += e*e; } return (unsigned)(sqrtf(q) * 100.0f); } return 0xFFFFFFFFu; }
/* s5901 raw per-bolt-sample log: group = consecutive calls with identical pp; line at group end: cycle (gap>4ms), pp, |dd|, min sd2/r2 over the group's collider rows + that collider's id/centre/r2. Offline NN matching. */
static uint8_t* rs5901_rdram; static unsigned rs5901_c1f; static uint32_t rs5901_obj;
static uint32_t rs5901_rw(uint32_t a) { return *(uint32_t*)(rs5901_rdram + (a - 0x80000000u)); }
static unsigned rs5901_did(unsigned id) { uint32_t tb = rs5901_rw(0x80130BB0u), n = rs5901_rw(tb + id * 8), d = ((n >> 24) == 0x80) ? rs5901_rw(n + 0x34) : 0; return ((d >> 24) == 0x80) ? rs5901_rw(d + 0x78) : 0xDEADu; }
static struct { int on; float pp[3]; float dl; float best; float bc[4]; unsigned bid, bc1, bdid; uint32_t bobj, rows; unsigned cyc; double tl; unsigned lines; } rs5901_S;
static void rs5901_emit(void) { if (!rs5901_S.rows) return; if (rs5901_S.lines++ < 60000) fprintf(stderr, "[s5901] c=%u pp=%g,%g,%g len=%g rows=%u best_ratio=%g id=%x c1f=%u did=%x obj=%08x ctr=%g,%g,%g r2=%g\n", rs5901_S.cyc, rs5901_S.pp[0], rs5901_S.pp[1], rs5901_S.pp[2], sqrtf(rs5901_S.dl), rs5901_S.rows, rs5901_S.best, rs5901_S.bid, rs5901_S.bc1, rs5901_S.bdid, rs5901_S.bobj, rs5901_S.bc[0], rs5901_S.bc[1], rs5901_S.bc[2], rs5901_S.bc[3]); rs5901_S.rows = 0; }
static void rs5901_sample(const float* pp, float dl, float sd2, const float* cc, unsigned id) {
    double now = rs5898_now(); float ratio = sd2 / (cc[3] > 0.0f ? cc[3] : 1.0f);
    int same = rs5901_S.rows && pp[0] == rs5901_S.pp[0] && pp[1] == rs5901_S.pp[1] && pp[2] == rs5901_S.pp[2];
    if (!same) { rs5901_emit(); if (now - rs5901_S.tl > 4.0) rs5901_S.cyc++; for (int i = 0; i < 3; i++) rs5901_S.pp[i] = pp[i]; rs5901_S.dl = dl; rs5901_S.best = 1e30f; }
    rs5901_S.tl = now; rs5901_S.rows++; if (ratio < rs5901_S.best) { rs5901_S.best = ratio; rs5901_S.bid = id; rs5901_S.bc1 = rs5901_c1f; rs5901_S.bdid = rs5901_did(id); rs5901_S.bobj = rs5901_obj; for (int i = 0; i < 4; i++) rs5901_S.bc[i] = cc[i]; }
}
static float rs5835_f(uint32_t w) { union { uint32_t u; float f; } x; x.u = w; return x.f; }
static void rs5835_probe(uint8_t* rdram, recomp_context* ctx) {
    rs5901_rdram = rdram;
    unsigned w = 0; /* s5855: who-classifier void (s5854); all bolts counted as w=0 */
    uint32_t c = (uint32_t)ctx->r2, p = (uint32_t)ctx->r6, d = (uint32_t)ctx->r7;
    if ((c >> 24) != 0x80 || (p >> 24) != 0x80 || (d >> 24) != 0x80) return;
    float cc[4], pp[3], dd[3];
    for (int i = 0; i < 4; i++) cc[i] = rs5835_f((uint32_t)MEM_W(S32((int32_t)c), 4 * i));
    for (int i = 0; i < 3; i++) { pp[i] = rs5835_f((uint32_t)MEM_W(S32((int32_t)p), 4 * i)); dd[i] = rs5835_f((uint32_t)MEM_W(S32((int32_t)d), 4 * i)); }
    if ((rs5856_proj >> 24) == 0x80) rs5897_track(rdram, rs5856_proj, pp); /* s5897 */
    if (rs5837_en == 2) { const char* e = getenv("ROGUESQ_TELE_BOLT"); rs5837_en = (e && e[0] == '1'); }
    unsigned c1f = 0; unsigned k39 = 99; { /* s5841: class of the loop's candidate NPC via slot table *0x80130BB0 id*8 */
        uint32_t tb = (uint32_t)MEM_W(S32((int32_t)0x80130BB0u), 0); uint32_t n = (uint32_t)MEM_W(S32((int32_t)(tb + (rs5841_cand & 0xFFFF) * 8)), 0);
        if ((n >> 24) == 0x80) { uint32_t d = (uint32_t)MEM_W(S32((int32_t)n), 0x34); if (d >= 0x80300000u && d < 0x80330000u) k39 = (unsigned)MEM_W(S32((int32_t)d), 0x70); }
        { static unsigned nd2[2]; if ((n >> 24) == 0x80 && nd2[w] < 24) { nd2[w]++; fprintf(stderr, "[ctx41] %s id=%x n=%08x:", w ? "N" : "P", (unsigned)(rs5841_cand & 0xFFFF), n); for (int q = 0; q < 0x80; q += 4) { uint32_t x = (uint32_t)MEM_W(S32((int32_t)n), q); if ((x >> 24) == 0x80 && x < 0x80800000u) fprintf(stderr, " +%x=%08x{70=%x}", q, x, (unsigned)MEM_W(S32((int32_t)x), 0x70)); else fprintf(stderr, " +%x=%x", q, x); } fprintf(stderr, "\n"); } }
        if ((n >> 24) == 0x80) { static uint32_t fk[2][24]; static unsigned fc[2][24], fn[2]; uint32_t f = (uint32_t)MEM_W(S32((int32_t)n), 0); unsigned z; c1f = (f == 0x800cabd4u || f == 0x800d93c0u || f == 0x800e7860u); for (z = 0; z < fn[w]; z++) if (fk[w][z] == f) break; if (z == fn[w] && z < 24) { fk[w][z] = f; fn[w]++; } if (z < 24) fc[w][z]++; if ((rs5835_tot & 4095) == 0) { fprintf(stderr, "[fn41] %s:", w ? "N" : "P"); for (z = 0; z < fn[w]; z++) fprintf(stderr, " %08x=%u", fk[w][z], fc[w][z]); fprintf(stderr, "\n"); } }
        if (k39 > 3) k39 = 4; rs5841_cl[w][k39]++; if ((rs5835_tot & 4095) == 0) fprintf(stderr, "[s5841] cand-class tally P=%u/%u/%u/%u/%u N=%u/%u/%u/%u/%u tele=%u\n", rs5841_cl[0][0], rs5841_cl[0][1], rs5841_cl[0][2], rs5841_cl[0][3], rs5841_cl[0][4], rs5841_cl[1][0], rs5841_cl[1][1], rs5841_cl[1][2], rs5841_cl[1][3], rs5841_cl[1][4], rs5839_tp); }
    { uint32_t o = rs5839_obj, dd0 = ((o >> 24) == 0x80) ? (uint32_t)MEM_W(S32((int32_t)o), 0x34) : 0; if ((dd0 >> 24) == 0x80) k39 = (unsigned)MEM_W(S32((int32_t)dd0), 0x70); if (w == 0) rs5839_cl[k39 < 4 ? k39 : 4]++; if (w == 0 && rs5839_tpc++ < 12) fprintf(stderr, "[sph39] P obj=%08x desc=%08x cls=%u\n", o, dd0, k39); if ((rs5835_tot & 4095) == 0) fprintf(stderr, "[sph39] P class tally c0=%u c1=%u c2=%u c3=%u other=%u tele=%u\n", rs5839_cl[0], rs5839_cl[1], rs5839_cl[2], rs5839_cl[3], rs5839_cl[4], rs5839_tp); }
    { static unsigned nd[2]; if (((rs5839_obj >> 24) == 0x80) && nd[w] < 40) { nd[w]++; fprintf(stderr, "[own40] %s obj=%08x w=", w ? "N" : "P", rs5839_obj); for (int q = 0; q < 0x100; q += 4) fprintf(stderr, "%08X ", (unsigned)MEM_W(S32((int32_t)rs5839_obj), q)); fprintf(stderr, "\n"); } } /* s5840 owner dump */ /* s5841 c1f */
    { /* s5903 owner join: per distinct (cand id, obj) pair, link tests between collider obj and slot node n / descriptor */
        static struct { unsigned id; uint32_t obj; } S3[256]; static unsigned nS3; unsigned id3 = rs5841_cand & 0xFFFF, z3; uint32_t o3 = rs5839_obj;
        if ((o3 >> 24) == 0x80) { for (z3 = 0; z3 < nS3; z3++) if (S3[z3].id == id3 && S3[z3].obj == o3) break;
          if (z3 == nS3 && nS3 < 256) { S3[nS3].id = id3; S3[nS3].obj = o3; nS3++;
            uint32_t tb3 = (uint32_t)MEM_W(S32((int32_t)0x80130BB0u), 0), n3 = (uint32_t)MEM_W(S32((int32_t)(tb3 + id3 * 8)), 0), d3 = 0, k3 = 0xFFFF, f3 = 0; unsigned lk_n = 0, lk_d = 0, np = 0;
            if ((n3 >> 24) == 0x80) { f3 = (uint32_t)MEM_W(S32((int32_t)n3), 0); d3 = (uint32_t)MEM_W(S32((int32_t)n3), 0x34); if (d3 >= 0x80300000u && d3 < 0x80330000u) k3 = (uint32_t)MEM_W(S32((int32_t)d3), 0x70); }
            for (int q = 0; q < 0x100; q += 4) { uint32_t x = (uint32_t)MEM_W(S32((int32_t)o3), q); if (x == n3 && n3) lk_n |= 1u << (q / 8 > 31 ? 31 : q / 8 % 32); if (x == d3 && d3) lk_d = 1; if ((x >> 24) == 0x80 && x < 0x80800000u) np++; }
            fprintf(stderr, "[own53] id=%x obj=%08x w0=%08x w4=%08x n=%08x f=%08x d34=%08x cls=%x c1f=%u lk_n=%x lk_d=%u nptr=%u pairs=%u", id3, o3, (unsigned)MEM_W(S32((int32_t)o3), 0), (unsigned)MEM_W(S32((int32_t)o3), 4), n3, f3, d3, k3, c1f, lk_n, lk_d, np, nS3);
            for (int q = 0; q < 0x100; q += 4) { uint32_t x = (uint32_t)MEM_W(S32((int32_t)o3), q); if ((x >> 24) == 0x80 && x < 0x80800000u && x != o3) fprintf(stderr, " +%x=%08x{0=%x,34=%x,70=%x}", q, x, (unsigned)MEM_W(S32((int32_t)x), 0), (unsigned)MEM_W(S32((int32_t)x), 0x34), (unsigned)MEM_W(S32((int32_t)x), 0x70)); }
            fprintf(stderr, "\n"); } }
    } /* s5903 */
    if (rs5837_en && w == 0 && cc[3] > 0.0f && c1f && (rs5837_cnt++ & 3) == 0) { /* s5837: force bolt segment through shape centre */
        float nf[3] = {cc[0]-0.5f*dd[0], cc[1]-0.5f*dd[1], cc[2]-0.5f*dd[2]};
        for (int i = 0; i < 3; i++) { union { float f; uint32_t u; } x; x.f = nf[i]; MEM_W(S32((int32_t)p), 4 * i) = (int32_t)x.u; pp[i] = nf[i]; }
        rs5839_tp++; if (rs5837_tele++ < 10) fprintf(stderr, "[sph] TELE obj=%08x ctr=(%g,%g,%g) r2=%g dir=(%g,%g,%g)\n", rs5839_obj, cc[0], cc[1], cc[2], cc[3], dd[0], dd[1], dd[2]);
    }
    rs5901_c1f = c1f; rs5901_obj = rs5839_obj;
    float v[3] = {cc[0]-pp[0], cc[1]-pp[1], cc[2]-pp[2]};
    float v2 = v[0]*v[0]+v[1]*v[1]+v[2]*v[2], dl = dd[0]*dd[0]+dd[1]*dd[1]+dd[2]*dd[2], t = v[0]*dd[0]+v[1]*dd[1]+v[2]*dd[2];
    float ap2 = (dl > 0.0f) ? v2 - t*t/dl : v2; unsigned in = (ap2 <= cc[3]);
    { float u = (dl > 0.0f) ? t/dl : 0.0f; if (u < 0.0f) u = 0.0f; if (u > 1.0f) u = 1.0f; float q0 = v[0]-u*dd[0], q1 = v[1]-u*dd[1], q2 = v[2]-u*dd[2]; float sd2 = q0*q0+q1*q1+q2*q2; unsigned sin_ = (sd2 <= cc[3]); rs5901_sample(pp, dl, sd2, cc, rs5841_cand & 0xFFFF); /* s5901 */ if (sd2 < rs5835_minsd[w]) { rs5835_minsd[w] = sd2; rs5835_minsdr2[w] = cc[3]; if (rs5835_mp[w]++ < 12) fprintf(stderr, "[sph] MINSD %s sd2=%g r2=%g ratio=%g u=%g dl=%g |v|2=%g\n", w ? "N" : "P", sd2, cc[3], sd2/(cc[3] > 0.0f ? cc[3] : 1.0f), (dl > 0.0f) ? t/dl : 0.0f, dl, v2); } rs5856_cin |= sin_; if (sin_) { rs5856_sinobj = rs5839_obj; rs5906_r2 = cc[3]; rs5904_tally(rdram, rs5839_obj, 0); } rs5835_sin[w] += sin_; if (sin_ && rs5835_sinp[w]++ < 10) fprintf(stderr, "[sph] SEGIN %s r2=%g |v|2=%g t=%g dl=%g sd2=%g\n", w ? "N" : "P", cc[3], v2, t, dl, sd2); }
    { /* s5855: per class-1/any id table: tests, min v2, min ap2, r2, segin */
        static struct { unsigned id, n, segin, c1; float mv2, map2, r2, fap2, fv2, fsn2; unsigned fn, did; } T[48]; static unsigned nT; unsigned id = rs5841_cand & 0xFFFF, z;
        for (z = 0; z < nT; z++) if (T[z].id == id) break;
        if (z == nT && z < 48) { T[z].id = id; T[z].mv2 = T[z].map2 = T[z].fap2 = T[z].fsn2 = 1e30f; { uint32_t tb2 = (uint32_t)MEM_W(S32((int32_t)0x80130BB0u), 0), n2 = (uint32_t)MEM_W(S32((int32_t)(tb2 + id * 8)), 0), d2 = ((n2 >> 24) == 0x80) ? (uint32_t)MEM_W(S32((int32_t)n2), 0x34) : 0; T[z].did = ((d2 >> 24) == 0x80) ? (unsigned)MEM_W(S32((int32_t)d2), 0x78) : 0xDEADu; } /* s5896 descriptor id */ nT++; }
        if (z < 48) { T[z].n++; T[z].c1 = c1f; if (v2 < T[z].mv2) { T[z].mv2 = v2; T[z].r2 = cc[3]; } if (ap2 < T[z].map2) T[z].map2 = ap2; if (t > 0.0f && dl > 0.0f) { T[z].fn++; if (ap2 < T[z].fap2) { T[z].fap2 = ap2; T[z].fv2 = v2; } if (v2 > 0.0f && v2 < 900.0f && ap2 / v2 < T[z].fsn2) T[z].fsn2 = ap2 / v2; } /* s5894 forward-only closest approach + min sin^2(angle) within 30 u */ if (ap2 <= cc[3]) T[z].segin++; }
        static unsigned tk; if ((++tk & 1023) == 0) { fprintf(stderr, "[s5855] ids=%u:", nT); for (z = 0; z < nT; z++) fprintf(stderr, " %x{did=%x c1=%u n=%u mv2=%g map2=%g r2=%g in=%u fwd=%u fap2=%g@v2=%g sin2_30u=%g}", T[z].id, T[z].did, T[z].c1, T[z].n, T[z].mv2, T[z].map2, T[z].r2, T[z].segin, T[z].fn, T[z].fap2, T[z].fv2, T[z].fsn2); fprintf(stderr, "\n"); }
    }
    if (w == 0) { /* s5853: new-minimum bolt-to-sphere separation, all NPCs (m0) and class-1 only (m1) */
        static float m0 = 1e30f, m1 = 1e30f; unsigned pr = 0; if (v2 < m0) { m0 = v2; pr |= 1; } if (c1f && v2 < m1) { m1 = v2; pr |= 2; }
        if (pr) fprintf(stderr, "[s5853] newmin%u c1=%u id=%x ctr=(%g,%g,%g) r2=%g bolt0=(%g,%g,%g) dir=(%g,%g,%g) v2=%g t=%g ap2=%g\n", pr, c1f, (unsigned)(rs5841_cand & 0xFFFF), cc[0], cc[1], cc[2], cc[3], pp[0], pp[1], pp[2], dd[0], dd[1], dd[2], v2, t, ap2);
    }
    rs5835_n[w]++; rs5835_tot++; if (in) rs5835_in[w]++; if (cc[0] == 0.0f && cc[1] == 0.0f && cc[2] == 0.0f) rs5835_zc[w]++;
    if (ap2 < rs5835_min[w]) { rs5835_min[w] = ap2; rs5835_minr2[w] = cc[3]; }
    if (rs5835_n[w] <= 20 || (w == 1 && in && rs5835_inprint++ < 10))
        fprintf(stderr, "[sph] %s ctr=(%g,%g,%g) r2=%g pt=(%g,%g,%g) dir=(%g,%g,%g) |v|2=%g t=%g ap2=%g in=%u\n", w ? "N" : "P", cc[0], cc[1], cc[2], cc[3], pp[0], pp[1], pp[2], dd[0], dd[1], dd[2], v2, t, ap2, in);
    if ((rs5835_tot & 4095) == 0) fprintf(stderr, "[sph] summary P n=%u in=%u segin=%u zeroctr=%u minap2=%g minsd2=%g(r2=%g) | N n=%u in=%u segin=%u zeroctr=%u minap2=%g minsd2=%g(r2=%g)\n", rs5835_n[0], rs5835_in[0], rs5835_sin[0], rs5835_zc[0], rs5835_min[0], rs5835_minsd[0], rs5835_minsdr2[0], rs5835_n[1], rs5835_in[1], rs5835_sin[1], rs5835_zc[1], rs5835_min[1], rs5835_minsd[1], rs5835_minsdr2[1]);
}
'''
S5903 = r'''    { /* s5903 owner join: per distinct (cand id, obj) pair, link tests between collider obj and slot node n / descriptor */
        static struct { unsigned id; uint32_t obj; } S3[256]; static unsigned nS3; unsigned id3 = rs5841_cand & 0xFFFF, z3; uint32_t o3 = rs5839_obj;
        if ((o3 >> 24) == 0x80) { for (z3 = 0; z3 < nS3; z3++) if (S3[z3].id == id3 && S3[z3].obj == o3) break;
          if (z3 == nS3 && nS3 < 256) { S3[nS3].id = id3; S3[nS3].obj = o3; nS3++;
            uint32_t tb3 = (uint32_t)MEM_W(S32((int32_t)0x80130BB0u), 0), n3 = (uint32_t)MEM_W(S32((int32_t)(tb3 + id3 * 8)), 0), d3 = 0, k3 = 0xFFFF, f3 = 0; unsigned lk_n = 0, lk_d = 0, np = 0;
            if ((n3 >> 24) == 0x80) { f3 = (uint32_t)MEM_W(S32((int32_t)n3), 0); d3 = (uint32_t)MEM_W(S32((int32_t)n3), 0x34); if (d3 >= 0x80300000u && d3 < 0x80330000u) k3 = (uint32_t)MEM_W(S32((int32_t)d3), 0x70); }
            for (int q = 0; q < 0x100; q += 4) { uint32_t x = (uint32_t)MEM_W(S32((int32_t)o3), q); if (x == n3 && n3) lk_n |= 1u << (q / 8 > 31 ? 31 : q / 8 % 32); if (x == d3 && d3) lk_d = 1; if ((x >> 24) == 0x80 && x < 0x80800000u) np++; }
            fprintf(stderr, "[own53] id=%x obj=%08x w0=%08x w4=%08x n=%08x f=%08x d34=%08x cls=%x c1f=%u lk_n=%x lk_d=%u nptr=%u pairs=%u", id3, o3, (unsigned)MEM_W(S32((int32_t)o3), 0), (unsigned)MEM_W(S32((int32_t)o3), 4), n3, f3, d3, k3, c1f, lk_n, lk_d, np, nS3);
            for (int q = 0; q < 0x100; q += 4) { uint32_t x = (uint32_t)MEM_W(S32((int32_t)o3), q); if ((x >> 24) == 0x80 && x < 0x80800000u && x != o3) fprintf(stderr, " +%x=%08x{0=%x,34=%x,70=%x}", q, x, (unsigned)MEM_W(S32((int32_t)x), 0), (unsigned)MEM_W(S32((int32_t)x), 0x34), (unsigned)MEM_W(S32((int32_t)x), 0x70)); }
            fprintf(stderr, "\n"); } }
    } /* s5903 */
'''
FN = "RECOMP_FUNC void intersectSegmentWithObjectSphere("
CAP = "    transformObjectColliderCenter(rdram, ctx);\n        goto after_0;"
ANC = "    after_0:\n    // 0x8006AE68: mfc1        $t0, $f20\n"
def apply(text, name=None):
    n = 0
    if "/* s5903 */" not in text and " /* s5840 owner dump */ /* s5841 c1f */\n" in text:
        text = text.replace(" /* s5840 owner dump */ /* s5841 c1f */\n", " /* s5840 owner dump */ /* s5841 c1f */\n" + S5903, 1); n += 1
    if "static float rs5834_pt[3]" in text and "unsigned rs5834_who = 2;" not in text:
        a = "rs5834_sh[8]; static unsigned rs5834_who, "
        assert a in text
        text = text.replace(a, "rs5834_sh[8]; unsigned rs5834_who = 2; static unsigned ", 1)
        b = "rs5834_zero[1]);\n}\n"
        assert text.count(b) == 1
        text = text.replace(b, "rs5834_zero[1]);\n    rs5834_who = 2; /* PATCH: s5835 */\n}\n", 1); n += 1
    if "rs5841_cand = " not in text and "PATCH: s5833 proj loop" in text:
        a = "    rs5833_ev(rdram, (uint32_t)ctx->r17, 1, (uint32_t)(ctx->r16 & 0xFFFF), 1); /* PATCH: s5833 proj loop */\n"
        if a in text:
            text = text.replace(a, "    rs5841_cand = (uint32_t)(ctx->r16 & 0xFFFF); /* PATCH: s5841 */\n" + a, 1)
            f = "RECOMP_FUNC void audioCueDispatcherNpcHandler("
            i = text.find(f); text = text[:i] + "uint32_t rs5841_cand; /* PATCH: s5841 */\n" + text[i:]; n += 1
    if "PATCH: s5856" not in text and "static void rs5834_post(" in text:
        k = "static void rs5834_pre(uint8_t* rdram, recomp_context* ctx) {\n"
        assert text.count(k) == 1
        text = text.replace(k, "extern uint32_t rs5841_cand; unsigned rs5856_cin; uint32_t rs5856_proj; unsigned rs5897_dist2(uint32_t); uint32_t rs5856_sinobj; void rs5904_tally(uint8_t*, uint32_t, int); void rs5904_dump(void); /* PATCH: s5856 */\n" + k + "    rs5856_cin = 0; rs5856_sinobj = 0; rs5856_proj = (uint32_t)ctx->r17;\n", 1)
        k = "static void rs5834_post(uint8_t* rdram, uint32_t hit) {\n    if (!rs5834_en) return;\n"
        assert text.count(k) == 1
        post = r'''    { /* PATCH: s5856 per-id: calls, ret!=0, clamped-in, clamped-in&&ret==0 */
        static struct { unsigned id, n, ret, cin, cmiss, wid; } T[64]; static unsigned nT, tk; unsigned id = rs5841_cand & 0xFFFF, z;
        for (z = 0; z < nT; z++) if (T[z].id == id) break;
        if (z == nT && z < 64) { T[z].id = id; nT++; }
        if (z < 64) { T[z].n++; if (hit) T[z].ret++; if (rs5856_cin) T[z].cin++; if (rs5856_cin && !hit) T[z].cmiss++; if ((rs5856_proj >> 24) == 0x80) T[z].wid = (unsigned)MEM_HU(S32((int32_t)rs5856_proj), 0xF8); }
        if (rs5856_cin && !hit) { static unsigned pm; if (pm++ < 15) fprintf(stderr, "[s5856] CMISS id=%x proj=%08x wid=%x\\n", id, rs5856_proj, (unsigned)MEM_HU(S32((int32_t)rs5856_proj), 0xF8)); }
        if (hit) { static unsigned ph; if (ph++ < 15) fprintf(stderr, "[s5856] RET id=%x proj=%08x cin=%u\\n", id, rs5856_proj, rs5856_cin); } { extern unsigned rs5897_dist2(uint32_t); static unsigned hn; if (hit && hn++ < 60) fprintf(stderr, "[s5897] HITDIST id=%x life_dist_x100=%u\\n", id, rs5897_dist2(rs5856_proj)); }
        if ((++tk & 1023) == 0) { fprintf(stderr, "[s5856] ids=%u:", nT); for (z = 0; z < nT; z++) fprintf(stderr, " %x{n=%u ret=%u cin=%u cmiss=%u wid=%x}", T[z].id, T[z].n, T[z].ret, T[z].cin, T[z].cmiss, T[z].wid); fprintf(stderr, "\\n"); }
    }
'''
        text = text.replace(k, k + post, 1); n += 1
    if "PATCH: s5904" not in text and "PATCH: s5856" in text and "static void rs5834_pre(" in text:
        a = "    rs5856_cin = 0; rs5856_proj = (uint32_t)ctx->r17;\n"
        assert text.count(a) == 1
        text = text.replace(a, "    rs5856_cin = 0; rs5856_sinobj = 0; rs5856_proj = (uint32_t)ctx->r17;\n", 1)
        a = "static void rs5834_pre(uint8_t* rdram, recomp_context* ctx) {\n"
        text = text.replace(a, "uint32_t rs5856_sinobj; void rs5904_tally(uint8_t*, uint32_t, int); void rs5904_dump(void); /* PATCH: s5904 */\n" + a, 1)
        b = "        if (hit) { static unsigned ph; if (ph++ < 15) fprintf(stderr, \"[s5856] RET id=%x proj=%08x cin=%u\\n\""
        assert text.count(b) == 1
        text = text.replace(b, "        if (hit) { static unsigned p4; rs5904_tally(rdram, rs5856_sinobj, 1); if (p4++ < 40) { uint32_t so = rs5856_sinobj; fprintf(stderr, \"[s5904] RET id=%x sinobj=%08x w0=%08x w4=%08x\\n\", id, so, ((so >> 24) == 0x80) ? (unsigned)MEM_W(S32((int32_t)so), 0) : 0u, ((so >> 24) == 0x80) ? (unsigned)MEM_W(S32((int32_t)so), 4) : 0u); } if ((p4 & 7) == 0) rs5904_dump(); }\n" + b, 1); n += 1
    if "PATCH: s5904 tally" not in text and "PATCH: s5835 helpers" in text and "rs5901_sample(pp, dl, sd2, cc" in text:
        k = "extern unsigned rs5834_who; extern unsigned rs5856_cin;\n"
        assert text.count(k) == 1
        hh = H[H.index("uint32_t rs5856_sinobj;"):H.index("static unsigned rs5835_sin[2]")]
        text = text.replace(k, k + "/* PATCH: s5904 tally */\n" + hh, 1)
        a = "rs5856_cin |= sin_; rs5835_sin[w] += sin_;"
        assert text.count(a) == 1
        text = text.replace(a, "rs5856_cin |= sin_; if (sin_) { rs5856_sinobj = rs5839_obj; rs5906_r2 = cc[3]; rs5904_tally(rdram, rs5839_obj, 0); } rs5835_sin[w] += sin_;", 1); n += 1
    if "static uint32_t rs5856_proj;" in text:
        text = text.replace("static uint32_t rs5856_proj;", "uint32_t rs5856_proj; unsigned rs5897_dist2(uint32_t);", 1); n += 1
    old = 'rs5856_proj, rs5856_cin); }\n'
    if "[s5897] HITDIST" not in text and "[s5856] RET id" in text:
        i = text.find("[s5856] RET id"); j = text.find("); }", i) + 4
        text = text[:j] + ' { static unsigned hn; if (hit && hn++ < 60) fprintf(stderr, "[s5897] HITDIST id=%x life_dist_x100=%u\\n", id, rs5897_dist2(rs5856_proj)); }' + text[j:]; n += 1
    if FN not in text: return text, n
    if "#include <time.h>\nextern unsigned rs5834_who" not in text and "PATCH: s5835 helpers" in text:
        a = text.find("/* PATCH: s5835 helpers */"); b = text.find(FN)
        text = text[:a] + H + text[b:]; n += 1
    if "rs5839_obj = " not in text:
        i = text.find(FN); a = "    transformObjectColliderCenter(rdram, ctx);\n        goto after_0;"
        j = text.find(a, i)
        if j > 0: text = text[:j] + "    rs5839_obj = (uint32_t)ctx->r4; /* PATCH: s5839 */\n" + text[j:]; n += 1
    if n and T in text: return text, n
    if T in text: return text, n
    i = text.find(FN); j = text.find(ANC, i)
    if j < 0: return text, n
    text = text[:j] + "    after_0:\n    rs5835_probe(rdram, ctx); /* %s */\n    // 0x8006AE68: mfc1        $t0, $f20\n" % T + text[j+len(ANC):]
    i = text.find(FN)
    return text[:i] + H + text[i:], n + 1
if __name__ == "__main__":
    for f in ("funcs_13.c", "funcs_16.c"):
        p = base / f; t = p.read_text(); t2, n = apply(t)
        if n: p.write_text(t2)
        print(f, n)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    s = fp.read_text()
    if "apply_s5835_sphere_probe" in s: print("fixup already")
    else:
        blk = ('    if p.name in ("funcs_13.c", "funcs_16.c"):\n'
               '        import apply_s5835_sphere_probe as _a5835\n'
               '        text, _n5835 = _a5835.apply(text)\n'
               '        if _n5835:\n'
               '            changed = True\n'
               '            report.append(f"{p.name}: s5835 sphere probe x{_n5835}")\n\n')
        anc = '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        assert s.count(anc) == 1
        s = s.replace(anc, blk + anc, 1)
        lst = '    "apply_s5834_seg_dump.py",\n'
        assert s.count(lst) == 1
        s = s.replace(lst, lst + '    "apply_s5835_sphere_probe.py",\n', 1)
        fp.write_text(s); print("fixup patched")
