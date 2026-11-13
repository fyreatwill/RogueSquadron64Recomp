# NEXT (s7258): fold s7257_dd6r_stack
HYPOTHESIS-ID: widewin-heavy-window-cost
State (s7257): on AC dd6r holds 60 in L4 t=77-97 (14.06 ms) but has 14 late dip seconds t=142-238 (min 34/s) that n4 lacks; stack under DUTY=1.4 = 44.5/s.
Queue: s7257_dd6r_stack (SOAK_NEEDS_IDLE=180; arms dd6r, dd6rs, dd6rsd, dd6rd). Check loop.log 'soak phase:' and clk= on arms.log first.
1. Control: dd6rd flat 30 in t=77-97. If it fails, the run says nothing.
2. Hypotheses for the late dips: H-ww (WIDEWIN cost: dd6rs removes them, window ms ~-3.5) vs H-radius (dd6 terrain/radius cost: dips stay in dd6rs)
   vs H-noise (dd6r repeat lacks them: one-run artefact). Score: python3 tools/s7257_dip_runs.py scratch/s7257/log_*.txt (beyond-route count).
3. H-ww -> propose stack riding with the dd6 auto bundle (owner opt-in note); H-radius -> next arm OFFMAPCULL K=0.6 at dd6r; H-noise -> close.
4. If it did not run: take the next offline G-ladder item (not another harness tweak or re-fold).
