# Next work unit

HYPOTHESIS-ID: m5-bus-error-reattribution

s4696 found the early musyxSynthFrame crash was our own VOICE_TRIGGER_CHAIN
diagnostic (unsigned 0x80150000 literal, now S32()). Any earlier crash
attributed to the "musyxSynthFrame bus-error family" (s4672, s4527, etc.) in a
recipe that armed ROGUESQ_LOG_VOICE_TRIGGER_CHAIN may be this bug.

Unit: re-run the canonical title->hangar recipe (run_s4695 style, SPIN_YIELD=0,
VOICE_TRIGGER_CHAIN=1, 4 concurrent) on the fixed build and count (a) crashes,
(b) arms reaching VI 512 hangar origin 0x006AB400. Hypotheses:
- H-diag-was-all: no crashes, all arms reach hangar -> bus-error family closed,
  proceed to M5 plan A16 (docs/M5-AUDIO-PLAN.md).
- H-residual: some arms still crash -> map pc with
  `python3 -I scratch/agent/s4696/map_pc.py <FUNC> <OFF>` (FUNC must live in
  funcs_24.c; edit src path for other files) and name the writer.
Also: check the s4672 `scratch/agent/s4672_overlay_route/` crash for the
0x400149714 signature before reinterpreting it.
