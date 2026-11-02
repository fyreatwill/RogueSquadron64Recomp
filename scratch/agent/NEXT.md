# NEXT: G3 render match vs retail angrylion, mission 3 flight (first mission past the s6744-s6748 matched pair)
HYPOTHESIS-ID: g3-render-match-m3

G1e closed s6776 (lvl5 FPS60 ~60 fps at dd1-dd4). G3 sim sweep 3-19 closed (s6760-s6773); render vs retail is matched
only for missions 1-2 (s6744-s6748). Mission 3 is the next biome.
Hypotheses (one matched pair of arms splits them):
- H-match: retail and port flight frames match (d within the same-run median band, as lvl1/lvl2: d 6.5-15 vs 36-47).
- H-render-diff: specific tiles/objects differ (missing geometry, texture, combiner or fog difference) -> localise with the
  worst pairs and the per-VI census (ROGUESQ_G3_CENSUS), then root-cause.
- H-pose: high d only from pose drift (unsteered craft) -> mean RGB within 1-2/channel, same scene (as s6748 late pairs).
Work unit (recipe = PORTING-STATE s6748):
1. Oracle save: `python3 tools/g3_eep_patch.py scratch/s6748/lvl2.eep scratch/s6777/lvl3.eep --set 0x31=2`.
2. Retail recon (mupen oracle with that save swapped in and restored), then retail 512-wide flight dumps ~40 s.
3. Port arm with the same save, window captures through flight (Display-P3 -> sRGB, s6740).
4. `tools/g3_oracle_match.py --w 512 --bases 690000,620000 --h 446 --dec shift` with a same-run median control.
Discriminating outcome: per-frame d vs the same-run median, plus eyeballed worst pairs.
