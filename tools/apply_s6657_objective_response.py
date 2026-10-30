"""Opt-in single-flight TELE windows and actual objective-store/victim joins."""
from pathlib import Path
import re
import sys

TAG = 'PATCH: s6657 objective response'
FILES = ('funcs_15.c', 'funcs_16.c', 'funcs_35.c', 'funcs_41.c', 'funcs_43.c')
DECL = r'''
extern int rs6657_gate(uint8_t*);
extern void rs6657_callback(uint8_t*);
extern void rs6657_force(uint8_t*, uint32_t, uint32_t, uint32_t);
extern void rs6657_damage(uint8_t*, uint32_t, int, int);
extern void rs6657_write(uint8_t*, recomp_context*, uint32_t, uint32_t, uint32_t, uint32_t);
extern _Thread_local uint32_t rs6657_victim;
'''
HELPERS = r'''
extern uint32_t rs64_vi_committed_width(void), rs64_vi_committed_origin(void);
extern volatile uint32_t rs64_vi_n_g;
_Thread_local uint32_t rs6657_victim;
static int rs6657_en = -1, rs6657_seen, rs6657_started, rs6657_done;
static uint32_t rs6657_start, rs6657_arm = 99, rs6657_rows[3], rs6657_hits[3], rs6657_dmg[3], rs6657_seq;
static uint32_t rs6657_prev[3]; static unsigned rs6657_read_init;
static struct { uint32_t seq, vi, shape, node, npc, desc, proj; } rs6657_events[256];
static unsigned rs6657_ne;
static int rs6657_enabled(void) {
    if (rs6657_en < 0) { const char* e = getenv("ROGUESQ_OBJECTIVE_RESPONSE"); rs6657_en = e && e[0] == '1'; }
    return rs6657_en;
}
static uint32_t rs6657_word(uint8_t* rdram, uint32_t a) { return (uint32_t)MEM_W(S32((int32_t)a), 0); }
static uint32_t rs6657_desc(uint8_t* rdram, uint32_t o) {
    return o >= 0x80000400u && o < 0x80800000u && !(o & 3) ? rs6657_word(rdram, o + 0x34) : 0;
}
static int rs6657_flight(uint8_t* rdram) {
    if (!rs6657_enabled() || rs6657_done) return 0;
    uint32_t origin = rs64_vi_committed_origin() & 0xFFFFFFu;
    int selected = MEM_BU(S32((int32_t)0x80130B40u), 0) == 0;
    int flight = rs64_vi_committed_width() == 512 && (origin == 0x690400 || origin == 0x620400);
    if (!rs6657_started) {
        if (!rs6657_seen || !selected || !flight) return 0;
        rs6657_started = 1; rs6657_start = rs64_vi_n_g;
        fprintf(stderr, "[objresp-epoch] epoch=1 vi=%u origin=%06x width=512 B40=0 callback=lv0_checkComplexObjectives\n", rs6657_start, origin);
    }
    uint32_t dv = rs64_vi_n_g - rs6657_start;
    uint32_t c1 = rs6657_word(rdram, 0x80138060u), c2 = rs6657_word(rdram, 0x80138064u), c3 = rs6657_word(rdram, 0x80138068u);
    if (!selected || !flight || dv >= 5400 || c1 >= 18 || c2 >= 1 || c3 >= 1) {
        rs6657_done = 1;
        fprintf(stderr, "[objresp-done] epoch=1 vi=%u dv=%u selected=%d flight=%d c=%u,%u,%u forces=%u,%u,%u writes=%u,%u,%u damage=%u,%u,%u\n", rs64_vi_n_g, dv, selected, flight, c1, c2, c3, rs6657_hits[0], rs6657_hits[1], rs6657_hits[2], rs6657_rows[0], rs6657_rows[1], rs6657_rows[2], rs6657_dmg[0], rs6657_dmg[1], rs6657_dmg[2]);
        fflush(stderr); return 0;
    }
    uint32_t arm = dv < 1800 ? 0 : dv < 4200 ? 1 : 2;
    if (arm != rs6657_arm) {
        rs6657_arm = arm;
        fprintf(stderr, "[objresp-arm] epoch=1 vi=%u dv=%u arm=%u tele=%u c=%u,%u,%u\n", rs64_vi_n_g, dv, arm, arm == 1, c1, c2, c3);
    }
    return 1;
}
int rs6657_gate(uint8_t* rdram) { return !rs6657_enabled() || (rs6657_flight(rdram) && rs6657_arm == 1); }
void rs6657_callback(uint8_t* rdram) {
    if (!rs6657_enabled()) return;
    rs6657_seen = 1;
    if (!rs6657_flight(rdram)) return;
    for (unsigned i = 0; i < 3; i++) {
        uint32_t value = rs6657_word(rdram, 0x80138060u + i * 4);
        if (!rs6657_read_init || value != rs6657_prev[i])
            fprintf(stderr, "[objresp-readback] epoch=1 vi=%u arm=%u id=%u old=%u new=%u initialized=%u\n", rs64_vi_n_g, rs6657_arm, i + 1, rs6657_prev[i], value, rs6657_read_init);
        rs6657_prev[i] = value;
    }
    rs6657_read_init = 1;
}
void rs6657_force(uint8_t* rdram, uint32_t shape, uint32_t npc, uint32_t proj) {
    if (!rs6657_enabled() || !rs6657_flight(rdram)) return;
    uint32_t node = npc;
    npc = node >= 0x80000400u && node < 0x80800000u && !(node & 3) ? rs6657_word(rdram, node + 4) : 0;
    uint32_t desc = rs6657_desc(rdram, npc);
    unsigned z;
    for (z = 0; z < rs6657_ne; z++) if (rs6657_events[z].node == node && rs6657_events[z].npc == npc && rs6657_events[z].desc == desc) break;
    if (z == rs6657_ne) { if (z == 256) return; rs6657_ne++; }
    rs6657_events[z].seq = ++rs6657_seq; rs6657_events[z].vi = rs64_vi_n_g;
    rs6657_events[z].shape = shape; rs6657_events[z].node = node; rs6657_events[z].npc = npc;
    rs6657_events[z].desc = desc; rs6657_events[z].proj = proj;
    rs6657_hits[rs6657_arm]++;
    if (rs6657_hits[rs6657_arm] <= 64)
        fprintf(stderr, "[objresp-force] epoch=1 vi=%u arm=%u seq=%u shape=%08x node=%08x npc=%08x desc=%08x proj=%08x\n", rs64_vi_n_g, rs6657_arm, rs6657_seq, shape, node, npc, rs6657_events[z].desc, proj);
}
static unsigned rs6657_match(uint32_t npc, uint32_t desc) {
    unsigned n = rs6657_ne < 256 ? rs6657_ne : 256, best = 256;
    for (unsigned i = 0; i < n; i++)
        if ((npc && (rs6657_events[i].npc == npc || rs6657_events[i].node == npc || rs6657_events[i].shape == npc)) || (desc && rs6657_events[i].desc == desc))
            if (best == 256 || rs6657_events[i].seq > rs6657_events[best].seq) best = i;
    return best;
}
void rs6657_damage(uint8_t* rdram, uint32_t npc, int before, int after) {
    if (!rs6657_enabled() || !rs6657_flight(rdram)) return;
    unsigned m = rs6657_match(npc, 0);
    if (rs6657_dmg[rs6657_arm]++ < 128)
        fprintf(stderr, "[objresp-damage] epoch=1 vi=%u arm=%u object=%08x matched_npc=%08x desc=%08x hp_old=%d hp_new=%d force_seq=%u age_vi=%u\n", rs64_vi_n_g, rs6657_arm, npc, m < 256 ? rs6657_events[m].npc : 0, m < 256 ? rs6657_events[m].desc : 0, before, after, m < 256 ? rs6657_events[m].seq : 0, m < 256 ? rs64_vi_n_g - rs6657_events[m].vi : 0);
}
void rs6657_write(uint8_t* rdram, recomp_context* ctx, uint32_t pc, uint32_t addr, uint32_t old, uint32_t desc) {
    if (!rs6657_enabled() || !rs6657_started || rs6657_done) return;
    /* A write crossing the stop threshold must be recorded before the gate closes. */
    uint32_t origin = rs64_vi_committed_origin() & 0xFFFFFFu;
    if (rs64_vi_committed_width() != 512 || (origin != 0x690400 && origin != 0x620400)) return;
    if (addr < 0x80138060u || addr >= 0x801388A0u || (addr & 3)) return;
    uint32_t value = rs6657_word(rdram, addr), npc = rs6657_victim;
    if (!desc) desc = rs6657_desc(rdram, npc);
    unsigned m = rs6657_match(npc, desc), matched_reg = 0;
    uint32_t regs[8] = {U32(ctx->r16), U32(ctx->r17), U32(ctx->r18), U32(ctx->r19), U32(ctx->r20), U32(ctx->r21), U32(ctx->r22), U32(ctx->r23)};
    if (m == 256) for (unsigned i = 0; i < 8; i++) {
        unsigned candidate = rs6657_match(regs[i], 0);
        if (candidate < 256 && rs6657_desc(rdram, rs6657_events[candidate].npc) == rs6657_events[candidate].desc && (m == 256 || rs6657_events[candidate].seq > rs6657_events[m].seq)) { m = candidate; matched_reg = 16 + i; }
    }
    if (m < 256) { npc = rs6657_events[m].npc; desc = rs6657_events[m].desc; }
    if (++rs6657_rows[rs6657_arm] <= 1024)
        fprintf(stderr, "[objresp-write] epoch=1 vi=%u arm=%u pc=%08x id=%u old=%u new=%u victim=%08x desc=%08x node=%08x matched_reg=%u force_seq=%u age_vi=%u s=%08x,%08x,%08x,%08x,%08x,%08x,%08x,%08x\n", rs64_vi_n_g, rs6657_arm, pc, (addr - 0x80138060u) / 4 + 1, old, value, npc, desc, m < 256 ? rs6657_events[m].node : 0, matched_reg, m < 256 ? rs6657_events[m].seq : 0, m < 256 ? rs64_vi_n_g - rs6657_events[m].vi : 0, U32(ctx->r16), U32(ctx->r17), U32(ctx->r18), U32(ctx->r19), U32(ctx->r20), U32(ctx->r21), U32(ctx->r22), U32(ctx->r23));
}
'''
WRITERS = {
    'funcs_15.c': (0x8006594C, 0x80065974, 0x80065A34),
    'funcs_35.c': (0x800C75E8, 0x800C7618),
    'funcs_41.c': (0x800F3D80, 0x800F4378),
}

def apply(text, name):
    if name not in FILES or TAG in text:
        return text, 0
    text = text.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + DECL + '/* ' + TAG + ' */\n', 1)
    assert TAG in text
    if name == 'funcs_16.c':
        a = 'static void rs5835_probe(uint8_t* rdram, recomp_context* ctx) {'
        assert text.count(a) == 1
        text = text.replace(a, HELPERS + '\n' + a)
        a = 'if (rs5837_en && w == 0 && cc[3] > 0.0f && c1f &&'
        assert text.count(a) == 1
        text = text.replace(a, 'if (rs5837_en && rs6657_gate(rdram) && w == 0 && cc[3] > 0.0f && c1f &&')
        a = '        rs5839_tp++; if (rs5837_tele++ < 10)'
        assert text.count(a) == 1
        text = text.replace(a, '        { uint32_t tb = rs6657_word(rdram, 0x80130BB0u); rs6657_force(rdram, rs5839_obj, rs6657_word(rdram, tb + (rs5841_cand & 0xFFFF) * 8), rs5856_proj); }\n' + a)
        a = '    datItemSetObjectiveBooleanCount(rdram, ctx);\n        goto after_53;'
        assert text.count(a) == 1
        text = text.replace(a, '    { uint32_t saved = rs6657_victim; rs6657_victim = U32(ctx->r17);\n    datItemSetObjectiveBooleanCount(rdram, ctx);\n    rs6657_victim = saved; }\n        goto after_53;')
    if name == 'funcs_43.c':
        a = 'RECOMP_FUNC void lv0_checkComplexObjectives(uint8_t* rdram, recomp_context* ctx) {'
        assert text.count(a) == 1
        text = text.replace(a, a + '\n    rs6657_callback(rdram);')
    if name == 'funcs_41.c':
        a = '    int post = rs5857_hp(rdram, o); unsigned z;'
        assert text.count(a) == 1
        text = text.replace(a, a + '\n    rs6657_damage(rdram, o, pre, post);')
    if name == 'funcs_15.c':
        a = 'RECOMP_FUNC void applyDatObjectiveTriggerEffect(uint8_t* rdram, recomp_context* ctx) {'
        assert text.count(a) == 1
        text = text.replace(a, a + '\n    uint32_t rs6657_dat = U32(ctx->r4);')
    for pc in WRITERS.get(name, ()):
        pattern = r'(?m)^([ \t]*)\{ (MEM_W\(([^,]+), (ctx->r\d+)\)) = ([^;]+); (RS64_S5798_ST\(0x' + f'{pc:08X}' + r'u,[^\n]+) \}'
        desc = 'rs6657_dat' if pc == 0x80065A34 else '0'
        def replace(m):
            indent, mem, off, reg, value, tail = m.groups()
            return (f'{indent}{{ uint32_t rs6657_old = (uint32_t){mem}; {mem} = {value}; {tail} '
                    f'rs6657_write(rdram, ctx, 0x{pc:08X}u, U32(ADD32({reg}, {off})), rs6657_old, {desc}); }}')
        text, n = re.subn(pattern, replace, text)
        assert n in (1, 2), (name, hex(pc), n)
    return text, 1

if __name__ == '__main__':
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('../N64Recomp/RecompiledFuncs')
    for name in FILES:
        p = base / name
        text, n = apply(p.read_text(), name)
        if n:
            p.write_text(text)
        print(name, n)
