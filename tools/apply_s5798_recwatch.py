"""s5798: runtime writer census for the projectile spawn record (0x80165C28 droid, 0x80165C58 wingman).

1. Every generated store (sw/sh/sb/swc1 via MEM_W/H/B lvalues, sd/sdc1 via SD) in every funcs_*.c gets a
   range check; stores into [0x80165B00, 0x80165E00) record (pc, read-back word, guest ra, enclosing function,
   seq) in a last-writer table (one slot per word).  The statement is wrapped as `{ store; hook; }`.
2. At projectile init (MIPS 0x8005CB10, funcs_13.c) under ROGUESQ_LOG_HUDBIT, first 3 per owner id: prints
   [recw] lines with the last writer of each record word 0..7 plus a match flag (logged value == memory now:
   the positive control that the hook saw the real writer), and a [recv] line with the node direction
   (+0xC0..C8), velocity (+0xD8..E0), origin, P=*(rec+0xC) relative to the shooter node, the verified player
   position (cached from the s5781 player terrain-sample call, funcs_43.c) and cos(vel, player-origin) and
   cos(vel, each of the three s5792 class-2 victim positions).
Idempotent; mirrored into fixup_game_funcs_vendored.py.
"""
import pathlib
import re
import sys

T = "PATCH: s5798 recwatch"
LO, SPAN = 0x80165B00, 0x300
HDR = ('/* ' + T + ' */\n'
       'extern void rs64_s5798_st(uint8_t* rdram, recomp_context* ctx, uint32_t pc, uint32_t a, int w, const char* fn);\n'
       '#define RS64_S5798_ST(pc, off, base, w) do { uint32_t _a5798 = (uint32_t)((base) + (off)); '
       'if ((uint32_t)(_a5798 - 0x%08Xu) < 0x%Xu) rs64_s5798_st(rdram, ctx, (pc), _a5798, (w), __func__); } while (0)\n' % (LO, SPAN))

HELPER13 = r'''/* PATCH: s5798 recwatch helper */
#include <execinfo.h>
#include <dlfcn.h>
float rs64_s5798_pl[4];
long long rs64_s5798_pl_ms;
static struct { uint32_t pc, val, ra, seq; const char* fn; } s5798_last[0x%X / 4];
static uint32_t s5798_seq;
void rs64_s5798_st(uint8_t* rdram, recomp_context* ctx, uint32_t pc, uint32_t a, int w, const char* fn) {
    uint32_t i = (a - 0x%08Xu) >> 2;
    s5798_seq++;
    s5798_last[i].pc = pc; s5798_last[i].val = (uint32_t)MEM_W(0, (gpr)(int32_t)(a & ~3u)); s5798_last[i].ra = (uint32_t)ctx->r31;
    s5798_last[i].seq = s5798_seq; s5798_last[i].fn = fn;
    if (w == 8 && i + 1 < 0x%X / 4) { s5798_last[i + 1] = s5798_last[i]; s5798_last[i + 1].val = (uint32_t)MEM_W(0, (gpr)(int32_t)((a & ~3u) + 4)); }
}
static float s5798_f(uint8_t* rdram, uint32_t a) { uint32_t w = (a >= 0x80000000u && a < 0x80800000u) ? (uint32_t)MEM_W(0, (gpr)(int32_t)a) : 0u; float f; memcpy(&f, &w, 4); return f; }
static float s5798_cos(const float* v, const float* o, const float* t) { float d[3] = { t[0] - o[0], t[1] - o[1], t[2] - o[2] };
    float a = sqrtf(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]), b = sqrtf(d[0]*d[0] + d[1]*d[1] + d[2]*d[2]);
    return (a > 1e-6f && b > 1e-6f) ? (v[0]*d[0] + v[1]*d[1] + v[2]*d[2]) / (a * b) : 9.f; }
static void s5798_init(uint8_t* rdram, recomp_context* ctx) {
    static int e = -1, n = 0; static uint32_t ids[24]; static int cnt[24];
    if (e < 0) { const char* s = getenv("ROGUESQ_LOG_HUDBIT"); e = (s && s[0]) ? 1 : 0; }
    if (!e) return;
    uint32_t rec = (uint32_t)ctx->r16, node = (uint32_t)ctx->r17;
    if (rec < 0x80000000u || rec >= 0x80400000u || node < 0x80000000u || node >= 0x80400000u) return;
    uint32_t sid = (uint32_t)MEM_HU(0, (gpr)(int32_t)(rec + 0x18)); int k = -1;
    for (int i = 0; i < n; i++) if (ids[i] == sid) k = i;
    if (k < 0 && n < 24) { k = n++; ids[k] = sid; }
    if (k < 0 || cnt[k] >= 3) return;
    cnt[k]++;
    extern long long rs64_s5773_ms(void);
    long long ms = rs64_s5773_ms();
    uint32_t P = (uint32_t)MEM_W(0, (gpr)(int32_t)(rec + 0xC));
    uint32_t tb = (uint32_t)MEM_W(0, (gpr)(int32_t)0x80130BB0u), sn = (uint32_t)MEM_W(0, (gpr)(int32_t)(tb + (sid & 0xFFFF) * 8));
    fprintf(stderr, "[recw] t=%%lld sid=%%04x n=%%d rec=%%08x sp=%%08x rec-sp=%%d hook_seq=%%u P=%%08x shooter=%%08x P-shooter=%%d\n", ms, sid, cnt[k], rec,
            (uint32_t)ctx->r29, (int)(rec - (uint32_t)ctx->r29), s5798_seq, P, sn, (int)(P - sn));
    for (int q = 0; q < 8; q++) {
        uint32_t a = rec + q * 4;
        if (a - 0x%08Xu >= 0x%Xu) continue;
        uint32_t i = (a - 0x%08Xu) >> 2, cur = (uint32_t)MEM_W(0, (gpr)(int32_t)a);
        fprintf(stderr, "[recw]   +%%02x cur=%%08x last_pc=%%08x val=%%08x match=%%d ra=%%08x fn=%%s age=%%u\n", q * 4, cur, s5798_last[i].pc, s5798_last[i].val,
                s5798_last[i].val == cur, s5798_last[i].ra, s5798_last[i].fn ? s5798_last[i].fn : "(none)", s5798_seq - s5798_last[i].seq);
    }
    { void* bt[10]; int nb = backtrace(bt, 10); char buf[600]; int off = 0; buf[0] = 0;
      for (int b = 1; b < nb && off < 560; b++) { Dl_info di; const char* nm = (dladdr(bt[b], &di) && di.dli_sname) ? di.dli_sname : "?"; off += snprintf(buf + off, sizeof(buf) - off, " %%s", nm); }
      fprintf(stderr, "[recw]   host_bt:%%s\n", buf); }
    float dir[3], vel[3], org[3], pl[3] = { rs64_s5798_pl[0], rs64_s5798_pl[1], rs64_s5798_pl[2] };
    for (int q = 0; q < 3; q++) { dir[q] = s5798_f(rdram, node + 0xC0 + q * 4); vel[q] = s5798_f(rdram, node + 0xD8 + q * 4); org[q] = s5798_f(rdram, P + q * 4); }
    static const float V[3][3] = { { 37.4f, -0.05f, 35.6f }, { 69.4f, -1.3f, 22.6f }, { 90.7f, 1.7f, 42.3f } };
    float dp[3] = { pl[0] - org[0], pl[1] - org[1], pl[2] - org[2] };
    fprintf(stderr, "[recv] t=%%lld sid=%%04x dir=(%%.3f %%.3f %%.3f) vel=(%%.3f %%.3f %%.3f) spd=%%.2f org=(%%.2f %%.2f %%.2f) pl=(%%.2f %%.2f %%.2f) pl_ok=%%d pl_age_ms=%%lld dist_pl=%%.1f "
            "cos_vel_pl=%%.3f cos_vel_v0=%%.3f cos_vel_v1=%%.3f cos_vel_v2=%%.3f\n", ms, sid, dir[0], dir[1], dir[2], vel[0], vel[1], vel[2], s5798_f(rdram, rec + 0x10),
            org[0], org[1], org[2], pl[0], pl[1], pl[2], (int)rs64_s5798_pl[3], ms - rs64_s5798_pl_ms, sqrtf(dp[0]*dp[0] + dp[1]*dp[1] + dp[2]*dp[2]),
            s5798_cos(vel, org, pl), s5798_cos(vel, org, V[0]), s5798_cos(vel, org, V[1]), s5798_cos(vel, org, V[2]));
}
''' % (SPAN, LO, SPAN, LO, SPAN, LO)

ANC13 = "    // 0x8005CB10: sh          $v0, 0xF8($s1)\n"
INC = '#include "funcs.h"\n'
RE_M = re.compile(r'^(\s+)(MEM_([WHB])\(([-0-9A-FX]+), (ctx->r\d+)\) = [^;]+;)$')
RE_SD = re.compile(r'^(\s+)(SD\(.+, ([-0-9A-FX]+), (ctx->r\d+)\);)$')
RE_PC = re.compile(r'^\s*// (0x[0-9A-F]{8}):')
W = {"W": 4, "H": 2, "B": 1}

# s5781 player terrain-sample hook: cache the verified player position (obj == 0x80137DBC) for [recv].
ANC43 = "    if (s5781_e && player) { x = s5781_f(pos); y = s5781_f(pos + 4); z = s5781_f(pos + 8); }\n"
ADD43 = ("    if (player) { extern float rs64_s5798_pl[4]; extern long long rs64_s5798_pl_ms; extern long long rs64_s5773_ms(void); "
         "rs64_s5798_pl[0] = s5781_f(pos); rs64_s5798_pl[1] = s5781_f(pos + 4); rs64_s5798_pl[2] = s5781_f(pos + 8); rs64_s5798_pl[3] = 1; "
         "rs64_s5798_pl_ms = rs64_s5773_ms(); } /* PATCH: s5798 player cache */\n")


def apply(text, name=""):
    if T in text:
        return text, 0
    if text.count(INC) != 1:
        return text, 0
    out, n, pc = [], 0, "0u"
    for line in text.splitlines(keepends=True):
        body = line.rstrip("\n")
        m = RE_PC.match(body)
        if m:
            pc = m.group(1) + "u"
        m = RE_M.match(body)
        if m:
            out.append("%s{ %s RS64_S5798_ST(%s, %s, %s, %d); }\n" % (m.group(1), m.group(2), pc, m.group(4), m.group(5), W[m.group(3)]))
            n += 1
            continue
        m = RE_SD.match(body)
        if m:
            out.append("%s{ %s RS64_S5798_ST(%s, %s, %s, 8); }\n" % (m.group(1), m.group(2), pc, m.group(3), m.group(4)))
            n += 1
            continue
        out.append(line)
    text = "".join(out).replace(INC, INC + HDR, 1)
    if name == "funcs_13.c":
        text = text.replace(INC + HDR, INC + HDR + HELPER13, 1)
        assert text.count(ANC13) == 1
        text = text.replace(ANC13, "    s5798_init(rdram, ctx); /* " + T + " init */\n" + ANC13, 1)
    if name == "funcs_43.c":
        assert text.count(ANC43) == 1, "s5781 must be applied first"
        text = text.replace(ANC43, ANC43 + ADD43, 1)
    return text, n


if __name__ == "__main__":
    base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
    tot = 0
    for p in sorted(base.glob("funcs_*.c")):
        t = p.read_text()
        t2, n = apply(t, p.name)
        if t2 != t:
            p.write_text(t2)
        tot += n
    print("stores hooked:", tot)
    fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
    s = fp.read_text()
    if "apply_s5798_recwatch" in s:
        print("fixup already")
    else:
        # last entry of RS64_REPLAY: every other patch has already matched its exact store-line anchors
        lst = '    "apply_s4991_per_origin_bad_budget.py",\n]\n'
        assert s.count(lst) == 1
        s = s.replace(lst, '    "apply_s4991_per_origin_bad_budget.py",\n    "apply_s5798_recwatch.py",\n]\n', 1)
        fp.write_text(s)
        print("fixup patched")
