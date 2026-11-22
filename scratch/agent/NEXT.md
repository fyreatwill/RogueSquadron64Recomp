# NEXT (s7833)
HYPOTHESIS-ID: g3-flight-pitch-rate
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks this unit. G6c and all G5 items wait on the owner only.
Why: s7832 found the port's lvl2 (Barkhesh) flight camera pitched ~0.1 deg vs retail under BOTH port schedules, retail ~0 across two
schedules (PORTING-STATE s7832). Sub-pixel, not owner-visible, so this thread gets at most 2 iterations, then close single-source.
Hypotheses:
 - H-rate: camera/craft integrate per game frame; the port renders ~20% more game frames than emulated retail over the same motion
   (s7821 rate split; s7832 flight R1 3277->4071 = 794 frames vs port 4139->5096 = 957). Retail at a game-frame rate nearer the
   port's would pick up the port's pose.
 - H-cpu-state: a port-side state difference independent of frame rate (retail pose invariant to its frame rate).
Discriminator (2 retail oracle runs, one at a time, no port run needed; port captures exist):
  `env CPO=1 RSECS=175 EEP=scratch/s7832/lvl.eep PP=19.5:start,31.5:start,43.5:start,67.5:start,79.5:start,91.5:start zsh tools/s7828_retail_cpo.sh scratch/s7833/cpo1`
  and the same with CPO=3 -> scratch/s7833/cpo3. Timeline with `python3 scratch/s7829/tl.py <bin>`; flight starts at the tri~334 tx~11
  band; find the static-sky bands matching s7832 band a (R1 3408:3475, tri~880) and band b (R1 3539:3594, tri~789).
  Per arm report: (1) frames from flight onset to the tri~1233 band (game frame rate; R1 794, port 957);
  (2) tools/s7827_tri_yshift_census.py vs R1 (--p-retail) and vs scratch/s7832/port.bin.zst, --controls --pose on bands a/b;
  (3) tools/s7826_rect_path_offset.py vs R1 (--p-retail) and vs port: the big-reticle '+0,+0.5' class count.
  Positive control already in hand: port vs R1 = +0.0023 rad / +0.5 on 539 frames; R1 vs R2 = ~0 / 0.00 px (s7832).
Outcomes: CPO changes the frame count AND the arm nearest the port's frame count reads pitched vs R1 (reticle one-signed) and ~0 vs
port -> H-rate (port pose = a legitimate frame-rate consequence; record and close). Frame count changes but pose stays ~0 vs R1 in
both arms -> H-rate refuted, H-cpu-state: one more unit, a per-frame guest camera pitch float dump in both arms (find the camera
struct from setupCameraMatrices). CPO does not change the frame count -> the lever is void; close single-source with s7832 data.
