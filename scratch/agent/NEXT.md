# NEXT: close the region-box texrect question (R78E080 moving marker), then G1d awaits owner; then ladder G3
HYPOTHESIS-ID: g1d-region-shift-scope

State (s6854): ROGUESQ_G1D_REGION_ZGATE + CFLIP (both default on): lvl17 21:9 only the disc shifts plus R78E080
(51x30 IA texrect, a world-anchored target marker moving through the box; 8-14 rects per 200 s shifted 256 px = a jump).

Unit: does ANY legitimate radar content reach the region gate as a texrect? Evidence so far: lvl1 16:9 none (s6853);
lvl17 only R78E080 (s6854); lvl5 R793B80 7 and lvl9 R79B070/R79B270 1-13 (s6852 soaks, unexamined).
- One lvl9 21:9 run, scratch/s6854/abd.sh 9 with KEEPBIN=1 SHIFT=0 (lvl9 control fires), then
  python3 tools/g1d_zoffobj.py <bin> --disc 7A37B0 --rule cflip  (and --only 79B070,79B270 for the per-VI trace).
Hypotheses:
- H-blip: R79B270-class are radar blips (fixed relative to the disc, small, drawn adjacent to disc tris) -> keep texrect
  shifting but exclude moving markers (e.g. require ul AND lr in the box).
- H-none: every in-box texrect is world-anchored (moves with the world like R78E080) -> stop shifting texrects in the
  region scan (env knob, default on), re-run lvl17 A/B counters.
Discriminator: per-VI centre of R79B270 relative to the disc centre (constant offset/small radius = blip) vs drifting
across the box and drawn elsewhere (marker).
Budget: 1 iteration. Then G1d awaits owner judgement; next ladder rung G3 (in-flight frame diffs vs retail).
