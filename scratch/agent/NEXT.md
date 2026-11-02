# NEXT: G3 SELECT GAME screen — backdrop photo pick and missing slot-preview inset
HYPOTHESIS-ID: g3-render-match-frontend

s6779: title and level/craft select match retail. SELECT GAME (1024 phase, after Start on the title) differs:
retail backdrop = wide Hoth hangar for Start at 26.1 s and 31.1 s (4.8/9.8 s after the title appears), inset (X-wing over
Tatooine) + gold/silver/bronze medal column ~1 s in. Port: Start at 16 s (3.1 s after title) -> Hoth crew backdrop, inset
at ~2 s; Start at 21 s (8.1 s after) -> X-wing-in-hangar backdrop, inset + medals NEVER (14 s hold). Evidence:
scratch/s6779/{retail_title_sheet,r3_sheet,selgame_pair}.png, r2/sheet.png.
Hypotheses:
- H-rand: the backdrop index comes from the rand stream (0x80003430 callers) or a free-running counter (osGetCount / VI
  count) that advances at a different rate in the port on the title screen.
- H-load: inset + medals wait on a ROM DMA / decompression that the port completes for some backdrops and not others
  (a real port defect: a stalled load).
- H-retail: retail also varies with press time (only 2 retail press times tried, both gave the same photo).
Work unit (one run pair, all instruments at once):
1. Retail: tools/g3_frontend/run.sh-style oracle with --exec-trace 0x80003430 (rand) + --exec-trace-also on the PI DMA
   entry (grep PROJECT-OVERVIEW for the osPiStartDma / romCopy wrapper pc) over the title -> SELECT GAME window, PRESS at
   6,11,16,21,26 and a third arm at 36 s (H-retail).
2. Port: same save, AP Start at 6,11,16 vs 6,11,21, ROGUESQ_RAND_TRACE + PI DMA log (ROGUESQ_LOG_PHASE carries DMA? check)
   and window captures.
3. Find the call whose result differs between the port @16 and @21 arms at the transition (backdrop pick), and the DMA
   (or decompress) that runs in r2 but not r3 (inset).
Discriminating outcome: backdrop pick = rand/counter call that differs per press time in port but not retail -> H-rand;
an inset DMA issued but never completed / never issued in the @21 arm -> H-load; retail third arm changes photo -> H-retail.
