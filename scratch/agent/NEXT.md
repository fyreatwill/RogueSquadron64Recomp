# NEXT: G3 texture fidelity on the texture-streaming level L6: RT64 vs angrylion with a per-swap RAM snapshot
HYPOTHESIS-ID: g3-flight-fidelity
Why: s7122 found L1 flight RT64 == angrylion (H-equal), but L6 textures could not be judged: with EVERY=20 the RAM snapshot is taken at the swap's first
range, while L6 streams textures during the frame, so angrylion replays garbled textures (magenta/cyan noise). s7123 closed presentation geometry
(centred; narrowness = owner-closed VI_SHAPE). Texture content on a streaming level is the remaining G3 fidelity gap.
Hypotheses:
  H-equal  : with a snapshot per swap, angrylion's L6 textures look like RT64's (residual = edges/speckle as on L1, frac>40 median ~0.02).
  H-tex    : RT64 samples stale or wrong texture data on L6 (TMEM/texture cache hash misses a streamed upload): coherent RT64 colour blocks that
             differ from angrylion on whole materials.
  H-tool   : even EVERY=1 snapshots are taken too early in the swap (textures loaded after the first range): angrylion still garbled -> the
             replay needs a snapshot per range (RNG) or per LOADBLOCK, not a fidelity datum.
Discriminator, one run: tools/s7122_arm.zsh 6 t6 "ROGUESQ_G5B_FRAME_EVERY=1 ROGUESQ_G5B_FRAME_FROM=5000 ROGUESQ_G5B_FRAME_MAX_MB=12000" 120 180
(arm.zsh hardcodes EVERY=20 in XENV_EXTRA; the extra env comes later on the line, check it wins, or edit a copy). L6 flight swaps were 4282..9542 in s7122
(c6.swaps). Replay ~300 consecutive swaps with scratch/s7098/frame_replay16 as s7122 did, score with tools/s7122_fidelity.py (rect from
tools/s7123_present_rect.py: capture rect 20,15,279,240) and build a sheet with tools/s7122_sheet.py. Delete the stream after replay (~10 GB).
Positive control: the s7122 painted-block control on one replay (one 400 px region). Same-run control for H-tool: a replay of the same swap from an
EVERY=1 snapshot vs one 20 swaps older must differ on streamed materials only.
Outcomes: H-equal -> G3 flight fidelity closed for L1+L6, take the next G3 item (hangar artifacts list in CURRENT-TRUTH). H-tex -> name the material,
dump its TMEM load and RT64's texture hash for that swap. H-tool -> fix the snapshot point in dpc_bridge.cpp (snapshot at the first LOADBLOCK/LOADTILE of
each range) and rerun.
