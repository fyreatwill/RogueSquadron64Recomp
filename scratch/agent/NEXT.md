# NEXT: G3 render fidelity -- retail hangar vs port hangar (angrylion oracle frames vs window captures)
HYPOTHESIS-ID: g3-hangar-oracle-diff

s6738-s6740: boot cinematic, attract Tatooine flight and the cinematic replay are H-match vs retail. Window captures are
Display-P3 tagged; tools/g3_oracle_match.py converts them to sRGB by default since s6740.
CURRENT-TRUTH lists parked native hangar artifacts. Hypotheses per artifact: H-match (retail shows it too), H-rt64
(port draws differently from angrylion on the same RDP stream), H-geom (missing/extra objects), H-pos (camera/state differs
because the routes reach the hangar at different times -> compare only frames with the same hangar camera pose).
Steps:
1. Retail: rs64_oracle with angrylion (copy scratch/s6740/retail_hoth.sh), --press Start every 5 s from 6..56 s per
   tools/oracle/README "Reaching the hangar" (hangar at ~38 s, 512 wide at 0x6ab400/0x6ab800; with angrylion check the
   width/origin trace first - the README timeline was measured with Rice). fb-dump on the first 512 VI + delays 1..20 s.
   Stop pressing by ~45 s so it stays in the hangar.
2. Port: hangar route window captures (port_win.sh style, ROGUESQ hangar route recipe from CURRENT-TRUTH run recipes),
   measure the 512 picture box first.
3. g3_oracle_match.py <oracle.log> <portdir> <out> --w 512 --bases <from origins> --h <rows> --win y0,y1 --winx x0,x1
   Control: a static hangar frame must match at d < ~2 or the crop/decoder is wrong.
Open small residual (not this unit): uniform 2.5% retail>port brightness in the 512 Tatooine flight only.
