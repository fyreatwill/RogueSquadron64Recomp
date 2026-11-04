# NEXT: make the regen tree compile, classify the residual, then link and boot it
HYPOTHESIS-ID: replay-patch-presence

Why: s6863 got tools/regen_replay.sh to exit 0 from pristine, but 8 of 52 files fail -fsyntax-only and 1,960 lines differ from live. Until this closes, a regen is unsafe and hard rule "fixups survive regen" is unproven.
Unit: offline first. zsh scratch/s6863/replay.sh (replay + diff, live hash check), zsh scratch/s6863/syntax.sh (compile check), python3 scratch/s6863/resid.py (residual by tag). Refresh the pristine input once: scratch/agent/s5547_frontchain.sh with fresh paths, since scratch_s5547_regen dates from s5547.
Fix order: funcs_0 g1d_* decls (s6201 carve, default dd path, behaviour) first; funcs_16 brace error; funcs_13 rs5907_hitobj; funcs_24 time.h; funcs_25/26 expected expression; funcs_42 backtrace_symbols_fd conflict (execinfo.h, stripped include); funcs_9 refs into the unwired s6500+ chain.
Hypotheses: H-diag (the whole residual is env-gated diagnostics, regen binary behaves as live) / H-beh (a default-path line differs).
Discriminator: after it compiles, strip diagnostics-only lines from both trees and compare -O2 asm per file as s5547 did (perturbation control must flag). Any asm difference on a default path -> H-beh, decide per line against retail, do not assume live is right (s6285 armed gate was matched to live on that assumption; re-check it). Then a separate build dir needs RECOMP_FUNCS_DIR overridable in CMakeLists (it is a plain set()), lvl1 boot + 120 s hold vs live.
Outcomes: H-diag -> close, add regen_replay.sh + compile check to the docs and CLAUDE regen order (owner file: ask first), remove the dead s4563 check. H-beh -> fix per line and A/B.
Owner judges: docs/owner_sheet_s6860_lvl10_hud_ab.png, docs/owner_sheet_s6861_pause_hud_ab.png.
