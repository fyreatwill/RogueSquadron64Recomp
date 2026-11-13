# NEXT (s7250): close the WIDEWIN stack's 60/s claim with a same-run slow-host control
HYPOTHESIS-ID: widewin-heavy-window-cost
State (s7249): the s7231 flat 30 ran on BATTERY at 10% (pmset log + constant 1.40x sd_cpu). On AC (s7248): off 10.06 / ww 13.16 / stack 9.59 ms, all 60.
1. If SOAK-RESULTS has s7248_fixed_fps_b: score scratch/s7248r/log_{offb,wwb,stackb}.txt with tools/s7230_headroom.py + tools/s7229_flat30_cost.py
   (2nd AC run; check arms.log pwr=AC).
2. Slow-host control, same recipe, one run: ww and stack with a controlled 1.4x CPU slow-down. Candidates: `taskpolicy -c utility` / `-b` on the game
   (moves threads toward E-cores; check sd_cpu ratio ~1.4, not 3x), or an ALLOW_BATT=1 arm when the owner unplugs. Positive control: ww goes flat 30
   (reproduces s7231). Outcomes: ww 30 + stack 60 -> tell the owner the stack keeps 60 even on battery, ask about folding it into the auto bundle;
   both 30 -> stack only helps on AC, next lever R=40 rescored with the hole scorer; ww stays 60 -> the slow-down is not 1.4x, recalibrate.
3. Recheck s7230's "L4 heavy window flat 30" (same afternoon, battery): grep its arms.log times against the pmset log before citing it.
