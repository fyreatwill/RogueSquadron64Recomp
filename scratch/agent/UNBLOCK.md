# UNBLOCK s5072 (route 1: refute)
Block (s5071): winctl key injection needs an unlocked/awake display with the SDL window focused.
Premise false: the dependency is only on HOW pad input is delivered. Added ROGUESQ_PAD_OVERRIDE_FILE to lib/N64ModernRuntime/librecomp/src/cont.cpp (file "btn sx sy" read each osContGetReadData; empty = none); no window/focus needed.
Observation: scratch/agent/padovr_test.sh -> padlog baseline btn=0x0000 (call=1), then btn=0x1000 (call=1031), then release 0x0000 (call=1091). Same-run baseline = positive control.
s5069_mission_snap.sh now uses hold() on the override file instead of winctl. Not yet run end-to-end (queued in NEXT.md).
