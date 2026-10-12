# NEXT: obtain a mission-capable retail handoff for the attached-mesh gap
HYPOTHESIS-ID: m3-attached-mesh-mission-route

The s4666 oracle control was valid and reached the handler, but only in
512-wide attract/demo origins; repeated Start presses did not produce a
mission phase. The next single unit is one retail-oracle run using the
verified post-title sequence from `scratch/s73_post_a_scene/run_mission_keys.sh`:
after the 1024 phase, press Start at relative +3s, +25s, +40s, then A at
+60s, followed by the same handler/`rs_free` watches and whole-RDRAM control.
Do not add a NULL guard or repeat the Start-only route.

Competing hypotheses and the discriminator are the same run's phase-qualified
watch results:

- H1: handler is reached in mission; handler rows plus `rs_free` predecessor
  rows identify the two freed pointers and their retail writer/legitimacy.
- H2: handler is reached but no matching `rs_free` predecessor appears; the
  action-2 call-site mapping is wrong and must be remapped.
- H3: whole-RDRAM control and mission phase qualify but handler is absent; the
  NULL/free gap is route-absent for this covered mission and remains parked.
- H4: whole-RDRAM control or mission phase is absent; the instrument is
  invalid and no conclusion is allowed.

Exact discriminator: whole-RDRAM control plus a mission VI/route transition,
then the two watched-PC summaries. H1 is handler plus matching action-2 free
rows; H2 is handler without matching frees; H3 is qualified mission with no
handler; H4 is missing control or mission phase and is unevaluable.
