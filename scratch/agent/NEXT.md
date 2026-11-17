# NEXT (s7537)
HYPOTHESIS-ID: class-ga-early-spcomplete

s7536: ROGUESQ_SP_LATE=0|1|alt landed; per-state spikes/big hulls equal -> H-colour-only (fidelity only, not a G5b/G5f cause).
Read PORTING-STATE s7536.

Work unit: fold the FPS60 cost soak.
1. tail scratch/agent/SOAK-RESULTS.md for s7536_splate_cost; read scratch/s7536_splate_cost/fps.txt (tools/g1e_level_fps.py rows,
   arms l{1,4,12}d{1,4}{e,l}; e = SP_LATE=0, l = SP_LATE=1). Check cur == lvl and pwr AC / clk <= 1.15 on the arms.log lines.
   If the soak has not run (battery / idle gate), run it yourself on AC: `zsh scratch/agent/soak_queue/s7536_splate_cost.sh`
   (~30 min; split per level if needed, each g1e invocation is one arm).
2. Hypotheses: H-free (late fl_shown within 0.5/s of early on every pair -> SP_LATE=1 becomes an owner fidelity opt-in in
   docs/OWNER-OPT-INS.md; mark the 2 census rows H-latent-FIXED(opt-in) in tools/s7535_ga_census.py so it exits 0 with --controls),
   H-cost (late drops below 59/s anywhere -> deliver sp_complete at the LLE's last RSP input fetch instead of after send_dl:
   instrument the fetch index of the last dma_rdram_to_dmem per task first, GA_CHK has the hook).
3. Never flip the default (owner). OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
