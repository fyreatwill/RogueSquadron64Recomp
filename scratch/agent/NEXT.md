# NEXT: G1d step 32 - 21:9 and 16:9 at OSMEM=12
HYPOTHESIS-ID: g1d-widescreen
Known (s6139): ROGUESQ_OSMEM_MB=12 4:3 L1 flight frame correct, 0 crash.
Hypotheses: H-ok (wide aspect + OSMEM=12 holds, heap deficit gone), H-heap-still (wide heap NULL persists), H-wide-render (frame garbage/HUD misanchored at wide).
Run: copy scratch/agent/s6139_run.sh, arms: XENV_EXTRA="ROGUESQ_OSMEM_MB=12 ROGUESQ_ASPECT=21:9 ROGUESQ_FB_DUMP_VI=1" (and 16:9), TITLE_ORIGIN=0x00B90400 MISSION_RE=A90400, HOLD_S=300, LEVEL=1; use the 4:3 12 MB arm as positive control. Read alive_at_end and [heapwalk-top]; view a dump per arm (sips -s format png).
Then: HUD x anchoring, menus/hangar at wide, default OSMEM bundling under ROGUESQ_ASPECT.
Note: macOS sed -i needs '' arg; write scripts via heredoc.
