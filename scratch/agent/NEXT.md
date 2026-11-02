# NEXT: G1e — cut the factor5_ucode interpreter cost (76% of the Gfx thread at dd4 FPS60, s6716)
HYPOTHESIS-ID: g1e-ucode-interp

G3 per-mission sim sweep is closed (s6773, missions 3-19 pinned-identical to retail). Next ladder rung with an
engineering lever: G1e. FPS60 holds 60 at dd1 but dd2 ~48-50, dd4 ~44 fps; the serial gfx task binds and s6716's
xctrace put 76% of Gfx-thread samples as factor5_ucode SELF (recompiled RSP ucode in build/factor5_ucode/*.c,
generated; hand edits go in tools/fixup_factor5_ucode.py).
Hypotheses (one profile splits them):
- H-vec: a few vector-op helpers/templates (VMULF/VMACF/VMADN accumulator, VRCP, VCH/VCL clip) dominate -> SIMD or
  specialisation of those helpers.
- H-dispatch: per-instruction overhead (jump-table dispatch, DMEM bounds/byteswap per load/store, the s6762 iteration
  counter at L_1090) dominates -> hoist/cheapen the per-op scaffolding.
- H-hotloop: one ucode loop (vertex transform / clip) is most of it -> optimise just that block.
Work unit:
1. scratch/agent/s6716_bridge.zsh recipe (lvl5 FPS60 dd4), attach `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
   xcrun xctrace record --template 'Time Profiler' --attach <pid> --time-limit 15s` at ~100 s; tools/xctrace_tp.py
   --dump-addrs on the factor5_ucode self samples, lldb `image lookup -a` to lines; bucket by ucode label/op helper.
2. Land the top lever in the fixup script (regen order: make_elf -> N64Recomp -> fixup_game_funcs -> cmake; the ucode
   fixup is tools/fixup_factor5_ucode.py).
3. Same-run control: RDP stream must be byte-identical (hash per gfx task, opt-out env restoring the old path, toggled
   within ONE run, phase-gated) and fps/tasks-per-s A/B from [g1b] lines.
Discriminating outcomes: profile buckets name H-vec / H-dispatch / H-hotloop; success = identical RDP hashes and a
measurable task-ms drop at dd4.
