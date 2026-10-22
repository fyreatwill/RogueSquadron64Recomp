# NEXT (s5896): join survivor slot ids to descriptor ids and sample heading per frame around fire
Context (s5895): stick echo reaches player record (control OK); heading rotates even with stick idle; survivors (~10 slots) never within ~2 u of bolt line (s5894).
Competing: (a) survivors are geometrically behind/off-axis for the ship's routed path (H-aim, autopilot-fixable); (b) survivors are non-targets by descriptor kind (e.g. scenery/id class); (c) bolt lifetime too short (H-range-limited).
Discriminator: extend [s5855] line with descriptor id (slot node +0x34 -> +0x78) and per-frame heading words w5/w7 at each fire; control: killed slots 86/66/15f must show their descriptor ids and fap2~0. Descriptor kinds uniform across survivors => (a)/(c); distinct non-target kind => (b).
HYPOTHESIS-ID: g1-mission-progression
