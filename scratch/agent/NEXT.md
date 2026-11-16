# NEXT (s7434)
HYPOTHESIS-ID: gfx-glue-cost

Class CQ (CURRENT-TRUTH Next steps item 1): what the Gfx Thread spends outside the F5 ucode. s7433's sample(1) run
(owner recipe FPS60 dd4 16:9, lvl1 autopilot flight) puts the Gfx Thread at ~9 ms/frame: factor5_ucode_nmac 42% self,
rsp_dpc_submit_impl 9%, _platform_memmove 5%, rs64_dpc_record_submit_impl 4% (bridge edit walkers), TMEMHasher 4%,
rs64LoadBlockRuns 3.5%; rs64_dpc_defer_end_impl 1.50 ms/frame inclusive.
Step 1 (offline, no run): python3 tools/s7433_probe_cost.py-style tree walk on scratch/s7433/sample_{4,8}.txt (busy-off
windows) for threads 'Gfx Thread': inclusive ms/frame per child of rs64_run_lle_gfx and of rs64_dpc_defer_end_impl, and
the callers of every _platform_memmove sample. Hypotheses: H-copy (memmove is a whole-buffer copy per task that could be
a range copy: name the caller and the byte count), H-walk (the bridge walkers re-scan the same RDP bytes several times:
record + defer_end + submit each walk the stream), H-rt64 (most of defer_end is RT64's own processRDPLists/TMEM hashing,
which we do not own -> close). Discriminator: the share of defer_end + record_submit that is our code (rs64_*/dpc_bridge
frames with only library calls beneath) vs RT64:: frames.
Step 2 only if H-copy or H-walk >= 0.5 ms/frame: fix it, then rerun env S7431_ARM=N zsh tools/s7433_probe_cost.sh with
--threads 'Gfx Thread' analysis (control: ROGUESQ_DIAG_BUSY_US=500 busy per gfx task must read back on the Gfx Thread),
old vs new by an env kill-switch in ONE run if possible (toggle), else two runs same recipe.
If H-rt64: close CQ and take ITERATION.md 3c's next rung (new idiom-class audit or the G5 renaming sweep).
