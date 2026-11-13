# NEXT (s7251): fold the slow-host control (s7250_slowhost) and the s7248 2nd AC run
HYPOTHESIS-ID: widewin-heavy-window-cost
State (s7250): battery = Low Power Mode (powermode 1), x1.40 per task. tools/s7250_duty + harness token DUTY=1.4 stand in for it (1.435x on a spin).
1. If SOAK-RESULTS has s7250_slowhost: read scratch/s7250/arms.log (pwr=AC, duty= lines) and duty_wwd.txt/duty_stackd.txt (achieved factor ~1.4),
   then score log_{ww,wwd,stack,stackd}.txt with tools/s7230_headroom.py + tools/s7229_flat30_cost.py.
   - Control: wwd sd_cpu per task ~1.4x ww AND flat 30 in t=77-97. If sd_cpu is 1.4x but wwd holds 60, the burst stall is not like a clock cap:
     rerun at DUTY_PERIOD=12000 or factor 1.6, or ask the owner for one battery arm (ALLOW_BATT=1).
   - Control passes: stackd 60 -> tell the owner the stack keeps 60 on battery and ask about folding it into the auto bundle; stackd 30 -> the stack only
     helps on AC, next lever R=40 rescored with tools/s7247_tog_pop.py.
2. If s7248_fixed_fps_b ran: score scratch/s7248r/log_{offb,wwb,stackb}.txt (the 2nd AC run).
3. If neither ran (owner active): offline, recheck s7230's "L4 heavy window flat 30" times against the pmset battery log (s7230 arms.log) and correct CURRENT-TRUTH.
