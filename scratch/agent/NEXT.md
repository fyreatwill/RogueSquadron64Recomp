# NEXT: H-D2 retest with guards widened (px2 / px3, scaled DL-chunk pool)
HYPOTHESIS-ID: g1c-dd-phase2
Fact (s6567): ROGUESQ_RAMTOP_MB=16 makes arena DL chunks >=0x80800000 valid to the 442 generated guards; head-prepend +384 at px1 is clean.
Arms (build once, already built; run sequentially, one game at a time), lvl1 pinned via `zsh scratch/agent/s6553_run.sh 6 <px> "<env>" <arm>`:
 A: px2, REINITX=2 DLPOOLX_MB=4 CHUNKCUT=1 RAMTOP_MB=16 ; B: same, REINITX unset (control, shows the s6062-style px2 chunk collapse) ; C: px3 with REINITX=3.
Outcomes: A survives and chunk-pool min len stays >0 while B collapses -> H-D2 confirmed (pool size was the px2 limit); A collapses like B -> pool size not binding, look at per-node submit leak; A faults -> another guard/alias (grep rs64_ram_top, 0x7FFFFF masks in rt64 and ucode) .
Then bundle RAMTOP_MB=16 into ROGUESQ_DRAW_DISTANCE>=3 handling.
