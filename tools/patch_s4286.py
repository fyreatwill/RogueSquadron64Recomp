#!/usr/bin/env python3
# s4286: ROGUESQ_WRAP_RESTORE=1 restores bump-time shadow words into RDRAM around submit_rdp_range at wrap flush;
# ROGUESQ_S4272_CAP raises the shadow range cap (idempotent).
p = 'src/rsp/dpc_bridge.cpp'
s = open(p).read()
if 's4286' in s:
    raise SystemExit('already patched')
a = "                ultramodern::submit_rdp_range(r.first, r.second);\n            }\n            g_deferred_ranges.clear(); g_s4272_sh.clear(); g_s4272_shadow.clear();"
assert s.count(a) == 1
b = '''                static const bool s_restore = []{ const char *e = std::getenv("ROGUESQ_WRAP_RESTORE"); return e && *e && *e != '0'; }();
                const S4272Sh *shp = nullptr;
                if (s_restore && g_rdram_for_submit) for (const S4272Sh &e : g_s4272_sh) if (e.lo == r.first && e.hi == r.second) { shp = &e; break; }
                static unsigned long rn = 0, rMiss = 0, rWordsRestored = 0, rPostDiff = 0, rCtl = 0;
                std::vector<uint8_t> liveSave;
                if (shp) {   // s4286: feed RT64 the bump-time bytes, then put live back
                    liveSave.assign(g_rdram_for_submit + r.first, g_rdram_for_submit + r.second);
                    for (uint32_t x = r.first; x < r.second; x += 4) { uint32_t was, now; memcpy(&was, &g_s4272_shadow[shp->off + (x - r.first)], 4); memcpy(&now, g_rdram_for_submit + x, 4); if (was != now) rWordsRestored++; }
                    memcpy(g_rdram_for_submit + r.first, &g_s4272_shadow[shp->off], r.second - r.first);
                    for (uint32_t x = r.first; x < r.second; x += 4) { uint32_t was, now; memcpy(&was, &g_s4272_shadow[shp->off + (x - r.first)], 4); memcpy(&now, g_rdram_for_submit + x, 4); if (was != now) rPostDiff++; }
                    rCtl += 1;
                } else if (s_restore) rMiss++;
                ultramodern::submit_rdp_range(r.first, r.second);
                if (shp) memcpy(g_rdram_for_submit + r.first, liveSave.data(), r.second - r.first);
                if (s_restore && (++rn <= 8 || (rn & 1023) == 0))
                    fprintf(stderr, "[s4286-restore] n=%lu restoredRanges=%lu noShadow=%lu wordsRestored=%lu postDiff(must be 0)=%lu\\n", rn, rCtl, rMiss, rWordsRestored, rPostDiff);
            }
            g_deferred_ranges.clear(); g_s4272_sh.clear(); g_s4272_shadow.clear();'''
s = s.replace(a, b, 1)
c = "if (sh && submit_hi - submit_lo <= 0x400) {"
assert s.count(c) == 1
s = s.replace(c, 'static const uint32_t cap = []{ const char *e = std::getenv("ROGUESQ_S4272_CAP"); return e ? (uint32_t)strtoul(e, nullptr, 0) : 0x400u; }(); /* s4286 */\n            if (sh && submit_hi - submit_lo <= cap) {')
open(p, 'w').write(s)
