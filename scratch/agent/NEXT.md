# NEXT (s7682)
HYPOTHESIS-ID: g6c-inline-draw-paths

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
s7681: npcShieldUpdate draws via 0x8005940C (view test wrapper) + inline bucket link, not addNpcToVisibilityBucket; the handoff
detector now sees it (tools/apply_s7681_shield_vt.py, sub-0x32-only match). One more handler uses only that inline path:
heavyAttachedAudioEmitterNpcHandler (funcs_19.c, 0x8007BF20 call).
Work unit (offline, at most ONE run): find which DAT subtype(s) dispatch to heavyAttachedAudioEmitterNpcHandler (slot handler
table / dispatcher) and whether handler_model_name() in src/main/rs64_standins.cpp or names_in_item() gives it a stand-in.
Hypotheses: H-none (no stand-in for that subtype: nothing to do, close G6c engineering), H-blind (it has stand-ins: its held
stand-in would linger like the shield; extend the s7681 hook to its 0x8005940C site, same sub filter, same two-arm proof on a level
that has one), H-attached (it draws only while attached to a parent object, so the parent handoff covers it).
If H-none: G6c waits on the owner's look; take the next rung (owner items, backlog 2-9, 20, 22).
One game at a time, SIGKILL only, <=2 CPU-heavy jobs, no repeat-hold soaks.
