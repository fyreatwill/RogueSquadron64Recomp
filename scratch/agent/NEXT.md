# NEXT: G1 — win arms: why ctr1 plateaus at 8 (need 21) and what feeds counter 10
s5826: s5824's end = FAIL arm (counter 2 reached 3 via class-2 descs e5c, cce, a9c destroyed; no-fire runs only lose e5c). Win arms: get(1)>=21 (needs B6A4==0,B6A8==0) or get(10)>=6.
Hypotheses: (a) lv0 DAT supplies only 8 class-1 sources until more NPCs spawn later/with progress; (b) class-1 NPCs despawn out-of-range (s5823) before being killed, so count stays 8; (c) counter 10 is fed by a different writer never reached.
Discriminator: offline from existing logs first: grep `[supply]` cls1 spawn count vs teardown count in s5825_aonly; then one run with A-held approach toward class-1 ground troops while avoiding class-2 (no fire), logging writers of counter 10 (0x80138064 +9*4?) - positive control: the ctr1 sets still fire.
HYPOTHESIS-ID: g1-mission-progression
