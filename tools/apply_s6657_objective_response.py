"""Opt-in single-flight TELE windows and actual objective-store/victim joins."""
from pathlib import Path
import re
import sys

TAG = 'PATCH: s6657 objective response'
FILES = ('funcs_10.c', 'funcs_42.c', 'funcs_8.c', 'funcs_13.c', 'funcs_15.c', 'funcs_16.c', 'funcs_35.c', 'funcs_36.c', 'funcs_38.c', 'funcs_41.c', 'funcs_43.c', 'funcs_44.c', 'funcs_45.c')
DECL = r'''
extern int rs6657_gate(uint8_t*);
extern void rs6657_callback(uint8_t*);
extern void rs6657_callback_level(uint8_t*, int);
extern void rs6657_force(uint8_t*, uint32_t, uint32_t, uint32_t);
extern void rs6657_damage(uint8_t*, uint32_t, int, int);
extern void rs6657_write(uint8_t*, recomp_context*, uint32_t, uint32_t, uint32_t, uint32_t);
extern _Thread_local uint32_t rs6657_victim;
'''
HELPERS = r'''
extern uint32_t rs64_vi_committed_width(void), rs64_vi_committed_origin(void);
#include <signal.h>
extern volatile uint32_t rs64_vi_n_g;
_Thread_local uint32_t rs6657_victim;
static int rs6657_en = -1, rs6657_seen, rs6657_started, rs6657_done;
static uint32_t rs6657_start, rs6657_arm = 99, rs6657_rows[3], rs6657_hits[3], rs6657_dmg[3], rs6657_seq;
static int rs6657_level;
static int rs6661_dosed;
static int rs6670_forced;
static uint32_t rs6671_generation[2048];
static struct { uint32_t node,npc,desc,slot,generation,detail,name,store,effect; int hp,ordinary; } rs6671_control;
static _Thread_local uint32_t rs6670_api_active;
static uint32_t rs6666_dat;
static int rs6668_repeat(uint8_t*, uint32_t, uint32_t, uint32_t);
static uint32_t rs6666_limit = 5400, rs6666_on;
static void rs6666_sample(uint8_t*, recomp_context*, const char*);
static uint32_t rs6657_prev[128], rs6657_bool6, rs6662_bools[128]; static unsigned rs6657_read_init;
static struct { uint32_t seq, vi, shape, node, npc, desc, proj, send_seq, send_vi, send_proj; } rs6657_events[256];
static unsigned rs6657_ne;
static uint32_t rs6660_pending_id, rs6660_pending_value, rs6660_observed;
static int rs6660_ok(uint32_t a) { return a >= 0x80000400u && a < 0x807FFF00u && !(a & 3); }
static int rs6668_named_rescue(uint32_t desc) {
    return rs6666_dat && (desc == rs6666_dat + 0x1510 || desc == rs6666_dat + 0x1628 || desc == rs6666_dat + 0x1740);
}
static int rs6660_named(uint32_t id) { return rs6657_level == 3 ? id == 28 : rs6657_level == 2 ? id == 40 : (id == 13 || id == 40 || id == 41); }
static void rs6660_census(uint8_t*);
static unsigned rs6657_match(uint32_t, uint32_t);
static int rs6660_candidate(uint8_t*, uint32_t, uint32_t, uint32_t, float, int);
static int rs6657_enabled(void) {
    if (rs6657_en < 0) { const char* e = getenv("ROGUESQ_OBJECTIVE_RESPONSE"); rs6657_en = e && e[0] == '1'; const char* l = getenv("ROGUESQ_OBJECTIVE_RESPONSE_LEVEL"); rs6657_level = l ? atoi(l) : 0; const char* v = getenv("ROGUESQ_OBJECTIVE_RESPONSE_VI"); if (rs6657_level == 2 && v && atoi(v) > 5400 && atoi(v) <= 12000) rs6666_limit = atoi(v); if (rs6657_level != 0 && rs6657_level != 1 && rs6657_level != 2 && rs6657_level != 3 && rs6657_level != 4 && rs6657_level != 5) rs6657_en = 0; }
    return rs6657_en;
}
static uint32_t rs6657_word(uint8_t* rdram, uint32_t a) { return (uint32_t)MEM_W(S32((int32_t)a), 0); }
static uint32_t rs6657_desc(uint8_t* rdram, uint32_t o) {
    return o >= 0x80000400u && o < 0x80800000u && !(o & 3) ? rs6657_word(rdram, o + 0x34) : 0;
}
static int rs6657_flight(uint8_t* rdram) {
    if (!rs6657_enabled() || rs6657_done) return 0;
    uint32_t origin = rs64_vi_committed_origin() & 0xFFFFFFu;
    int selected = MEM_BU(S32((int32_t)0x80130B40u), 0) == rs6657_level;
    int flight = rs64_vi_committed_width() == 512 && (origin == 0x690400 || origin == 0x620400);
    if (!rs6657_started) {
        if (!rs6657_seen || !selected || !flight) return 0;
        rs6657_started = 1; rs6657_start = rs64_vi_n_g;
        fprintf(stderr, "[objresp-epoch] epoch=1 vi=%u origin=%06x width=512 B40=%d callback=lv%d_checkComplexObjectives\n", rs6657_start, origin, rs6657_level, rs6657_level);
    }
    uint32_t dv = rs64_vi_n_g - rs6657_start;
    uint32_t c1 = rs6657_word(rdram, 0x80138060u), c2 = rs6657_word(rdram, 0x80138064u), c3 = rs6657_word(rdram, 0x80138068u);
    if ((rs6660_observed && !((rs6657_level == 2 || rs6657_level == 3 || rs6657_level == 4) && rs6661_dosed)) || !selected || !flight || dv >= rs6666_limit || (rs6657_level == 0 ? (c1 >= 18 || c2 >= 1 || c3 >= 1) : rs6657_level == 2 ? (rs6657_read_init && ((rs6657_prev[39] && !rs6661_dosed) || MEM_BU(S32((int32_t)0x80138903u), 0) || MEM_BU(S32((int32_t)0x8013890Cu), 0))) : rs6657_level == 5 ? (rs6657_prev[1] >= 3 || rs6657_prev[3] >= 8) : rs6657_level == 4 ? (rs6657_prev[14] >= 2 || rs6657_prev[15] >= 2 || MEM_BU(S32((int32_t)0x801388B9u),0)) : rs6657_level == 3 ? (MEM_BU(S32((int32_t)0x801388A3u),0) || MEM_BU(S32((int32_t)0x801388B1u),0) || MEM_BU(S32((int32_t)0x801388B4u),0) || rs6657_word(rdram,0x801380B4u)) : (rs6657_read_init && (rs6657_prev[12] >= 3 || MEM_BU(S32((int32_t)0x801388A5u), 0))))) {
        rs6657_done = 1;
        fprintf(stderr, "[objresp-done] epoch=1 vi=%u dv=%u selected=%d flight=%d c=%u,%u,%u forces=%u,%u,%u writes=%u,%u,%u damage=%u,%u,%u\n", rs64_vi_n_g, dv, selected, flight, c1, c2, c3, rs6657_hits[0], rs6657_hits[1], rs6657_hits[2], rs6657_rows[0], rs6657_rows[1], rs6657_rows[2], rs6657_dmg[0], rs6657_dmg[1], rs6657_dmg[2]);
        fflush(stderr); return 0;
    }
    uint32_t arm = dv < 1800 ? 0 : dv < 4200 ? 1 : 2;
    if (rs6657_level == 2 && rs6666_limit > 5400)
        arm = !rs6666_on ? 0 : rs64_vi_n_g - rs6666_on < 1800 ? 1 : 2;
    if (arm != rs6657_arm) {
        rs6657_arm = arm;
        fprintf(stderr, "[objresp-arm] epoch=1 vi=%u dv=%u arm=%u tele=%u c=%u,%u,%u\n", rs64_vi_n_g, dv, arm, arm == 1, c1, c2, c3);
    }
    return 1;
}
int rs6657_gate(uint8_t* rdram) { return !rs6657_enabled() || (rs6657_level != 4 && rs6657_level != 5 && rs6657_flight(rdram) && rs6657_arm == 1 && !rs6660_pending_id && !rs6661_dosed && !(rs6657_level == 3 && rs6670_forced)); }
void rs6657_callback_level(uint8_t* rdram, int level) {
    if (!rs6657_enabled() || level != rs6657_level) return;
    rs6657_seen = 1;
    if (!rs6657_flight(rdram)) return;
    if (rs6657_level >= 1) rs6660_census(rdram);
    for (unsigned i = 0; i < (rs6657_level == 0 ? 3u : 128u); i++) {
        uint32_t value = rs6657_word(rdram, 0x80138060u + i * 4);
        if (!rs6657_read_init || value != rs6657_prev[i])
            fprintf(stderr, "[objresp-readback] epoch=1 vi=%u arm=%u id=%u old=%u new=%u initialized=%u\n", rs64_vi_n_g, rs6657_arm, i + 1, rs6657_prev[i], value, rs6657_read_init);
        rs6657_prev[i] = value;
        if (i + 1 == rs6660_pending_id && value == rs6660_pending_value) rs6660_observed = 1;
    }
    uint32_t bool6 = MEM_BU(S32((int32_t)0x801388A5u), 0);
    if (rs6657_level == 1 && (!rs6657_read_init || bool6 != rs6657_bool6))
        fprintf(stderr, "[objresp-bool] epoch=1 vi=%u arm=%u id=6 old=%u new=%u initialized=%u\n", rs64_vi_n_g, rs6657_arm, rs6657_bool6, bool6, rs6657_read_init);
    if (rs6657_level >= 2) for (unsigned i = 0; i < 128; i++) {
        uint32_t value = MEM_BU(S32((int32_t)(0x801388A0u + i)), 0);
        if (!rs6657_read_init || value != rs6662_bools[i])
            fprintf(stderr, "[objresp-bool] epoch=1 vi=%u arm=%u id=%u old=%u new=%u initialized=%u\n", rs64_vi_n_g, rs6657_arm, i + 1, rs6662_bools[i], value, rs6657_read_init);
        rs6662_bools[i] = value;
    }
    rs6657_bool6 = bool6;
    if (!rs6657_read_init && rs6657_level == 2) fprintf(stderr, "[objresp-semantics] level=2 vi=%u c40=%u friendlies=1-c40 fail=c40-positive-to-bool109 success=bool31+32+33+99\n", rs64_vi_n_g, rs6657_word(rdram, 0x801380FCu));
    if (!rs6657_read_init && rs6657_level < 2) fprintf(stderr, "[objresp-semantics] level=%d vi=%u c13=%u c40=%u c41=%u bool6=%u friendlies=19-(c40+c13+c41)\n", rs6657_level, rs64_vi_n_g, rs6657_word(rdram, 0x80138090u), rs6657_word(rdram, 0x801380FCu), rs6657_word(rdram, 0x80138100u), MEM_BU(S32((int32_t)0x801388A5u), 0));
    if (!rs6657_read_init && rs6657_level == 3) fprintf(stderr, "[objresp-semantics] level=3 vi=%u friendlies=100-(c27+c28) loss=bool4+18+21 success=c22\n", rs64_vi_n_g);
    rs6657_read_init = 1;
}
void rs6657_callback(uint8_t* rdram) { rs6657_callback_level(rdram, 0); }
void rs6657_force(uint8_t* rdram, uint32_t shape, uint32_t npc, uint32_t proj) {
    if (!rs6657_enabled() || !rs6657_flight(rdram)) return;
    if (rs6657_level == 3) rs6670_forced = 1;
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
    if (rs6657_level == 3 && rs6670_api_active) desc = rs6666_dat + 0x48c;
    if (!desc) desc = rs6657_desc(rdram, npc);
    if (rs6657_level >= 1 && rs6660_named((addr - 0x80138060u) / 4 + 1) && old != value) {
        rs6660_pending_id = (addr - 0x80138060u) / 4 + 1; rs6660_pending_value = value;
    }
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

static void rs6660_fields(uint8_t* rdram, uint32_t desc, uint32_t f[6]) {
    for (unsigned i = 0; i < 6; i++) f[i] = rs6660_ok(desc) ? rs6657_word(rdram, desc + 0x70 + i * 4) : 0;
}
static int rs6660_selected(uint32_t f[6]) {
    if (rs6657_level == 4 || rs6657_level == 5) return f[0] == 40 && f[1] == 1 && !f[2] && !f[3] && !f[4];
    if (rs6657_level == 3) return f[0] == 28 && f[1] == 1 && !f[2] && !f[3] && !f[4];
    if (rs6657_level == 2) return ((f[0] == 40 && f[1]) || (f[4] == 40 && f[5])) &&
        !(f[3] && (f[2] == 1 || f[2] == 2 || f[2] == 3 || f[2] == 4 || f[2] == 31 || f[2] == 32 || f[2] == 33 || f[2] == 99));
    return !(f[2] == 6 && f[3]) && ((rs6660_named(f[0]) && f[1]) || (rs6660_named(f[4]) && f[5]));
}
static uint8_t rs6663_free[2048];
static int rs6663_valid;
static uint32_t rs6663_table;
static uint32_t rs6663_half(uint8_t* rdram, uint32_t a) { return MEM_HU(S32((int32_t)a), 0); }
static int rs6663_refresh(uint8_t* rdram) {
    rs6663_valid = 0;
    rs6663_table = rs6657_word(rdram, 0x80130BB0u);
    if (!rs6660_ok(rs6663_table) || rs6663_table > 0x807FC000u) return 0;
    memset(rs6663_free, 0, sizeof(rs6663_free));
    uint32_t i = rs6663_half(rdram, 0x80130BB4u), n = 0;
    while (i != 0xFFFFu) {
        if (i >= 2048 || rs6663_free[i] || ++n > 2048) return 0;
        rs6663_free[i] = 1;
        i = rs6663_half(rdram, rs6663_table + i * 8 + 4);
    }
    return rs6663_valid = 1;
}
static int rs6663_owned(uint8_t* rdram, uint32_t node) {
    uint32_t pool = rs6657_word(rdram, 0x80130BB8u);
    return rs6660_ok(pool) && node >= pool && node - pool < 192 * 60 && (node - pool) % 60 == 0;
}
static int rs6663_kind(uint32_t handler) {
    switch (handler) {
    case 0x8006CBB0u:
    case 0x800D3894u:
    case 0x800DE80Cu:
    case 0x800CABD4u:
    case 0x800D5208u:
    case 0x800D93C0u:
    case 0x800DB11Cu:
        return 1;
    case 0x800ECE10u:
        return 3;
    case 0x800403ECu:
    case 0x80044724u:
    case 0x8004C6C8u:
    case 0x8005427Cu:
    case 0x8005BCC4u:
    case 0x8005C874u:
    case 0x80060690u:
    case 0x80060D8Cu:
    case 0x8006C3A0u:
    case 0x80075720u:
    case 0x8006F6A0u:
    case 0x8006FC90u:
    case 0x800700A8u:
    case 0x80072EC4u:
    case 0x80076BE4u:
    case 0x800B7168u:
    case 0x800BF4A0u:
    case 0x800C0084u:
    case 0x800C68A0u:
    case 0x800ECC28u:
        return 2;
    default:
        return 0;
    }
}
static uint32_t rs6663_descriptor(uint8_t* rdram, uint32_t node, uint32_t* npc, uint32_t* handler) {
    *npc = *handler = 0;
    if (!rs6663_owned(rdram, node)) return 0;
    *handler = rs6657_word(rdram, node);
    *npc = rs6657_word(rdram, node + 4);
    if (!rs6660_ok(*npc)) return 0;
    int kind = rs6663_kind(*handler);
    return kind == 1 ? rs6657_desc(rdram, *npc) : kind == 3 ? rs6657_word(rdram, *npc) : 0;
}
void rs6663_scan(uint8_t* rdram) {
    static int busy;
    static uint32_t seen[2048][10], birth[2048], last_report = 0xFFFFFFFFu;
    if (busy || !rs6657_enabled() || (rs6657_level != 2 && rs6657_level != 3 && rs6657_level != 4 && rs6657_level != 5) || !rs6657_started || rs6657_done) return;
    busy = 1;
    int valid = rs6663_refresh(rdram);
    uint32_t active = 0, stale = 0, unknown = 0, named = 0, typed = 0;
    static unsigned controls[3];
    if (valid) for (unsigned i = 0; i < 2048; i++) {
        uint32_t raw = rs6657_word(rdram, rs6663_table + i * 8);
        stale += rs6663_free[i] && raw != 0;
        uint32_t node = rs6663_free[i] ? 0 : raw, npc = 0, handler = 0;
        uint32_t desc = rs6663_descriptor(rdram, node, &npc, &handler), f[6];
        int owned = node && rs6663_owned(rdram, node), known = owned ? rs6663_kind(handler) : 0;
        rs6660_fields(rdram, known == 1 ? desc : 0, f);
        int selected = known == 1 && rs6660_selected(f);
        if (known == 1 && rs6660_ok(desc) && controls[rs6657_arm] == 0) {
            uint32_t control[6] = {rs6657_level == 3 ? 28u : 40u, 1, 0, 0, 0, 0};
            int accepts = rs6660_selected(control);
            control[2] = rs6657_level == 3 ? 4 : 31; control[3] = 1;
            fprintf(stderr, "[objresp-select-control] epoch=1 vi=%u arm=%u slot=%u node=%08x handler=%08x desc=%08x local_fixture=1 accepts_named=%d rejects_success=%d guest_writes=0\n", rs64_vi_n_g, rs6657_arm, i, node, handler, desc, accepts, !rs6660_selected(control));
            controls[rs6657_arm]++;
        }

        if (selected && !rs6666_on && rs64_vi_n_g - rs6657_start >= 1800) rs6666_on = rs64_vi_n_g;
        active += node != 0; unknown += node && !known; typed += known != 0; named += selected;
        uint32_t values[10] = {node, npc, handler, desc, f[0], f[1], f[2], f[3], f[4], f[5]};
        int changed = memcmp(seen[i], values, sizeof(values)) != 0;
        if (changed) {
            if (seen[i][0] && (seen[i][0] != node || seen[i][1] != npc || seen[i][2] != handler))
                fprintf(stderr, "[objresp-retire] epoch=1 vi=%u arm=%u slot=%u generation=%u birth=%u node=%08x npc=%08x handler=%08x desc=%08x\n", rs64_vi_n_g, rs6657_arm, i, rs6671_generation[i], birth[i], seen[i][0], seen[i][1], seen[i][2], seen[i][3]);
            if (node && (!seen[i][0] || seen[i][0] != node || seen[i][1] != npc || seen[i][2] != handler)) { rs6671_generation[i]++; birth[i] = rs64_vi_n_g; }
            memcpy(seen[i], values, sizeof(values));
            if (node) fprintf(stderr, "[objresp-live] epoch=1 vi=%u arm=%u slot=%u generation=%u birth=%u node=%08x npc=%08x handler=%08x owned=%d typed=%d canonical=%u desc=%08x id=%u delta=%d bool=%u bval=%u id2=%u delta2=%d selected=%d\n", rs64_vi_n_g, rs6657_arm, i, rs6671_generation[i], birth[i], node, npc, handler, owned, known, owned ? rs6663_half(rdram, node + 0x16) : 0xFFFFu, desc, f[0], (int32_t)f[1], f[2], f[3], f[4], (int32_t)f[5], selected);
        }
    }
    uint32_t report = (rs64_vi_n_g - rs6657_start) / 300 + rs6657_arm * 100;
    if (report != last_report) {
        last_report = report;
        fprintf(stderr, "[objresp-census] epoch=1 vi=%u arm=%u valid=%d live=%u named=%u typed=%u unknown=%u stale_free=%u slots=2048\n", rs64_vi_n_g, rs6657_arm, valid, active, named, typed, unknown, stale);
    }
    busy = 0;
}
static void rs6660_census(uint8_t* rdram) {
    if (rs6657_level >= 2) { rs6663_scan(rdram); return; }

    static uint32_t tick = 0xFFFFFFFFu, seen[3][2048][8];
    uint32_t now = (rs64_vi_n_g - rs6657_start) / 300;
    if (now == tick) return;
    tick = now;
    uint32_t tb = rs6657_word(rdram, 0x80130BB0u), live = 0, named = 0;
    if (!rs6660_ok(tb) || tb > 0x807FC000u) return;
    for (unsigned i = 0; i < 2048; i++) {
        uint32_t node = rs6657_word(rdram, tb + i * 8);
        if (!rs6660_ok(node)) continue;
        uint32_t npc = rs6657_word(rdram, node + 4), desc = rs6657_desc(rdram, npc), f[6];
        rs6660_fields(rdram, desc, f); live++; named += rs6660_selected(f);
        uint32_t values[8] = {node, desc, f[0], f[1], f[2], f[3], f[4], f[5]};
        int changed = 0;
        for (unsigned k = 0; k < 8; k++) { if (seen[rs6657_arm][i][k] != values[k]) changed = 1; seen[rs6657_arm][i][k] = values[k]; }
        if (changed) fprintf(stderr, "[objresp-live] epoch=1 vi=%u arm=%u slot=%u node=%08x npc=%08x desc=%08x id=%u delta=%d bool=%u bval=%u id2=%u delta2=%d selected=%d\n", rs64_vi_n_g, rs6657_arm, i, node, npc, desc, f[0], (int32_t)f[1], f[2], f[3], f[4], (int32_t)f[5], rs6660_selected(f));
    }
    fprintf(stderr, "[objresp-census] epoch=1 vi=%u arm=%u live=%u named=%u slots=2048\n", rs64_vi_n_g, rs6657_arm, live, named);
}
static int rs6660_candidate(uint8_t* rdram, uint32_t slot, uint32_t shape, uint32_t proj, float radius, int c1f) {
    if (!rs6657_enabled() || rs6657_level == 0) return c1f;
    if (!rs6657_flight(rdram)) return 0;
    uint32_t tb = rs6657_word(rdram, 0x80130BB0u);
    uint32_t node = rs6660_ok(tb) && slot < 2048 ? rs6657_word(rdram, tb + slot * 8) : 0;
    uint32_t npc = rs6660_ok(node) ? rs6657_word(rdram, node + 4) : 0, desc = rs6657_desc(rdram, npc), f[6], handler = 0;
    int typed = 1;
    if (rs6657_level >= 2) {
        if (!rs6663_refresh(rdram) || slot >= 2048 || rs6663_free[slot]) { node = npc = desc = 0; typed = 0; }
        else { desc = rs6663_descriptor(rdram, node, &npc, &handler); typed = rs6663_owned(rdram, node) ? rs6663_kind(handler) : 0; }
    }
    rs6660_fields(rdram, typed == 1 ? desc : 0, f);
    int selected = typed == 1 && rs6660_selected(f);
    if (rs6657_level == 3) selected = 0;
    const char* dose = getenv("ROGUESQ_OBJECTIVE_RESPONSE_LETHAL");
    if (rs6657_level == 2 && dose && dose[0] == '1')
        selected = selected && handler == 0x800D3894u && rs6668_named_rescue(desc);
    static uint32_t last[3][2048][4];
    uint32_t identity[4] = {shape, node, desc, handler};
    if (slot < 2048 && memcmp(last[rs6657_arm][slot], identity, sizeof(identity))) {
        memcpy(last[rs6657_arm][slot], identity, sizeof(identity));
        fprintf(stderr, "[objresp-candidate] epoch=1 vi=%u arm=%u slot=%u shape=%08x proj=%08x node=%08x npc=%08x handler=%08x typed=%d desc=%08x id=%u delta=%d bool=%u bval=%u id2=%u delta2=%d mark_all=1 c1f=%d radius=%g selected=%d reason=%s\n", rs64_vi_n_g, rs6657_arm, slot, shape, proj, node, npc, handler, typed, desc, f[0], (int32_t)f[1], f[2], f[3], f[4], (int32_t)f[5], c1f, radius, selected, selected ? (radius > 0 ? "eligible" : "radius") : typed == 1 ? "descriptor" : typed ? "ineligible-kind" : "untyped");
    }
    if (rs6657_level == 2) {
        for (unsigned m = 0; m < rs6657_ne; m++)
            if (rs6657_events[m].npc == npc && rs6657_events[m].desc == desc && !rs6668_repeat(rdram, node, npc, desc)) return 0;
    }
    return selected && !rs6660_pending_id;
}
void rs6660_send(uint8_t* rdram, uint32_t proj, uint32_t slot) {
    if (!rs6657_enabled() || !rs6657_started || rs6657_done) return;
    uint32_t tb = rs6657_word(rdram, 0x80130BB0u);
    uint32_t node = rs6660_ok(tb) && slot < 2048 ? rs6657_word(rdram, tb + slot * 8) : 0;
    uint32_t npc = rs6660_ok(node) ? rs6657_word(rdram, node + 4) : 0, desc = rs6657_desc(rdram, npc);
    unsigned m = rs6657_match(npc, desc); static unsigned rows[3];
    if (m < 256 && rs6657_events[m].npc == npc && rs6657_events[m].desc == desc && rs6657_events[m].proj == proj) {
        rs6657_events[m].send_seq = rs6657_events[m].seq;
        rs6657_events[m].send_vi = rs64_vi_n_g;
        rs6657_events[m].send_proj = proj;
    }
    if (rows[rs6657_arm]++ < 512) fprintf(stderr, "[objresp-send] epoch=1 vi=%u arm=%u proj=%08x node=%08x npc=%08x desc=%08x force_seq=%u\n", rs64_vi_n_g, rs6657_arm, proj, node, npc, desc, m < 256 ? rs6657_events[m].seq : 0);
}


static int rs6661_hp(uint8_t* rdram, uint32_t actor) {
    if (!rs6660_ok(actor) || actor > 0x807FFC00u) return -999999;
    uint32_t base = rs6657_word(rdram, actor + 0x190);
    if (MEM_BU(S32((int32_t)actor), 0x1A7)) return (int32_t)base;
    uint32_t detail = rs6657_word(rdram, 0x80137CE4u);
    uint32_t address = base + 4u * detail;
    if (detail > 32 || !rs6660_ok(address)) return -999998;
    return (int32_t)rs6657_word(rdram, address);
}
static struct { uint32_t node, npc, desc, actor; int controlled; } rs6661_target;
static int rs6668_repeat(uint8_t* rdram, uint32_t node, uint32_t npc, uint32_t desc) {
    const char* e = getenv("ROGUESQ_OBJECTIVE_RESPONSE_LETHAL");
    return rs6657_level == 2 && e && e[0] == '1' && !rs6661_dosed &&
        rs6668_named_rescue(desc) && rs6661_target.controlled &&
        node == rs6661_target.node && npc == rs6661_target.npc && desc == rs6661_target.desc &&
        rs6663_owned(rdram, node) && rs6657_word(rdram, node) == 0x800D3894u &&
        rs6657_word(rdram, npc + 0x38) == rs6661_target.actor;
}
void rs6668_counter_return(uint8_t* rdram, recomp_context* ctx) {
    if (!rs6657_enabled() || rs6657_level != 2 || !rs6657_started) return;
    static uint32_t previous = 0xffffffffu;
    uint32_t value = U32(ctx->r2), memory = rs6657_word(rdram, 0x801380FCu);
    if (value != previous) {
        fprintf(stderr, "[objresp-counter-return] vi=%u pc=801020b8 id=40 returned=%u memory=%u dosed=%d observed=%u bool109=%u bool101=%u\n", rs64_vi_n_g, value, memory, rs6661_dosed, rs6660_observed, MEM_BU(S32((int32_t)0x8013890Cu),0), MEM_BU(S32((int32_t)0x80138904u),0));
        previous = value;
    }
    if (rs6661_dosed && rs6660_observed && rs6660_pending_id == 40 && value == rs6660_pending_value && value == memory) {
        fprintf(stderr, "[objresp-done] epoch=1 vi=%u dv=%u reason=counter40-getter-before-failure forces=%u,%u,%u\n", rs64_vi_n_g, rs64_vi_n_g-rs6657_start, rs6657_hits[0],rs6657_hits[1],rs6657_hits[2]);
        fflush(stderr);
        raise(SIGSTOP);
    }
}

static _Thread_local struct { uint32_t node, npc, desc, actor, msg, raw, requested, seq, proj, send_vi; int hp, eligible, lethal, active; } rs6661_hit;
static void rs6664_transport_common(uint8_t* rdram, recomp_context* ctx, int stage, uint32_t npc, uint32_t msg) {
    if (!rs6657_enabled() || rs6657_level == 0 || !rs6657_started || rs6657_done) return;
    if (stage == 0) {
        rs6661_hit.active = 0;
        if (!rs6657_flight(rdram)) return;
        uint32_t actor = U32(ctx->r4), desc = rs6657_desc(rdram, npc), f[6];
        rs6660_fields(rdram, desc, f);
        unsigned m = rs6657_match(npc, desc);
        int exact = m < 256 && rs6657_events[m].npc == npc && rs6657_events[m].desc == desc &&
            rs6657_events[m].send_seq == rs6657_events[m].seq && rs6657_events[m].send_seq &&
            rs64_vi_n_g - rs6657_events[m].send_vi <= 60;
        rs6661_hit.npc = npc; rs6661_hit.actor = actor; rs6661_hit.desc = desc;
        rs6661_hit.msg = msg; rs6661_hit.raw = U32(ctx->r5);
        rs6661_hit.hp = rs6661_hp(rdram, actor); rs6661_hit.lethal = 0;
        rs6661_hit.node = exact ? rs6657_events[m].node : 0;
        rs6661_hit.seq = exact ? rs6657_events[m].seq : 0;
        rs6661_hit.proj = exact ? rs6657_events[m].send_proj : 0;
        rs6661_hit.send_vi = exact ? rs6657_events[m].send_vi : 0;
        rs6661_hit.eligible = exact && rs6657_arm == 1 && rs6660_ok(npc) &&
            actor == rs6657_word(rdram, npc + 0x38) &&
            (rs6657_level == 2 ? rs6660_selected(f) :
                (((f[0] == 13 && f[1] > 0 && f[1] < 3) || (f[4] == 13 && f[5] > 0 && f[5] < 3)) && !(f[2] == 6 && f[3]))) && rs6661_hit.hp > 0 && rs6661_hit.hp < 1000000;
        const char* lethal = getenv("ROGUESQ_OBJECTIVE_RESPONSE_LETHAL");
        if ((rs6657_level == 1 || rs6668_repeat(rdram, rs6661_hit.node, npc, desc)) && lethal && lethal[0] == '1' && rs6661_hit.eligible && !rs6661_dosed &&
            rs6661_target.controlled && rs6661_target.node == rs6661_hit.node &&
            rs6661_target.npc == npc && rs6661_target.desc == desc && rs6661_target.actor == actor) {
            ctx->r5 = S32(rs6661_hit.hp + 1); rs6661_hit.lethal = 1; rs6661_dosed = 1;
        }
        rs6661_hit.requested = U32(ctx->r5); rs6661_hit.active = 1;
        fprintf(stderr, "[objresp-transport-pre] vi=%u arm=%u node=%08x npc=%08x desc=%08x actor=%08x msg=%08x raw=%u requested=%u hp=%d force_seq=%u proj=%08x send_vi=%u eligible=%d lethal=%d id=%u delta=%d bool=%u bval=%u id2=%u delta2=%d\n", rs64_vi_n_g, rs6657_arm, rs6661_hit.node, npc, desc, actor, rs6661_hit.msg, rs6661_hit.raw, rs6661_hit.requested, rs6661_hit.hp, rs6661_hit.seq, rs6661_hit.proj, rs6661_hit.send_vi, rs6661_hit.eligible, rs6661_hit.lethal, f[0], (int32_t)f[1], f[2], f[3], f[4], (int32_t)f[5]);
    } else if (rs6661_hit.active && rs6661_hit.npc == npc) {
        if (stage == 1) {
            int hp = rs6661_hp(rdram, rs6661_hit.actor), ret = (int32_t)ctx->r2;
            if (!rs6661_target.controlled && rs6661_hit.eligible && !rs6661_hit.lethal && hp > 0 &&
                rs6661_hit.raw > 0 && rs6661_hit.hp - hp == (int)rs6661_hit.raw && ret == hp) {
                rs6661_target.node = rs6661_hit.node; rs6661_target.npc = rs6661_hit.npc;
                rs6661_target.desc = rs6661_hit.desc; rs6661_target.actor = rs6661_hit.actor; rs6661_target.controlled = 1;
            }
            fprintf(stderr, "[objresp-transport-return] vi=%u arm=%u node=%08x npc=%08x desc=%08x actor=%08x msg=%08x raw=%u requested=%u hp_old=%d hp_new=%d returned=%d death=%d force_seq=%u proj=%08x lethal=%d controlled=%d\n", rs64_vi_n_g, rs6657_arm, rs6661_hit.node, rs6661_hit.npc, rs6661_hit.desc, rs6661_hit.actor, rs6661_hit.msg, rs6661_hit.raw, rs6661_hit.requested, rs6661_hit.hp, hp, ret, ret <= 0, rs6661_hit.seq, rs6661_hit.proj, rs6661_hit.lethal, rs6661_target.controlled);
        } else if (stage == 2) {
            fprintf(stderr, "[objresp-transport-effect] vi=%u arm=%u node=%08x npc=%08x desc=%08x actor=%08x force_seq=%u lethal=%d bool=%u bval=%u id=%u delta=%d id2=%u delta2=%d\n", rs64_vi_n_g, rs6657_arm, rs6661_hit.node, rs6661_hit.npc, rs6661_hit.desc, rs6661_hit.actor, rs6661_hit.seq, rs6661_hit.lethal, U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), (int32_t)ctx->r7, rs6657_word(rdram, U32(ctx->r29) + 0x10), (int32_t)rs6657_word(rdram, U32(ctx->r29) + 0x14));
        }
    }
}

void rs6661_transport(uint8_t* rdram, recomp_context* ctx, int stage) {
    rs6664_transport_common(rdram, ctx, stage, U32(ctx->r17), U32(ctx->r19));
}
void rs6664_transport(uint8_t* rdram, recomp_context* ctx, int stage, uint32_t npc, uint32_t msg) {
    if (rs6657_enabled() && rs6657_level == 2) rs6664_transport_common(rdram, ctx, stage, npc, msg);
}

static uint32_t rs6666_offsets[6] = {0x1510,0x1628,0x1740,0x1270,0x1350,0x1430};
static int rs6666_index(uint32_t desc) {
    for (int i = 0; i < 6; i++) if (rs6666_dat && desc == rs6666_dat + rs6666_offsets[i]) return i;
    return -1;
}
static float rs6666_float(uint8_t* rdram, uint32_t a) {
    uint32_t w = rs6657_word(rdram, a); float f; memcpy(&f, &w, 4); return f;
}
void rs6666_dat_loaded(uint8_t* rdram, uint32_t base) {
    if (!rs6657_enabled() || (rs6657_level != 2 && rs6657_level != 3 && rs6657_level != 4 && rs6657_level != 5) || MEM_BU(S32((int32_t)0x80130B40u),0) != rs6657_level || !rs6660_ok(base)) return;
    if (rs6657_level == 5) { rs6666_dat=base; fprintf(stderr,"[objresp-definition] vi=%u index=0 base=%08x offset=1afc desc=%08x name=x_wing_wedge subtype=%u hp=%u id=%u delta=%u\n",rs64_vi_n_g,base,base+0x1afc,rs6663_half(rdram,base+0x1afc),rs6657_word(rdram,base+0x1b68),rs6657_word(rdram,base+0x1b6c),rs6657_word(rdram,base+0x1b70)); return; }
    if (rs6657_level == 4) { rs6666_dat=base; fprintf(stderr,"[objresp-definition] vi=%u index=0 base=%08x offset=6a7c desc=%08x name=x_wing_hobbie subtype=%u hp=%u id=%u delta=%u\n",rs64_vi_n_g,base,base+0x6a7c,rs6663_half(rdram,base+0x6a7c),rs6657_word(rdram,base+0x6ae8),rs6657_word(rdram,base+0x6aec),rs6657_word(rdram,base+0x6af0)); return; }
    if (rs6657_level == 3) { rs6666_dat = base; fprintf(stderr,"[objresp-definition] vi=%u index=0 base=%08x offset=48c desc=%08x name=City_1 subtype=%u hp=%u id=%u delta=%u\n",rs64_vi_n_g,base,base+0x48c,MEM_HU(S32((int32_t)(base+0x48c)),0),rs6657_word(rdram,base+0x48c+0x6c),rs6657_word(rdram,base+0x48c+0x70),rs6657_word(rdram,base+0x48c+0x74)); return; }
    rs6666_dat = base;
    for (unsigned i = 0; i < 6; i++) {
        uint32_t d = base + rs6666_offsets[i];
        fprintf(stderr,"[objresp-definition] vi=%u index=%u base=%08x offset=%x desc=%08x subtype=%u hp=%u activation=%u id=%u delta=%u\n",rs64_vi_n_g,i,base,rs6666_offsets[i],d,MEM_HU(S32((int32_t)d),0),rs6657_word(rdram,d+0x6c),rs6657_word(rdram,d+0x60),rs6657_word(rdram,d+0x70),rs6657_word(rdram,d+0x74));
    }
}
static void rs6666_sample(uint8_t* rdram, recomp_context* ctx, const char* stage) {
    if (!rs6657_enabled() || rs6657_level != 2 || !rs6657_started || rs6657_done) return;
    static uint32_t last[2] = {0xffffffffu,0xffffffffu}, predicate[2];
    unsigned k = stage[0] == 'r';
    uint32_t ids[10] = {1,2,3,7,8,9,21,22,23,59}, b[10], bits = 0;
    for (unsigned i=0;i<10;i++) { b[i]=MEM_BU(S32((int32_t)(0x8013889fu+ids[i])),0); bits |= !!b[i] << i; }
    float t = rs6666_float(rdram,0x8010c9fcu);
    bits |= (t >= 100.0f) << 10;
    uint32_t tick=(rs64_vi_n_g-rs6657_start)/300;
    if(last[k]==tick && predicate[k]==bits) return;
    last[k]=tick; predicate[k]=bits;
    fprintf(stderr,"[objresp-activation] vi=%u dv=%u arm=%u stage=%s timer1=%.9g returned=%.9g gate59=%u threshold=%d b1=%u b2=%u b3=%u b7=%u b8=%u b9=%u b21=%u b22=%u b23=%u\n",rs64_vi_n_g,rs64_vi_n_g-rs6657_start,rs6657_arm,stage,t,ctx->f0.fl,b[9],t>=100.0f,b[0],b[1],b[2],b[3],b[4],b[5],b[6],b[7],b[8]);
}
void rs6666_gate_sample(uint8_t* rdram, recomp_context* ctx, int returned) { rs6666_sample(rdram,ctx,returned?"return":"decision"); }
void rs6666_scalar(uint8_t* rdram, uint32_t pc, uint32_t addr, uint32_t requested) {
    if (!rs6657_enabled() || rs6657_level != 2 || rs6657_done || MEM_BU(S32((int32_t)0x80130b40u),0)!=2) return;
    int timer = addr == 0x8010c9fcu;
    if (!timer && (addr < 0x801388a0u || addr >= 0x80138920u)) return;
    static uint32_t tick = 0xffffffffu, rows[2];
    if (timer && pc == 0x800fa924u) {
        uint32_t now = rs6657_started ? (rs64_vi_n_g-rs6657_start)/300 : 0;
        if(tick == now) return;
        tick=now;
    } else if (++rows[!!rs6657_started] > 512) return;
    fprintf(stderr,"[objresp-scalar] vi=%u epoch=%d pc=%08x addr=%08x requested=%08x actual=%08x timer1=%.9g\n",rs64_vi_n_g,rs6657_started,pc,addr,requested,timer?rs6657_word(rdram,addr):MEM_BU(S32((int32_t)addr),0),rs6666_float(rdram,0x8010c9fcu));
}
void rs6666_spawn(uint8_t* rdram, uint32_t pc, uint32_t desc, uint32_t result) {
    if (!rs6657_enabled() || rs6657_level != 2 || rs6657_done) return;
    int i=rs6666_index(desc);
    if(i<0) return;
    static uint32_t seen[2][6][3], value[2][6][3];
    unsigned epoch=!!rs6657_started, col=pc==0x80047554u?0:pc==0x80047570u?1:2;
    uint32_t tick=epoch?(rs64_vi_n_g-rs6657_start)/300+1:1;
    if(seen[epoch][i][col]==tick && value[epoch][i][col]==result) return;
    seen[epoch][i][col]=tick; value[epoch][i][col]=result;
    uint32_t id=rs6657_word(rdram,desc+0x60);
    fprintf(stderr,"[objresp-spawn] vi=%u epoch=%u pc=%08x index=%d base=%08x offset=%x desc=%08x result=%08x activation=%u actual=%u\n",rs64_vi_n_g,epoch,pc,i,rs6666_dat,rs6666_offsets[i],desc,result,id,id&&id<=128?MEM_BU(S32((int32_t)(0x8013889fu+id)),0):0);
}

void rs6670_building(uint8_t* rdram, recomp_context* ctx, int stage, uint32_t node, uint32_t message, uint32_t action) {
    if (!rs6657_enabled() || rs6657_level != 3 || !rs6657_started || rs6657_done || action != 5 || (!rs6663_owned(rdram,node) && !(stage==3 && rs6670_api_active && node==rs6671_control.node))) return;
    uint32_t npc=rs6657_word(rdram,node+4), desc=rs6657_desc(rdram,npc), detail=rs6657_word(rdram,0x80137ce4u);
    if (!rs6660_ok(desc) || detail>32 || !rs6660_ok(message)) return;
    if (stage==3 && rs6670_api_active && node==rs6671_control.node) { npc=rs6671_control.npc; desc=rs6671_control.desc; }
    if (stage==2 && rs6670_api_active)
        fprintf(stderr,"[objresp-building-effect] vi=%u api_seq=%u pc=8006d6f0 node=%08x npc=%08x desc=%08x bool=%u bval=%u id=%u delta=%u id2=%u delta2=%u\n",rs64_vi_n_g,rs6670_api_active,node,npc,desc,U32(ctx->r4),U32(ctx->r5),U32(ctx->r6),U32(ctx->r7),rs6657_word(rdram,U32(ctx->r29)+16),rs6657_word(rdram,U32(ctx->r29)+20));
    unsigned m=rs6657_match(npc,desc);
    static unsigned rows[3][4];
    if (m==256 && rows[rs6657_arm][stage]++>=32) return;
    uint32_t address=desc+0x6c+detail*4;
    int hp=(int32_t)rs6657_word(rdram,address);
    uint32_t request=rs6663_half(rdram,message+6);
    if (rs6670_api_active && node==rs6671_control.node && npc==rs6671_control.npc && desc==rs6671_control.desc) {
        if (stage==1 && (int32_t)rs6657_word(rdram,U32(ctx->r2))==rs6671_control.hp && (int32_t)ctx->r3==rs6671_control.hp-(int)request && U32(ctx->r2)==address) rs6671_control.store=rs6670_api_active;
        if (stage==2) rs6671_control.effect=rs6670_api_active;
    }
    fprintf(stderr,"[objresp-building] epoch=1 vi=%u arm=%u stage=%d api_seq=%u pc=%08x node=%08x npc=%08x desc=%08x name=%s slot=%u handler=%08x message=%08x source=%u subtype=%u detail=%u health_addr=%08x hp=%d request=%u store_old=%d store_new=%d force_seq=%u proj=%08x c28=%u\n",rs64_vi_n_g,rs6657_arm,stage,rs6670_api_active,stage==1?0x8006cfe8u:stage==2?0x8006d6f0u:stage==3?0x8006d8c0u:0x8006cbb0u,node,npc,desc,rs6666_dat&&desc==rs6666_dat+0x48c?"City_1":"other",rs6663_half(rdram,node+0x16),rs6657_word(rdram,node),message,rs6663_half(rdram,message+2),rs6663_half(rdram,desc),detail,address,hp,request,stage==1?(int32_t)rs6657_word(rdram,U32(ctx->r2)):hp,stage==1?(int32_t)ctx->r3:hp,m<256?rs6657_events[m].seq:0,m<256?rs6657_events[m].proj:0,rs6657_word(rdram,0x801380ccu));
}
void rs6670_reader(uint8_t* rdram, recomp_context* ctx, uint32_t pc) {
    if (!rs6657_enabled() || rs6657_level!=3 || !rs6657_started || rs6657_done) return;
    static uint32_t values[3][3], initialized[3];
    uint32_t c27=rs6657_word(rdram,0x801380c8u),c28=rs6657_word(rdram,0x801380ccu);
    uint32_t value=pc==0x80103560u?U32(ctx->r4):U32(ctx->r2);
    unsigned k=pc==0x80103540u?0:pc==0x80103550u?1:2;
    if (!(initialized[rs6657_arm]&(1u<<k)) || values[rs6657_arm][k]!=value) {
        values[rs6657_arm][k]=value; initialized[rs6657_arm]|=1u<<k;
        fprintf(stderr,"[objresp-building-reader] epoch=1 vi=%u arm=%u pc=%08x value=%u c27=%u c28=%u expected=%u\n",rs64_vi_n_g,rs6657_arm,pc,value,c27,c28,k==0?c27:k==1?c28:100-c27-c28);
    }
}

void rs6670_tick(uint8_t* rdram, recomp_context* ctx) {
    if (!rs6657_enabled() || rs6657_level!=3 || !rs6657_started || rs6657_done) return;
    uint32_t ids[3]={3,27,28}, got[3];
    static uint32_t previous[3][3], initialized[3];
    for (unsigned i=0;i<3;i++) {
        recomp_context probe=*ctx; probe.r4=ids[i];
        getObjectiveCount(rdram,&probe); got[i]=U32(probe.r2);
        if (!initialized[rs6657_arm] || got[i]!=previous[rs6657_arm][i])
            fprintf(stderr,"[objresp-probe-getter] epoch=1 vi=%u arm=%u probe_call=1 id=%u returned=%u memory=%u\n",rs64_vi_n_g,rs6657_arm,ids[i],got[i],rs6657_word(rdram,0x80138060u+(ids[i]-1)*4));
        previous[rs6657_arm][i]=got[i];
    }
    initialized[rs6657_arm]=1;
    if (rs6661_dosed && rs6660_observed && got[2]==rs6660_pending_value && got[2]==rs6657_word(rdram,0x801380ccu)) {
        fprintf(stderr,"[objresp-done] epoch=1 vi=%u reason=level3-named-response c28=%u getter=%u bool4=%u bool18=%u bool21=%u c22=%u\n",rs64_vi_n_g,got[2],got[2],MEM_BU(S32((int32_t)0x801388a3u),0),MEM_BU(S32((int32_t)0x801388b1u),0),MEM_BU(S32((int32_t)0x801388b4u),0),rs6657_word(rdram,0x801380b4u));
        rs6657_done=1; fflush(stderr); raise(SIGSTOP); return;
    }
    const char* lethal=getenv("ROGUESQ_OBJECTIVE_RESPONSE_LETHAL");
    int dose=rs6670_forced && lethal && lethal[0]=='1' && rs6671_control.ordinary && !rs6661_dosed;
    if (rs6657_arm!=1 || (rs6670_forced && !dose) || !rs6666_dat) return;
    uint32_t desc=rs6666_dat+0x48c, name=rs6657_word(rdram,desc+0xc), detail=rs6657_word(rdram,0x80137ce4u);
    if (!rs6660_ok(desc) || name<0x80000400u || name>0x807fff00u || detail>32 || rs6663_half(rdram,desc)!=20) return;
    recomp_context probe=*ctx; probe.r4=S32(name);
    getLevelDatItemByName(rdram,&probe);
    uint32_t slot=rs6663_half(rdram,desc+6),node=0,npc=0,handler=0,owned=0;
    int valid=rs6663_refresh(rdram);
    if (valid && slot<2048 && !rs6663_free[slot]) {
        node=rs6657_word(rdram,rs6663_table+slot*8);
        owned=rs6663_descriptor(rdram,node,&npc,&handler)==desc;
    }
    static uint32_t report[3][5];
    uint32_t state[5]={name,U32(probe.r2),slot,handler,owned};
    if (memcmp(report[rs6657_arm],state,sizeof(state))) {
        memcpy(report[rs6657_arm],state,sizeof(state));
        fprintf(stderr,"[objresp-api-eligibility] vi=%u arm=%u desc=%08x name_ptr=%08x name_bytes=%02x%02x%02x%02x%02x%02x%02x lookup=%08x slot=%u handler=%08x owned=%u valid=%d\n",rs64_vi_n_g,rs6657_arm,desc,name,MEM_BU(S32((int32_t)name),0),MEM_BU(S32((int32_t)name),1),MEM_BU(S32((int32_t)name),2),MEM_BU(S32((int32_t)name),3),MEM_BU(S32((int32_t)name),4),MEM_BU(S32((int32_t)name),5),MEM_BU(S32((int32_t)name),6),U32(probe.r2),slot,handler,owned,valid);
    }
    if (U32(probe.r2)!=desc || (int32_t)rs6657_word(rdram,desc+0x6c+detail*4)<=10) return;
    if (!owned || handler!=0x8006cbb0u || slot>=2048) return;
    if (dose && (node!=rs6671_control.node || npc!=rs6671_control.npc || desc!=rs6671_control.desc || slot!=rs6671_control.slot || rs6671_generation[slot]!=rs6671_control.generation || detail!=rs6671_control.detail || name!=rs6671_control.name)) {
        fprintf(stderr,"[objresp-dose-inhibit] vi=%u reason=ownership-changed\n",rs64_vi_n_g); rs6671_control.ordinary=0; return;
    }
    int hp=(int32_t)rs6657_word(rdram,desc+0x6c+detail*4);
    if (dose && (hp!=rs6671_control.hp || hp<=0 || hp>=65535 || got[2])) { rs6671_control.ordinary=0; return; }
    uint32_t request=dose?(uint32_t)hp+1:10;
    rs6670_forced=1; rs6670_api_active=dose?2:1;
    rs6671_control.node=node; rs6671_control.npc=npc; rs6671_control.desc=desc; rs6671_control.slot=slot; rs6671_control.generation=rs6671_generation[slot]; rs6671_control.detail=detail; rs6671_control.name=name; rs6671_control.hp=hp;
    if (dose) rs6661_dosed=1;
    fprintf(stderr,"[objresp-api] epoch=1 vi=%u arm=%u stage=pre api_seq=%u route=named-script name=City_1 name_ptr=%08x base=%08x desc=%08x slot=%u node=%08x npc=%08x handler=%08x detail=%u hp=%d request=%u c28=%u generation=%u\n",rs64_vi_n_g,rs6657_arm,rs6670_api_active,name,rs6666_dat,desc,slot,node,npc,handler,detail,hp,request,got[2],rs6671_generation[slot]);
    probe=*ctx; probe.r4=S32(name); probe.r5=request;
    dealDamagetoDatItem(rdram,&probe);
    fprintf(stderr,"[objresp-api] epoch=1 vi=%u arm=%u stage=post api_seq=%u desc=%08x node=%08x npc=%08x hp=%d returned=%d c28=%u\n",rs64_vi_n_g,rs6657_arm,rs6670_api_active,desc,node,npc,(int32_t)rs6657_word(rdram,desc+0x6c+detail*4),(int32_t)probe.r2,rs6657_word(rdram,0x801380ccu));
    if (!dose && rs6671_control.store==1 && !rs6671_control.effect && (int32_t)probe.r2==hp-10 && (int32_t)rs6657_word(rdram,desc+0x6c+detail*4)==hp-10 && hp>10) { rs6671_control.ordinary=1; rs6671_control.hp=hp-10; }
    rs6670_api_active=0;
}

void rs6670_fallback(uint8_t* rdram,recomp_context* ctx,int stage) {
    if (!rs6657_enabled() || rs6657_level!=3 || !rs6670_api_active) return;
    uint32_t desc=U32(ctx->r16),detail=rs6657_word(rdram,0x80137ce4u);
    fprintf(stderr,"[objresp-fallback] vi=%u arm=%u api_seq=%u stage=%d desc=%08x detail=%u slot=%u hp=%d result=%d request=%u c28=%u\n",rs64_vi_n_g,rs6657_arm,rs6670_api_active,stage,desc,detail,rs6663_half(rdram,desc+6),(int32_t)rs6657_word(rdram,desc+0x6c+detail*4),(int32_t)ctx->r17,U32(ctx->r18),rs6657_word(rdram,0x801380ccu));
}


static uint32_t rs6673_actor, rs6673_address, rs6673_mode, rs6673_message, rs6673_request;
static _Thread_local int rs6673_active;
static uint32_t rs6674_stores, rs6674_entries, rs6674_returns, rs6674_effects;
static uint32_t rs6673_health_address(uint8_t* rdram, uint32_t actor, uint32_t detail) {
    if (!rs6660_ok(actor) || actor>0x807ffd00u || detail>32) return 0;
    uint32_t address=MEM_BU(S32((int32_t)(actor+0x1a7)),0) ? actor+0x190 : rs6657_word(rdram,actor+0x190)+detail*4;
    return rs6660_ok(address) ? address : 0;
}
static void rs6673_log(uint8_t* rdram,recomp_context* ctx,const char* stage,uint32_t pc,uint32_t address,int next) {
    fprintf(stderr,"[objresp-wingman] epoch=1 vi=%u arm=%u stage=%s api_seq=%u pc=%08x node=%08x npc=%08x desc=%08x slot=%u generation=%u handler=%08x actor=%08x detail=%u mode=%u health_addr=%08x message=%08x request=%u hp=%d next=%d returned=%d c40=%u\n",rs64_vi_n_g,rs6657_arm,stage,rs6673_active,pc,rs6671_control.node,rs6671_control.npc,rs6671_control.desc,rs6671_control.slot,rs6671_control.generation,rs6657_word(rdram,rs6671_control.node),rs6673_actor,rs6671_control.detail,rs6673_mode,address,rs6673_message,rs6673_request,(int32_t)rs6657_word(rdram,address),next,(int32_t)ctx->r2,rs6657_word(rdram,0x801380fcu));
}
void rs6673_wingman(uint8_t* rdram,recomp_context* ctx,int stage,uint32_t node,uint32_t message,uint32_t action) {
    if (!rs6673_active || action!=5 || node!=rs6671_control.node) return;
    rs6673_message=message;
    if (stage==0) rs6674_entries++;
    if (stage==2 && (int32_t)ctx->r2==rs6671_control.hp-(int)rs6673_request && (int32_t)rs6657_word(rdram,rs6673_address)==(int32_t)ctx->r2) rs6674_returns++;
    if (stage==3) {
        rs6674_effects++;
        fprintf(stderr,"[objresp-wingman-effect] api_seq=%u pc=800d9d28 node=%08x npc=%08x desc=%08x id=%u delta=%d bool=%u bval=%u id2=%u delta2=%d\n",rs6673_active,node,U32(ctx->r16),rs6657_word(rdram,U32(ctx->r16)+0x34),U32(ctx->r6),(int32_t)ctx->r7,U32(ctx->r4),U32(ctx->r5),rs6657_word(rdram,U32(ctx->r29)+16),(int32_t)rs6657_word(rdram,U32(ctx->r29)+20));
    }
    fprintf(stderr,"[objresp-wingman-observed] stage=%d node=%08x npc=%08x desc=%08x actor=%08x message=%08x action=%u\n",stage,node,rs6657_word(rdram,node+4),rs6657_desc(rdram,rs6657_word(rdram,node+4)),stage==1?U32(ctx->r4):rs6657_word(rdram,rs6657_word(rdram,node+4)+0x38),message,action);
    rs6673_request=rs6663_half(rdram,message+6);
    rs6673_log(rdram,ctx,stage==0?"entry":stage==1?"damage-pre":stage==2?"damage-post":"effect",stage==0?0x800d93c0u:stage==1?0x800d9c54u:stage==2?0x800d9c5cu:0x800d9d28u,rs6673_address,0);
}
void rs6673_store(uint8_t* rdram,recomp_context* ctx,uint32_t pc,uint32_t address) {
    if (!rs6673_active) return;
    fprintf(stderr,"[objresp-wingman-store-observed] pc=%08x actor=%08x address=%08x mode=%u detail=%u\n",pc,U32(ctx->r4),address,MEM_BU(ctx->r4,0x1a7),rs6657_word(rdram,0x80137ce4u));
    if (U32(ctx->r4)==rs6673_actor && address==rs6673_address && (int32_t)rs6657_word(rdram,address)==rs6671_control.hp && (int32_t)ctx->r2==rs6671_control.hp-(int)rs6673_request) rs6674_stores++;
    rs6673_log(rdram,ctx,"store",pc,address,(int32_t)ctx->r2);
}
void rs6673_tick(uint8_t* rdram,recomp_context* ctx) {
    if (!rs6657_enabled() || (rs6657_level!=4 && rs6657_level!=5) || !rs6657_started || rs6657_done) return;
    static uint32_t previous[3][128], init[3], after_request;
    const char* lethal=getenv("ROGUESQ_OBJECTIVE_RESPONSE_LETHAL");
    int dose=rs6657_level==4 && rs6670_forced && lethal && lethal[0]=='1' && rs6671_control.ordinary && !rs6661_dosed;
    for (unsigned i=0;i<128;i++) {
        recomp_context probe=*ctx; probe.r4=i+1; getObjectiveCount(rdram,&probe);
        uint32_t value=U32(probe.r2);
        if (!init[rs6657_arm] || previous[rs6657_arm][i]!=value || (rs6670_forced && !after_request && i==39))
            fprintf(stderr,"[objresp-probe-getter] epoch=1 vi=%u arm=%u probe_call=1 id=%u returned=%u memory=%u\n",rs64_vi_n_g,rs6657_arm,i+1,value,rs6657_word(rdram,0x80138060u+i*4));
        previous[rs6657_arm][i]=value;
    }
    init[rs6657_arm]=1; if (rs6670_forced) after_request=1;
    if (rs6661_dosed && rs6660_observed && rs6660_pending_id==40 && previous[rs6657_arm][39]==1 && rs6657_word(rdram,0x801380fcu)==1) {
        fprintf(stderr,"[objresp-done] epoch=1 vi=%u reason=level4-named-response c40=1 getter=1 c15=%u c16=%u c28=%u bool26=%u\n",rs64_vi_n_g,rs6657_word(rdram,0x80138098u),rs6657_word(rdram,0x8013809cu),rs6657_word(rdram,0x801380ccu),MEM_BU(S32((int32_t)0x801388b9u),0));
        fflush(stderr); rs6657_done=1; raise(SIGSTOP); return;
    }
    if (!rs6666_dat || (rs6670_forced && !dose)) return;
    uint32_t desc=rs6666_dat+(rs6657_level==5?0x1afc:0x6a7c),name=rs6657_word(rdram,desc+12),detail=rs6657_word(rdram,0x80137ce4u);
    if (!rs6660_ok(desc) || name<0x80000400u || name>0x807fff00u || detail>32) return;
    recomp_context probe=*ctx; probe.r4=S32(name); getLevelDatItemByName(rdram,&probe);
    uint32_t slot=rs6663_half(rdram,desc+6),node=0,npc=0,handler=0,owned=0,actor=0,address=0;
    int valid=rs6663_refresh(rdram);
    if (valid && slot<2048 && !rs6663_free[slot]) {
        node=rs6657_word(rdram,rs6663_table+slot*8);
        owned=rs6663_descriptor(rdram,node,&npc,&handler)==desc && rs6663_half(rdram,node+0x16)==slot;
        if (owned) { actor=rs6657_word(rdram,npc+0x38); address=rs6673_health_address(rdram,actor,detail); }
    }
    static uint32_t report[3][8];
    uint32_t state[8]={U32(probe.r2),slot,node,npc,handler,owned,actor,address};
    if (memcmp(report[rs6657_arm],state,sizeof(state))) {
        memcpy(report[rs6657_arm],state,sizeof(state));
        fprintf(stderr,"[objresp-wingman-eligibility] epoch=1 vi=%u arm=%u desc=%08x lookup=%08x slot=%u node=%08x npc=%08x handler=%08x owned=%u valid=%d actor=%08x health_addr=%08x generation=%u reason=%s\n",rs64_vi_n_g,rs6657_arm,desc,U32(probe.r2),slot,node,npc,handler,owned,valid,actor,address,slot<2048?rs6671_generation[slot]:0,!valid?"free-list-invalid":!owned?"not-owned":handler!=0x800d93c0u?"handler":!address?"health":U32(probe.r2)!=desc?"lookup":"eligible");
    }
    if (!owned || handler!=0x800d93c0u || !address || U32(probe.r2)!=desc || rs6663_half(rdram,desc)!=0x27) return;
    static unsigned mark[3];
    if (!mark[rs6657_arm]++) fprintf(stderr,"[objresp-wingman-control] epoch=1 vi=%u arm=%u mark_all=1 node=%08x actor=%08x mode=%u detail=%u health_addr=%08x hp=%d\n",rs64_vi_n_g,rs6657_arm,node,actor,MEM_BU(S32((int32_t)(actor+0x1a7)),0),detail,address,(int32_t)rs6657_word(rdram,address));
    int hp=(int32_t)rs6657_word(rdram,address);
    if (rs6657_arm!=1 || hp<=10) return;
    if (dose && (node!=rs6671_control.node || npc!=rs6671_control.npc || desc!=rs6671_control.desc || slot!=rs6671_control.slot || rs6671_generation[slot]!=rs6671_control.generation || detail!=rs6671_control.detail || name!=rs6671_control.name || actor!=rs6673_actor || address!=rs6673_address || MEM_BU(S32((int32_t)(actor+0x1a7)),0)!=rs6673_mode || hp!=rs6671_control.hp || hp>=65535 || rs6657_word(rdram,0x801380fcu))) {
        fprintf(stderr,"[objresp-dose-inhibit] vi=%u reason=level4-identity-health-counter\n",rs64_vi_n_g); rs6671_control.ordinary=0; return;
    }
    if (rs6657_level==4 && (rs6657_word(rdram,0x80138098u) || rs6657_word(rdram,0x8013809cu) || rs6657_word(rdram,0x801380ccu) || MEM_BU(S32((int32_t)0x801388b9u),0))) return;
    if (rs6657_word(rdram,desc+0x70)!=40 || rs6657_word(rdram,desc+0x74)!=1 || rs6657_word(rdram,desc+0x78) || rs6657_word(rdram,desc+0x7c) || rs6657_word(rdram,desc+0x80) || rs6657_word(rdram,desc+0x84)!=1) return;
    uint32_t request=dose?(uint32_t)hp+1:10;
    rs6674_stores=rs6674_entries=rs6674_returns=rs6674_effects=0;
    if (dose) rs6661_dosed=1;
    rs6670_forced=1; rs6673_active=dose?2:1; rs6673_actor=actor; rs6673_address=address; rs6673_mode=MEM_BU(S32((int32_t)(actor+0x1a7)),0); rs6673_request=request; rs6673_message=0;
    rs6671_control.node=node; rs6671_control.npc=npc; rs6671_control.desc=desc; rs6671_control.slot=slot; rs6671_control.generation=rs6671_generation[slot]; rs6671_control.detail=detail; rs6671_control.name=name; rs6671_control.hp=hp;
    rs6673_log(rdram,ctx,"api-pre",0x800c7390u,address,0);
    probe=*ctx; probe.r4=S32(name); probe.r5=request; dealDamagetoDatItem(rdram,&probe);
    rs6673_log(rdram,&probe,"api-post",0x800c7390u,address,0);
    if (!dose && rs6674_entries==1 && rs6674_stores==1 && rs6674_returns==1 && !rs6674_effects && (int32_t)probe.r2==hp-10 && (int32_t)rs6657_word(rdram,address)==hp-10) { rs6671_control.ordinary=1; rs6671_control.hp=hp-10; }
    rs6673_active=0;
}

'''
WRITERS = {
    'funcs_15.c': (0x8006594C, 0x80065974, 0x80065A34),
    'funcs_35.c': (0x800C75E8, 0x800C7618),
    'funcs_41.c': (0x800F3D80, 0x800F4378),
}

def _apply(text, name):
    if name not in FILES:
        return text, 0
    if name == 'funcs_38.c':
        marker = '/* PATCH: s6661 transport dose */'
        if marker in text:
            return text, 0
        start = text.index('RECOMP_FUNC void npcGroundTransportUpdate(')
        stop = text.index('\nRECOMP_FUNC ', start + 1)
        body = text[start:stop]
        a = '    dealDamageToNpc(rdram, ctx);'
        assert body.count(a) == 1
        body = body.replace(a, '    rs6661_transport(rdram, ctx, 0);\n' + a + '\n    rs6661_transport(rdram, ctx, 1);')
        a = '    datItemSetObjectiveBooleanCount(rdram, ctx);'
        assert body.count(a) == 1
        body = body.replace(a, '    rs6661_transport(rdram, ctx, 2);\n    { uint32_t saved = rs6657_victim; rs6657_victim = U32(ctx->r17);\n' + a + '\n    rs6657_victim = saved; }')
        text = text[:start] + body + text[stop:]
        text = text.replace('#include "funcs.h"', '#include "funcs.h"\n' + marker + '\nextern void rs6661_transport(uint8_t*, recomp_context*, int);\nextern _Thread_local uint32_t rs6657_victim;', 1)
        return text, 1
    if name == 'funcs_8.c':
        marker = '/* PATCH: s6663 slot lifetime */'
        if marker in text: return text, 0
        text = text.replace('#include "funcs.h"', '#include "funcs.h"\n' + marker + '\nextern void rs6663_scan(uint8_t*);', 1)
        for fn in ('slotDispatcherIter', 'unregisterAndFreeNpcSlot'):
            start = text.index('RECOMP_FUNC void ' + fn + '(')
            stop = text.index('RECOMP_FUNC void ', start + 1)
            body = text[start:stop]
            if fn == 'slotDispatcherIter':
                body = body.replace('    uint64_t hi', '    rs6663_scan(rdram);\n    uint64_t hi', 1)
                anchor = '    LOOKUP_FUNC(ctx->r2)(rdram, ctx);'
                assert body.count(anchor) == 1
                body = body.replace(anchor, anchor + '\n    rs6663_scan(rdram);')
            else:
                body = body.replace('    return;', '    rs6663_scan(rdram);\n    return;')
            text = text[:start] + body + text[stop:]
        return text, 1
    if name == 'funcs_13.c':
        hook = '    rs6660_send(rdram, (uint32_t)ctx->r17, (uint32_t)(ctx->r4 & 0xFFFF));'
        if hook in text:
            return text, 0
        a = '    rs5838_send(rdram, (uint32_t)ctx->r17, (uint32_t)(ctx->r4 & 0xFFFF));'
        assert text.count(a) == 1
        return text.replace('#include "funcs.h"', '#include "funcs.h"\nextern void rs6660_send(uint8_t*, uint32_t, uint32_t);', 1).replace(a, hook + '\n' + a), 1
    callback_changed = 0
    if name == 'funcs_43.c' and 'rs6668_counter_return(rdram, ctx);' not in text:
        anchor = '    getObjectiveCount(rdram, ctx);\n        goto after_26;'
        start = text.index('RECOMP_FUNC void lv2_checkComplexObjectives(')
        at = text.index(anchor, start)
        text = text[:at] + text[at:].replace(anchor, '    getObjectiveCount(rdram, ctx);\n    rs6668_counter_return(rdram, ctx);\n        goto after_26;', 1)
        text = text.replace('#include "funcs.h"', '#include "funcs.h"\nextern void rs6668_counter_return(uint8_t*, recomp_context*);', 1)
        callback_changed = 1
    if name == 'funcs_43.c' and 'rs6657_callback_level(rdram, 2);' not in text:
        a = 'RECOMP_FUNC void lv2_checkComplexObjectives(uint8_t* rdram, recomp_context* ctx) {'
        assert text.count(a) == 1
        text = text.replace(a, a + '\n    rs6657_callback_level(rdram, 2);')
        callback_changed = 1
    candidate_changed = 0
    if name == 'funcs_16.c':
        a = '    if (rs5837_en && rs6657_gate(rdram) && w == 0 && cc[3] > 0.0f && c1f &&'
        b = '    int rs6660_eligible = rs6660_candidate(rdram, rs5841_cand & 0xFFFF, rs5839_obj, rs5856_proj, cc[3], c1f);\n    if (rs5837_en && rs6657_gate(rdram) && w == 0 && cc[3] > 0.0f && rs6660_eligible &&'
        if a in text:
            text = text.replace(a, b, 1); candidate_changed = 1
    if TAG in text:
        if name == 'funcs_16.c':
            original = text
            text = text.replace('#include <signal.h>\n', '')
            start = text.index('extern uint32_t rs64_vi_committed_width(void), rs64_vi_committed_origin(void);', text.index('/* ' + TAG))
            stop = text.index('static void rs5835_probe(', start)
            updated = text[:start] + HELPERS.lstrip('\n') + '\n' + text[stop:]
            return updated, int(updated != original or candidate_changed)
        if name == 'funcs_43.c' and 'rs6657_callback_level(rdram, 1);' not in text:
            text = text.replace('extern void rs6657_callback(uint8_t*);', 'extern void rs6657_callback(uint8_t*);\nextern void rs6657_callback_level(uint8_t*, int);', 1)
            a = 'RECOMP_FUNC void lv1_checkComplexObjectives(uint8_t* rdram, recomp_context* ctx) {'
            assert text.count(a) == 1
            return text.replace(a, a + '\n    rs6657_callback_level(rdram, 1);'), 1
        return text, callback_changed
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
        a = 'RECOMP_FUNC void lv1_checkComplexObjectives(uint8_t* rdram, recomp_context* ctx) {'
        assert text.count(a) == 1
        text = text.replace(a, a + '\n    rs6657_callback_level(rdram, 1);')
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
    if name == 'funcs_16.c':
        text = text.replace('    if (rs5837_en && rs6657_gate(rdram) && w == 0 && cc[3] > 0.0f && c1f &&', '    int rs6660_eligible = rs6660_candidate(rdram, rs5841_cand & 0xFFFF, rs5839_obj, rs5856_proj, cc[3], c1f);\n    if (rs5837_en && rs6657_gate(rdram) && w == 0 && cc[3] > 0.0f && rs6660_eligible &&')
    return text, 1

def activation_hooks(text, name):
    if name not in ('funcs_10.c','funcs_35.c','funcs_42.c','funcs_43.c') or '/* PATCH: s6666 activation join */' in text:
        return text, 0
    declaration = ('\n/* PATCH: s6666 activation join */\n'
        'extern void rs6666_dat_loaded(uint8_t*, uint32_t);\n'
        'extern void rs6666_gate_sample(uint8_t*, recomp_context*, int);\n'
        'extern void rs6666_scalar(uint8_t*, uint32_t, uint32_t, uint32_t);\n'
        'extern void rs6666_spawn(uint8_t*, uint32_t, uint32_t, uint32_t);\n')
    text = text.replace('#include "funcs.h"', '#include "funcs.h"' + declaration, 1)
    if name == 'funcs_10.c':
        start = text.index('RECOMP_FUNC void loadDatFile(')
        stop = text.index('\nRECOMP_FUNC ',start+1)
        body=text[start:stop]
        anchor='    load_asset(rdram, ctx);'
        assert body.count(anchor)==1
        body=body.replace(anchor,anchor+'\n    rs6666_dat_loaded(rdram, U32(ctx->r2));')
        text=text[:start]+body+text[stop:]
        for pc, call, desc in ((0x80047554,'isPointXzWithinRangeOfRef','U32(ctx->r5)-0x10u'),(0x80047570,'isDatItemConditionMet','U32(ctx->r4)'),(0x80047640,'setupNpcUpdateFunctions','U32(ctx->r4)')):
            at=text.index(f'// 0x{pc:08X}: jal')
            at=text.index(f'    {call}(rdram, ctx);',at)
            anchor=f'    {call}(rdram, ctx);'
            replacement=f'    {{ uint32_t rs6666_desc = {desc};\n{anchor}\n    rs6666_spawn(rdram, 0x{pc:08x}u, rs6666_desc, U32(ctx->r2)); }}'
            text=text[:at]+text[at:].replace(anchor,replacement,1)
    if name == 'funcs_43.c':
        anchor='L_80102174:\n'
        assert text.count(anchor)==1
        text=text.replace(anchor,anchor+'    rs6666_gate_sample(rdram, ctx, 0);\n')
        anchor='    after_40:\n    // 0x8010218C:'
        assert text.count(anchor)==1
        text=text.replace(anchor,'    after_40:\n    rs6666_gate_sample(rdram, ctx, 1);\n    // 0x8010218C:')
    sites = {'funcs_35.c':((0x800C7564,'ctx->r3','ctx->r5'),(0x800C7714,'ctx->r4','ctx->r5')),
             'funcs_42.c':((0x800FA618,'ctx->r3','0'),(0x800FA924,'ctx->r5','ctx->f0.u32l'))}
    for pc, address, requested in sites.get(name,()):
        pattern = r'(?m)^(    \{ MEM_[BW]\(0X0, '+re.escape(address)+r'\) = [^\n]+RS64_S5798_ST\(0x'+f'{pc:08X}'+r'u,[^\n]+\})$'
        text,n=re.subn(pattern,lambda m:m[0]+f'\n    rs6666_scalar(rdram, 0x{pc:08x}u, U32({address}), U32({requested}));',text)
        assert n in (1,2),(name,hex(pc),n)
    return text, 1

def level3_hooks(text, name):
    marker = '/* PATCH: s6670 ordinary building response */'
    if name not in ('funcs_16.c', 'funcs_44.c') or marker in text:
        if name == 'funcs_44.c' and 'rs6670_tick(rdram,ctx);' not in text:
            text=text.replace('    rs6657_callback_level(rdram,3);','    rs6657_callback_level(rdram,3);\n    rs6670_tick(rdram,ctx);',1)
            text=text.replace(marker,marker+'\nextern void rs6670_tick(uint8_t*,recomp_context*);',1)
            return text,1
        return text, 0
    if name == 'funcs_16.c':
        start = text.index('RECOMP_FUNC void updateDestructionDebrisNpc(')
        stop = text.index('\nRECOMP_FUNC ', start + 1)
        body = text[start:stop]
        at = body.index('{') + 1
        body = body[:at] + '\n    uint32_t rs6670_node=U32(ctx->r4), rs6670_action=U32(ctx->r5)&0xFFFF, rs6670_message=U32(ctx->r6);\n    rs6670_building(rdram,ctx,0,rs6670_node,rs6670_message,rs6670_action);' + body[at:]
        anchor = '    { MEM_W(0X0, ctx->r2) = ctx->r3; RS64_S5798_ST(0x8006CFE8u, 0X0, ctx->r2, 4); }'
        assert body.count(anchor) == 1
        body = body.replace(anchor, '    rs6670_building(rdram,ctx,1,rs6670_node,rs6670_message,rs6670_action);\n'+anchor)
        anchor = '    datItemSetObjectiveBooleanCount(rdram, ctx);'
        assert body.count(anchor) == 1
        body = body.replace(anchor, '    rs6670_building(rdram,ctx,2,rs6670_node,rs6670_message,rs6670_action);\n    { uint32_t saved=rs6657_victim; rs6657_victim=U32(ctx->r17);\n'+anchor+'\n    rs6657_victim=saved; }')
        body = body.replace('L_8006D8C0:\n', 'L_8006D8C0:\n    rs6670_building(rdram,ctx,3,rs6670_node,rs6670_message,rs6670_action);\n')
        text=text[:start]+body+text[stop:]
    else:
        anchor='RECOMP_FUNC void lv3_checkComplexObjectives(uint8_t* rdram, recomp_context* ctx) {'
        assert text.count(anchor)==1
        text=text.replace(anchor,anchor+'\n    rs6657_callback_level(rdram,3);\n    rs6670_tick(rdram,ctx);')
        start=text.index('RECOMP_FUNC void lv3_calculateFriendliesSaved(')
        stop=text.index('\nRECOMP_FUNC ',start+1)
        body=text[start:stop]
        # after_N labels are beyond jal delay-slot duplication.
        for label, pc in (('after_0:',0x80103540),('after_1:',0x80103550)):
            assert body.count(label)==1
            body=body.replace(label,label+f'\n    rs6670_reader(rdram,ctx,0x{pc:08x}u);')
        anchor='    setFriendliesSaved(rdram, ctx);'
        assert body.count(anchor)==1
        body=body.replace(anchor,'    rs6670_reader(rdram,ctx,0x80103560u);\n'+anchor)
        text=text[:start]+body+text[stop:]
    text=text.replace('#include "funcs.h"','#include "funcs.h"\n'+marker+'\nextern void rs6670_tick(uint8_t*,recomp_context*);\nextern void rs6670_building(uint8_t*,recomp_context*,int,uint32_t,uint32_t,uint32_t);\nextern void rs6670_reader(uint8_t*,recomp_context*,uint32_t);\nextern void rs6657_callback_level(uint8_t*,int);',1)
    return text, 1

def level3_fallback_hooks(text,name):
    marker='/* PATCH: s6670 fallback health and effect */'
    if name!='funcs_35.c' or marker in text:return text,0
    start=text.index('RECOMP_FUNC void dealDamagetoDatItem(')
    stop=text.index('\nRECOMP_FUNC ',start+1)
    body=text[start:stop]
    anchor='    { MEM_W(0X6C, ctx->r3) = ctx->r17; RS64_S5798_ST(0x800C74ACu, 0X6C, ctx->r3, 4); }'
    assert body.count(anchor)==1
    body=body.replace(anchor,'    rs6670_fallback(rdram,ctx,0);\n'+anchor+'\n    rs6670_fallback(rdram,ctx,1);')
    anchor='    datItemSetObjectiveBooleanCount(rdram, ctx);'
    assert body.count(anchor)==1
    body=body.replace(anchor,'    rs6670_fallback(rdram,ctx,2);\n'+anchor)
    text=text[:start]+body+text[stop:]
    return text.replace('#include "funcs.h"','#include "funcs.h"\n'+marker+'\nextern void rs6670_fallback(uint8_t*,recomp_context*,int);',1),1


def level5_hooks(text,name):
    marker='/* PATCH: s6676 level5 ordinary wingman response */'
    if name != 'funcs_45.c' or marker in text: return text,0
    anchor='RECOMP_FUNC void lv5_checkComplexObjectives(uint8_t* rdram, recomp_context* ctx) {'
    assert text.count(anchor)==1
    text=text.replace(anchor,anchor+'\n    rs6657_callback_level(rdram,5);\n    rs6673_tick(rdram,ctx);')
    return text.replace('#include "funcs.h"','#include "funcs.h"\n'+marker+'\nextern void rs6673_tick(uint8_t*,recomp_context*);\nextern void rs6657_callback_level(uint8_t*,int);',1),1

def level4_hooks(text,name):
    marker='/* PATCH: s6673 ordinary wingman response */'
    if name not in ('funcs_38.c','funcs_41.c','funcs_45.c') or marker in text: return text,0
    decl='\n'+marker+'\nextern void rs6673_tick(uint8_t*,recomp_context*);\nextern void rs6657_callback_level(uint8_t*,int);\nextern void rs6673_wingman(uint8_t*,recomp_context*,int,uint32_t,uint32_t,uint32_t);\nextern void rs6673_store(uint8_t*,recomp_context*,uint32_t,uint32_t);\n'
    if name=='funcs_45.c':
        anchor='RECOMP_FUNC void lv4_checkComplexObjectives(uint8_t* rdram, recomp_context* ctx) {'
        assert text.count(anchor)==1
        text=text.replace(anchor,anchor+'\n    rs6657_callback_level(rdram,4);\n    rs6673_tick(rdram,ctx);')
    elif name=='funcs_38.c':
        start=text.index('RECOMP_FUNC void npcWingmanUpdate('); stop=text.index('\nRECOMP_FUNC ',start+1)
        body=text[start:stop]; at=body.index('{')+1
        body=body[:at]+'\n    uint32_t rs6673_node=U32(ctx->r4),rs6673_action=U32(ctx->r5)&0xffff,rs6673_msg=U32(ctx->r6);\n    rs6673_wingman(rdram,ctx,0,rs6673_node,rs6673_msg,rs6673_action);'+body[at:]
        anchor='    dealDamageToNpc(rdram, ctx);'; assert body.count(anchor)==1
        body=body.replace(anchor,'    rs6673_wingman(rdram,ctx,1,rs6673_node,rs6673_msg,rs6673_action);\n'+anchor+'\n    rs6673_wingman(rdram,ctx,2,rs6673_node,rs6673_msg,rs6673_action);')
        anchor='    datItemSetObjectiveBooleanCount(rdram, ctx);'; assert body.count(anchor)==1
        body=body.replace(anchor,'    rs6673_wingman(rdram,ctx,3,rs6673_node,rs6673_msg,rs6673_action);\n'+anchor)
        text=text[:start]+body+text[stop:]
    else:
        for pc,off,reg in ((0x800F2148,'0X0','r3'),(0x800F2158,'0X190','r4')):
            anchor=f'    {{ MEM_W({off}, ctx->{reg}) = ctx->r2; RS64_S5798_ST(0x{pc:08X}u, {off}, ctx->{reg}, 4); }}'
            assert text.count(anchor)==2,(hex(pc),text.count(anchor))
            text=text.replace(anchor,f'    rs6673_store(rdram,ctx,0x{pc:08x}u,U32(ADD32(ctx->{reg},{off})));\n'+anchor)
    return text.replace('#include "funcs.h"','#include "funcs.h"'+decl,1),1

def apply(text, name):
    text, changed = _apply(text, name)
    text, extra = level5_hooks(text,name)
    changed |= extra
    text, extra = level4_hooks(text,name)
    changed |= extra
    text, extra = level3_fallback_hooks(text,name)
    changed |= extra
    text, extra = level3_hooks(text, name)
    changed |= extra
    handlers = {
        'funcs_36.c': (('npcProbeDriod', 17, 19, (0x800CBD34,)),),
        'funcs_38.c': (('npcDebrisFieldUpdate', 17, 19, (0x800D5DA8,)),
                       ('npcWingmanUpdate', 16, 18, (0x800D9D28,)),
                       ('npcTieVariantUpdate', 17, 16, (0x800DBF68,))),
    }
    if name == 'funcs_38.c' and '/* PATCH: s6666 shuttle damage */' not in text:
        start = text.index('RECOMP_FUNC void npcShuttleUpdate(')
        stop = text.index('\nRECOMP_FUNC ', start + 1)
        body = text[start:stop]
        anchor = '    dealDamageToNpc(rdram, ctx);'
        assert body.count(anchor) == 1
        body = body.replace(anchor, '    rs6664_transport(rdram, ctx, 0, U32(ctx->r17), U32(ctx->r18));\n' + anchor + '\n    rs6664_transport(rdram, ctx, 1, U32(ctx->r17), U32(ctx->r18));')
        anchor = '    datItemSetObjectiveBooleanCount(rdram, ctx);'
        assert body.count(anchor) == 1
        body = body.replace(anchor, '    rs6664_transport(rdram, ctx, 2, U32(ctx->r17), U32(ctx->r18));\n    { uint32_t saved = rs6657_victim; rs6657_victim = U32(ctx->r17);\n' + anchor + '\n    rs6657_victim = saved; }')
        text = text[:start] + body + text[stop:]
        text = text.replace('#include "funcs.h"', '#include "funcs.h"\n/* PATCH: s6666 shuttle damage */\nextern void rs6664_transport(uint8_t*, recomp_context*, int, uint32_t, uint32_t);\nextern _Thread_local uint32_t rs6657_victim;', 1)
        changed = 1
    text, extra = activation_hooks(text, name)
    changed |= extra
    if name not in handlers:
        return text, changed
    marker = '/* PATCH: s6664 typed objective damage */'
    if marker in text:
        return text, changed
    for fn, npc, msg, effects in handlers[name]:
        start = text.index('RECOMP_FUNC void ' + fn + '(')
        stop = text.index('\nRECOMP_FUNC ', start + 1)
        body = text[start:stop]
        args = f'U32(ctx->r{npc}), U32(ctx->r{msg})'
        anchor = '    dealDamageToNpc(rdram, ctx);'
        assert body.count(anchor) == 1, fn
        body = body.replace(anchor, f'    rs6664_transport(rdram, ctx, 0, {args});\n' + anchor + f'\n    rs6664_transport(rdram, ctx, 1, {args});')
        for pc in effects:
            at = body.index(f'// 0x{pc:08X}: jal')
            at = body.index('    datItemSetObjectiveBooleanCount(rdram, ctx);', at)
            anchor = '    datItemSetObjectiveBooleanCount(rdram, ctx);'
            replacement = (f'    rs6664_transport(rdram, ctx, 2, {args});\n'
                           f'    {{ uint32_t saved = rs6657_victim; rs6657_victim = U32(ctx->r{npc});\n'
                           + anchor + '\n    rs6657_victim = saved; }')
            body = body[:at] + body[at:].replace(anchor, replacement, 1)
        text = text[:start] + body + text[stop:]
    text = text.replace('#include "funcs.h"', '#include "funcs.h"\n' + marker + '\nextern void rs6664_transport(uint8_t*, recomp_context*, int, uint32_t, uint32_t);\nextern _Thread_local uint32_t rs6657_victim;', 1)
    return text, 1

if __name__ == '__main__':
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('../N64Recomp/RecompiledFuncs')
    for name in FILES:
        p = base / name
        text, n = apply(p.read_text(), name)
        if n:
            p.write_text(text)
        print(name, n)
