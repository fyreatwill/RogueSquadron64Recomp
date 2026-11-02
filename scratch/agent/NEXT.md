# NEXT: fold the s6789 spansent soaks, close G3e, then start G2b (Chapter II crawl audio chop)
HYPOTHESIS-ID: g2b-crawl-audio-chop

Done s6789: the dd4 periodic terrain dip was the scanConvert low clamp (-128.0) colliding with the span-table 0x80 sentinel.
dd>1 now clamps at -127 (tools/apply_s6789_spansent.py). lvl1 dd4/dd3: 0 in-flight drops; same-run A/B 4 -> 0.
1. Fold SOAK-RESULTS lines s6789_spansent_lvl5_dd4 / lvl10_dd4:
   `python3 scratch/s6788/census_drops.py scratch/s6788/soak6789_census_lvl{5,10}.txt` and `python3 scratch/s6788/rej.py
   scratch/s6788/soak6789_trace_lvl{5,10}.txt 3`. Count only drops with tri>0. tri=0/tx=0 frames are cuts; check that each one
   also appears in a dd1 run before dismissing it. If the in-flight terrain drops are 0, close G3e in CURRENT-TRUTH and tell
   the owner dd4 is clean.
   If drops remain: rej.py on those VIs, and if spaneq spikes again, check the high clamp (127) the same way.
2. G2b (ITERATION 3c): choppy audio on the Chapter II opening text crawl (owner run FPS60, likely dd1). Hypotheses:
   H-fps60 (the crawl's audio/song tick is frame-counted and FPS60 doubles or halves it), H-underrun (AI buffer underruns
   during the crawl from host stalls, e.g. crawl text texture loads), H-retail (retail crawl audio is the same).
   One build, one run, two arms (FPS60 on/off) on the same crawl: [ai] cadence/underrun counters, host frame times, plus a
   PCM capture for an offline gap scan. Retail control: the oracle/angrylion crawl audio, if obtainable.
