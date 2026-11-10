# NEXT: fold the s7062 L10/L15 21:9 dd6 auto holds -> close the 21:9 dd6 level survey
HYPOTHESIS-ID: dd6-219-levelK-survey
Context s7062: 9:8192 is now in the 21:9 auto bundle (L9 60.00 fps). Every level except L10 (cloud, crash check only) and L15 has a 21:9 dd6 survey row.
Soaks queued: scratch/agent/soak_queue/s7062_219auto_L10.sh, _L15.sh (the loop runs them; verdict lines in SOAK-RESULTS.md).
If they have not run yet: run one directly (screen unlocked: /usr/sbin/ioreg -n Root -d1 | grep -c '"CGSSessionScreenIsLocked"=Yes' must print 0):
  env WD=90 zsh scratch/s7058/run_hold.zsh L15g 15 auto 130 230; pkill -9 -x RogueSquadron64Recomp
Score: python3 tools/s7060_survey_table.py --suf g --levels 10,15   (or --levels 10-15 if the list form is not accepted)
Hypotheses:
 H-ok: both alive, 0 crash, L15 >= 59.5 fps excl. gaps -> 21:9 dd6 survey CLOSED; write the 19-level table summary into CURRENT-TRUTH, OWNER-OPT-INS one line.
 H-laggard: L15 < 59.5 with RSP-bound slow frames -> same-run cap toggle like s7061 (scratch/s7061/run_caplevel.zsh with level 15).
 H-crash: any crash (L15 had a 21:9 crash fixed by s6992 PTRMASK) -> G4 side-effect rule: capture a backtrace and root-cause first.
After closing: the ladder rungs left are owner-judgement items; take the next non-owner item in CURRENT-TRUTH Next steps (e.g. the rare dd4/dd8 gfx SIGBUS only if a soak hits it).
