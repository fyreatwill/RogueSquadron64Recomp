# M5: wire A10 apply into the regen chain, then relax one guard class

HYPOTHESIS-ID: m5-audio-destub-mission-route

s4808: A10 guards live at mission, 265 evaluations all in range, writer legit (see PORTING-STATE s4808). tools/apply_s4681_m5_a10.py is not called by any fixup stage; its post-check aborts when run on an already-partially-patched tree.
Work unit: (1) make the script idempotent/regen-safe and invoke it from the post-fixup stage; (2) build one arm with the songtempo guard class relaxed (ROGUESQ_A10_GUARD_OFF=1 already exists) and run it vs default at hangar then mission, phase-gated, in one iteration; record ORIGIN.
Discriminator: GUARD_OFF arm crash=0 and identical VI progression => guards are dead code at these phases; any crash => guard still protecting something (name writer).
