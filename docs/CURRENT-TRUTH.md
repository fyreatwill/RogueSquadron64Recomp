# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 6654 (2026-10-29).
`PORTING-STATE.md` is the chronological ledger. Historical detail, the
retired backlog, and the verbatim s6378-s6551 body of this file are in
`docs/PROJECT-OVERVIEW.md` ("Migrated from CURRENT-TRUTH (s6552 maintenance)"
and "Archive: CURRENT-TRUTH body s6378-s6551").

## Headline

- The qualified route boots attribution, N64 logo, intro, Factor 5 logo, title,
  hangar, and mission origins; mission input reaches flight code.
- M5 audio de-stubbing, M3 idiom audits, generated-symbol renaming (G5), M6
  first-mission endurance (3x600 s lvl1/5/7, s6442), and G2 audio are closed.
  G4 crash hunting is parked after clean coverage. G1 is mission coverage and
  visual quality, not autopilot work.
- **Active thread closed: G1d 21:9 level-select tear (g1d-levelselect-heap).**
  s6631. The wide gap punch in `buildHeapFreeList` places the `8010FEFC`
  free-tail header exactly on `801163E4`. A walker that stops at `a >= e4`
  never cuts it (first binary, `did=0`, overlap unchanged). The fix, aspect
  > 4:3 only, shortens the previous block and plants the terminator at
  `e4-0x10`. It does not write the image and does not run at 4:3. Second
  binary, both widths, screen unlocked: level-select `did=3`. 21:9
  `e4=0x80B56000` head `0x80961000` cut `0x80A0AFF0` oldsz `0x14B000` newsz
  `0x14AFF0`; heap end becomes `0x80B56000`. 16:9 end becomes `0x80B7BD80`.
  Neither width has a malloc covering `0xBB0020`. The 21:9 zlib `0x8000`
  block ends at `0xB53A20`, below the image. The upload word is
  `0xFFFCFFFC`, not the memset zero. 16:9 45.9 s / 50 frames, fail [];
  21:9 45.2 s / 54, fail [] (edge-px and dy reasons gone; dy180 20.11,
  edges 46.72/31.59). Both floor_frac 1.0, alive, rc -9, 0 crashes.
  Evidence: `scratch/agent/s6631_heapcap_at/`. Pre-fix baseline remains
  s6630. Do not skip `rs_memset` or restore depth. OS window stays 640x480.
- **G3c (owner visual report): engineering closed, owner judgement pending.**
  (a) far-edge stair: no opt-in rougher than retail (s6449, s6544);
  (b) spike wedges: H-hw-draws, angrylion lights the same 16/79 wedges
  (s6454), `ROGUESQ_CULL_SPIKE` stays opt-in; (c) turning shake: retail 30 fps
  judder (s6455, s6458).
- **G1d (aspect): level-select floor tear closed (s6631).** Flight radar
  inset matches retail (s6610). Extra width is real scene and the left HUD
  stays pinned. Heap `8010FEFC` now stops at the depth pointer when aspect
  is wider than 4:3. The OS window stays 640x480, so wider modes letterbox.
  Do not return to the combiner or the pixel pipe.
- **G1e (frame rate): closed** (retail ~30 fps vs FPS60 ~59, s6452).
- **G1 (c) level 2 flight framebuffer: present.** s6632, retail 4:3, draw
  distance left at 1. Selector B40=2, cursor=2. After the hangar, VI
  alternates `0x690400` and `0x620400`; every-50 dumps landed on
  `0x620400` (512x444). 7/8 of those frames pass sky, terrain, craft and
  HUD. Title, hangar and the other origins in the same run score 0/49.
  Sheet `docs/g1_lvl2_flight_s6632.png`. Objective hit-response (d) was
  not run. No crash in the 30 s hold.
- **G1 (c) level 3 flight framebuffer: extended class rule accepts it.**
  s6634, offline on the s6633 dumps. No new capture. Sky and HUD stay
  the s6632 cuts. Terrain is relative local edge energy on y 0.45-0.95,
  mean((|dLx|+|dLy|)/(L+12)) in [0.08, 0.33]: night dumps 0.114-0.266,
  oracle 0.129, level 2 0.106, title 0.410, level-select floor 0.709.
  Craft keeps the engine bloom, or a chase-band metal hull (fraction
  >= 0.10 of pixels at least 30 luma above the band median, chroma
  <= 80), or a saturated green reticle (fraction >= 0.004). Five-file
  table holds: oracle, level-2 `fb_0002700`, and level-3 `fb_0002700`
  pass; the floor and the s6633 title dump fail. 11/13 mission dumps
  pass. n=2550 fails craft (hull 0.054, no reticle; the picture is
  still a flight). n=3150 fails the unchanged sky cut (dark fraction
  0.41). Tool: `tools/g1_flight_class.py`. Objective (d) was not run.
- **G1 (c) level 4 flight framebuffer: extended class rule accepts it.**
  s6636, offline on the s6635 dumps. No new capture. Sky gains a third
  arm, luma ≥ 140 and R ≥ G+40 and R ≥ B+20. Craft gains a dark hull
  when the chase-band median is ≥ 120 (fraction ≥ 0.06 at least 50
  below that median, chroma ≤ 90). Terrain floor stays 0.08. Canon
  table still prints canon_bad 0; the level-3 mission lines stay
  11/13. Six of the seven phase-7 dumps pass. n=2300 passes sky and
  craft and still misses terrain (rel 0.065); left as a near-miss.
  Same-run title `fb_0000800_w512.ppm` stays sky 0 / terr 0 (luma 80.5,
  R−G 29). Hangar `fb_0001700_w512.ppm` still fails HUD only. Sheet
  `docs/g1_lvl4_flight_s6635.png`. Tool: `tools/g1_flight_class.py`.
  Objective (d) was not run.
- **G1 (c) level 5 flight framebuffer: frozen rule accepts it.**
  s6637, retail 4:3, draw distance 1, aspect unset. Selector B40=5,
  cursor=5. Nine phase-7 dumps, n=2450..2850, are 512x444 at origin
  `0x00620400` (the other buffer; `0x690400` is in the VI log). Night
  sky, rocky ground, X-wing, radar, reticle. 7/9 pass all four
  clauses. n=2800 rel 0.338 and n=2850 rel 0.331 miss only the 0.33
  terrain ceiling and are not required. Same-run title
  `fb_0000800_w512.ppm` fails sky and terrain (rel 0.432). Hangar
  `fb_0001700_w512.ppm` fails HUD only (radar 0). Sheet
  `docs/g1_lvl5_flight_s6637.png`. 0 crashes in the 30 s hold. The
  classifier was not edited. Objective (d) was not run.
- **G1 (c) level 6 flight framebuffer: frozen rule accepts it.**
  s6638, retail 4:3, draw distance 1, aspect unset. Selector B40=6,
  cursor=6. Eleven phase-7 dumps, n=2650..3150, are 512x444 at origin
  `0x00620400` (the other buffer; `0x690400` is in the VI log). Canyon,
  snowspeeder, radar, reticle. 8/11 pass all four clauses. n=2800
  misses sky only (dark 0.019, luma 56.0, R−G 10.2) and is not
  required. n=2850 and n=2900 show no chase craft and no radar, so
  they are not four-part frames. Same-run title `fb_0000800_w512.ppm`
  fails sky and terrain (rel 0.423). Hangar `fb_0001700_w512.ppm`
  fails HUD only (radar 0). Sheet `docs/g1_lvl6_flight_s6638.png`.
  0 crashes in the 30 s hold. The classifier was not edited.
  Objective (d) was not run.
- **G1 (c) level 7 flight framebuffer: frozen rule accepts it.**
  s6639, retail 4:3, draw distance 1, aspect unset. Selector B40=7,
  cursor=7. Twelve phase-7 dumps, n=2450..3000, are 512x444 at origin
  `0x00690400` (this run sampled the route key; `0x620400` is in the
  VI log). Canyon, Y-wing, radar, reticle. 4/12 pass all four clauses
  (n=2550, 2600, 2800, 2850). Five miss sky only (luma 46.3..60.1,
  dark 0.371..0.536) and three miss the terrain ceiling only (rel
  0.332, 0.353, 0.359). Those are the same near-miss families as
  level 6's luma-56 sky and level 5's rel 0.331/0.338, and they are
  not required. Same-run title `fb_0000800_w512.ppm` fails sky and
  terrain (rel 0.437). Hangar `fb_0001700_w512.ppm` fails HUD only
  (radar 0). Sheet `docs/g1_lvl7_flight_s6639.png`. 0 crashes in the
  30 s hold. The classifier was not edited. Objective (d) was not run.
- **G1 (c) level 8 flight framebuffer: dusk rule accepts it.**
  s6641, offline on the s6640 dumps. No new capture. The orange sky
  arm is now luma≥80 with the same R≥G+40 and R≥B+20 gates. Craft
  adds a lower-centre metal edge: low-chroma grey with a coloured
  neighbour, fraction ≥0.05. Six of seven phase-7 dumps pass all
  four clauses (edge 0.063..0.115). n=2600 is the side view and
  misses craft only (edge 0.041). Same-run title fails sky and
  terrain (edge 0.017, luma 85.2, R−G 32.1). Craft-select fails HUD
  only (edge 0.021, radar 0). `canon_bad 0`, mission 11/13. The
  0.08 floor, the 0.33 ceiling and the luma≥70 blue arm were not
  moved. Sheet remains `docs/g1_lvl8_flight_s6640.png`. Objective
  (d) was not run.
- **G1 (c) level 9 flight framebuffer: frozen rule accepts it.**
  s6642, one retail 4:3 capture, draw distance 1, aspect unset.
  Selector B40=9, cursor=9. Thirteen phase-7 dumps, n=2350..2950,
  are 512x444 at origin `0x00690400` (this run sampled the route
  key; `0x620400` is in the VI log). Orange canyon, X-wing, radar,
  reticle. 8/13 pass all four clauses. Not required: n=2350 craft
  only (edge 0.019), n=2600 and n=2650 sky only (luma 74.8 and
  56.9), n=2700 and n=2800 terrain only (rel 0.074 and 0.076).
  Same-run title fails sky and terrain. Craft-select fails HUD
  only (radar 0.001). Sheet `docs/g1_lvl9_flight_s6642.png`.
  0 crashes in the 30 s hold. The classifier was not edited.
  Objective (d) was not run.
- **G1 (c) level 10 flight framebuffer: tan-cloud rule accepts it.**
  s6644, offline on the s6643 dumps. No new capture. Sky gains a
  fourth arm: luma≥70, R−G in [20, 32], R−B≥40 and G−B≥18.
  Eleven of twelve phase-7 dumps pass all four clauses. n=2900
  now passes sky and still misses craft (edge 0.013, ship beside
  the station); not required. The title shares R−G 27.1 but
  G−B is 5.5, so its sky stays false and the overall verdict
  stays fail. Craft-select still fails HUD only (radar 0.002).
  `canon_bad 0`, mission 11/13. The 0.08 floor, the 0.33 ceiling,
  the blue arm, the orange arm and the edge≥0.05 cut were not
  moved. Sheet remains `docs/g1_lvl10_flight_s6643.png`.
  Objective (d) was not run.
- **G1 (c) level 11 flight framebuffer: frozen rule accepts it.**
  s6645, one retail 4:3 capture, draw distance 1, aspect unset.
  Selector B40=11, cursor=11. Nine phase-7 dumps, n=2450..2850,
  are 512x444 at origin `0x00690400` (this run sampled the route
  key; `0x620400` is in the VI log, 19 lines). Snow field,
  snowspeeder, radar, reticle. 8/9 pass all four clauses. n=2450
  misses craft only (metal 0.014, sil 0.044, edge 0.003): the
  speeder is small and low. Not required. Same-run title
  `fb_0000800_w512.ppm` fails sky and terrain (luma 82.8, R−G
  30.5, rel 0.441). Hangar `fb_0001700_w512.ppm` fails sky and
  HUD (radar 0); terrain rel 0.195 does not accept it. Sheet
  `docs/g1_lvl11_flight_s6645.png`. 0 crashes in the 30 s hold.
  The classifier was not edited. Objective (d) was not run.
- **G1 (c) level 12 flight framebuffer: frozen rule accepts it.**
  s6646, one retail 4:3 capture, draw distance 1, aspect unset.
  Selector B40=12, cursor=12. Five phase-7 dumps, n=2400..2600,
  are 512x444. The phase transition origin is `0x00690400`;
  every dump's own origin field is the other buffer
  `0x00620400` (16 and 15 VI lines). Blue sky, green ridge,
  X-wing, TIEs, radar, reticle, shield badge. 4/5 pass all
  four clauses. n=2400 misses craft only (metal 0.078, sil
  0.000, edge 0.043): the ship is banked against cloud and
  does not clear the chase cuts. Not required. Same-run title
  `fb_0000800_w512.ppm` fails sky and terrain (luma 83.7,
  R-G 31.2, rel 0.444). Craft-select `fb_0001700_w512.ppm`
  (origin `0x006AB400`) fails HUD only (radar 0.002). Sheet
  `docs/g1_lvl12_flight_s6646.png`. 0 crashes in the 30 s
  hold. The classifier was not edited. Objective (d) was not run.
- **G1 (c) level 13 flight framebuffer: frozen rule accepts it.**
  s6647, one retail 4:3 capture, draw distance 1, aspect unset.
  Selector B40=13, cursor=13. Nine phase-7 dumps, n=2800..3200,
  are 512x444 at origin `0x00690400` (this run sampled the route
  key; `0x620400` is in the VI log, 13 lines). Dark sky, lava
  field, Y-wing, radar, reticle, shield badge. 2/9 pass all four
  clauses (n=3150 rel 0.325, n=3200 rel 0.217). Seven miss the
  terrain ceiling only (rel 0.362..0.611): the lava is
  high-contrast and is not required. Same-run title
  `fb_0000800_w512.ppm` fails sky and terrain (luma 81.2, R-G
  29.3, rel 0.432). Craft-select `fb_0001700_w512.ppm` (origin
  `0x006AB400`, Y-wing) fails sky and HUD (radar 0.001). Sheet
  `docs/g1_lvl13_flight_s6647.png`. 0 crashes in the 30 s hold.
  The classifier was not edited. Objective (d) was not run.
- **G1 (c) level 14 flight framebuffer: frozen rule accepts it.**
  s6648, one retail 4:3 capture, draw distance 1, aspect unset.
  Selector B40=14, cursor=14. Nine phase-7 dumps, n=2450..2850,
  are 512x444 at origin `0x00690400` (this run sampled the route
  key; `0x620400` is in the VI log, 14 lines). Grey cloud, rocky
  ridge, X-wing, radar, reticle, shield badge. 6/9 pass all four
  clauses (n=2550, 2600, 2650, 2700, 2750, 2800). Not required:
  n=2450 terrain floor only (rel 0.065; the ship is in cloud and
  the ground is a sliver), n=2500 terrain ceiling only (rel
  0.357), and n=2850, a ground view with no chase craft and no
  radar (rel 0.625, radar 0). Same-run title fails sky and
  terrain. Craft-select fails HUD only (radar 0). Sheet
  `docs/g1_lvl14_flight_s6648.png`. 0 crashes in the 30 s hold.
  The classifier was not edited. Objective (d) was not run.
- **G1 (c) level 15 flight framebuffer: frozen rule accepts it.**
  s6649, one retail 4:3 capture, draw distance 1, aspect unset,
  `ROGUESQ_FORCE_PLANET_UNLOCK=0xFF`. Selector B40=15, cursor=15.
  Eight phase-7 dumps, n=3050..3400, are 512x444 at origin
  `0x00620400` (this run sampled the other buffer; `0x690400` is
  in the VI log, 16 lines). Blue sky, ocean and islands, V-wing,
  radar, reticle, shield badge. 6/8 pass all four clauses. Not
  required: n=3350 and n=3400 miss the terrain floor only (rel
  0.079 and 0.075). Both are still flights. Same-run title fails
  sky and terrain. Craft-select fails HUD only (radar 0). Sheet
  `docs/g1_lvl15_flight_s6649.png`. 0 crashes in the 30 s hold.
  The classifier was not edited. Objective (d) was not run.
- **G1 (c) level 16 flight framebuffer: frozen rule accepts it.**
  s6650, one retail 4:3 capture, draw distance 1, aspect unset.
  No planet unlock. Selector B40=16, cursor=16. Beggar's Canyon,
  "WIN THE RACE", skyhopper. Eleven post-hangar dumps,
  n=1600..2100, are 512x444. Every dump's own origin field is
  `0x00620400`; `0x690400` is in the VI log (13 lines). The
  phase field stays 5: `rs64_phase_ord` bumps only on a VI-width
  change, and the hangar and the flight are both width 512.
  There is no phase-7 dump. 3/11 pass all four clauses (n=1600
  chase, edge 0.076, rel 0.083; n=1650 and n=1850 cockpit,
  metal 0.187 and 0.177). Not required: n=1700, 1900 and 1950
  miss craft only (small or oversized engine), and five dumps
  are the start-key pause overlay (radar 0). Same-run title
  fails sky and terrain. Craft-select `fb_0001550_w512.ppm`
  fails terrain and HUD. Sheet `docs/g1_lvl16_flight_s6650.png`.
  0 crashes in the 30 s hold. The classifier was not edited.
  Objective (d) was not run.
- **G1 (c) level 17 flight framebuffer: grey-trench rule accepts it.**
  s6652, offline on the s6651 dumps. No new capture. Sky gains a
  fifth arm: luma in [38, 55], |R−G| ≤ 8, |R−B| ≤ 8, |G−B| ≤ 8,
  and at least 0.80 of the sky-window samples have channel
  spread ≤ 8. n=2300 is the chase (neutral8 0.845, luma 42.5)
  and passes all four clauses. That is 1/10 of the post-hangar
  dumps. Not required: n=2250 stays a sky miss (luma 32.8, below
  the 38 floor) and a craft miss; six pause overlays stay HUD
  fails (radar 0); n=2050 and n=2200 stay crest frames (radar 0).
  The binding separator from the level-3 sky miss m3150 is
  neutral8 (0.845 vs 0.613). m3150's luma 40.0 is inside
  [38, 55], so the luma band is not what keeps mission at 11/13.
  Both title skies stay false (canon neutral8 0.344, luma 75.0,
  R−G 24.7; same-run title neutral8 0.345, luma 73.4, R−G 23.6).
  Craft-select stays an overall fail. `canon_bad 0`, mission
  11/13. The 0.08 floor, the 0.33 ceiling, dark ≥ 0.60, and the
  sky sample window were not moved. Sheet remains
  `docs/g1_lvl17_flight_s6651.png`. Objective (d) was not run.

- **G1 (c) level 18: snow-surface rule accepts both flight frames.**
  s6654, offline on the s6653 capture; no launch or build. n=2200/2250
  pass all four clauses. The extra terrain arm requires mean luma ≥180,
  at least 0.50 of terrain samples with luma ≥180 and channel spread ≤64,
  and relative edge energy in [0.02,0.08). Measured luma 217.5/210.5,
  bright low-chroma fraction 0.977/0.937, rel 0.046/0.068. A stricter
  spread≤22 grey test misses blue-tinted snow (fraction <0.001).
  All eight same-run negatives (title, craft-select, three crest and
  three pause frames) reject overall and none selects the snow arm.
  Full table: canon_bad 0; level-3 mission remains 11/13. The original
  [0.08,0.33] arm, sky/craft/HUD cuts and windows are unchanged.
  Independent content evidence is the inspected s6653 contact sheet;
  numeric generalization remains single-capture evidence, not retail
  equivalence. No runtime change; objective (d) was not run.

## Superseded conclusions — do not act on these
- s6653 "level 18 has visual evidence but no numeric terrain acceptance" (s6654: the bounded bright low-chroma snow arm accepts both flight views while every control holds). Believable because their rel 0.046/0.068 is below the original 0.08 floor; that band remains unchanged.
- s6651 "level 17 does not pass the frozen rule, and the grey trench box is not a sky arm" (s6652: neutral8 ≥ 0.80 inside luma [38, 55] with |channel means| ≤ 8 accepts n=2300, 1/10; canon_bad 0; mission 11/13; both title skies stay false; m3150 stays a sky miss at neutral8 0.613). Believable because dark ≥ 0.60, the blue arm, the orange arm and the tan-cloud arm all miss luma 42.5 with R−G 1.4, and the top 4% of that frame is the same grey, so lowering dark does not accept the chase.
- s6649 method "the flight set is the phase-7 dumps" (s6650: level 16's flight dumps stay phase 5). Believable because levels 11-15 insert a 640-wide crawl that bumps `rs64_phase_ord` through 6 into 7. The ordinal bumps only on a VI-width change, so a 512-wide flight after a 512-wide hangar does not.
- s6643 "level 10 is a flight and the frozen rule rejects the sky 0/12" (s6644: tan-cloud arm accepts 11/12; n=2900 stays a craft miss at edge 0.013; title sky stays false because G−B is ~5 while the clouds are ≥22; canon_bad 0; mission 11/13). Believable because dark≥0.60, the blue arm (R−G≤15) and the orange arm (R−G≥40) all miss a luma 73..104 sky with R−G 23..28.
- s6640 "level 8 is a flight and no craft clause accepts it without breaking canon, so the rule stays 0/7" (s6641: lower-centre metal against a coloured neighbour, edge≥0.05, plus luma≥80 orange sky, accepts 6/7; n=2600 stays a side-view near-miss at edge 0.041; canon_bad 0; mission 11/13; title and craft-select still fail). Believable because the engine, bright-metal, reticle and median≥120 dark-hull arms all missed, and a raw grey fraction in the same box also matched the title.
- s6636 "the orange flight sky is the luma≥140 sunset arm" (s6640: level 8's orange sky is luma 84.4..97.0, R−G 86.8..94.3, and that arm misses 7/7; s6641 lowered the floor to 80). Believable because the only orange flight measured before that capture was the level-4 sunset, which cleared 140. Level 4's own acceptance is unchanged.
- s6635 "level 4 is a picture only; the class rule rejects it 0/7, and no sunset arm was shown to keep canon_bad at 0" (s6636: luma≥140 with R≥G+40 and R≥B+20, plus a dark hull against a bright chase band, accepts 6/7; n=2300 stays a terrain near-miss at rel 0.065; canon_bad 0; same-run title and hangar still fail). Believable because the s6634 sky clause had no orange arm and the center-box pink cap treated that sunset as an oversized engine.
- s6634 "a flight sky is either dark (dark≥0.60) or bright with R≤G+15" (s6635: the level-4 sunset is bright, R−G about 48..67, and sky fails 7/7). Believable because the only flight skies measured before this capture were level 1's blue sky and level 3's night. The level-3 acceptance itself still holds.
- s6633 "the level-3 night flight has no numeric acceptance that still rejects the floor and the title" (s6634: relative edge energy in [0.08, 0.33], plus a metal hull or green reticle, accepts 11/13 night dumps; floor rel 0.709 and title rel 0.410 fail). Believable because the only rule that had been run, luma stddev and engine colour, scored 0/13.
- s6632 class rule "those four numeric cuts accept a frame that shows sky, terrain, craft and HUD" (s6633: the level-3 night flight shows all four and scores 0/13). Believable because level 1 and level 2 are bright scenes and both passed the same cuts.
- s6632 "only a dump whose own origin field is 0x690400 is the mission picture" (same run: that origin is in the VI log, and every dump in the window is the other buffer 0x620400, which is the flight picture). Believable because the route key is 0x690400 and EVERY=50 phase-locked onto one of the two buffers.
- s6631 first cut "any block with next > e4 is the tail, so walking until then caps the arena" (same session, did=3 at a header exactly equal to e4). Believable because s6630 described the free block as covering [e4, top) and the header as e4-0x10. The punch's reserved size ends on e4, so the free header is e4 and the old walker returned before cutting.
- s6630's first classifier label "H-stale-target, because inflateEnd frees the zlib window before the depth upload" (same session, H-live-overlap). Believable because that free is real and precedes the read. It does not move `801163E4`, which still names `0x80B56000` at malloc, free, SETZIMG and the upload.
- s6629 "why the zlib window overlaps the depth image is open" (s6630: the image was still reserved when `rs_malloc` returned inside it; s6631 then stopped that heap at the depth pointer). Believable because s6629 named only the store. At s6630 heap `8010FEFC` still ran through to RAM top; heap `8010FF18` already stopped at the depth pointer.
- s6628 "writer between A/B unknown" is resolved at the watched word by s6629 exact pre/post stores and caller context: rs_zcalloc clears a zlib window there. The earlier witness lacked store hooks. s6630 resolves the ownership class; it does not make the whole stripe one 32 KB zero.
- s6628 closes H-swap/H-alias for the measured upload (single-source): believable because the earlier native witness preceded byteswapping and did not record the live mapping. Post-swap and exit preserve `0x9EC4`, and both sites use the identical host address; the zero appears between them.
- s6627 closes "the 1024x447 `copyToRAM` at `0x00B20000` writes the `0x0000` stripe" (it covers `0x00BB0020`). Believable because that span contains every stripe address and the same write's own image y=180 is rawBe 0. Refuted: the absolute sample is rawBe `0x9F4C` on all 935 covering writebacks, the call count does not move, and the upload still reads `0x0000`. The image-y zero is phys `0x00B7A020`.
- s6626 closes "fbChangesDrawDepth, its boolean mask, or its viewport manufactures the 21:9 depth stripe from a clear or smooth guest field" (H-upload). Believable because the GPU image goes from a read-back clear of 1.0 to the stripe inside copyFromChanges, and a discard mask cannot paint 0 by itself. Refuted: the guest words already are the stripe and match the GPU on 142/142 samples (mae 0), shader endian, site state.cpp:2604.
- s6625 "after the zero head, x=16 is a smooth 0.964..0.961 ramp and x=1007 stays 1.0". Believable because x=16 does contain 0.96408 and x=1007 has more exact-1 samples (31 vs 13). Both columns actually interleave ~0.96 and 1.0. The stable part is the exact-0 head.
- s6625 closes "the 21:9 zeros are unwritten depth tiles (create-clear never applied, so a readback of 0)". Believable because Metal does not clear a D32 texture at creation, and a different 1024x480 target's first sample in the same run was exact 0. Refuted on the floor texture: clearDepthTarget read back 1.0 on both columns, and the following copyFromChanges replaced those pixels.
- s6623 "shader-to-attachment MAE 37 at 21:9 means the first wrong stage is an attachment write after a sane shader" (s6624: the same shader color is stored at 16:9, where depth is 1.0 and LESS passes, and rejected at 21:9, where a nearer striped depth already occupies the columns). Believable because the UAV record is written before the depth test and matched the 16:9 attachment exactly.
- s6614 lead "dtdx*x at the outer third diverges on 21:9" (s6615: dtdx shrinks by about 796/1024 and the texel matches to about 0.05). Believable because the sample x grows with the framebuffer and s6613 only cancelled that product at x=0.
- s6612 "21:9 S at the left edge walks off the 64-wide mask while 16:9 stays inside" (s6613: 0/16 pairs do that; S at x=0 matches). Believable because the x span and dsdx scale with width. x_major moves the other way and the product cancels.
- s6610 ring-only "second=fbw-512 fixes the 16:9 radar" (the ring reached the retail inset, but the wedge stayed at 769..792 with 0 pixels inside the ring). Believable because s6609's red-ring edge equalled retail+second. The disc is a separate pre-shift `ROGUESQ_SHIFT_REGION` writer; shift must be A, not RA.
- s6602 "wide-only bottom garbage selects a stale/stride renderer family"
  (s6607-s6608: diagnostic height exceeded the VI source; corrected bounded
  dumps and OS window captures lack the tail). Believable because raw guest
  PPMs looked like window captures. This does not close native geometry issues.
- s6606 "the wide hangar band is already in source pixels" (s6607: source
  fingerprint checks columns 269..335 in 336 rows; visible bottom garbage is
  in a raw 448-row dump beyond that copy). Believable because the raw PPM
  looked like window output and nonzero/transition counts appeared to confirm
  it. The PPM header explicitly says rdram-readback-not-window; its fixed
  height is not the actual VI source height. Actual window fidelity remains
  open; the source-versus-presentation split was not closed.
- (s6579) "dd4 bundle-only / dd4 holds without ROGUESQ_DD_UNSAFE ran at dd4" (superseded: they ran dd3). Believable because the knob was set to 4 and nothing warned except a "multiplier 3" log line, which looked like a display quirk; the s6446 cap in apply_s6036_dd.py:7 clamps silently otherwise.
- s6576 "lvl1 ddclamp area saturates at level extent by dd6, not an engine table" (s6577: at dd6 the cell cap trims the window below the extent in ~55% of samples on lvl1/5/10; the earlier 4096 maximum was a single sample).
- s6574 "dd12 holds clean": believable because the env var was 12 and the run was clean; overturned s6575 - the multiplier is clamped to 8, so it was dd8. Raising the clamp is not the next step; the 64-wide terrain table saturates first (single-source, one run's log).
- (s6559, superseded s6560) "The ~600 chunk/frame loss comes from a head write the store hook cannot see (MEM_W grow hooks, fixup force-zero)." Believable because the hook showed no far/mid/null stores yet the list shrank. Refuted: tracked==actual head 199/199 with a firing positive control; the off-chain stores are in the hooked path, mislabelled 'splice'.

One line each: claim (superseded by; why it was believable).

- s6555/s6554 "chunks consumed by a runaway consumer / free path leaks" (s6556: pops==pushes per frame; chunks vanish without a pop).
- s6554 "runaway consumer in traverseSceneGraphRecursive" (s6555: sibling loop visits 8-17 nodes/frame, 0 revisits at the fault frames; the fault stack merely passes through it).

- s6553 "dd>1 NULL node = DL-chunk supply shortfall" (s6554: a 12x larger arena is consumed in ~24 frames; chunk-empty is the symptom of a runaway scene-graph walk).
- s6550 "split POOLX=3 vs 4 for a threshold" (s6551: px2-4 all fault; the cap scaled with POOLX).
- s6545 "cap0 vs inf undecided" / s6544 "pinned pose" sheet (s6546; s6544 pinned only the stair-metric window, not the camera).
- s6539 cap ordering 0<40<120<inf for terrain (s6541 retracted as run-to-run scatter; 4-10 frames/arm looked monotonic).
- s6542 cap0 dearer than cap120 (s6543: post-inf hysteresis; rotation order confounded it).
- s6540 "default path differs from explicit cap120" (s6541 H-noise; single runs differed).
- s6537 "a cell cap keeps most of the gain cheaply" (s6543: gain is all-or-nothing; cap arms were cross-run).
- s6525 dd4-rejected cells have sentinel recs -2 (s6526 raw dump: normal recs; the joined log read unpopulated bytes).
- s6520 span bytes 0x80 "never written" (s6521: clamp/clear values; 0x80 resembled an init fill).
- s6516 dd4 EMPTY reads another table (s6517: sampling-phase confound; dump rows covered different key ranges).
- s6509 DC0 writes outside a 24-byte span table (s6510/s6511: it is a 64x64 grid; only 24 bytes were dumped).
- s6502 thread-local / s6500-s6505 cumulative writer joins (s6505/s6506: cross-function shared counter; guest IDs matched).
- s6495 all-127 table = rasterizer produced no rows (s6514; snapshot is taken after the filter's own 0x7F stamp).
- s6491 cell list never empty (s6492: read stale r16; head is v0).
- s6488/s6489 low-vs-high-ground tri split (suspect: tool hardcodes non-flight fbs).
- s6472 fixed 64x64 grid tables limit dd3 (s6473 offline: window is post-clamp, kept<cap).
- s6470/s6471 "game submits shorter DL at dd3" break point (explained by the span-filter chain; pinned vs unpinned recipes disagreed).
- s6466 dd8 att1 "route failure" (real SIGBUS; soak summary alone mislabelled it).
- s6446: s6420 "dd3+fix lvl1/5/10 clean" holds were dd2 (run.log said `capped to 2`).
- s6414 durable constraint "dd>2 exhausts the DL chunk supply" ([dlpool] identical across arms; H-chunk refuted).
- s6407 ~5% HUD-absent at dd3/dd4 (s6409: scorer counted menu frames).
- s6399 aspect side-edge lean (s6401 withdrawn: outer-column scalars are noise).
- s6393/s6391 fixed wide-flight origin gate (origin is allocator-dependent).
- s6380 zero-FD57 interpretation (s6380long route audit: retry arm took a different route).
- s6292 FPS60 owns the turning shake (s6455: VI wall-stamp artifact).
- s6426 menu garble = wide-FB stride defect (s6427: 640-wide cam scaling).
- s6434 hangar only ~340/448 rows (s6438: 436-448 lit; dumps misread).

## Run recipes and hard config

- Run from `build/` with the ROM beside it; SIGKILL to stop; one game run at a time.
- Current pinned dd4 lvl1 run: `zsh scratch/agent/s6549_run.sh <dd> <poolx>`.
- dd>2 needs `ROGUESQ_DD_UNSAFE=1` (clamp 8); confirm run.log echoes `multiplier N`.
- lvl10/15 need `ROGUESQ_FORCE_PLANET_UNLOCK=0xFF`. Wide soaks need
  `MISSION_WIDTH=796|1024` + `WIDE_ROUTE=1`; ASPECT implies `OSMEM_MB=12`.
- Pose control: `ROGUESQ_POSE_LOCK=1` + `ROGUESQ_POSE_PIN_POSITION=1`; dump
  ordinal is not a phase key, join dumps to `[vi]`/origin
  (`tools/g1c_fbdump_join.py`).
- Soak verdicts: `scratch/agent/SOAK-RESULTS.md`; read `alive_at_end` /
  `crashlines`, never rc. A queued repeat soak is not a work unit.
- Per-frame cost meter: `[g1b]` lines in run.log (sd_wall, tasks/s).
- Full dd knob/instrument table: PROJECT-OVERVIEW "G1c draw-distance knob and
  recipe reference"; owner guide `docs/DRAW-DISTANCE.md`.

## G1 mission coverage

Playable levels are 0..18 (`NUM_LEVELS=0x13`; 19 and 20 are sentinels). Levels
1–9 and 11–18 have route/hold coverage; levels 10 and 15 need the planet
unlock or its long retail intro. Level 1 has a retail flight match. Level 2 passes the numeric class
rule (s6632). Level 3 passes the extended rule (s6634, 11/13 of the
s6633 dumps; floor and title rejected). Level 4 passes the extended rule on 6/7 phase-7 dumps (s6636);
n=2300 remains a terrain near-miss at rel 0.065 and is not required.
Level 5 passes the frozen rule on 7/9 phase-7 dumps (s6637);
n=2800 and n=2850 remain terrain-ceiling near-misses at rel 0.338
and 0.331 and are not required. Level 6 passes the frozen rule on
8/11 phase-7 dumps (s6638); n=2800 remains a sky near-miss at luma
56.0 and is not required. Level 7 passes the frozen rule on 4/12
phase-7 dumps (s6639); five sky misses (luma 46.3..60.1) and three
terrain-ceiling misses (rel 0.332..0.359) are not required.
Level 8 passes the dusk rule on 6/7 phase-7 dumps (s6641, offline
on the s6640 capture). n=2600 remains a side-view craft near-miss
at edge 0.041 and is not required. Level 9 passes the frozen rule
on 8/13 phase-7 dumps (s6642, one capture). Not required: n=2350
craft (edge 0.019), n=2600 and n=2650 sky (luma 74.8 and 56.9),
n=2700 and n=2800 terrain (rel 0.074 and 0.076). Level 10 passes the tan-cloud rule on 11/12 phase-7 dumps
(s6644, offline on the s6643 capture). n=2900 remains a craft
near-miss at edge 0.013 and is not required. The new arm is
only an extra sky accept, so a level 2–9 frame that already
passed still passes. Those earlier pass counts were not re-opened.
Level 11 passes the frozen rule on 8/9 phase-7 dumps (s6645,
one capture). n=2450 remains a distant-craft near-miss (metal
0.014, sil 0.044, edge 0.003) and is not required.
Level 12 passes the frozen rule on 4/5 phase-7 dumps (s6646,
one capture). n=2400 remains a banked-craft near-miss (metal
0.078, sil 0.000, edge 0.043) and is not required.
Level 13 passes the frozen rule on 2/9 phase-7 dumps (s6647,
one capture). Seven lava frames miss the terrain ceiling only
(rel 0.362..0.611) and are not required.
Level 14 passes the frozen rule on 6/9 phase-7 dumps (s6648,
one capture). Not required: n=2450 terrain floor (rel 0.065),
n=2500 terrain ceiling (rel 0.357), and n=2850, a ground view
with no chase craft and no radar. Those are not a reason to
move 0.08 or 0.33.
Level 15 passes the frozen rule on 6/8 phase-7 dumps (s6649,
one capture, planet unlock on). Not required: n=3350 terrain
floor (rel 0.079) and n=3400 terrain floor (rel 0.075). Both
are still flights. Those are not a reason to move 0.08.
Level 16 passes the frozen rule on 3/11 post-hangar
mission-origin dumps (s6650, one capture, no planet unlock).
Those dumps are phase 5, not phase 7: the width stayed 512.
Not required: three craft-only misses and five pause-overlay
frames (radar 0). n=1600 rel 0.083 is inside the band and is
not a reason to move 0.08.
Level 17 passes the grey-trench rule on 1/10 post-hangar
mission-origin dumps (s6652, offline on the s6651 capture).
n=2300 is the chase. Not required: n=2250 (luma 32.8, under
the new arm's 38 floor, and a craft miss), six pause overlays
(radar 0), and two crest frames (radar 0). The new arm is
only an extra sky accept. m3150 stays a sky miss (neutral8
0.613) even though its luma 40.0 sits inside [38, 55], so
mission stays 11/13. Both title skies stay false. dark was
not moved from 0.60. The 0.08 floor and the 0.33 ceiling
were not moved.
Level 18 passes the snow-surface arm on 2/8 mission-origin dumps
(s6654, offline on s6653): n=2200/2250. Crest/pause frames remain
fails. Numeric acceptance and inspected imagery agree; no claim of
retail equivalence. Next is the existing level-0 capture, omitted from
this recent numeric sweep. Objective response coverage remains partial;
mission wins, autopilot aim and mission-to-mission progression stay
owner playtest scope.

## Durable constraints

- Retail defaults remain unchanged. Opt-ins include draw distance, aspect,
  FPS60, spike culling, and audio control. Do not make an opt-in default from
  a single-source result.
- `ROGUESQ_DRAW_DISTANCE`: dd2 qualified lvl1/5/10; dd3/dd4/dd6 300 s holds
  clean lvl1/5/10 under DD_UNSAFE; dd8 lvl1/5 clean. Crash-free holds do not
  mean "renders correctly" (s6468: dd>=4 ground missing before the bypass).
  No mitigation is acceptable without naming the writer and establishing value
  legitimacy; dd>1 fixes live in `tools/apply_s6*.py` and fixup scripts.
- Wide rendering uses runtime RAM-top handling and a larger reported memory
  arm; default remains 4:3/retail. Native hangar artifacts remain parked.
- The title plume is parked after clean boots. Reopen only on new evidence.
- Read `docs/F5-UCODE-REFERENCE.md` before interpreting Factor 5 streams.
  Ground truth must precede new instrumentation; every null needs a positive
  control and two independent lines of evidence before changing this file.
- Generated diagnostics must survive regeneration through fixup tooling.
  Never reset, clean, checkout, or update submodules. If editing `lib/`, run
  `./submodule-patches/export.sh` and commit the refreshed patches.

## Next steps (single monotonic backlog)
1. **(s6654) Close the level-0 framebuffer class table offline.** Use
   `docs/g3_port_lvl0_oracle_pair_f5000.png` and
   `docs/g3_port_lvl0_flight.png`, already inspected in s5985/s5998.
   Score with the current rule and inspect against the saved retail oracle;
   do not launch a repeat hold. Report whether these cropped images can
   meet the unchanged four-part rule. Do not relabel level 1 as level 0
   from the oracle filename. See NEXT.md for hypotheses and commands.

### Archived historical next-step entries
-1. **(s6602) Attribute the wide-only hangar bands to the framebuffer stride path.**
  Build one instrumented binary and rerun the three same-phase arms only if
  needed for the new witness. Log, per hangar VI phase, the selected width,
  VI origin, source framebuffer address, row stride, and the copy/flip source
  range; include a positive control from the retail 512-wide arm. Discriminator:
  a source range or row stride that lands on the measured 16:9/21:9 band selects
  H-stride; matching stride with a fixed screen-space scissor selects
  H-viewport/H-RDP; identical source geometry and pixels across arms selects
  H-game. Do not add a cull, skip, or default change until the writer is named.
-1. **(s6601) Audit the parked hangar artifacts under `g3-hangar-artifacts`.**
  Build/run one same-phase capture table for retail 4:3, ASPECT 16:9, and
  ASPECT 21:9 at the hangar origin, joining the framebuffer dumps to the VI
  origin and width. Competing hypotheses are H-viewport (wrong scissor or
  viewport exposes the rim band), H-stride (wide framebuffer row/flip stride
  leaves stale right-edge data), H-rdp (RT64/RDP edge treatment produces the
  holo spikes), and H-game (the submitted hangar geometry itself contains the
  artifact). Discriminator: the artifact's first/last changed pixel bounds
  and command-range attribution in the same phase; width-proportional stale
  bands select H-stride, fixed screen-space clipping selects H-viewport or
  H-rdp, and identical geometry in the retail control selects H-game. Keep
  default retail behavior unchanged and produce an owner-viewable contact
  sheet before any mitigation.
-1. **(s6598) Read the mapped `getTextureTlutEntry` return before the `0x800496A8` store.** The new `tlut_return` witness is persistent but the dd4 run did not finish. Run one bounded dd4 route with `ROGUESQ_HUDPTRWATCH=1` and inspect `[hudptrr] stage=tlut_return` against the known controls. Hypotheses: H-return-wild (the function returns `0x951335B0`), H-between-store (the return is valid but another generated store changes `r4`), H-host-alias (valid guest state is changed by host address conversion), H-stale (the return is an old object). Discriminator: return value equal to `0x951335B0` selects the return writer; a valid return followed by the mapped store selects an intervening generated write; a host-only mismatch selects conversion; retail/dd4-valid returns with divergent lifetime select stale state. Do not add a guard.
-1. **(s6581) True dd4 (DD_UNSAFE=1, bundle) is clean on lvl1/5/10: 300 s holds each, 0 stall, 0 crashlines, log `multiplier 4` (one run per level; the rare dd4 gfx SIGBUS, rate <=~1/9, is not excluded). (s6582 DONE: cap lifted, dd4 allowed without UNSAFE, 150 s lvl1 clean.) Remaining: a valid same-pose dd1-vs-dd4 sheet (log g_rs64_dd_blk per fb dump; s6582 sheet invalid). Old text: lift the dd>3 cap in apply_s6036_dd.py:7 (cap to 4 without DD_UNSAFE) -> regen/rebuild, then dd1-vs-dd4 same-pose contact sheet for the owner. Default stays retail.** (s6583 DONE: valid same-pose dd1 vs dd4 sheet at docs/owner_sheet_s6583.png, [fbdump] now carries dd= tag; dd4 shows only slightly more far terrain at lvl1 pose 3 — extent-bound per s6576; sheet sent to owner for judging.)
- [s6576, do first] lvl1 footprint saturates at the level's own terrain extent by dd6 (post area 4096=64x64; s6575's 'table too small' was mis-framed - tw/th are level dims). Census tw/th/cap per level (1,5,10 + others) via ROGUESQ_DD_LOG; if every level is extent-bound, dd range is done at ~6: bundle far/pool/cap behind the single knob and run 300 s holds on lvl 1,5,10 at dd6 + contact sheet for owner. See NEXT.md.
- [s6567] dd6 px2/px3 with RAMTOP_MB=16 all die with Bus error si_addr=0x38000000x (A/B/C identical): pool size is NOT the px2 limit; the chunk list also still collapses. Next: symbolize the crash pc / backtrace, name the writer of the 0x80000000-offset access (see NEXT.md).

0. **(s6572 SOLVED the px3+spill hud fault; supersedes s6570/s6571 "zeroed/empty record" framing.) ROOT CAUSE = `TO_PTR` in lib/N64ModernRuntime/ultramodern/include/ultramodern/ultra64.h masked guest addresses to 8 MB (`& 0x7FFFFF`, s5240), so host osCreateMesgQueue/osSendMesg/osRecvMesg on a queue above 8 MB (record 0x80954F60 + 0x1D0 = 0x80955130, which exists only with RAMTOP_MB=16 + spill) read/wrote the ALIASED low-RAM copy 0x80155130 while generated guest code (MEM_W, unmasked) saw the real address, still all-zero. Two lines of evidence: (a) ROGUESQ_RECV_TRACE `[createmq] mq=0x80955130 msg=0x80955150 count=66` fired while a 16-byte poller watch on 0x955138..0x955147 saw 0 writes over a whole run (same-arm positive control: the record head 0x954F60 showed writes); (b) mask widened to 0x1FFFFFF -> px3+spill hold `mission_verified_130s`, 0 CRASH, svcrecv now returns real slots (validCount=31) vs 8/8 faults before. 1 clean run so far -> NEXT: 3-run px3/px4 confirm, then re-measure the dd3/dd4 limits. Any other host-side `& 0x7FFFFF` on guest pointers (ultramodern/librecomp, src/main) is the same bug class: audit them.** 
0. **(s6569) px3 NULL = guest heap0 exhaustion** (malloc 0x192CC -> NULL, 5.4 MB live). `ROGUESQ_MALLOC_SPILL=1` (+RAMTOP_MB=16) serves NULLs from 0x80800000-0x80C00000; px1+spill clean, px3+spill gets past the pool but faults NULL+0x14 in hudDisplayUpdateWorker+3332. NEXT: name that NULL's writer (what hud pointer is 0 at px3?). Single-run each.
1. **(s6567 SOLVED the px1 arena-chunk fault: ROOT CAUSE = `rs64_ram_top` (default 0x80800000, set from osMemSize in recomp.cpp:565) is the limit of 442 generated `RS64_RAM_TOP` pointer guards in funcs_3.c plus the RT64 DL-read masks (rt64_render_context.cpp), so every arena chunk at 0x80F… was rejected as a wild pointer. `ROGUESQ_RAMTOP_MB=16` (new, widens only the guard limit, not osMemSize) makes head-prepend +384 at px1 clean (0 crashes, alive 131 s; ASC order and prior 4/4 runs without it fault) -- single-source until repeated.)** NEXT: with RAMTOP_MB=16 retest REINITX=2 at px2 and px3 (H-D2: does a scaled DL-chunk pool stop the px2 chunk collapse?), then fold RAMTOP_MB=16 into the ROGUESQ_DRAW_DISTANCE bundle for dd>=3. (g1c-dd-phase2, top; NEXT.md). Older: s6555 REFUTED traverseSceneGraphRecursive as the runaway. Chunk drain is inside per-node submit work or a failed chunk return (reclaim=0 everywhere; px1 len rises, px2 leaks ~5/frame then collapses).
2. **Lift the 0x80130C4C 2048-cell cap with its pool** once item 1 is fixed;
   qualify on lvl1, then on a level with terrain larger than 64x64 (s6548).
3. **Owner decision: dd>1 bypass cap.** cap120 is pointless; choose cap0
   (cheap, drops ground) or inf (terrain, ~1.7x wall). Sheets
   `docs/owner_sheet_s6546.png` (same-pose), `docs/owner_sheet_s6540_cap.png`
   (not pose-matched).
4. **Name the span-grid saturation writer** (edge loop at 0x80042820/0x800426D8
   `sb trunc(clamp(f0,f12,f10))`, s6521) and fix at the writer to retire the
   bypass workaround; two-arm qualify.
5. **dd4/dd8 gfx-thread SIGBUS (rare).** On recurrence: backtrace, map si_addr
   to a guest address, test H-16MB (keep gfx-read data below 0x81000000).
6. **dd8 hangar scanline garbage** (s6468, unresolved, single-source).
7. **G3c owner judgement**: edge sheet `docs/owner_sheet_s6449_edge.png`,
   `docs/owner_sheet_s6439.png`; ask whether `ROGUESQ_CULL_SPIKE` should be
   default-on.
8. **G1d owner sheets: aspect `docs/owner_sheet_s6609_aspect.png`, radar
   `docs/owner_sheet_s6610_radar.png`.** The level-select tear closed in
   s6631. Do not recapture the radar.
9. **G1 coverage (c)+(d)**: framebuffer terrain/craft/HUD evidence and a
   forced-hit objective response for every level 0..18.
10. **Ladder (ITERATION.md 3c)**: after the above, G3 render fidelity
    (hangar artifacts, in-flight diffs vs retail frames). G4 and aim/steer stay
    parked; G2, G5 closed.

## Evidence index

Recent session findings are in `PORTING-STATE.md` sessions 6378–6551. Durable
background, closed threads, and the archived backlogs are in
`docs/PROJECT-OVERVIEW.md`. Queued-soak verdicts are in
`scratch/agent/SOAK-RESULTS.md`.

The s6596-s6597 retries were checkpoint close-outs only: they did not rerun the
s6595 experiment or add a conclusion. The s6599 retry was also a checkpoint
close-out: the s6598 retail arm completed, while the dd4 wrapper produced no
witness-phase summary before termination. The saved s6595/s6598 artifacts
remain the active evidence for the HUD SIGBUS mapping work.

## Update s6568
- s6567 conclusion 'pool size not px2 limit' SUPERSEDED: recipe lacked ROGUESQ_DLPOOLX=1. px2 with DLPOOLX=1 DLPOOLX_MB=4 DLPOOLX_AT=3000 RAMTOP_MB=16 holds clean (1/1 90s; control 3/3 crash). px3 5/5 crashes in allocAndInitDoublyLinkedNodePool12 (NULL+2): next binding limit is that node-pool allocator, not the DL arena.

- s6571 (SUPERSEDED by s6572: queue was never zero-written, the host aliased it to 0x80155130 via the 8 MB TO_PTR mask).  Tool note s6572: ROGUESQ_LOG_FL_ZERO_WATCH=1 ROGUESQ_FL_ZERO_ADDR=<phys hex, now up to 32 MB> ROGUESQ_FL_ZERO_ALWAYS=1 is a no-lldb 16-byte write watch with function attribution (lldb launch hangs in dyld under this harness).

- s6573: px3+spill dd6 confirmed 4/4 clean after TO_PTR mask widening (s6572); px3 fault CLOSED. Next: px4/dd=8 (see NEXT.md).
- s6574: px4/dd8 (2/2) lvl1 130 s clean with spill recipe. The px5 "dd12" run was really dd8 (s6575: clamp [0.25,8] under DD_UNSAFE, apply_s6036_dd.py:7; run.log prints multiplier 8) - no dd12 evidence exists.

- s6579/6580: true dd4 (DD_UNSAFE=1) lvl5 300 s clean; lvl10 s6579 failure was MISSION_RE false-nomission (needs MISSION_RE='6A2900|644D00'); s6580 lvl10 (MISSION_RE='6A2900|644D00') and lvl1 true-dd4 300 s holds PASS (s6581).

- s6589: lvl7 dd4 CAPX=2 fault: window (x0=0,w=64,z0=31,d=65) is inside the 93x96 grid, so not an overrun; desc 0x80136DC0 words +0/+4 are NULL. Next: is desc+4 ever filled in retail on lvl7 (NEXT.md).
- s6591: lvl7 dd4 desc+0/+4 NULL root-caused: streamTerrainGridCellsByDistance slot-clear (pc 80043020) indexes a 64x64-word slot array at 0x80132DC0 that ends at the descriptor 0x80136DC0; window d=65 rows overran it. Fixed by capping the dd clamp window at 64x64 (apply_s6037_ddclamp.py). Supersedes s6586-s6590 (overrun/unbuilt/load-race hypotheses). New open: phase-7 SIGBUS in hudDisplayUpdateWorker (wild ptr 0x951335B0) on lvl7 dd4 after the fix. ROGUESQ_DESCWATCH=1 is the store-watch for 0x80136DC0..+0x40.
- s6593: one-setting removal bisect: retail and the full dd4 bundle reached the route cleanly, while removing any one of SPILL_HI, RAMTOP_MB=20, DLPOOLX_MB=8, DD_CAPX=2, or DD_UNSAFE reproduced the same phase-7 SIGBUS at hudDisplayUpdateWorker+5084 with guest pointer 0x951335B0 (5/5 attempts per arm; all arms reached mission before dying). This rules out H-retail and any single bundle setting as sufficient; H-dd-interaction remains. No guard is justified: the writer and legitimacy of 0x951335B0 are still unknown.
