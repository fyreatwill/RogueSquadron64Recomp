# NEXT (s7281): fold the L12 QoS minimal-set replicate, then close G5c QoS split
HYPOTHESIS-ID: g5c-qos-split
State (s7280, L4 CPU toggle, single run per arm): none 52.0 fps on-load / 48 gaps>=100 / 3 lit freezes; QOS_ALL 59.6 / 1 / 0;
GUEST 55.0 / 1 / 0; GFX 47.7 / 38 / 1; GUEST+PRESENT+WL+UPLOAD 58.0 / 7 / 0; GUEST+PRESENT 57.9 / 1 / 0 -> H-present selected.
Queued soaks (loop runs them; SOAK_NEEDS_IDLE=120): scratch/agent/soak_queue/s7280_l12_gp.sh, s7280_l12_all.sh.
Expected outcomes (L12 baseline none = 49.4 fps, 5 gaps 250-567 ms, s7277):
  - gp ~= all (both >= ~57 fps on-load, 0 lit holds) -> minimal set replicates on a 2nd level; close the split, update
    OWNER-OPT-INS ("GUEST+PRESENT is the minimal pair") and leave the default question with the owner (backlog item 13).
  - gp clearly < all (> ~3 fps or lit holds in gp only) -> WL/UPLOAD matter on L12's denser scene; the recommendation stays QOS_ALL.
Fold: read SOAK-RESULTS.md tail; scored output is in scratch/agent/soak_results/s7280_l12_*.log; lit holds = sheet ctl=0 with held luma (field 8) > 20, view scratch/s7272/l12*/holds_sheet.jpg.
If the soaks have not run yet (host busy/locked), do not babysit: run one arm in-session only if HID idle >= 120 s and the screen is
unlocked; otherwise take the next non-owner-gated ladder rung (CURRENT-TRUTH Next steps; items 2-13 are all owner-gated).
Do not change the default without the owner.
