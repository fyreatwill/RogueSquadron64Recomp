# NEXT: G3 render fidelity -- the second attract demo (Hoth) vs retail, plus the s6739 green offset
HYPOTHESIS-ID: g3-hoth-attract-diff

s6739: the Tatooine attract flight is H-match (two port runs, d 4.6-5.5, monotonic). The port's attract then shows a
cockpit segment and a Hoth demo (port ~118-135 s; frames looked very white/overexposed, and one frame was flat grey).
Retail has never been compared there. Hypotheses: H-match (Hoth snow is genuinely near-white in retail too; d < ~6);
H-shade (port too bright/white: fog/combiner/shade difference, smooth whole-frame offset); H-geom (missing/extra objects,
clustered hot tiles); H-grey (the flat grey port frame is a missing-draw frame retail lacks).
Also: retail G +3.6..+3.9/255 over port on all 12 Tatooine best pairs. Split it by region (sky rows vs sand vs HUD) offline
on scratch/s6739/match2|match3 pairs: uniform across regions -> VI/output-stage (H-vi); sky-only or sand-only -> combiner/fog
(H-shade); HUD-only -> 2D path.
Steps:
1. Retail: copy scratch/s6739/retail_attract.sh, SECS=230, fb-dump arms on the FIRST 512 VI (Tatooine, t=101.5 s), so use
   delays 40..118 s step ~0.85 (92 dumps) to cover cockpit + Hoth (port/retail demo rate ratio ~1.6, Hoth expected retail
   ~150-200 s). Check the width trace: if Hoth uses another width/base, read origins from [vi] lines.
2. Port: scratch/s6739/attract2/attract3 captures already cover the Hoth demo (115-140 s) -- no new port run needed
   unless the crop differs (measure the picture box on a Hoth frame; 512 box was x 85-1191, y 60-1024).
3. python3 tools/g3_oracle_match.py <oracle.log> scratch/s6739/attract3 <out> --w 512 --bases <bases> --h 446
   --win 60,1024 --winx 85,1191 ; view pairs; per-channel means.
Control: Tatooine pairs from the same retail run must re-match at d~5 or the run/crop is broken.
