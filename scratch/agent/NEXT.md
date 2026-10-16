# Next work unit: fold s5043 poison on/off (GUARD2 restored) verdicts; then caller attribution of rs_free ptrs with hdr size 0x10
HYPOTHESIS-ID: m3-idiom-class-audit
s5042 arms stalled (nohangar) because the recipe dropped GUARD2 (or added FREE_CENSUS) vs the working s5037 recipe; see PORTING-STATE s5043.
Queued: soak_queue/s5043_poison_off_g2.sh, s5043_poison_on_g2.sh (results in SOAK-RESULTS.md and soak_results/s5043_*/keys1.log).
Outcomes: off_g2 reaches 0x6AB400 + mission_onset => GUARD2 was the route breaker; then compare on_g2: crashes/verify_bad/divergence vs off => H-raf supported, none => refuted on route.
off_g2 nohangar => FREE_CENSUS perturbs the route; rerun both without FREE_CENSUS (poison alone).
Then step 3: caller attribution (guest ra) of rs_free ptrs with header size 0x10 (0x80787810, 0x8075A010); the poison hook saw ra=0, use last-guest-pc or the s5041 ra.
