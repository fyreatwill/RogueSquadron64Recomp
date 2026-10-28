# NEXT: valid same-pose dd1 vs dd4 owner contact sheet
HYPOTHESIS-ID: g1c-dd-phase2
State (s6582): dd cap lifted (dd4 w/o UNSAFE verified, 150 s clean). docs/owner_sheet_s6582.png is invalid (assumed frame<->toggle mapping, poses differ).
Work unit: emit g_rs64_dd_blk in the fb-dump filename/log (extern volatile int, set in apply_s6036_dd) so each dump is tagged dd1/dd4; rerun scratch/agent/s6582_run.sh (pose lock + toggle) and pair adjacent dumps of opposite tag with minimal pose diff (use owner_sheet_s6546.py style). Positive control: tags must alternate in the dump list.
Outcome: pair with ship/HUD identical, dd4 showing more terrain => send sheet; else widen pose lock.
