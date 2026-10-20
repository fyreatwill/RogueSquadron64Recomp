# NEXT (s5686): fold s5685 altitude-hold soaks
Queued: s5685_ctrl, s5685_hold_a, s5685_hold_b (schedule a/sl/a/sr, no su/sd; hold arms ROGUESQ_ALT_HOLD=2.0).
Control = "[althold] target" and "n=.. acted=.." lines in hold logs (must show acted>0), absent in ctrl.
Hypotheses: H1 altitude hold keeps alive_at_end/no mission_cycles vs ctrl; H2 no difference (crash not altitude); H3 y hold fails (acted=0 / sign wrong -> err grows).
Discriminator: err trajectory + alive_at_end/mission_cycles/vi_stalls, hold vs ctrl in SOAK-RESULTS logs.
HYPOTHESIS-ID: g1-mission-progression
