# NEXT: hangar-length default-flags run (ring-lap fix now default)

HYPOTHESIS-ID: wild-setcimg-writeback

s4549: wild SETCIMG origin = ring-lap overwrite (s4283-s4287); WRAP_FLUSH+shadow+restore now default ON. Open (s4287 Q1): in a >=150 s run that reaches hangar VI 512 with pure defaults, are odd cimgs / [fb-fl-writeback] hit=1 / fb-set growth absent? Use s4549d_defaults.sh as template with sleep 170 plus the s4548 probe.sh key route for the hangar; arms: default vs ROGUESQ_DPC_WRAP_FLUSH=0 ROGUESQ_S4272=0 (control must show odd>0). Outcomes: default odd=0 in hangar => H-ring-lap covers hangar; odd>0 in hangar => a different hangar writer (new lead).
