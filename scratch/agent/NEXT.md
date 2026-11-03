# NEXT: fold s6817 scrape-fix seeds 2/3, then audit other dt-scaled deflection quanta
HYPOTHESIS-ID: g3-fps60-scrape

State (s6817): FPS60 scrape fix landed (tools/fixup_fps60_scrape.py; case multiplies in collision resolver 0x800FEF10 use
max(dt,1/30) under ROGUESQ_FPS60; ROGUESQ_FPS60_SCRAPE=0 restores). Seed 1: contacts 2 (30 Hz) / 4 (fix) / 7 (off); exit
pitch exact; hit50/s 0.107/0.094/0.057; death 81.3/90.6/none. Residual: extra +20 deg heading contact at 15.6 s at FPS60.
Step 1: read SOAK-RESULTS for s6817_scrape_b60fix_s2/s3 (traces scratch/s6817/b60fix_s{2,3}.rand.txt). Score:
  python3 tools/g3_scrape_contacts.py 60 scratch/s6817/b60fix_s2.rand.txt scratch/s6817/b60fix_s3.rand.txt
  python3 tools/g3_death_time.py 60 scratch/s6817/b60fix_s2.rand.txt scratch/s6817/b60fix_s3.rand.txt
  Compare to s6816 batch1 a30_s2/s3 (30 Hz) and b60_s2/s3 (old FPS60). If soaks did not run: env ARMS=b60fix SEED=2 zsh scratch/s6817/arms.sh
Discriminating outcomes:
  - seeds 2/3 contacts drop toward 2 and hit50/s / death move toward 30 Hz -> fix confirmed (two lines); close scrape thread.
  - no move in seeds 2/3 -> seed 1 was path luck; reopen (the heading case / damage-per-tick may need the same treatment).
Step 2 (if confirmed): idiom audit - other per-event steps scaled by the dt arg (mul.s by dt feeding rotate/clamp/bounce in
  mission overlay collision code: npc collision resolvers that call the same 0x8001CC3C/0x8001CD6C rotate helpers). Enumerate
  callers of 0x8001CC3C/0x8001CD6C whose angle argument is dt*const inside a loop/contact branch; classify each.
