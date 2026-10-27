# NEXT: G3c(b) close-out - clamp-path check or owner decision on ROGUESQ_CULL_SPIKE
HYPOTHESIS-ID: g3c-owner-visual-b
Hypotheses: H-rsp-emu-clamp (output clamp on saturated lane differs), H-clip/H-retail (legit; RT64 lacks RDP coordinate clamp).
s6379: acc arithmetic matches 90/90 (lane 0). Work unit: extend the [spike-vu] ring to log ALL 8 lanes of vs/vt/preACC and the vd result, rerun lvl2 hold once, replay with tools/agent/rsp_vu_replay.py (extend to 8 lanes + clamp compare to vd). Positive control: saturated lane (FD57 lane1) present. Mismatch -> fix clamp; match -> write owner question in BLOCKED-free note, then take G3c(a) jagged far edge or (c) shake.
