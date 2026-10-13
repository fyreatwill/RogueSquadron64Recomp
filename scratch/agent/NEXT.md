# Bisect the spTaskSchedulerThread+9632 startup crash: DROP=1 vs DROP unset

HYPOTHESIS-ID: factor5-overlay-0x2c-splice

s4789: DROP=1 run crashed at startup again (3rd time at this PC, load 7-13). Work unit: `uptime`; run `zsh scratch/agent/s4788_drop1.sh` as-is, then again with `ROGUESQ_OVL2C_DROP=1` removed from the env line. Control: the no-DROP arm must reach `vi_width=512` (s4787 did).
Outcomes: crash only with DROP => the flag causes it (guard/fix); crash in both => startup race/load, need a human to quiet the host; neither crashes => earlier crashes were load, proceed to the per-phase `res=0x2C` count after `vi_width=512`.
