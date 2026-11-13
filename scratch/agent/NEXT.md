# NEXT (s7261): fold s7260_dd4_auto_stack — does the WIDEWIN stack (now auto at any dd>1 + WIDEWIN) engage in mission at dd4?
HYPOTHESIS-ID: widewin-heavy-window-cost
State (s7260): L12 21:9 dd6 limit lifted by the stack (H-ww, control PASS, single run). main.cpp rs64_g1c_apply_dd_policy now sets the stack for
any dd>1 with ROGUESQ_DD_WIDEWIN on (startup check passed: dd4ww prints "[s7258] dd4 ...", STACK=0 and no-WIDEWIN print none).
Queue: scratch/agent/soak_queue/s7260_dd4_auto_stack.sh (SOAK_NEEDS_IDLE=180; L4 21:9 dd4 WIDEWIN; arms auto / off=STACK=0 / offd=off+DUTY1.4; results scratch/s7260q).
1. Fold: control offd must show clearly more <55/s seconds than off (else re-run).
   Engaged: auto has "[s7258] dd4" and "auto merged" > 0; win77-97 ~9.6-10 ms (s7248 fixed-on 9.6) vs off ~12.6-13.2 -> stack auto at dd4 confirmed;
   add the timing to OWNER-OPT-INS line 63 ("A timing check ... is queued" -> result).
   Not engaged (merged 0 or auto ~= off): the merge/R latch is read before rs64_g1c_apply_dd_policy at dd<6 -> check upstream_compat S7239Init/S7233 latch order.
2. If the soak did not run (owner active): G-ladder next rung after G1c/G1d stack work: check CURRENT-TRUTH Next steps top item (do not wait).
