# NEXT: (optional, low value) generated call-site gate for the synth-read / lowfield store hooks
HYPOTHESIS-ID: host-selftime-audit
Context (s7068): ROGUESQ_DIAG_GATE gates landed; residual [Game] 0 diag = rs64_s4307_synth_read 70 + rs64_m5_lowfield_store 42
samples per ~268 s flight (function entry from generated code, ~0.1% of a core). Everything owner-facing is awaiting owner
flights (CURRENT-TRUTH Next steps 1-12). AN OWNER REPORT PREEMPTS THIS.
Hypotheses: H-callsite (an inline `if (g_rs64_diag_hooks)` before each generated call removes the residual) vs H-floor (the
residual is sampler attribution of the surrounding guest code; gating changes nothing).
Work: emit the guard in tools/apply_s4307_synth_read_join.py / apply_s4340_m5_lowfield_writer.py (and the s4982/s4986/s4542/s4805
needle strings that match those lines; fixup_live_replay.py moves lowfield lines by regex) -> full regen order make_elf ->
N64Recomp -> fixup_game_funcs -> cmake. Measure with scratch/s7068/both.zsh (on vs ROGUESQ_DIAG_GATE=0).
If the needle chain makes this risky (many patches key on the exact line text), CLOSE the audit instead and take the next
ladder rung in ITERATION.md 3c.
