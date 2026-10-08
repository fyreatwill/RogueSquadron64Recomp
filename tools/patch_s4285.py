#!/usr/bin/env python3
# s4285: at WRAP_FLUSH time compare bump-time shadow vs live RDRAM (idempotent).
p = 'src/rsp/dpc_bridge.cpp'
s = open(p).read()
if 's4285-flush' in s:
    raise SystemExit('already patched')
a = "        {\n            uint32_t b = 0;\n            for (const auto &r : g_deferred_ranges) {\n                if (should_drop_wrap_rdp"
assert s.count(a) == 1
new = '''        {   // s4285: at flush, is the lap-1 content RT64 is about to read already overwritten (bump-time shadow vs live)?
            static unsigned long fl = 0, flDiff = 0, flWords = 0, flDiffWords = 0, flCtl = 0;
            unsigned long d = 0, w = 0;
            if (g_rdram_for_submit) for (const S4272Sh &e : g_s4272_sh)
                for (uint32_t x = e.lo; x < e.hi; x += 4) { uint32_t was, now; memcpy(&was, &g_s4272_shadow[e.off + (x - e.lo)], 4); memcpy(&now, g_rdram_for_submit + x, 4); w++; if (was != now) d++; }
            fl++; flWords += w; flDiffWords += d; if (d) flDiff++;
            { uint32_t x = 0, y = 1; flCtl += (x != y); }
            if (fl <= 8 || (fl & 63) == 0)
                fprintf(stderr, "[s4285-flush] n=%lu shRanges=%zu words=%lu diffWords=%lu | tot flushes=%lu withDiff=%lu words=%lu diff=%lu control=%lu\\n", fl, g_s4272_sh.size(), w, d, fl, flDiff, flWords, flDiffWords, flCtl);
        }
'''
s = s.replace(a, new + a)
open(p, 'w').write(s)
