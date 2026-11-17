// ROGUESQ s7521 class FR: executed RSP code bytes vs the image RSPRecomp compiled.
// The port picks the RSP function by task TYPE only (main.cpp get_rsp_microcode: gfx -> factor5 runner, audio -> ucode B),
// and skips every IMEM DMA (rsp.hpp: the compiled code already IS the ucode; overlay swaps are spliced statically). A real
// RSP runs whatever bytes the task's ucode/ucode_boot/ucode_data pointers and the ucode's own IMEM DMAs bring in from RDRAM.
// ROGUESQ_S7521_UCODEWATCH=1, at every SP task (get_rsp_microcode): compare RDRAM [boot], [ucode text], [ucode_data] with the
// ROM bytes of the main segment (ram 0x80000400 <- rom 0x1000, size 0xA4D30); log every distinct task tuple, every new
// differing byte offset per region (budgeted), non-ROM sources; at every IMEM DMA compare the source bytes with the ROM and
// log each distinct (mem, dram, len, rom). [s7521-sum] every 2000 tasks and at exit-ish intervals.
// Ctl ROGUESQ_S7521_CTL=1: gfx task 600 flips one byte each of boot/text/data before the check and restores it right after
// (the runner stages ucode_data after this hook, so it sees the original byte); the first IMEM DMA after gfx task 900 flips
// one source byte for the compare only. Scored by tools/s7521_ucode_bytes.py.
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <mutex>
#include <set>
#include <map>
#include <tuple>
#include "ultramodern/ultra64.h"
#include "librecomp/game.hpp"

extern "C" int rs64_s7521_on = [] {
    const char* e = std::getenv("ROGUESQ_S7521_UCODEWATCH");
    return (e && e[0] && e[0] != '0') ? 1 : 0;
}();

namespace {
constexpr uint32_t kMainPhysLo = 0x400, kMainPhysHi = 0xA5130, kRomDelta = 0xC00;  // main segment ROM 0x1000..0xA5D30 (splat yaml)
std::mutex m;
int ctl = -1;
unsigned long tasks = 0, gfx = 0, aud = 0, other = 0, reg_checks = 0, reg_bad = 0, reg_nonrom = 0, bytes_checked = 0;
unsigned long imem = 0, imem_ok = 0, imem_bad = 0, imem_nonrom = 0, ctl_rows = 0;
long rows = 0;
std::set<std::tuple<uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t>> tuples;
std::set<std::pair<int, uint32_t>> seen_off;                // (region kind, byte offset) already reported
std::map<std::tuple<uint32_t, uint32_t, uint32_t, int>, unsigned long> imem_seen;
bool imem_ctl_pending = false, imem_ctl_done = false;
// hardware IMEM window model (gfx): 0 = boot image (text DMA to 0x1080), else phys source of the last DMA into 0x1DB0
uint32_t win = 0; unsigned long l1db0[3][7] = {}; int force_state = 0;  // 0 idle, 1 armed, 2 done
constexpr uint32_t kOvl0 = 0x025748;
// s7522 class FS: per-word model of hardware IMEM (gfx): isrc[w] = RDRAM phys of the byte DMA'd into IMEM word w (0 = none this task).
// ctl (ROGUESQ_S7521_CTL=1): after gfx task 800 the next real overlay DMA into 0x1DB0 (not ovl0) is modelled 8 bytes off, so the
// dispatches into it until the next 0x1DB0 DMA must score as non-resident code (their rows carry ctl=1).
uint32_t isrc[1024] = {}; int fs_ctl = 0;  // 0 idle, 2 perturbed, 3 done
unsigned long ndisp = 0, n28 = 0, fs_gen = 0, fs_ctl_dmas = 0;
std::map<std::tuple<uint32_t, uint32_t, uint32_t, int>, unsigned long> disp;
std::set<uint32_t> src28;
int ctl_get();
void fs_dma(uint32_t mem, uint32_t phys, uint32_t len, unsigned long gfxn, unsigned long taskn) {
    int shift = 0;
    if ((mem & 0x1FFF) == 0x1DB0) {
        if (fs_ctl == 2) fs_ctl = 3;
        else if (fs_ctl == 0 && ctl_get() == 1 && gfxn >= 800 && phys != kOvl0) { fs_ctl = 2; shift = 8; ++fs_ctl_dmas;
            std::fprintf(stderr, "[s7522-ctl] perturb mem=%04X dram=%06X len=%X task=%lu gfx=%lu\n", mem, phys, len, taskn, gfxn); }
    }
    for (uint32_t i = 0; i < len && i < 0x1000; i += 4) isrc[(((mem & 0xFFF) + i) >> 2) & 1023] = phys + i + shift;
}
inline int wkind() { return win == 0 ? 0 : win == kOvl0 ? 1 : 2; }

inline uint8_t ramb(const uint8_t* rdram, uint32_t phys) { return rdram[phys ^ 3]; }
inline void ctl_init() { if (ctl < 0) { const char* c = std::getenv("ROGUESQ_S7521_CTL"); ctl = c ? std::atoi(c) : 0; } }
int ctl_get() { ctl_init(); return ctl; }

// returns differing byte count; -1 if the range is outside the ROM-backed main segment
long cmp_rom(const uint8_t* rdram, uint32_t phys, uint32_t len, uint32_t* first) {
    if (len == 0 || phys < kMainPhysLo || phys + len > kMainPhysHi || phys + len < phys) return -1;
    auto rom = recomp::get_rom();
    if ((uint64_t)phys + kRomDelta + len > rom.size()) return -1;
    long bad = 0;
    for (uint32_t i = 0; i < len; i++)
        if (ramb(rdram, phys + i) != rom[phys + kRomDelta + i]) { if (!bad && first) *first = i; ++bad; }
    bytes_checked += len;
    return bad;
}

void region(const uint8_t* rdram, int kind, const char* nm, uint32_t type, uint32_t va, uint32_t len, int c) {
    if (va == 0 && len == 0) return;
    ++reg_checks;
    const uint32_t phys = va & 0x1FFFFFFFu;
    uint32_t first = 0;
    if (phys >= kMainPhysLo && phys < kMainPhysHi && phys + len > kMainPhysHi) {  // ROM-backed prefix + overlay-window tail
        if (seen_off.insert({kind + 200, phys}).second && rows < 400) {
            ++rows; std::fprintf(stderr, "[s7521-reg] kind=TAIL region=%s type=%u va=%08X len=%X rom_backed=%X tail=%X task=%lu ctl=%d\n", nm, type, va,
                                 len, kMainPhysHi - phys, phys + len - kMainPhysHi, tasks, c);
        }
        len = kMainPhysHi - phys;
    }
    long bad = cmp_rom(rdram, phys, len, &first);
    if (bad < 0) {
        ++reg_nonrom;
        if (seen_off.insert({kind + 100, phys}).second && rows < 400) {
            ++rows; std::fprintf(stderr, "[s7521-reg] kind=NONROM region=%s type=%u va=%08X len=%X task=%lu ctl=%d\n", nm, type, va, len, tasks, c);
        }
        return;
    }
    if (!bad) return;
    ++reg_bad;
    auto rom = recomp::get_rom();
    for (uint32_t i = first; i < len; i++) {
        uint8_t a = ramb(rdram, phys + i), b = rom[phys + kRomDelta + i];
        if (a == b) continue;
        if (!c && !seen_off.insert({kind, i}).second) continue;
        if (c) ++ctl_rows;
        if (rows < 600 || c) {
            ++rows; std::fprintf(stderr, "[s7521-reg] kind=DIFF region=%s type=%u va=%08X off=%X ram=%02X rom=%02X romoff=%X task=%lu ctl=%d\n",
                                 nm, type, va, i, a, b, phys + kRomDelta + i, tasks, c);
        }
    }
}
void sum(const char* why) {
    ++fs_gen;  // s7522 rows first: the FR scorer reads the l1db0 rows that follow [s7521-sum]
    std::fprintf(stderr, "[s7522-sum] gen=%lu why=%s ndisp=%lu keys=%zu n28=%lu src28=%zu ctl_dmas=%lu fs_ctl=%d\n", fs_gen, why, ndisp, disp.size(), n28,
                 src28.size(), fs_ctl_dmas, fs_ctl);
    for (uint32_t v : src28) std::fprintf(stderr, "[s7522-src28] gen=%lu src=%06X\n", fs_gen, v);
    for (auto& kv : disp)
        std::fprintf(stderr, "[s7522-disp] gen=%lu t=%04X b153=%02X src=%06X ctl=%d n=%lu\n", fs_gen, std::get<0>(kv.first), std::get<1>(kv.first),
                     std::get<2>(kv.first), std::get<3>(kv.first), kv.second);
    std::fprintf(stderr, "[s7521-sum] why=%s tasks=%lu gfx=%lu aud=%lu other=%lu tuples=%zu reg_checks=%lu reg_bad=%lu reg_nonrom=%lu bytes=%lu "
                 "imem=%lu imem_ok=%lu imem_bad=%lu imem_nonrom=%lu imem_distinct=%zu ctl_rows=%lu ctl=%d\n", why, tasks, gfx, aud, other,
                 tuples.size(), reg_checks, reg_bad, reg_nonrom, bytes_checked, imem, imem_ok, imem_bad, imem_nonrom, imem_seen.size(), ctl_rows, ctl);
    static const char* wn[3] = {"boot", "ovl0", "other"};
    for (int w = 0; w < 3; w++)
        std::fprintf(stderr, "[s7521-l1db0] why=%s win=%s entry=%lu b0=%lu b1=%lu b2=%lu b3=%lu b4=%lu b5=%lu\n", why, wn[w], l1db0[w][6], l1db0[w][0],
                     l1db0[w][1], l1db0[w][2], l1db0[w][3], l1db0[w][4], l1db0[w][5]);
}
}  // namespace

extern "C" void rs64_s7521_task(uint8_t* rdram, const OSTask* task) {
    if (!rs64_s7521_on || !task || !rdram) return;
    std::lock_guard<std::mutex> g(m);
    ctl_init();
    ++tasks;
    const uint32_t type = task->t.type;
    if (type == M_GFXTASK) { ++gfx; win = 0; for (auto& w : isrc) w = 0; }  // rspboot reloads the ucode text (IMEM 0x1080..) at every task start
    else if (type == M_AUDTASK) ++aud; else ++other;
    const uint32_t bt = (uint32_t)task->t.ucode_boot, bs = task->t.ucode_boot_size, tx = (uint32_t)task->t.ucode,
                   ts = task->t.ucode_size, dt = (uint32_t)task->t.ucode_data, ds = task->t.ucode_data_size;
    if (tuples.insert({type, bt, bs, tx, ts, dt, ds}).second)
        std::fprintf(stderr, "[s7521-tuple] type=%u boot=%08X/%X ucode=%08X/%X data=%08X/%X flags=%X task=%lu\n", type, bt, bs, tx, ts, dt, ds,
                     (uint32_t)task->t.flags, tasks);
    // ctl: flip one byte per region on gfx task 600 (restored below, before the runner stages DMEM)
    const bool c = ctl == 1 && type == M_GFXTASK && gfx == 600;
    struct Flip { uint32_t phys; } fl[3] = {{(bt & 0x1FFFFFFFu) + 0x10}, {(tx & 0x1FFFFFFFu) + 0x100}, {(dt & 0x1FFFFFFFu) + 0x40}};
    if (c) { for (auto& f : fl) rdram[f.phys ^ 3] ^= 0x5A; std::fprintf(stderr, "[s7521-ctl] flip boot+10 text+100 data+40 task=%lu\n", tasks); }
    region(rdram, 0, "boot", type, bt, bs, c);
    region(rdram, 1 + (type == M_AUDTASK ? 10 : 0), "text", type, tx, ts, c);
    region(rdram, 2 + (type == M_AUDTASK ? 10 : 0), "data", type, dt, ds, c);
    if (c) { for (auto& f : fl) rdram[f.phys ^ 3] ^= 0x5A; std::fprintf(stderr, "[s7521-ctl] restore task=%lu\n", tasks); }
    if (ctl == 1 && type == M_GFXTASK && gfx == 900 && !imem_ctl_done) imem_ctl_pending = true;
    if (tasks % 2000 == 0) sum("periodic");
}

// ev 6 = L_1DB0 entry (rs64_e9prov_l1db0_reset), 0..5 = rs64_inline_probe_trigen_branch (5 = path A: j L_1E5C past L_1E48)
extern "C" void rs64_s7521_l1db0(int ev) {
    if (!rs64_s7521_on) return;
    std::lock_guard<std::mutex> g(m);
    ctl_init();
    const int w = wkind();
    if (ev < 0 || ev > 6) return;
    if (!l1db0[w][ev]++ ) std::fprintf(stderr, "[s7521-l1db0] first win=%d ev=%d task=%lu gfx=%lu ctl=%d\n", w, ev, tasks, gfx, force_state == 1 && ev != 6);
    if (ev == 6 && ctl == 1 && gfx >= 700 && force_state == 0) { force_state = 1; }
    else if (ev != 6 && force_state == 1) {
        force_state = ev == 5 ? 2 : 0;
        std::fprintf(stderr, "[s7521-ctl] l1db0 forced current win=%d ev=%d caught=%d task=%lu gfx=%lu\n", w, ev, ev == 5, tasks, gfx);
        if (ev == 5) { ++ctl_rows; --l1db0[w][5]; }   // the planted path-A is not a live count
    }
}
// dpc_bridge rs64_dpc_current_read: one forced 'RDP still busy' read while the ctl is armed inside L_1DB0
extern "C" int rs64_s7521_force_cur() { return rs64_s7521_on && force_state == 1; }

extern "C" void rs64_s7521_imem(uint8_t* rdram, uint32_t mem, uint32_t dram, uint32_t len, int aud) {
    if (!rs64_s7521_on || !rdram) return;
    std::lock_guard<std::mutex> g(m);
    ctl_init();
    ++imem;
    const uint32_t phys = dram & 0x1FFFFFFFu;
    if (!aud && (mem & 0x1000)) fs_dma(mem, phys, len, gfx, tasks);  // s7522: model first (the FR ctl branch below returns early)
    const bool c = imem_ctl_pending && !aud;
    if (c) { rdram[(phys + len / 2) ^ 3] ^= 0x5A; }
    uint32_t first = 0;
    long bad = cmp_rom(rdram, phys, len, &first);
    if (c) { rdram[(phys + len / 2) ^ 3] ^= 0x5A; imem_ctl_pending = false; imem_ctl_done = true; ++ctl_rows;
             std::fprintf(stderr, "[s7521-ctl] imem flip mem=%04X dram=%06X len=%X bad=%ld caught=%d task=%lu\n", mem, phys, len, bad, bad > 0, tasks); return; }
    if (bad < 0) ++imem_nonrom; else if (bad) ++imem_bad; else ++imem_ok;
    if (!aud) { if (mem == 0x1080 && len == 0xF80) win = 0; else if (mem == 0x1DB0) win = phys; }
    auto key = std::make_tuple(mem, phys, len, aud);
    auto it = imem_seen.find(key);
    const int st = bad < 0 ? 2 : bad ? 1 : 0;
    if (it == imem_seen.end()) {
        imem_seen[key] = 1;
        std::fprintf(stderr, "[s7521-imem] new mem=%04X dram=%06X len=%X aud=%d rom=%X state=%s bad=%ld first=%X task=%lu\n", mem, phys, len, aud,
                     bad < 0 ? 0 : phys + kRomDelta, st == 0 ? "ROM" : st == 1 ? "DIFF" : "NONROM", bad, first, tasks);
    } else {
        ++it->second;
        if (st && rows < 600) { ++rows; std::fprintf(stderr, "[s7521-imem] bad mem=%04X dram=%06X len=%X aud=%d state=%s bad=%ld first=%X task=%lu\n",
                                                     mem, phys, len, aud, st == 1 ? "DIFF" : "NONROM", bad, first, tasks); }
    }
}

// s7522 class FS: every do_indirect_jump (target, DMEM 0x153) against the modelled resident source of the target word
extern "C" void rs64_s7522_disp(uint32_t target, uint32_t b153) {
    if (!rs64_s7521_on) return;
    std::lock_guard<std::mutex> g(m);
    const uint32_t t = (target | 0x1000) & 0x1FFF;
    ++ndisp; ++disp[std::make_tuple(t, b153 & 0xFF, isrc[(t & 0xFFF) >> 2], fs_ctl == 2 ? 1 : 0)];
}
// the ovl28 hand route: hardware DMAs 0x330 bytes from src into IMEM 0x12A0 (main's L_12A0..L_15CC restore) before j 0x122C
extern "C" void rs64_s7522_ovl28(uint32_t src) {
    if (!rs64_s7521_on) return;
    std::lock_guard<std::mutex> g(m);
    const uint32_t phys = src & 0x1FFFFFFFu;
    ++n28; src28.insert(phys);
    fs_dma(0x12A0, phys, 0x330, gfx, tasks);
}
