# NEXT (s5897): per-fire heading vs direction-to-survivor sample (no descriptor join)
Context (s5896): +0x34 join impossible; node +0x14 flags don't split killed/survivor. Survivors ~10 slots never aimed within ~2 u (s5894).
Competing: (a) survivors off-axis for the routed path (H-aim; autopilot-fixable by steering toward a survivor); (b) bolt lifetime/range too short (H-range); (c) survivors only hittable by a different weapon/msg path.
Discriminator: at each bolt fire in the sphere probe, log bolt origin/dir and the unit vector to the nearest survivor centre (min fap2 over c1 ids with segin==0), plus the angle in degrees; control: killed slots 86/66 must show angle~0 at their hit. Then arm 2: poke player pos/heading toward a survivor (ROGUESQ_PLPOS_POKE recipe s5892) and see if msg5 count rises. Angle large + poke fixes => (a); poke aimed ok but no hit => (b)/(c).
Recipe base: scratch/agent/s5896_did.sh.
HYPOTHESIS-ID: g1-mission-progression
