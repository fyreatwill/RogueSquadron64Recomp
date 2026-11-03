# NEXT: G3 in-flight frame match vs retail angrylion on lvl3 (third biome, not yet matched)
HYPOTHESIS-ID: g3-lvl3-flight-match

State (s6809): g3-preempt-audit CLOSED (title + hangar-entry + mission-load AI gaps fixed via rs64_preempt_point).
Fold the s6809_preempt2_lvl1_fps60 soak verdict first (expect qzero only at boot in scratch/s6809/soak_lvl1_ai.txt via
tools/g2b_ai_scan.py; a post-boot qzero = another OS-call-free stretch, name it with g3_title_gap.py + `sample`).
Matched so far (CURRENT-TRUTH G3 bullet): lvl1 flight/HUD/bolts, lvl2 flight/bolts, lvl9 HUD (cap fix), menus.
Hypotheses: H-match (lvl3 flight frames d within same-run match band, like lvl1/2); H-diff (a lvl3-specific material/
effect/geometry differs: name it with g3_rdp_frame_match.py on the RDP stream); H-pose (only drift from the unsteered craft).
Method = s6748 recipe (PORTING-STATE s6748): scratch/s6807/lvl3.eep already selects lvl3 in the port (s6809 route reaches
flight 0x00690400 at 61.2 s with the AP below). Retail arm: same eep swapped into the oracle save dir (tools/g3_eep_patch.py
if re-sign needed), recon timings, then 512 dumps flight +2..+41 s. Port arm:
  env SAVE_FROM=scratch/s6807/lvl3.eep SECS=110 CAP0=63 AP=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,50:start \
    zsh tools/g3_port_capture.sh scratch/s6810/port
  python3 tools/g3_oracle_match.py --w 512 --bases 690000,620000 --h 446 --win 60,1024 --winx 85,1191 --dec shift ...
Control: same-run median d over non-matching pairs (must be well above matched d). Report d band + any outlier class.
