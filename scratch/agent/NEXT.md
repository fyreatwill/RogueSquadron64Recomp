# NEXT: L9 21:9 dd6 dense-burst dip: does a smaller cell cap (8192) hold 60 fps in the burst? then a level-scoped cap
HYPOTHESIS-ID: dd6-219-levelK-survey
Context s7060: L9 dips to ~55 fps in a 30-40 s combat burst (rsp 17-22 ms). K=0.5 does not help (same run). Same-run CAP 4096/10240/4096: burst window
60.0/58.7/60.0 fps -> the dd6 window's extra cells cost it (H-dd-window). Single run, mild burst.
First: python3 tools/s7060_survey_table.py  (fold s7058_219auto_L17/L18 if SOAK-RESULTS shows them; LAGGARD rows need the same treatment).
Run (screen unlocked check: /usr/sbin/ioreg -n Root -d1 | grep -c '"CGSSessionScreenIsLocked"=Yes' must print 0):
  sed 's/CAP=4096,10240,4096/CAP=8192,10240,8192/; s#scratch/s7060#scratch/s7061#' scratch/s7060/run_cap.zsh > scratch/s7061/run_cap.zsh (mkdir first)
  env WD=90 zsh scratch/s7061/run_cap.zsh L9c8 9 tog ; pkill -9 -x RogueSquadron64Recomp
Score: find the burst: python3 tools/g5e_cost_by_parity.py --phases 1 --skip-s 130 --gaps 25 <tl> <log> | grep 't=' (bin by 30 s), then
  --phases 3 --skip-s <a> --until-s <b> on the burst window, plus --shift-ms 333 as control. Positive control: rsp p1-p0 > 0 over the whole run.
Hypotheses:
 H-8192-holds: 8192 phases ~60 fps / P(>=2VI) ~0 in the burst while 10240 dips -> implement a level-scoped cap (ROGUESQ_DD_WIDEWIN_CAPLEVEL=9:8192,
   auto at 21:9 like KLEVEL in src/main/main.cpp s7037/s7056 block), then pose-qualify the edge (scratch/s7057/run.zsh pattern).
 H-8192-dips: 8192 dips too -> try 6144 the same way (s7012: edge gain already in by 6144); if even that dips, the burst is game-side cost (record, close).
 H-noburst: no burst in the run (needs heavy combat) -> repeat once; if still none, record and keep the s7060 result as single-source.
Any crash: side-effect failure (G4 rule) -> capture and root-cause first.
