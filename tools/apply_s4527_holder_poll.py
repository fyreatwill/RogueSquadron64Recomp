#!/usr/bin/env python3
"""s4527/s4529: install the ROGUESQ_LOG_S4526 holder poller.

Idempotent. Replaces a poller that lacks the [s4529-H] head-in-block cap, so a
re-apply cannot restore the shared 30-snapshot cap that title-phase next
pointers exhaust before the VI-512 heads exist. A file that already logs
[s4529-H] is left unchanged.
"""
import sys
p = 'src/main/upstream_compat.cpp'
s = open(p).read()
new = r'''    if (const char* e = std::getenv("ROGUESQ_LOG_S4526"); e && e[0] && e[0] != '0') {
        // s4526: every 5 ms walk the node lists at 0x1499B4/0x1499E4 (node = {romA,romB,size,dram,prev,next}, next at +0x14)
        // and scan the voice array; log the FIRST hits where any node address / node word / voice word lies in
        // 0x8017D000..0x80188000. That 40-hit cap is spent on 0x8017D030, which is below the freed block.
        // s4529: a second cap snapshots a chain whose head or any node lies in [0x8017D910, 0x80189340).
        // Dumping every poll would spend all 30 slots on the first head (~150 ms) and miss the later one,
        // so a new head gets itself plus 4 more polls, and later word changes are at most 8 snapshots
        // >=200 ms apart. Guest pc is not logged on those lines: it is not the store.
        std::thread([rdram] {
            const auto W = [rdram](uint32_t g) -> uint32_t { g &= 0x1FFFFFFFu; return g < 0x800000u ? *(volatile uint32_t*)(rdram + (g & ~3u)) : 0u; };
            const auto in = [](uint32_t v) { return v >= 0x8017D000u && v < 0x80188000u; };
            const auto freed = [](uint32_t v) { return v >= 0x8017D910u && v < 0x80189340u; };
            unsigned long ticks = 0; int hits = 0; int snaps = 0; int repeat_snaps = 0; bool cap_logged = false;
            uint32_t lastlen[2] = {0, 0};
            uint32_t last_sig[2] = {0, 0};
            uint32_t last_head[2] = {0xFFFFFFFFu, 0xFFFFFFFFu};
            unsigned long last_snap_tick[2] = {0, 0};
            int burst[2] = {0, 0};
            bool have_sig[2] = {false, false};
            // Head-in-block cap is separate. The shared cap above is spent at width 1024 on
            // next-pointers into the block (heads still 0x80192Cxx) and never sees the
            // VI-512 heads 0x8017DA10 / 0x8017D9E0.
            int head_snaps = 0; int head_repeat = 0; bool head_cap_logged = false;
            uint32_t head_sig_last[2] = {0, 0};
            uint32_t head_addr_last[2] = {0xFFFFFFFFu, 0xFFFFFFFFu};
            unsigned long head_tick_last[2] = {0, 0};
            int head_burst[2] = {0, 0};
            bool head_have[2] = {false, false};
            for (;;) {
                const uint32_t heads[2] = {0x1499B4u, 0x1499E4u};
                for (int l = 0; l < 2; l++) {
                    uint32_t rec[64][4];
                    uint32_t nstored = 0;
                    bool trunc = false;
                    bool in_freed = false;
                    uint32_t head = W(heads[l]);
                    if (freed(head)) in_freed = true;
                    uint32_t n = head, len = 0, sig = head;
                    while (n >= 0x80000000u && n < 0x80800000u && len < 2100) {
                        len++;
                        uint32_t words[6];
                        for (uint32_t k = 0; k < 6; k++) words[k] = W(n + k * 4);
                        if (freed(n)) in_freed = true;
                        sig = (sig * 16777619u) ^ n ^ words[0] ^ (words[1] * 0x9E3779B9u) ^ words[5] ^ (len * 0x85EBCA6Bu);
                        if (nstored < 64) { rec[nstored][0] = n; rec[nstored][1] = words[0]; rec[nstored][2] = words[1]; rec[nstored][3] = words[5]; nstored++; }
                        else trunc = true;
                        if (in(n) && hits < 40) { hits++; std::fprintf(stderr, "[s4526-P] NODE-IN-RANGE list=%d idx=%u node=%08X t=%lu pc=%08X width=%u\n", l, len, n, ticks, (unsigned)g_rs64_last_guest_pc, rs64_vi_committed_width()); }
                        for (uint32_t k = 0; k < 6; k++) { if (in(words[k]) && k != 3 && hits < 40) { hits++; std::fprintf(stderr, "[s4526-P] LINK-IN-RANGE list=%d idx=%u node=%08X word%u=%08X t=%lu pc=%08X width=%u\n", l, len, n, k, words[k], ticks, (unsigned)g_rs64_last_guest_pc, rs64_vi_committed_width()); } }
                        n = words[5];
                    }
                    if (len != lastlen[l]) { lastlen[l] = len; std::fprintf(stderr, "[s4526-P] chain list=%d len=%u head=%08X t=%lu pc=%08X width=%u\n", l, len, W(heads[l]), ticks, (unsigned)g_rs64_last_guest_pc, rs64_vi_committed_width()); }
                    if (!in_freed) burst[l] = 0;
                    else if (snaps < 30) {
                        bool new_head = !have_sig[l] || head != last_head[l];
                        bool sig_changed = !have_sig[l] || sig != last_sig[l];
                        bool cooled = have_sig[l] && (ticks - last_snap_tick[l]) >= 40;
                        const char* kind = nullptr;
                        if (new_head) { kind = "head"; burst[l] = 4; }
                        else if (burst[l] > 0) { kind = "burst"; burst[l]--; }
                        else if (sig_changed && cooled && repeat_snaps < 8) { kind = "change"; repeat_snaps++; }
                        if (kind) {
                            snaps++;
                            have_sig[l] = true;
                            last_sig[l] = sig;
                            last_head[l] = head;
                            last_snap_tick[l] = ticks;
                            std::fprintf(stderr, "[s4529-P] SNAP n=%d list=%d kind=%s len=%u head=%08X stored=%u width=%u t=%lu\n", snaps, l, kind, len, head, nstored, rs64_vi_committed_width(), ticks);
                            for (uint32_t i = 0; i < nstored; i++) {
                                std::fprintf(stderr, "[s4529-P] NODE snap=%d list=%d idx=%u addr=%08X w0=%08X w1=%08X w5=%08X\n", snaps, l, i + 1, rec[i][0], rec[i][1], rec[i][2], rec[i][3]);
                            }
                            if (trunc) std::fprintf(stderr, "[s4529-P] TRUNC snap=%d list=%d len=%u stored=%u\n", snaps, l, len, nstored);
                            std::fflush(stderr);
                        }
                    } else if (!cap_logged) {
                        cap_logged = true;
                        std::fprintf(stderr, "[s4529-P] SNAP-CAP snaps=%d width=%u t=%lu\n", snaps, rs64_vi_committed_width(), ticks);
                        std::fflush(stderr);
                    }
                    if (!freed(head)) head_burst[l] = 0;
                    else if (head_snaps < 30) {
                        bool new_head = !head_have[l] || head != head_addr_last[l];
                        bool sig_changed = !head_have[l] || sig != head_sig_last[l];
                        bool cooled = head_have[l] && (ticks - head_tick_last[l]) >= 200;
                        const char* hkind = nullptr;
                        if (new_head) { hkind = "head"; head_burst[l] = 4; }
                        else if (head_burst[l] > 0) { hkind = "burst"; head_burst[l]--; }
                        else if (sig_changed && cooled && head_repeat < 6) { hkind = "change"; head_repeat++; }
                        if (hkind) {
                            head_snaps++;
                            head_have[l] = true;
                            head_sig_last[l] = sig;
                            head_addr_last[l] = head;
                            head_tick_last[l] = ticks;
                            std::fprintf(stderr, "[s4529-H] SNAP n=%d list=%d kind=%s len=%u head=%08X stored=%u width=%u t=%lu\n", head_snaps, l, hkind, len, head, nstored, rs64_vi_committed_width(), ticks);
                            for (uint32_t i = 0; i < nstored; i++) {
                                std::fprintf(stderr, "[s4529-H] NODE snap=%d list=%d idx=%u addr=%08X w0=%08X w1=%08X w5=%08X\n", head_snaps, l, i + 1, rec[i][0], rec[i][1], rec[i][2], rec[i][3]);
                            }
                            if (trunc) std::fprintf(stderr, "[s4529-H] TRUNC snap=%d list=%d len=%u stored=%u\n", head_snaps, l, len, nstored);
                            std::fflush(stderr);
                        }
                    } else if (!head_cap_logged) {
                        head_cap_logged = true;
                        std::fprintf(stderr, "[s4529-H] SNAP-CAP snaps=%d width=%u t=%lu\n", head_snaps, rs64_vi_committed_width(), ticks);
                        std::fflush(stderr);
                    }
                }
                const uint32_t vb = W(0x1496F8u); const uint32_t vc = (W(0x149700u) >> 16) & 0xFFFFu;
                if (vb >= 0x80000000u && vb < 0x80800000u && vc && vc < 512) {
                    for (uint32_t o = 0; o < vc * 0x40u && o < 0x8000u; o += 4) { uint32_t v = W(vb + o); if (in(v) && hits < 40) { hits++; std::fprintf(stderr, "[s4526-P] VOICE-IN-RANGE base=%08X cnt=%u off=%04X word=%08X t=%lu pc=%08X width=%u\n", vb, vc, o, v, ticks, (unsigned)g_rs64_last_guest_pc, rs64_vi_committed_width()); } }
                }
                ticks++; if ((ticks % 400) == 0) std::fprintf(stderr, "[s4526-P] alive ticks=%lu len0=%u len1=%u voicebase=%08X cnt=%u\n", ticks, lastlen[0], lastlen[1], vb, vc);
                std::this_thread::sleep_for(std::chrono::milliseconds(5));
            }
        }).detach();
    }
'''
if 's4529-H' in s:
    sys.exit(0)
anchor = "    std::thread([rdram] {\n        uint32_t pv[3] = {0xDEADBEEFu"
start = s.find('    if (const char* e = std::getenv("ROGUESQ_LOG_S4526");')
if start != -1:
    end = s.find(anchor, start)
    if end < 0:
        sys.exit('s4526 poller present but s4231 anchor missing after it')
    s = s[:start] + new + s[end:]
else:
    if anchor not in s:
        sys.exit('anchor missing')
    s = s.replace(anchor, new + anchor, 1)
open(p, 'w').write(s)
