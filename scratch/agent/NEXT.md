# NEXT: G3 render fidelity -- second biome (level 2) vs retail angrylion
HYPOTHESIS-ID: g3-second-biome-oracle-diff

s6747: lvl1 impacts H-match by population (tools/g3_effect_count.py --class orange --mask 390,0,512,200 --mask
220,260,300,300); bolts H-match (s6746). lvl1 is now covered for intro, crawl, flight, fire, impacts. Next a different
biome so terrain textures, fog/haze colour, sky and enemy types are tested on a second level.
Hypotheses: H-match (d within same-run 4-8 band, monotonic); H-biome-tex (a texture/palette/combiner used only on that
level differs: localized high-d region in otherwise matched frames); H-fog (haze colour/distance differs: low-frequency
whole-frame bias rising with depth); H-desync (no monotonic match: route or level differs -> fix the harness first).
Steps (one game run at a time):
1. Check what the oracle EEPROM unlocks (scratch/s6746/oracle.eep is the retail save): run retail with --press dright
   before the hangar Start (scratch/s6747/retail_flight.sh, PRESS=...) and dump the level-select frames to see the
   selected level name. If only lvl1 is unlocked, look for the save's level-unlock byte (ROGUESQ_FORCE_UNLOCK in
   src/main writes it on the port side) and patch a copy of the .eep so BOTH arms use the same unlocked save.
2. Retail: 80 x 512 dumps at flight +2..+41.5 s, no input. Port: tools/g3_port_capture.sh with SAVE_FROM=<patched eep>,
   AP with "right" at the same point and the "42.5:w640"-style phase gate (s6747 autopilot) before the crawl-skip Start
   (gate width/time must be re-read from the new run's [phase] lines).
3. g3_oracle_match.py --dec shift (s6745 geometry) + --worst 6; then a B/Z fire arm and g3_effect_count.py bolt+orange.
Owner save must be restored and cmp-verified after every port run (g3_port_capture.sh does it).
