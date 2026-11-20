# NEXT (s7714)
HYPOTHESIS-ID: multi-reader-truth-census

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report, then
scratch/agent/CONTRACT-CARRY.md if it exists. If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay 8/8.

s7713 closed the clamp half of the multi-reader class (tools/s7713_multireader_census.py, OSMEM_MB fixed). The OTHER half was only
hand-reviewed with a throwaway heuristic: one ROGUESQ_X whose sites disagree on (a) what UNSET means (default-on `!(e && *e=='0')`
vs default-off `e && *e != '0'`) or (b) which values are truthy (`*e == '1'` vs `*e != '0'`: =2/=yes/=true split). Make it a gate:
  tools/s7714_truth_census.py: per site, isolate the expression on the getenv'd variable only (not the conjuncts on other vars -
  that was all of s7713's 16 heuristic false flags), evaluate it for unset, "0", "1", "2", "t", "yes" (translate the C boolean on
  that var to Python), and flag names whose sites give different on/off for any value. REVIEWED dict for deliberate mode letters
  (CULL_SPIKE 't', DD_WIDEWIN 'tog3', LOG_G1D_RECT '2', G1D_SPRITE_DIAG '2', DIAG_GATE). Owner names that split -> normalise in the
  sanitizer or align the reader, like s7712/s7713.
  Known positive: tools/fixup_game_funcs_vendored.py m5 lines label unset AUDIO_UCODE as audio_stub while main.cpp/rsp.cpp run the
  real ucode (default-on). Must flag (then fix the label in the vendored fixup; it shows after the next regen).
Controls (same run): plant a default-on vs default-off pair -> flag; plant '1'-only vs non-'0' pair -> flag on "2"; FPS60's readers
(all `*f != '0'`) -> agree.
Hypotheses: H-label (only the AUDIO_UCODE diagnostic label splits), H-owner (an owner setting splits on a plausible value like =2 or
=yes), H-none (heuristic noise only; the AUDIO_UCODE label is the sole positive).
Standing check after any src/ or lib/ change: `python3 tools/s7651_gate_sweep.py --jobs 2`. Owner defaults: never flip.
