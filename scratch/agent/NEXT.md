# NEXT: lvl14 FPS60 residual scrape damage - 20 hp per contact TICK, find the re-hit gate
HYPOTHESIS-ID: g3-fps60-contact-damage

State (s6818): scrape deflection fix confirmed on 3 seeds (contacts 7 -> 4, 30 Hz 2). Residual: scrape hp 30 Hz 40 (2x20),
FPS60+fix 80 (4x20 at 15.417/15.6/15.617/15.65 s), FPS60 off 140 (7x20). Contacts at 15.6/15.617/15.65 are 1-2 ticks apart.
Hypotheses:
  H-tick-cooldown: the 20-hp collision damage writer has a re-hit/invulnerability gate counted in TICKS (frame-locked,
    half as long in real time at FPS60) -> fix: scale the counter (or gate on dt-accumulated time) under ROGUESQ_FPS60.
  H-no-gate: damage applies on every contact tick with no gate; FPS60 samples the surface twice as often, so a
    near-tangent pass produces more contact ticks -> fix candidate: scale the per-tick damage by dt*30 under FPS60
    (damage per real contact second matches 30 Hz).
  H-sampling-only: the extra contacts are geometric (sub-tick surface sampling) and damage is already gated by game
    time -> leave as inherent to 60 Hz, close.
Step 1 (offline first): s6816 added an hp-writer trace row (see PORTING-STATE s6816, g3_bolt_attrib.py/g3_guided_attrib.py)
  - grep the s6817 b60fix traces for the writer PC of the 20-hp drops; read that function in
  ../N64Recomp/RecompiledFuncs for a counter compared before the hp sub (lb/lh/lw field, addiu -1 per tick, or a
  timer float decremented by dt). Discriminator: integer tick counter -> H-tick-cooldown; dt-float timer or none ->
  H-no-gate / H-sampling-only.
Step 2: implement the fix as a fixup script (ROGUESQ_FPS60 only, env off-switch), run seed 1 three arms with
  env ARMS="a30 b60fix" SEED=1 zsh scratch/s6817/arms.sh (+ new arm), score with tools/g3_scrape_damage.py and
  tools/g3_death_time.py. Success = FPS60 scrape hp 40 like 30 Hz, retail unchanged.
