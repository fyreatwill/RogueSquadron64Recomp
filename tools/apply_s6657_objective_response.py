"""Opt-in single-flight TELE windows and actual objective-store/victim joins."""
from pathlib import Path
import re
import sys

TAG = 'PATCH: s6657 objective response'
FILES = ('funcs_10.c', 'funcs_42.c', 'funcs_8.c', 'funcs_13.c', 'funcs_15.c', 'funcs_16.c', 'funcs_35.c', 'funcs_36.c', 'funcs_38.c', 'funcs_41.c', 'funcs_43.c')
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
static int rs6660_named(uint32_t id) { return rs6657_level == 2 ? id == 40 : (id == 13 || id == 40 || id == 41); }
static void rs6660_census(uint8_t*);
static unsigned rs6657_match(uint32_t, uint32_t);
static int rs6660_candidate(uint8_t*, uint32_t, uint32_t, uint32_t, float, int);
static int rs6657_enabled(void) {
    if (rs6657_en < 0) { const char* e = getenv("ROGUESQ_OBJECTIVE_RESPONSE"); rs6657_en = e && e[0] == '1'; const char* l = getenv("ROGUESQ_OBJECTIVE_RESPONSE_LEVEL"); rs6657_level = l ? atoi(l) : 0; const char* v = getenv("ROGUESQ_OBJECTIVE_RESPONSE_VI"); if (rs6657_level == 2 && v && atoi(v) > 5400 && atoi(v) <= 12000) rs6666_limit = atoi(v); if (rs6657_level != 0 && rs6657_level != 1 && rs6657_level != 2) rs6657_en = 0; }
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
    if ((rs6660_observed && !(rs6657_level == 2 && rs6661_dosed)) || !selected || !flight || dv >= rs6666_limit || (rs6657_level == 0 ? (c1 >= 18 || c2 >= 1 || c3 >= 1) : rs6657_level == 2 ? (rs6657_read_init && ((rs6657_prev[39] && !rs6661_dosed) || MEM_BU(S32((int32_t)0x80138903u), 0) || MEM_BU(S32((int32_t)0x8013890Cu), 0))) : (rs6657_read_init && (rs6657_prev[12] >= 3 || MEM_BU(S32((int32_t)0x801388A5u), 0))))) {
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
int rs6657_gate(uint8_t* rdram) { return !rs6657_enabled() || (rs6657_flight(rdram) && rs6657_arm == 1 && !rs6660_pending_id && !rs6661_dosed); }
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
    if (rs6657_level == 2) for (unsigned i = 0; i < 128; i++) {
        uint32_t value = MEM_BU(S32((int32_t)(0x801388A0u + i)), 0);
        if (!rs6657_read_init || value != rs6662_bools[i])
            fprintf(stderr, "[objresp-bool] epoch=1 vi=%u arm=%u id=%u old=%u new=%u initialized=%u\n", rs64_vi_n_g, rs6657_arm, i + 1, rs6662_bools[i], value, rs6657_read_init);
        rs6662_bools[i] = value;
    }
    rs6657_bool6 = bool6;
    if (!rs6657_read_init && rs6657_level == 2) fprintf(stderr, "[objresp-semantics] level=2 vi=%u c40=%u friendlies=1-c40 fail=c40-positive-to-bool109 success=bool31+32+33+99\n", rs64_vi_n_g, rs6657_word(rdram, 0x801380FCu));
    if (!rs6657_read_init && rs6657_level != 2) fprintf(stderr, "[objresp-semantics] level=%d vi=%u c13=%u c40=%u c41=%u bool6=%u friendlies=19-(c40+c13+c41)\n", rs6657_level, rs64_vi_n_g, rs6657_word(rdram, 0x80138090u), rs6657_word(rdram, 0x801380FCu), rs6657_word(rdram, 0x80138100u), MEM_BU(S32((int32_t)0x801388A5u), 0));
    rs6657_read_init = 1;
}
void rs6657_callback(uint8_t* rdram) { rs6657_callback_level(rdram, 0); }
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
    static uint32_t seen[2048][10], generation[2048], birth[2048], last_report = 0xFFFFFFFFu;
    if (busy || !rs6657_enabled() || rs6657_level != 2 || !rs6657_started || rs6657_done) return;
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
            uint32_t control[6] = {40, 1, 0, 0, 0, 0};
            int accepts = rs6660_selected(control);
            control[2] = 31; control[3] = 1;
            fprintf(stderr, "[objresp-select-control] epoch=1 vi=%u arm=%u slot=%u node=%08x handler=%08x desc=%08x local_fixture=1 accepts40=%d rejects_success=%d guest_writes=0\n", rs64_vi_n_g, rs6657_arm, i, node, handler, desc, accepts, !rs6660_selected(control));
            controls[rs6657_arm]++;
        }

        if (selected && !rs6666_on && rs64_vi_n_g - rs6657_start >= 1800) rs6666_on = rs64_vi_n_g;
        active += node != 0; unknown += node && !known; typed += known != 0; named += selected;
        uint32_t values[10] = {node, npc, handler, desc, f[0], f[1], f[2], f[3], f[4], f[5]};
        int changed = memcmp(seen[i], values, sizeof(values)) != 0;
        if (changed) {
            if (seen[i][0] && (seen[i][0] != node || seen[i][1] != npc || seen[i][2] != handler))
                fprintf(stderr, "[objresp-retire] epoch=1 vi=%u arm=%u slot=%u generation=%u birth=%u node=%08x npc=%08x handler=%08x desc=%08x\n", rs64_vi_n_g, rs6657_arm, i, generation[i], birth[i], seen[i][0], seen[i][1], seen[i][2], seen[i][3]);
            if (node && (!seen[i][0] || seen[i][0] != node || seen[i][1] != npc || seen[i][2] != handler)) { generation[i]++; birth[i] = rs64_vi_n_g; }
            memcpy(seen[i], values, sizeof(values));
            if (node) fprintf(stderr, "[objresp-live] epoch=1 vi=%u arm=%u slot=%u generation=%u birth=%u node=%08x npc=%08x handler=%08x owned=%d typed=%d canonical=%u desc=%08x id=%u delta=%d bool=%u bval=%u id2=%u delta2=%d selected=%d\n", rs64_vi_n_g, rs6657_arm, i, generation[i], birth[i], node, npc, handler, owned, known, owned ? rs6663_half(rdram, node + 0x16) : 0xFFFFu, desc, f[0], (int32_t)f[1], f[2], f[3], f[4], (int32_t)f[5], selected);
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
    if (rs6657_level == 2) { rs6663_scan(rdram); return; }

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
    if (rs6657_level == 2) {
        if (!rs6663_refresh(rdram) || slot >= 2048 || rs6663_free[slot]) { node = npc = desc = 0; typed = 0; }
        else { desc = rs6663_descriptor(rdram, node, &npc, &handler); typed = rs6663_owned(rdram, node) ? rs6663_kind(handler) : 0; }
    }
    rs6660_fields(rdram, typed == 1 ? desc : 0, f);
    int selected = typed == 1 && rs6660_selected(f);
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
    if (!rs6657_enabled() || rs6657_level != 2 || MEM_BU(S32((int32_t)0x80130B40u),0) != 2 || !rs6660_ok(base)) return;
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

def apply(text, name):
    text, changed = _apply(text, name)
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
