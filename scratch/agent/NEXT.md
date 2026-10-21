# NEXT: forced-death slot-watch (s5762 had no death, so kill source still unobserved)
Rerun s5762_slotwatch_lvsel recipe with an env that provably kills the player (find the existing damage/death-forcing env in the s5743_hpwatch_lvsel / s5760 recipes; s5760 used GODMODE3=2+HOLD_MS=1800 on the plain route which failed). Control: wp4 must stop with a lives DECREMENT (run.log `lives--` or value drop), not only init writers. Then bt of wp2 (0x137F24) writes setting 0x8/0x10 before it.
Outcomes: collision/damage PC = H1; objective-timer script = H2; stale value/stubbed subsystem = H3.
HYPOTHESIS-ID: g1-nonhealth-fail
