# NEXT: inspect post-fix widescreen title/hangar captures
HYPOTHESIS-ID: g1d-widescreen

s6170 selected H-menu-fb-fixed for the pre-mission crash: the width-aware
partition hook made the 16:9/12 MB arm reach mission and hold clean. The next
single work unit is a bounded render check of the same opt-in route, using the
paired framebuffer dumps already produced by the valid s6169b run and one
fresh paired run only if the existing phase coverage is insufficient.

Competing hypotheses and discriminator:

- H-menu-pixels-fixed: the title and hangar framebuffer dumps contain coherent
  16:9 content, with the wide RDP/VI width and origin joins matching the dump;
  the allocation fix is sufficient.
- H-menu-layout: wide title/hangar dumps are still horizontally garbage or
  cropped while route and allocation joins are sane; the next writer is a
  menu-specific viewport/scissor/HUD policy.
- H-wide-present: the guest dump is coherent but the displayed/presented wide
  image is wrong; compare VI-origin bytes and the on-screen capture before
  changing game code.

Discriminator: compare same-phase control/wide framebuffer dumps at title and
hangar, then correlate each with `[fballoc]`, `[rdp-route]`, and `[phase]`
rows. A valid result requires the control and wide route markers, the wide
`512x340 wv=796` allocation positive control, and no crash/30-second VI stall.
Do not add a mitigation or alter the retail default.

Useful bounded commands:

    find scratch/agent/m6/g1_lvl1_s6169b_ctl/fbd scratch/agent/m6/g1_lvl1_s6169b_wide/fbd -type f | sort
    grep -a -E '^\[phase\]|^\[rdp-route\].*phase=5|^\[fbw\] pfm a2=512 a3=340|^\[CRASH\]|^\[ABORT\]' scratch/agent/m6/g1_lvl1_s6169b_{ctl,wide}/run.log | tail -120

If the existing dumps do not contain both title and hangar, run the paired
route with `ROGUESQ_OSMEM_MB=12 ROGUESQ_ASPECT=16:9
ROGUESQ_FB_DUMP_VI=1 ROGUESQ_LOG_FB_ALLOC=1 ROGUESQ_LOG_RDP_ROUTE=1`, actual
mission origin `690400`/`A52438`, and a 180-second hold.
