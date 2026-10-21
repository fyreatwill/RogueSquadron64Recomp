# NEXT: fold s5742_hpwatch_god — does hp->0 / lives decrement fire under the death-arm env, and which PC writes it?
Read scratch/agent/m6/s5742_hpwatch_god/{summary,lldb_att*.log}; tally `frame #0` names per watchpoint (grep 'stop reason = watchpoint N').
Control: wp1 (0x3470) hit + 'trap-at-swap' in run.log. Positive: wp3 (lives) fires on a death.
Hypotheses: (H1) GODMODE3 thread / autopilot hold causes the kill (writer is main.cpp thread or a game routine reacting to its writes); (H2) idle craft in plain route never reaches terrain; (H3) port defect needing held stick.
Discriminator: top frame at the hp->0 write. If no death under lldb (timing change), run without lldb ROGUESQ_GODMODE3=1 variants / compare.
HYPOTHESIS-ID: g1-gameover-cause
