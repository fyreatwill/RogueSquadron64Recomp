# NEXT (s7279): G5c which QoS part removes the load freezes (split QOS_ALL into its five knobs)
HYPOTHESIS-ID: g5c-qos-split
State: QOS_ALL=1 removes CPU-load freezes on L12 (s7277) and L4 (s7278): on-load 52 -> 59.6 fps, real image freezes 3 -> 0,
control 3/3. QOS_ALL = GFX_QOS + GUEST_QOS + PRESENT_QOS + WL_QOS + UPLOAD_QOS (main.cpp s6989). Owner default question open.
Hypotheses: H-guest (the guest CPU / game thread losing P-cores is the freeze: GUEST_QOS alone ~= QOS_ALL);
H-gfx (the RSP gfx / RDP thread: GFX_QOS alone ~= QOS_ALL); H-combo (no single knob suffices, need >= 2).
Commands (one game at a time; HID idle >= 120 s, screen unlocked: ioreg -n Root -d1 | grep CGSSessionScreenIsLocked):
  env LOAD=cpu TAG=l4guest LEVEL=4 GXE=ROGUESQ_GUEST_QOS=1 zsh tools/s7277_toggle_load_arm.zsh
  env LOAD=cpu TAG=l4gfx   LEVEL=4 GXE=ROGUESQ_GFX_QOS=1   zsh tools/s7277_toggle_load_arm.zsh
  python3 tools/s7277_toggle_score.py l4guest ; python3 tools/s7277_toggle_score.py l4gfx
  grep ctl=0 scratch/s7272/l4{guest,gfx}/sheet.txt   # held luma > 0 = real freeze, 0 = black transition
Baselines (same recipe): l4cpu on-load 52.0 fps, 3 real freezes; l4cpuqos 59.6 fps, 0.
Expected: one arm ~59.5 fps / 0 real freezes -> that part carries it (smaller default proposal for the owner);
both ~52 -> H-combo, run GUEST+GFX together next. Do not change the default without the owner.
