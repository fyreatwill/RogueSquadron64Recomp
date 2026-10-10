#!/usr/bin/env python3
"""s4527: insert the ROGUESQ_LOG_S4526 stale-node holder poller into upstream_compat.cpp (idempotent)."""
import sys
p = 'src/main/upstream_compat.cpp'
s = open(p).read()
if 'ROGUESQ_LOG_S4526' in s:
    sys.exit(0)
anchor = "    std::thread([rdram] {\n        uint32_t pv[3] = {0xDEADBEEFu"
new = r'''    if (const char* e = std::getenv("ROGUESQ_LOG_S4526"); e && e[0] && e[0] != '0') {
        // s4526: every 5 ms walk the node lists at 0x1499B4/0x1499E4 (node = {romA,romB,size,dram,prev,next}, next at +0x14)
        // and scan the voice array; log the FIRST hits where any node address / node word / voice word lies in the freed
        // block 0x8017D000..0x80188000, with holder, word and last guest pc. Chain length is the positive control.
        std::thread([rdram] {
            const auto W = [rdram](uint32_t g) -> uint32_t { g &= 0x1FFFFFFFu; return g < 0x800000u ? *(volatile uint32_t*)(rdram + (g & ~3u)) : 0u; };
            const auto in = [](uint32_t v) { return v >= 0x8017D000u && v < 0x80188000u; };
            unsigned long ticks = 0; int hits = 0; uint32_t lastlen[2] = {0, 0};
            for (;;) {
                const uint32_t heads[2] = {0x1499B4u, 0x1499E4u};
                for (int l = 0; l < 2; l++) {
                    uint32_t n = W(heads[l]), len = 0;
                    while (n >= 0x80000000u && n < 0x80800000u && len < 2100) {
                        len++;
                        if (in(n) && hits < 40) { hits++; std::fprintf(stderr, "[s4526-P] NODE-IN-RANGE list=%d idx=%u node=%08X t=%lu pc=%08X width=%u\n", l, len, n, ticks, (unsigned)g_rs64_last_guest_pc, rs64_vi_committed_width()); }
                        for (uint32_t k = 0; k < 6; k++) { uint32_t v = W(n + k * 4); if (in(v) && k != 3 && hits < 40) { hits++; std::fprintf(stderr, "[s4526-P] LINK-IN-RANGE list=%d idx=%u node=%08X word%u=%08X t=%lu pc=%08X width=%u\n", l, len, n, k, v, ticks, (unsigned)g_rs64_last_guest_pc, rs64_vi_committed_width()); } }
                        n = W(n + 0x14);
                    }
                    if (len != lastlen[l]) { lastlen[l] = len; std::fprintf(stderr, "[s4526-P] chain list=%d len=%u head=%08X t=%lu pc=%08X width=%u\n", l, len, W(heads[l]), ticks, (unsigned)g_rs64_last_guest_pc, rs64_vi_committed_width()); }
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
assert anchor in s
open(p, 'w').write(s.replace(anchor, new + anchor, 1))
