#!/usr/bin/env python3
# s4284: add per-commit ring-lap census to src/rsp/dpc_bridge.cpp (idempotent).
p = 'src/rsp/dpc_bridge.cpp'
s = open(p).read()
if 's_c4284_laps' in s:
    raise SystemExit('already patched')
s = s.replace("static uint32_t s_submit_last_end = 0;\n",
 "static uint32_t s_submit_last_end = 0;\n// s4284: per-commit ring-lap census (END < seen). Reset at each deferred commit.\nstatic uint32_t s_c4284_laps = 0, s_c4284_first_lo = 0, s_c4284_first_hi = 0, s_c4284_start = 0, s_c4284_maxseen = 0;\n", 1)
a = "        g_last_wrap_n.store((uint32_t)n, std::memory_order_release);\n"
assert a in s
s = s.replace(a, a + "        if (s_c4284_laps++ == 0) { s_c4284_first_lo = end_phys; s_c4284_first_hi = s_last_end; s_c4284_start = start_phys; }\n        if (s_last_end > s_c4284_maxseen) s_c4284_maxseen = s_last_end;\n", 1)
a = "            RT64::g_s4280_n = 0;\n            static unsigned long cnt = 0;"
assert a in s
b = '''            { static unsigned long cm = 0, cmLap = 0, oddCm = 0, oddCmLap = 0, shown4284 = 0; cm++; if (s_c4284_laps) cmLap++;
              bool anyOdd = false; for (int i = 0; i < n && i < 256; i++) if (RT64::g_s4280_ev[i].odd) { anyOdd = true;
                  const uint32_t off = (uint32_t)RT64::g_s4280_ev[i].off;
                  if (shown4284++ < 60) fprintf(stderr, "[s4284-odd] off=%06X laps=%u firstLap end=%06X seen=%06X start=%06X maxseen=%06X inDropped=%d\\n", off, s_c4284_laps, s_c4284_first_lo, s_c4284_first_hi, s_c4284_start, s_c4284_maxseen, (s_c4284_laps && off >= s_c4284_start && off < s_c4284_maxseen) ? 1 : 0); }
              if (anyOdd) { oddCm++; if (s_c4284_laps) oddCmLap++; }
              if ((cm & 0xFF) == 0) fprintf(stderr, "[s4284-tot] commits=%lu withLap=%lu oddCommits=%lu oddWithLap=%lu\\n", cm, cmLap, oddCm, oddCmLap); }
'''
s = s.replace(a, b + a, 1)
a = "    g_deferred_ranges.clear();\n}\n\n// s68"
assert a in s
s = s.replace(a, "    s_c4284_laps = 0; s_c4284_maxseen = 0;\n" + a, 1)
open(p, 'w').write(s)
